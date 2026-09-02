#!/usr/bin/env python3
"""Run one isolated onboarding evaluation case."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


EVAL_ROOT = Path(__file__).resolve().parent
SKILL_ROOT = EVAL_ROOT.parent
SCHEMA_ROOT = EVAL_ROOT / "schemas"
PROMPT_ROOT = EVAL_ROOT / "prompts"
SKILL_ITEMS = ("SKILL.md", "agents", "references", "scripts")


class EvalError(RuntimeError):
    """The harness could not complete a valid eval run."""


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EvalError(f"Expected a JSON object: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def eval_environment() -> dict[str, str]:
    environment = os.environ.copy()
    cache = EVAL_ROOT / "cache" / "uv"
    cache.mkdir(parents=True, exist_ok=True)
    environment["UV_CACHE_DIR"] = str(cache)
    return environment


def run_command(
    command: Sequence[str],
    *,
    cwd: Path,
    log_path: Path | None = None,
    timeout: int = 1800,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(command),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
        env=eval_environment(),
    )
    if log_path is not None:
        log_path.write_text(result.stdout, encoding="utf-8")
    return result


def require_ok(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode:
        tail = result.stdout[-4000:]
        raise EvalError(f"{label} failed with exit {result.returncode}:\n{tail}")


def prepare_cache(case: dict[str, Any], requested: Path | None) -> Path:
    if requested is not None:
        cache = requested.resolve()
        if not (cache / ".git").exists():
            raise EvalError(f"Repository cache is not a Git checkout: {cache}")
    else:
        cache = EVAL_ROOT / "cache" / str(case["id"])
        if not cache.exists():
            cache.parent.mkdir(parents=True, exist_ok=True)
            result = run_command(
                ["git", "clone", "--no-tags", str(case["repository"]), str(cache)],
                cwd=cache.parent,
                timeout=3600,
            )
            require_ok(result, "repository clone")

    result = run_command(
        ["git", "cat-file", "-e", f"{case['base_commit']}^{{commit}}"],
        cwd=cache,
    )
    require_ok(result, "base commit lookup")
    return cache


def extract_snapshot(cache: Path, commit: str, destination: Path) -> None:
    destination.mkdir(parents=True)
    archive = subprocess.Popen(
        ["git", "-C", str(cache), "archive", commit],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert archive.stdout is not None
    extract = subprocess.run(
        ["tar", "-x", "-C", str(destination)],
        stdin=archive.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    archive.stdout.close()
    _, archive_error = archive.communicate()
    if archive.returncode or extract.returncode:
        details = (archive_error + extract.stderr).decode("utf-8", errors="replace")
        raise EvalError(f"Could not extract base snapshot:\n{details}")


def initialize_clean_history(workspace: Path, commit: str) -> None:
    commands = (
        ["git", "init", "-b", "main"],
        ["git", "config", "user.name", "Onboarding Eval"],
        ["git", "config", "user.email", "eval@local.invalid"],
        ["git", "add", "-A"],
        ["git", "commit", "-m", f"eval baseline {commit}"],
    )
    for command in commands:
        require_ok(run_command(command, cwd=workspace), " ".join(command))

    exclude = workspace / ".git" / "info" / "exclude"
    with exclude.open("a", encoding="utf-8") as stream:
        stream.write("\n.onboarding/\n.codex/\n")


def install_skill(workspace: Path) -> None:
    target = workspace / ".codex" / "skills" / "onboarding"
    target.mkdir(parents=True)
    for name in SKILL_ITEMS:
        source = SKILL_ROOT / name
        destination = target / name
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)


def product_status(workspace: Path) -> list[str]:
    result = run_command(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=workspace,
    )
    require_ok(result, "git status")
    ignored = (".onboarding/", ".codex/", ".venv/")
    lines = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else line
        if not path.startswith(ignored):
            lines.append(line)
    return lines


def parse_agent_stream(stdout: str) -> tuple[str, dict[str, Any]]:
    thread_id = ""
    final_text = ""
    for raw_line in stdout.splitlines():
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "thread.started":
            thread_id = str(event.get("thread_id", ""))
        item = event.get("item")
        if (
            event.get("type") == "item.completed"
            and isinstance(item, dict)
            and item.get("type") == "agent_message"
        ):
            final_text = str(item.get("text", ""))
    if not final_text:
        raise EvalError("Agent stream has no final message")
    try:
        payload = json.loads(final_text)
    except json.JSONDecodeError as exc:
        raise EvalError(f"Agent final message is not JSON: {final_text}") from exc
    if not isinstance(payload, dict):
        raise EvalError("Agent final message must be a JSON object")
    return thread_id, payload


def run_agent_process(
    command: list[str],
    *,
    prompt: str,
    cwd: Path,
    timeout: int,
) -> tuple[str, str, int]:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        text=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
        env=eval_environment(),
    )

    def stop_process() -> None:
        if process.poll() is not None:
            return
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()

    try:
        stdout, stderr = process.communicate(prompt, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        stop_process()
        raise EvalError(f"Agent timed out after {timeout}s") from exc
    except BaseException:
        stop_process()
        raise
    return stdout, stderr, process.returncode


def invoke_agent(
    *,
    role: str,
    prompt: str,
    schema: Path,
    workspace: Path,
    run_dir: Path,
    index: int,
    thread_id: str = "",
    model: str = "",
    sandbox: str = "workspace-write",
    ephemeral: bool = False,
    timeout: int = 1800,
) -> tuple[str, dict[str, Any]]:
    if thread_id:
        command = [
            "codex",
            "exec",
            "resume",
            "--json",
            "--ignore-user-config",
            "--ignore-rules",
            "--output-schema",
            str(schema),
        ]
        if model:
            command.extend(["--model", model])
        command.append(thread_id)
    else:
        command = [
            "codex",
            "exec",
            "--json",
            "--ignore-user-config",
            "--ignore-rules",
            "--sandbox",
            sandbox,
            "--cd",
            str(workspace),
            "--output-schema",
            str(schema),
        ]
        if ephemeral:
            command.append("--ephemeral")
        if model:
            command.extend(["--model", model])

    stdout, stderr, returncode = run_agent_process(
        command,
        prompt=prompt,
        cwd=workspace,
        timeout=timeout,
    )
    prefix = f"{index:02d}-{role}"
    (run_dir / f"{prefix}.jsonl").write_text(stdout, encoding="utf-8")
    (run_dir / f"{prefix}.stderr.log").write_text(stderr, encoding="utf-8")
    if returncode:
        raise EvalError(f"{role} agent failed with exit {returncode}:\n{stderr[-4000:]}")
    new_thread_id, payload = parse_agent_stream(stdout)
    return thread_id or new_thread_id, payload


def setup_workspace(
    case_dir: Path,
    case: dict[str, Any],
    workspace: Path,
    run_dir: Path,
    cache: Path,
    arm: str,
    skip_setup: bool,
) -> None:
    extract_snapshot(cache, str(case["base_commit"]), workspace)
    initialize_clean_history(workspace, str(case["base_commit"]))
    if arm == "skill":
        install_skill(workspace)
    if skip_setup:
        return
    for index, command in enumerate(case.get("setup_commands", []), start=1):
        result = run_command(
            [str(part) for part in command],
            cwd=workspace,
            log_path=run_dir / f"setup-{index}.log",
            timeout=3600,
        )
        require_ok(result, f"setup command {index}")


def run_oracle(
    case_dir: Path,
    case: dict[str, Any],
    workspace: Path,
    run_dir: Path,
) -> dict[str, Any]:
    source = case_dir / str(case["oracle_file"])
    target = workspace / str(case["oracle_target"])
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    commands = []
    try:
        for index, command in enumerate(case.get("oracle_commands", []), start=1):
            result = run_command(
                [str(part) for part in command],
                cwd=workspace,
                log_path=run_dir / f"oracle-{index}.log",
                timeout=1800,
            )
            commands.append(
                {
                    "command": command,
                    "exit_code": result.returncode,
                    "passed": result.returncode == 0,
                }
            )
    finally:
        target.unlink(missing_ok=True)

    diff_check = run_command(["git", "diff", "--check"], cwd=workspace)
    return {
        "commands": commands,
        "oracle_passed": bool(commands) and all(item["passed"] for item in commands),
        "diff_check_passed": diff_check.returncode == 0,
        "diff_check_output": diff_check.stdout,
        "product_status": product_status(workspace),
    }


def build_coach_prompt(arm: str, issue: str) -> str:
    prompt_name = "coach-skill.md" if arm == "skill" else "coach-baseline.md"
    instructions = (PROMPT_ROOT / prompt_name).read_text(encoding="utf-8")
    return f"{instructions}\n\nIssue to complete:\n\n{issue}"


def build_learner_prompt(persona: dict[str, Any], coach_message: str) -> str:
    instructions = (PROMPT_ROOT / "learner.md").read_text(encoding="utf-8")
    profile = json.dumps(persona, ensure_ascii=False, indent=2)
    return (
        f"{instructions}\n\nLearner profile:\n\n{profile}"
        f"\n\nCoach message:\n\n{coach_message}"
    )


def run_dialogue(
    *,
    arm: str,
    issue: str,
    persona: dict[str, Any],
    workspace: Path,
    run_dir: Path,
    model: str,
    max_turns: int,
    timeout: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    transcript: list[dict[str, Any]] = []
    coach_violations: list[dict[str, Any]] = []
    event_index = 1

    before = product_status(workspace)
    coach_thread, coach = invoke_agent(
        role="coach",
        prompt=build_coach_prompt(arm, issue),
        schema=SCHEMA_ROOT / "coach.json",
        workspace=workspace,
        run_dir=run_dir,
        index=event_index,
        model=model,
        timeout=timeout,
    )
    event_index += 1
    after = product_status(workspace)
    if after != before:
        coach_violations.append({"turn": 0, "before": before, "after": after})
    transcript.append({"role": "coach", **coach})

    learner_thread = ""
    stop_reason = "max_turns"
    for turn in range(1, max_turns + 1):
        learner_prompt = (
            build_learner_prompt(persona, str(coach["message"]))
            if not learner_thread
            else f"Coach message:\n\n{coach['message']}"
        )
        learner_thread, learner = invoke_agent(
            role="learner",
            prompt=learner_prompt,
            schema=SCHEMA_ROOT / "learner.json",
            workspace=workspace,
            run_dir=run_dir,
            index=event_index,
            thread_id=learner_thread,
            model=model,
            timeout=timeout,
        )
        event_index += 1
        transcript.append({"role": "learner", **learner})

        before = product_status(workspace)
        coach_thread, coach = invoke_agent(
            role="coach",
            prompt=f"Learner reply:\n\n{learner['reply']}\n\nEvidence:\n{json.dumps(learner['evidence'], ensure_ascii=False)}",
            schema=SCHEMA_ROOT / "coach.json",
            workspace=workspace,
            run_dir=run_dir,
            index=event_index,
            thread_id=coach_thread,
            model=model,
            timeout=timeout,
        )
        event_index += 1
        after = product_status(workspace)
        if after != before:
            coach_violations.append({"turn": turn, "before": before, "after": after})
        transcript.append({"role": "coach", **coach})

        if coach["status"] in {"done", "blocked"}:
            stop_reason = str(coach["status"])
            break

    return transcript, coach_violations, stop_reason


def review_run(
    *,
    transcript: list[dict[str, Any]],
    checks: dict[str, Any],
    workspace: Path,
    run_dir: Path,
    model: str,
    timeout: int,
) -> dict[str, Any]:
    skill_copy = workspace / ".codex" / "skills" / "onboarding"
    if skill_copy.exists():
        shutil.rmtree(skill_copy)
    instructions = (PROMPT_ROOT / "reviewer.md").read_text(encoding="utf-8")
    prompt = (
        f"{instructions}\n\nDeterministic checks:\n"
        f"{json.dumps(checks, ensure_ascii=False, indent=2)}\n\nTranscript:\n"
        f"{json.dumps(transcript, ensure_ascii=False, indent=2)}"
    )
    _, review = invoke_agent(
        role="reviewer",
        prompt=prompt,
        schema=SCHEMA_ROOT / "review.json",
        workspace=workspace,
        run_dir=run_dir,
        index=99,
        model=model,
        sandbox="read-only",
        ephemeral=True,
        timeout=timeout,
    )
    return review


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--persona", default="junior")
    parser.add_argument("--arm", choices=("skill", "baseline"), default="skill")
    parser.add_argument("--repo-cache", type=Path)
    parser.add_argument("--model", default="")
    parser.add_argument("--max-turns", type=int, default=12)
    parser.add_argument("--agent-timeout", type=int, default=1800)
    parser.add_argument("--skip-setup", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--smoke-first-turn", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    case_dir = args.case_dir.resolve()
    case = read_json(case_dir / "case.json")
    persona_path = case_dir / "personas" / f"{args.persona}.json"
    persona = read_json(persona_path)
    issue = (case_dir / str(case["issue_file"])).read_text(encoding="utf-8")
    cache = prepare_cache(case, args.repo_cache)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = EVAL_ROOT / "runs" / str(case["id"]) / f"{stamp}-{args.persona}-{args.arm}"
    run_dir.mkdir(parents=True)
    workspace = run_dir / "workspace"

    manifest = {
        "case": case["id"],
        "base_commit": case["base_commit"],
        "persona": args.persona,
        "arm": args.arm,
        "model": args.model or "codex-default",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(run_dir / "manifest.json", manifest)

    try:
        setup_workspace(
            case_dir,
            case,
            workspace,
            run_dir,
            cache,
            args.arm,
            args.skip_setup,
        )
        if args.prepare_only:
            print(workspace)
            return 0

        transcript, coach_violations, stop_reason = run_dialogue(
            arm=args.arm,
            issue=issue,
            persona=persona,
            workspace=workspace,
            run_dir=run_dir,
            model=args.model,
            max_turns=0 if args.smoke_first_turn else args.max_turns,
            timeout=args.agent_timeout,
        )
        write_json(run_dir / "transcript.json", transcript)

        if args.smoke_first_turn:
            write_json(
                run_dir / "checks.json",
                {
                    "coach_product_write_violations": coach_violations,
                    "stop_reason": "first_coach_smoke",
                },
            )
            print(run_dir)
            return 0

        diff = run_command(["git", "diff", "--binary", "HEAD"], cwd=workspace)
        require_ok(diff, "solution diff")
        (run_dir / "solution.diff").write_text(diff.stdout, encoding="utf-8")

        checks = run_oracle(case_dir, case, workspace, run_dir)
        checks["coach_product_write_violations"] = coach_violations
        checks["stop_reason"] = stop_reason
        write_json(run_dir / "checks.json", checks)

        state = workspace / ".onboarding" / "state.json"
        if state.exists():
            shutil.copy2(state, run_dir / "onboarding-state.json")

        review = review_run(
            transcript=transcript,
            checks=checks,
            workspace=workspace,
            run_dir=run_dir,
            model=args.model,
            timeout=args.agent_timeout,
        )
        write_json(run_dir / "review.json", review)
    except KeyboardInterrupt:
        write_json(run_dir / "harness-error.json", {"error": "interrupted"})
        print(f"eval interrupted: {run_dir}", file=sys.stderr)
        return 130
    except (EvalError, subprocess.TimeoutExpired) as exc:
        write_json(run_dir / "harness-error.json", {"error": str(exc)})
        print(f"eval failed: {exc}", file=sys.stderr)
        print(run_dir, file=sys.stderr)
        return 1

    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
