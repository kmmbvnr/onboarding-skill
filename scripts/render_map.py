#!/usr/bin/env python3
"""Validate onboarding state and render a self-contained HTML learning map."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import html
import json
import re
import subprocess
import sys
import webbrowser
from pathlib import Path


KINDS = {"orientation", "check", "setup", "trace", "lab", "task", "review"}
TARGETS = {"recognize", "operate", "modify"}
STATUSES = {"locked", "ready", "active", "waiting", "done", "revisit", "skipped"}
ENVIRONMENT_STATUSES = {"unknown", "ready", "partial", "blocked"}
BLOCKER_SCOPES = {"machine", "service", "access", "project", "unknown"}
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

    preferences = state.get("preferences")
    if preferences is not None:
        if not isinstance(preferences, dict) or set(preferences) != {"editor"}:
            fail("preferences must contain only editor")
        if preferences.get("editor") not in {"zed", "code", "cursor", "subl"}:
            fail("preferences.editor is invalid")

    blocked_node_refs: list[tuple[str, str]] = []
    environment = state.get("environment")
    if environment is not None:
        if not isinstance(environment, dict):
            fail("environment must be an object")
        expected = {"checked_at", "status", "working", "blockers"}
        if set(environment) != expected:
            fail(f"environment must contain only: {sorted(expected)}")
        require_text(environment.get("checked_at"), "environment.checked_at")
        if environment.get("status") not in ENVIRONMENT_STATUSES:
            fail("environment.status is invalid")
        working = environment.get("working")
        if not isinstance(working, list):
            fail("environment.working must be an array")
        for index, fact in enumerate(working):
            require_text(fact, f"environment.working[{index}]")
        blockers = environment.get("blockers")
        if not isinstance(blockers, list):
            fail("environment.blockers must be an array")
        blocker_ids: set[str] = set()
        for index, blocker in enumerate(blockers):
            label = f"environment.blockers[{index}]"
            required_blocker = {"id", "scope", "summary", "evidence", "next_action"}
            optional_blocker = {"waiting_for", "blocks"}
            if not isinstance(blocker, dict):
                fail(f"{label} must be an object")
            missing = required_blocker - set(blocker)
            extra = set(blocker) - required_blocker - optional_blocker
            if missing or extra:
                fail(f"{label} keys are invalid; missing={sorted(missing)}, extra={sorted(extra)}")
            blocker_id = require_text(blocker.get("id"), f"{label}.id")
            if not CODENAME.fullmatch(blocker_id):
                fail(f"{label}.id must use uppercase words and hyphens")
            if blocker_id in blocker_ids:
                fail(f"Duplicate environment blocker: {blocker_id}")
            blocker_ids.add(blocker_id)
            if blocker.get("scope") not in BLOCKER_SCOPES:
                fail(f"{label}.scope is invalid")
            for field in ("summary", "evidence", "next_action"):
                require_text(blocker.get(field), f"{label}.{field}")
            has_waiting_for = "waiting_for" in blocker
            has_blocks = "blocks" in blocker
            if has_waiting_for != has_blocks:
                fail(f"{label} must contain both waiting_for and blocks")
            if has_waiting_for:
                require_text(blocker.get("waiting_for"), f"{label}.waiting_for")
                blocked = blocker.get("blocks")
                if not isinstance(blocked, list) or not blocked:
                    fail(f"{label}.blocks must be a non-empty array")
                for code in blocked:
                    if not isinstance(code, str) or not CODENAME.fullmatch(code):
                        fail(f"{label}.blocks must contain node codenames")
                    blocked_node_refs.append((blocker_id, code))
        if environment["status"] == "ready" and blockers:
            fail("environment.status ready cannot have blockers")
        if environment["status"] in {"partial", "blocked"} and not blockers:
            fail(f"environment.status {environment['status']} requires a blocker")

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
        if "chapter" in node:
            require_text(node.get("chapter"), f"{label}.chapter")
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
        wait = node.get("wait")
        if node.get("status") == "waiting":
            expected_wait = {"waiting_for", "check_after", "check_action"}
            if not isinstance(wait, dict) or set(wait) != expected_wait:
                fail(f"{label}.wait must contain only: {sorted(expected_wait)}")
            require_text(wait.get("waiting_for"), f"{label}.wait.waiting_for")
            check_after = require_text(
                wait.get("check_after"), f"{label}.wait.check_after"
            )
            try:
                datetime.date.fromisoformat(check_after)
            except ValueError:
                fail(f"{label}.wait.check_after must use YYYY-MM-DD")
            require_text(wait.get("check_action"), f"{label}.wait.check_action")
        elif "wait" in node:
            fail(f"{label}.wait is allowed only when status is waiting")
        if not isinstance(node.get("requires"), list):
            fail(f"{label}.requires must be an array")
        if not isinstance(node.get("project_paths"), list):
            fail(f"{label}.project_paths must be an array")
        minutes = node.get("estimated_minutes")
        if not isinstance(minutes, int) or not 1 <= minutes <= 25:
            fail(f"{label}.estimated_minutes must be between 1 and 25; split longer work")

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
    blocked_codes = {code for _, code in blocked_node_refs}
    for blocker_id, code in blocked_node_refs:
        if code not in seen:
            fail(f"Environment blocker {blocker_id} blocks unknown codename: {code}")
        if status_by_code[code] in {"ready", "active"}:
            fail(f"Environment blocker {blocker_id} blocks {code}, but the node is {status_by_code[code]}")

    if environment is not None and environment["status"] in {"partial", "blocked"}:
        available = {
            code
            for code, status in status_by_code.items()
            if status in {"ready", "active", "revisit"} and code not in blocked_codes
        }
        if environment["status"] == "partial" and not available:
            fail("environment.status partial requires an unblocked available node")
        if environment["status"] == "blocked" and available:
            fail(f"environment.status blocked has unblocked available nodes: {sorted(available)}")

    for node in nodes:
        if node["status"] in {"ready", "active", "waiting"}:
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


def open_map(path: Path) -> tuple[bool, str]:
    """Open a rendered map with the browser handler, then the OS opener."""
    errors: list[str] = []
    resolved = path.resolve()
    try:
        if webbrowser.open(resolved.as_uri(), new=2):
            return True, ""
        errors.append("the default browser handler returned false")
    except (OSError, webbrowser.Error) as exc:
        errors.append(f"the default browser handler failed: {exc}")

    command: list[str] | None = None
    if sys.platform == "darwin":
        command = ["open", str(resolved)]
    elif sys.platform.startswith("linux"):
        command = ["xdg-open", str(resolved)]
    elif sys.platform == "win32":
        command = ["cmd", "/c", "start", "", str(resolved)]

    if command is None:
        errors.append(f"no fallback opener is defined for {sys.platform}")
        return False, "; ".join(errors)

    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError as exc:
        errors.append(f"the system opener failed: {exc}")
        return False, "; ".join(errors)

    if result.returncode == 0:
        return True, ""
    detail = result.stderr.strip() or f"exit code {result.returncode}"
    errors.append(f"the system opener failed: {detail}")
    return False, "; ".join(errors)


UI_TEXT = {
    "en": {
        "claim": "Claim reward",
        "claimed": "Reward claimed",
        "locked": "Locked",
        "skipped": "Skipped",
        "copied": "Copied",
        "rewards": "rewards",
        "live": "Auto-updates",
        "filter_waiting": "Waiting",
        "waiting_for": "Waiting for",
        "check_after": "Check after",
        "check_action": "Check",
        "checks": "Checks passed",
        "blockers": "Blockers",
        "environment": {
            "unknown": "Environment not checked",
            "ready": "Environment ready",
            "partial": "Environment partly ready",
            "blocked": "Environment blocked",
        },
        "status": {
            "ready": "Ready",
            "active": "Now",
            "done": "Done",
            "revisit": "Try again",
            "waiting": "Waiting",
            "locked": "Locked",
            "skipped": "Skipped",
        },
    },
    "ru": {
        "claim": "Забрать награду",
        "claimed": "Награда получена",
        "locked": "Пока закрыто",
        "skipped": "Пропущено",
        "copied": "Команда скопирована",
        "rewards": "наград",
        "live": "Обновляется автоматически",
        "filter_waiting": "Ожидание",
        "waiting_for": "Ждём",
        "check_after": "Проверить после",
        "check_action": "Что проверить",
        "checks": "Проверено",
        "blockers": "Блокеры",
        "environment": {
            "unknown": "Окружение не проверено",
            "ready": "Окружение готово",
            "partial": "Окружение готово частично",
            "blocked": "Окружение заблокировано",
        },
        "status": {
            "ready": "Можно начать",
            "active": "Сейчас",
            "done": "Готово",
            "revisit": "Повторить",
            "waiting": "Ждём ответа",
            "locked": "Закрыто",
            "skipped": "Пропущено",
        },
    },
}


def render_node(node: dict, index: int, labels: dict, ui: dict) -> str:
    status = node["status"]
    paths = "".join(f"<code>{esc(path)}</code>" for path in node["project_paths"])
    requires = ", ".join(node["requires"]) or labels["none"]
    command = f"$onboarding {node['codename']}"
    image = ""
    if node["image"]:
        image = f'<img class="node-image" src="{esc(node["image"])}" alt="">'
    if status == "done":
        action = (
            f'<button class="reward" type="button" data-reward="{esc(node["codename"])}">'
            f'⭐ {esc(ui["claim"])}</button>'
        )
    elif status == "locked":
        action = f'<button type="button" disabled>🔒 {esc(ui["locked"])}</button>'
    elif status == "waiting":
        wait = node["wait"]
        action = (
            '<div class="wait-status">'
            f'<strong>⏳ {esc(ui["waiting_for"])}: {esc(wait["waiting_for"])}</strong>'
            f'<span>{esc(ui["check_after"])}: {esc(wait["check_after"])}</span>'
            f'<span>{esc(ui["check_action"])}: {esc(wait["check_action"])}</span>'
            '</div>'
        )
    elif status == "skipped":
        action = f'<p class="terminal-status">{esc(ui["skipped"])}</p>'
    else:
        action = f'<button type="button" data-command="{esc(command)}">{esc(command)}</button>'
    return f"""
    <article class="node {esc(status)}" data-status="{esc(status)}" data-code="{esc(node['codename'])}" id="{esc(node['codename'])}">
      <div class="step">{index + 1}</div>
      <div class="badge" aria-hidden="true">{esc(node['icon'])}</div>
      <div class="card">
        {image}
        <div class="meta"><span>{node['estimated_minutes']} {esc(labels['minutes'])}</span><span class="status-pill">{esc(ui['status'][status])}</span></div>
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
        {action}
      </div>
    </article>"""


def render_nodes(nodes: list[dict], labels: dict, ui: dict) -> str:
    output: list[str] = []
    previous_chapter: str | None = None
    for index, node in enumerate(nodes):
        chapter = node.get("chapter")
        if chapter and chapter != previous_chapter:
            output.append(
                f'<section class="chapter-marker"><span>{esc(chapter)}</span></section>'
            )
        output.append(render_node(node, index, labels, ui))
        previous_chapter = chapter
    return "\n".join(output)


def render(state: dict) -> str:
    project = state["project"]
    learner = state["learner"]
    labels = state["labels"]
    theme = state["theme"]
    nodes = state["nodes"]
    ui = UI_TEXT.get(str(state["language"]).split("-")[0], UI_TEXT["en"])
    environment = state.get("environment")
    environment_html = ""
    if environment is not None:
        environment_status = environment["status"]
        environment_icon = {
            "unknown": "○",
            "ready": "✓",
            "partial": "!",
            "blocked": "×",
        }[environment_status]
        environment_html = (
            f'<p class="environment {esc(environment_status)}" '
            f'data-environment-status="{esc(environment_status)}">'
            f'<strong>{environment_icon} {esc(ui["environment"][environment_status])}</strong>'
            f' · {esc(ui["checks"])}: {len(environment["working"])}'
            f' · {esc(ui["blockers"])}: {len(environment["blockers"])}</p>'
        )
    complete = sum(node["status"] in {"done", "skipped"} for node in nodes)
    percent = round(complete * 100 / len(nodes))
    build_id = hashlib.sha256(
        json.dumps(state, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]
    project_key = hashlib.sha256(project["root"].encode("utf-8")).hexdigest()[:16]
    path_color = theme["path"].replace("#", "%23")
    node_html = render_nodes(nodes, labels, ui)
    return f"""<!doctype html>
