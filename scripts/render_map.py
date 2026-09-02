#!/usr/bin/env python3
"""Validate onboarding state and render a self-contained HTML learning map."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path


KINDS = {"orientation", "check", "setup", "trace", "lab", "task", "review"}
TARGETS = {"recognize", "operate", "modify"}
STATUSES = {"locked", "ready", "active", "done", "revisit", "skipped"}
CODENAME = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$")
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
LABEL_KEYS = {
    "filter_all",
    "filter_ready",
    "filter_active",
    "filter_done",
    "filter_revisit",
    "details",
    "why",
    "evidence",
    "requires",
    "none",
    "nodes",
    "minutes",
    "footer",
}
THEME_COLOR_KEYS = {
    "ink",
    "muted",
    "paper",
    "background_top",
    "background_bottom",
    "path",
    "accent",
    "done",
    "locked",
    "revisit",
}


def fail(message: str) -> None:
    raise ValueError(message)


def load_state(path: Path) -> dict:
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"State file does not exist: {path}")
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
    if not isinstance(state, dict):
        fail("State root must be an object")
    return state


def require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be non-empty text")
    return value.strip()


def validate(state: dict) -> None:
    if state.get("version") != 1:
        fail("version must be 1")
    require_text(state.get("language"), "language")

    labels = state.get("labels")
    if not isinstance(labels, dict):
        fail("labels must be an object")
    if set(labels) != LABEL_KEYS:
        missing = sorted(LABEL_KEYS - set(labels))
        extra = sorted(set(labels) - LABEL_KEYS)
        fail(f"labels keys are invalid; missing={missing}, extra={extra}")
    for field in LABEL_KEYS:
        require_text(labels.get(field), f"labels.{field}")

    theme = state.get("theme")
    if not isinstance(theme, dict):
        fail("theme must be an object")
    expected_theme_keys = THEME_COLOR_KEYS | {"logo"}
    if set(theme) != expected_theme_keys:
        missing = sorted(expected_theme_keys - set(theme))
        extra = sorted(set(theme) - expected_theme_keys)
        fail(f"theme keys are invalid; missing={missing}, extra={extra}")
    for field in THEME_COLOR_KEYS:
        value = theme.get(field)
        if not isinstance(value, str) or not HEX_COLOR.fullmatch(value):
            fail(f"theme.{field} must be a six-digit CSS hex color")
    if not isinstance(theme.get("logo"), str):
        fail("theme.logo must be text")

    project = state.get("project")
    if not isinstance(project, dict):
        fail("project must be an object")
    for field in ("name", "root", "goal"):
        require_text(project.get(field), f"project.{field}")

    learner = state.get("learner")
    if not isinstance(learner, dict):
        fail("learner must be an object")
    require_text(learner.get("role"), "learner.role")
    for field in ("experience", "placed_out"):
        if not isinstance(learner.get(field), list):
            fail(f"learner.{field} must be an array")

    nodes = state.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        fail("nodes must be a non-empty array")
    sessions = state.get("sessions")
    if not isinstance(sessions, list):
        fail("sessions must be an array")

    seen: set[str] = set()
    for index, node in enumerate(nodes):
        label = f"nodes[{index}]"
        if not isinstance(node, dict):
            fail(f"{label} must be an object")
        for field in ("codename", "title", "summary", "why", "evidence", "icon"):
            require_text(node.get(field), f"{label}.{field}")
        if not isinstance(node.get("image"), str):
            fail(f"{label}.image must be text")
        code = node["codename"]
        if not CODENAME.fullmatch(code):
            fail(f"{label}.codename must use uppercase words and hyphens")
        if code in seen:
            fail(f"Duplicate codename: {code}")
        seen.add(code)
        if node.get("kind") not in KINDS:
            fail(f"{label}.kind is invalid")
        if node.get("target") not in TARGETS:
            fail(f"{label}.target is invalid")
        if node.get("status") not in STATUSES:
            fail(f"{label}.status is invalid")
        if not isinstance(node.get("requires"), list):
            fail(f"{label}.requires must be an array")
        if not isinstance(node.get("project_paths"), list):
            fail(f"{label}.project_paths must be an array")
        minutes = node.get("estimated_minutes")
        if not isinstance(minutes, int) or minutes < 1:
            fail(f"{label}.estimated_minutes must be a positive integer")

    for index, node in enumerate(nodes):
        for requirement in node["requires"]:
            if requirement not in seen:
                fail(f"nodes[{index}] requires unknown codename: {requirement}")
            if requirement == node["codename"]:
                fail(f"nodes[{index}] cannot require itself")

    graph = {node["codename"]: node["requires"] for node in nodes}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(code: str) -> None:
        if code in visiting:
            fail(f"Dependency cycle includes: {code}")
        if code in visited:
            return
        visiting.add(code)
        for requirement in graph[code]:
            visit(requirement)
        visiting.remove(code)
        visited.add(code)

    for code in graph:
        visit(code)

    active = [node["codename"] for node in nodes if node["status"] == "active"]
    if len(active) > 1:
        fail(f"Only one node can be active: {active}")
    status_by_code = {node["codename"]: node["status"] for node in nodes}
    for node in nodes:
        if node["status"] in {"ready", "active"}:
            blocked = [
                code
                for code in node["requires"]
                if status_by_code[code] not in {"done", "skipped"}
            ]
            if blocked:
                fail(f"{node['codename']} is {node['status']} but requires incomplete nodes: {blocked}")

    for index, session in enumerate(sessions):
        label = f"sessions[{index}]"
        if not isinstance(session, dict):
            fail(f"{label} must be an object")
        expected = {"date", "codename", "result", "evidence", "gap"}
        if set(session) != expected:
            fail(f"{label} must contain only: {sorted(expected)}")
        for field in expected:
            require_text(session.get(field), f"{label}.{field}")
        if session["codename"] not in seen:
            fail(f"{label}.codename is unknown: {session['codename']}")
        if session["result"] not in {"done", "revisit", "stopped"}:
            fail(f"{label}.result is invalid")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_node(node: dict, index: int, labels: dict) -> str:
    status = node["status"]
    paths = "".join(f"<code>{esc(path)}</code>" for path in node["project_paths"])
    requires = ", ".join(node["requires"]) or labels["none"]
    command = f"$onboarding {node['codename']}"
    image = ""
    if node["image"]:
        image = f'<img class="node-image" src="{esc(node["image"])}" alt="">'
    return f"""
    <article class="node {esc(status)}" data-status="{esc(status)}" id="{esc(node['codename'])}">
      <div class="step">{index + 1}</div>
      <div class="badge" aria-hidden="true">{esc(node['icon'])}</div>
      <div class="card">
        {image}
        <div class="meta"><span>{node['estimated_minutes']} {esc(labels['minutes'])}</span></div>
        <p class="codename">{esc(node['codename'])}</p>
        <h2>{esc(node['title'])}</h2>
        <p>{esc(node['summary'])}</p>
        <details>
          <summary>{esc(labels['details'])}</summary>
          <dl>
            <dt>{esc(labels['why'])}</dt><dd>{esc(node['why'])}</dd>
            <dt>{esc(labels['evidence'])}</dt><dd>{esc(node['evidence'])}</dd>
            <dt>{esc(labels['requires'])}</dt><dd>{esc(requires)}</dd>
          </dl>
          <div class="paths">{paths}</div>
        </details>
        <button type="button" data-command="{esc(command)}">{esc(command)}</button>
      </div>
    </article>"""


def render(state: dict) -> str:
    project = state["project"]
    learner = state["learner"]
    labels = state["labels"]
    theme = state["theme"]
    nodes = state["nodes"]
    complete = sum(node["status"] in {"done", "skipped"} for node in nodes)
    percent = round(complete * 100 / len(nodes))
    node_html = "\n".join(render_node(node, index, labels) for index, node in enumerate(nodes))
    return f"""<!doctype html>