<html lang="{esc(state['language'])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="onboarding-build" content="{build_id}">
<title>{esc(project['name'])}</title>
<style>
:root{{--ink:{theme['ink']};--muted:{theme['muted']};--paper:{theme['paper']};--grass:{theme['background_bottom']};--grass2:{theme['background_top']};--path:{theme['path']};--line:{theme['muted']};--ready:{theme['accent']};--done:{theme['done']};--locked:{theme['locked']};--active:{theme['accent']};--revisit:{theme['revisit']};}}
*{{box-sizing:border-box}} html{{scroll-behavior:smooth}} body{{margin:0;color:var(--ink);font:15px/1.4 ui-rounded,"SF Pro Rounded",system-ui,sans-serif;background:linear-gradient(155deg,var(--grass2),var(--grass) 58%,var(--paper));min-height:100vh}}
header{{position:sticky;top:0;z-index:10;padding:12px 18px;background:color-mix(in srgb,var(--paper) 91%,transparent);backdrop-filter:blur(14px);border-bottom:1px solid rgba(38,50,37,.14)}}
.top{{max-width:920px;margin:auto;display:grid;grid-template-columns:1fr auto;gap:18px;align-items:center}} h1{{font-size:clamp(22px,4vw,34px);line-height:1.05;margin:0}} .goal{{max-width:650px;margin:5px 0 0;color:var(--muted);font-size:14px}} .environment{{display:inline-block;margin:7px 0 0;padding:4px 8px;border-radius:999px;background:rgba(255,255,255,.62);color:var(--muted);font-size:11px}} .environment.ready strong{{color:var(--done)}} .environment.partial strong{{color:var(--revisit)}} .environment.blocked strong{{color:#b42318}}
.score{{display:flex;align-items:center;gap:10px;padding:8px 12px;background:var(--paper);border:1px solid rgba(38,50,37,.14);border-radius:16px;box-shadow:0 4px 12px rgba(38,50,37,.08)}} .meter{{min-width:130px;text-align:right;font-weight:850}} progress{{display:block;width:130px;height:9px;accent-color:var(--done)}} #reward-count{{font-size:18px;font-weight:900;white-space:nowrap}}
.filters{{max-width:920px;margin:9px auto 0;display:flex;gap:6px;overflow:auto}} .filters button{{white-space:nowrap}} .live{{margin-left:auto;color:var(--muted);font-size:12px;align-self:center;white-space:nowrap}}
main{{position:relative;max-width:920px;margin:auto;padding:30px 18px 100px;overflow:hidden}} .trail{{position:absolute;z-index:0;left:50%;top:0;bottom:0;width:150px;transform:translateX(-50%);background-size:150px 360px;background-repeat:repeat-y;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 150 360'%3E%3Cpath d='M75-20 C8 48 142 118 75 180 C8 242 142 312 75 380' fill='none' stroke='{path_color}' stroke-width='58' stroke-linecap='round'/%3E%3Cpath d='M75-20 C8 48 142 118 75 180 C8 242 142 312 75 380' fill='none' stroke='%23ffffff' stroke-opacity='.58' stroke-width='3' stroke-dasharray='7 12'/%3E%3C/svg%3E");filter:drop-shadow(0 3px 0 rgba(38,50,37,.12))}}
.chapter-marker{{position:relative;z-index:2;display:flex;justify-content:center;margin:22px 0 8px}} .chapter-marker span{{padding:7px 14px;border:2px solid color-mix(in srgb,var(--ink) 22%,transparent);border-radius:999px;background:var(--paper);box-shadow:0 4px 0 rgba(38,50,37,.12);font-size:12px;font-weight:900;letter-spacing:.06em;text-transform:uppercase}}
.node{{position:relative;z-index:1;display:grid;grid-template-columns:1fr 120px 1fr;align-items:center;min-height:178px}} .node:nth-of-type(odd) .card{{grid-column:1}} .node:nth-of-type(even) .card{{grid-column:3}} .node .badge{{grid-column:2}}
.badge{{grid-row:1;z-index:2;justify-self:center;display:grid;place-items:center;width:62px;height:62px;font-size:28px;background:var(--paper);border:4px solid var(--ready);border-radius:50%;box-shadow:0 6px 0 rgba(38,50,37,.18),0 10px 22px rgba(38,50,37,.12)}} .node:nth-of-type(4n+1) .badge{{transform:translateX(-30px)}} .node:nth-of-type(4n+2) .badge{{transform:translateX(24px)}} .node:nth-of-type(4n+3) .badge{{transform:translateX(38px)}}
.step{{position:absolute;left:calc(50% + 38px);top:52px;z-index:3;background:var(--ink);color:#fff;border-radius:999px;padding:2px 7px;font-size:11px;font-weight:900}}
.card{{grid-row:1;background:color-mix(in srgb,var(--paper) 94%,white);border:1px solid rgba(38,50,37,.16);border-radius:18px;padding:14px;box-shadow:0 6px 0 rgba(38,50,37,.12),0 12px 30px rgba(38,50,37,.08);max-width:330px}} .node:nth-of-type(odd) .card{{justify-self:end}} .node:nth-of-type(even) .card{{justify-self:start}}
.node-image{{display:block;width:100%;height:92px;object-fit:cover;border-radius:12px;margin-bottom:10px}} .meta{{display:flex;gap:6px;flex-wrap:wrap}} .meta span,.codename{{font-size:10px;font-weight:900;letter-spacing:.07em;text-transform:uppercase}} .meta span{{padding:3px 7px;background:rgba(255,255,255,.72);border-radius:999px}} .status-pill{{color:var(--active)}} .waiting .status-pill{{color:var(--revisit)}} .codename{{color:var(--active);margin:9px 0 2px}} h2{{font-size:19px;line-height:1.12;margin:0 0 5px}} p{{margin:5px 0}} details{{margin-top:8px}} summary{{cursor:pointer;font-weight:800}} dl{{display:grid;grid-template-columns:minmax(0,1fr);row-gap:2px;margin:8px 0}} dt{{min-width:0;margin-top:7px;font-weight:800;overflow-wrap:anywhere}} dt:first-child{{margin-top:0}} dd{{min-width:0;margin:0;overflow-wrap:anywhere}} .paths{{display:flex;gap:5px;flex-wrap:wrap}} code{{background:#eef0e3;border-radius:5px;padding:2px 5px;font-size:11px}}
button{{border:1px solid rgba(38,50,37,.18);border-radius:10px;background:#fff;padding:7px 10px;cursor:pointer;font-weight:800}} button:focus-visible{{outline:3px solid var(--active);outline-offset:2px}} .card>button{{width:100%;margin-top:9px;background:var(--ink);color:white}} .card>button:disabled{{cursor:not-allowed;background:var(--locked)}} .card>.reward{{background:linear-gradient(135deg,#ffd85a,#ff9d45);color:#3d2600;border-color:#e28d20;box-shadow:0 4px 0 #c87516}} .card>.reward.claimed{{background:var(--done);color:#fff;border-color:var(--done);box-shadow:none}} .terminal-status{{font-weight:800;color:var(--muted)}}
.done .badge{{border-color:var(--done)}} .active .badge{{border-color:var(--active);animation:pulse 1.6s infinite}} .revisit .badge,.waiting .badge{{border-color:var(--revisit)}} .locked{{opacity:.58}} .skipped{{opacity:.65}} .wait-status{{display:grid;gap:3px;margin-top:9px;padding:9px 10px;border-radius:10px;background:color-mix(in srgb,var(--revisit) 12%,white);font-size:12px}} .wait-status span{{color:var(--muted)}} .hidden{{display:none}} .toast{{position:fixed;z-index:30;left:50%;bottom:22px;transform:translateX(-50%);padding:10px 14px;background:var(--ink);color:white;border-radius:999px;font-weight:800;opacity:0;pointer-events:none;transition:.2s}} .toast.show{{opacity:1;transform:translate(-50%,-6px)}} .spark{{position:fixed;z-index:40;pointer-events:none;font-size:22px;animation:burst .85s ease-out forwards}}
@keyframes pulse{{50%{{scale:1.08}}}} @keyframes burst{{to{{translate:var(--x) var(--y);rotate:var(--r);opacity:0;scale:.5}}}}
.legend{{max-width:920px;margin:auto;padding:0 20px 36px;color:var(--muted);text-align:center}}
@media(max-width:700px){{.top{{grid-template-columns:1fr}}.score{{justify-content:space-between}}.meter{{text-align:left}}.live{{display:none}}main{{padding-left:10px}}.trail{{left:49px;width:92px;background-size:92px 280px}}.node{{grid-template-columns:82px 1fr;min-height:166px}}.node .badge,.node:nth-of-type(odd) .badge,.node:nth-of-type(even) .badge{{grid-column:1;justify-self:center;transform:none}}.node .card,.node:nth-of-type(odd) .card,.node:nth-of-type(even) .card{{grid-column:2;justify-self:stretch;max-width:none}}.step{{left:65px;top:49px}}}}
@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important;animation:none!important;transition:none!important}}}} @media print{{header{{position:static}}.filters,.card>button,.trail{{display:none}}body{{background:#fff}}.node{{break-inside:avoid}}}}
</style>
</head>
<body>
<header>
  <div class="top"><div>{f'<img src="{esc(theme["logo"])}" alt="" style="max-width:110px;max-height:36px;margin-bottom:6px">' if theme['logo'] else ''}<h1>{esc(project['name'])}</h1><p class="goal">{esc(project['goal'])}<br>{esc(learner['role'])}</p>{environment_html}</div><div class="score"><span id="reward-count">0 ⭐</span><div class="meter">{complete}/{len(nodes)} {esc(labels['nodes'])}<progress value="{complete}" max="{len(nodes)}">{percent}%</progress></div></div></div>
  <nav class="filters"><button data-filter="all" aria-pressed="true">{esc(labels['filter_all'])}</button><button data-filter="ready">{esc(labels['filter_ready'])}</button><button data-filter="active">{esc(labels['filter_active'])}</button><button data-filter="waiting">{esc(ui['filter_waiting'])}</button><button data-filter="done">{esc(labels['filter_done'])}</button><button data-filter="revisit">{esc(labels['filter_revisit'])}</button><span class="live">↻ {esc(ui['live'])}</span></nav>
</header>
<main><div class="trail" aria-hidden="true"></div>{node_html}</main>
<p class="legend">{percent}% · {esc(labels['footer'])}</p>
<div class="toast" role="status" aria-live="polite"></div>
<script>
const buildId='{build_id}';
const storageKey='onboarding:{project_key}';
const viewKey=storageKey+':view';
const toast=document.querySelector('.toast');
let activeFilter='all';
function showToast(message){{toast.textContent=message;toast.classList.add('show');setTimeout(()=>toast.classList.remove('show'),1400)}}
function applyFilter(filter){{
  activeFilter=filter;
  document.querySelectorAll('[data-filter]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.filter===filter)));
  document.querySelectorAll('.node').forEach(node=>node.classList.toggle('hidden',filter!=='all'&&node.dataset.status!==filter));
}}
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{{
  const filter=button.dataset.filter;
  applyFilter(filter);
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
  showToast('{esc(ui['copied'])}');
}}));
let claims;
try{{claims=new Set(JSON.parse(localStorage.getItem(storageKey)||'[]'))}}catch(error){{claims=new Set()}}
const earnedCodes=new Set([...document.querySelectorAll('[data-reward]')].map(button=>button.dataset.reward));
claims=new Set([...claims].filter(code=>earnedCodes.has(code)));
function updateRewards(){{
  document.querySelectorAll('[data-reward]').forEach(button=>{{
    const claimed=claims.has(button.dataset.reward);
    button.classList.toggle('claimed',claimed);
    button.textContent=claimed?'✓ {esc(ui['claimed'])}':'⭐ {esc(ui['claim'])}';
  }});
  document.querySelector('#reward-count').textContent=claims.size+' ⭐';
}}
function celebrate(button){{
  const box=button.getBoundingClientRect();
  for(let index=0;index<14;index++){{
    const spark=document.createElement('span');spark.className='spark';spark.textContent=index%3===0?'⭐':'✨';
    spark.style.left=(box.left+box.width/2)+'px';spark.style.top=(box.top+box.height/2)+'px';
    spark.style.setProperty('--x',((Math.random()-.5)*240)+'px');spark.style.setProperty('--y',(-45-Math.random()*150)+'px');spark.style.setProperty('--r',((Math.random()-.5)*240)+'deg');
    document.body.appendChild(spark);setTimeout(()=>spark.remove(),900);
  }}
}}
document.querySelectorAll('[data-reward]').forEach(button=>button.addEventListener('click',()=>{{
  const code=button.dataset.reward;if(claims.has(code))return;
  claims.add(code);try{{localStorage.setItem(storageKey,JSON.stringify([...claims]))}}catch(error){{}}updateRewards();celebrate(button);showToast('{esc(ui['claimed'])} · +1 ⭐');
}}));
function rememberView(){{
  const open=[...document.querySelectorAll('.node details[open]')].map(item=>item.closest('.node').dataset.code);
  try{{sessionStorage.setItem(viewKey,JSON.stringify({{scrollY,activeFilter,open,time:Date.now()}}))}}catch(error){{}}
}}
function restoreView(){{
  try{{const view=JSON.parse(sessionStorage.getItem(viewKey)||'null');if(!view||Date.now()-view.time>60000)return;applyFilter(view.activeFilter||'all');(view.open||[]).forEach(code=>document.querySelector('[data-code="'+code+'"] details')?.setAttribute('open',''));requestAnimationFrame(()=>scrollTo(0,view.scrollY||0))}}catch(error){{}}
}}
window.addEventListener('beforeunload',rememberView);restoreView();updateRewards();
let refreshRunning=false;
async function refreshMap(){{
  if(refreshRunning||document.visibilityState!=='visible')return;
  refreshRunning=true;
  rememberView();
  if(location.protocol==='file:'){{refreshRunning=false;location.reload();return}}
  try{{const response=await fetch(location.href.split('#')[0]+'?map-check='+Date.now(),{{cache:'no-store'}});const source=await response.text();const match=source.match(/name="onboarding-build" content="([^"]+)"/);if(match&&match[1]!==buildId)location.reload()}}catch(error){{}}
  finally{{refreshRunning=false}}
}}
window.addEventListener('focus',refreshMap);
document.addEventListener('visibilitychange',()=>{{if(document.visibilityState==='visible')refreshMap()}});
setInterval(refreshMap,10000);
</script>
</body>
</html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path, help="Path to state.json")
    parser.add_argument("--output", type=Path, help="HTML output path")
    parser.add_argument("--check", action="store_true", help="Validate without rendering")
    parser.add_argument("--open", action="store_true", help="Open the rendered map in the default browser")
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
        if args.open:
            opened, error = open_map(output)
            if not opened:
                print(
                    f"Error: rendered the map but could not open the browser: {error}. "
                    f"Map: {output.resolve()}",
                    file=sys.stderr,
                )
                return 2
            print(f"Opened onboarding map: {output.resolve()}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