<html lang="{esc(state['language'])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(project['name'])}</title>
<style>
:root{{--ink:{theme['ink']};--muted:{theme['muted']};--paper:{theme['paper']};--grass:{theme['background_bottom']};--grass2:{theme['background_top']};--path:{theme['path']};--line:{theme['muted']};--ready:{theme['accent']};--done:{theme['done']};--locked:{theme['locked']};--active:{theme['accent']};--revisit:{theme['revisit']};}}
*{{box-sizing:border-box}} html{{scroll-behavior:smooth}} body{{margin:0;color:var(--ink);font:16px/1.45 ui-rounded,"SF Pro Rounded",system-ui,sans-serif;background:linear-gradient(var(--grass2),var(--grass) 52%,var(--paper))}}
header{{position:sticky;top:0;z-index:5;padding:14px 20px;background:rgba(255,253,242,.92);backdrop-filter:blur(10px);border-bottom:2px solid rgba(38,50,37,.15)}}
.top{{max-width:840px;margin:auto;display:grid;grid-template-columns:1fr auto;gap:10px;align-items:end}} h1{{font-size:clamp(22px,5vw,38px);line-height:1.05;margin:0}} .goal{{margin:6px 0 0;color:var(--muted)}}
.meter{{min-width:150px;text-align:right;font-weight:800}} progress{{display:block;width:150px;height:12px;accent-color:var(--done)}}
.filters{{max-width:840px;margin:10px auto 0;display:flex;gap:6px;overflow:auto}} .filters button{{white-space:nowrap}}
main{{position:relative;max-width:840px;margin:auto;padding:42px 18px 120px;overflow:hidden}} main:before{{content:"";position:absolute;left:50%;top:0;bottom:0;width:58px;transform:translateX(-50%);background:var(--path);border:3px solid rgba(143,117,67,.35);border-radius:45% 55% 48% 52%;box-shadow:inset 0 0 0 8px rgba(255,255,255,.22)}}
.node{{position:relative;display:grid;grid-template-columns:1fr 84px 1fr;align-items:center;min-height:230px}} .node:nth-child(odd) .card{{grid-column:1}} .node:nth-child(even) .card{{grid-column:3}} .node:nth-child(odd) .badge,.node:nth-child(even) .badge{{grid-column:2}}
.badge{{grid-row:1;z-index:2;justify-self:center;display:grid;place-items:center;width:70px;height:70px;font-size:31px;background:var(--paper);border:5px solid var(--ready);border-radius:50%;box-shadow:0 7px 0 rgba(79,83,45,.2)}}
.step{{position:absolute;left:calc(50% + 34px);top:74px;z-index:3;background:var(--ink);color:#fff;border-radius:10px;padding:2px 7px;font-size:12px;font-weight:800}}
.card{{grid-row:1;background:var(--paper);border:2px solid rgba(38,50,37,.18);border-radius:22px;padding:18px;box-shadow:0 9px 0 rgba(80,85,47,.16);max-width:340px}} .node:nth-child(odd) .card{{justify-self:end}} .node:nth-child(even) .card{{justify-self:start}}
.node-image{{display:block;width:100%;height:120px;object-fit:cover;border-radius:13px;margin-bottom:12px}}
.meta{{display:flex;gap:6px;flex-wrap:wrap}} .meta span,.codename{{font-size:11px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}} .meta span{{padding:3px 7px;background:#edf0df;border-radius:20px}} .codename{{color:var(--active);margin:12px 0 2px}} h2{{font-size:21px;line-height:1.1;margin:0 0 8px}} p{{margin:7px 0}} details{{margin-top:12px}} summary{{cursor:pointer;font-weight:750}} dl{{display:grid;grid-template-columns:70px 1fr;gap:5px;margin:10px 0}} dt{{font-weight:800}} dd{{margin:0}} .paths{{display:flex;gap:5px;flex-wrap:wrap}} code{{background:#eef0e3;border-radius:5px;padding:2px 5px;font-size:12px}}
button{{border:1px solid rgba(38,50,37,.18);border-radius:10px;background:#fff;padding:7px 10px;cursor:pointer;font-weight:700}} .card>button{{width:100%;margin-top:12px;background:var(--ink);color:white}}
.done .badge{{border-color:var(--done)}} .active .badge{{border-color:var(--active);animation:pulse 1.6s infinite}} .revisit .badge{{border-color:var(--revisit)}} .locked{{filter:grayscale(.8);opacity:.62}} .skipped{{opacity:.67}} .hidden{{display:none}}
@keyframes pulse{{50%{{transform:scale(1.08)}}}}
.legend{{max-width:840px;margin:auto;padding:0 20px 40px;color:var(--muted)}}
@media(max-width:680px){{.top{{grid-template-columns:1fr}}.meter{{text-align:left}}.node{{grid-template-columns:68px 1fr;min-height:210px}}main:before{{left:51px}}.node .badge,.node:nth-child(odd) .badge,.node:nth-child(even) .badge{{grid-column:1;justify-self:center}}.node .card,.node:nth-child(odd) .card,.node:nth-child(even) .card{{grid-column:2;justify-self:stretch;max-width:none}}.step{{left:69px;top:70px}}}}
@media print{{header{{position:static}}.filters,.card>button{{display:none}}body{{background:#fff}}main:before{{background:#f3e8c7}}.node{{break-inside:avoid}}}}
</style>
</head>
<body>
<header>
  <div class="top"><div>{f'<img src="{esc(theme["logo"])}" alt="" style="max-width:120px;max-height:42px;margin-bottom:8px">' if theme['logo'] else ''}<h1>{esc(project['name'])}</h1><p class="goal">{esc(project['goal'])}<br>{esc(learner['role'])}</p></div><div class="meter">{complete}/{len(nodes)} {esc(labels['nodes'])}<progress value="{complete}" max="{len(nodes)}">{percent}%</progress></div></div>
  <nav class="filters"><button data-filter="all">{esc(labels['filter_all'])}</button><button data-filter="ready">{esc(labels['filter_ready'])}</button><button data-filter="active">{esc(labels['filter_active'])}</button><button data-filter="done">{esc(labels['filter_done'])}</button><button data-filter="revisit">{esc(labels['filter_revisit'])}</button></nav>
</header>
<main>{node_html}</main>
<p class="legend">{percent}% · {esc(labels['footer'])}</p>
<script>
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{{
  const filter=button.dataset.filter;
  document.querySelectorAll('.node').forEach(node=>node.classList.toggle('hidden',filter!=='all'&&node.dataset.status!==filter));
}}));
async function copyText(value) {{
  if (navigator.clipboard && window.isSecureContext) {{
    try {{ await navigator.clipboard.writeText(value); return; }} catch (error) {{}}
  }}
  const field=document.createElement('textarea'); field.value=value; field.style.position='fixed'; field.style.opacity='0';
  document.body.appendChild(field); field.select(); document.execCommand('copy'); field.remove();
}}
document.querySelectorAll('[data-command]').forEach(button=>button.addEventListener('click',async()=>{{
  await copyText(button.dataset.command);
  const old=button.textContent; button.textContent='✓ '+old; setTimeout(()=>button.textContent=old,1200);
}}));
</script>
</body>
</html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path, help="Path to state.json")
    parser.add_argument("--output", type=Path, help="HTML output path")
    parser.add_argument("--check", action="store_true", help="Validate without rendering")
    args = parser.parse_args()

    try:
        state = load_state(args.state)
        validate(state)
        if args.check:
            print(f"Valid onboarding state: {args.state}")
            return 0
        output = args.output or args.state.with_name("map.html")
        output.write_text(render(state), encoding="utf-8")
        print(f"Rendered onboarding map: {output}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
