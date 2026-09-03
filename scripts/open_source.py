#!/usr/bin/env python3
"""Detect a graphical code editor and open a local source file at a line."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


EDITOR_ORDER = ("zed", "code", "cursor", "subl")
COMMAND_NAMES = {
    "zed": ("zed",),
    "code": ("code",),
    "cursor": ("cursor",),
    "subl": ("subl",),
}
MACOS_COMMANDS = {
    "zed": (Path("/Applications/Zed.app/Contents/MacOS/cli"),),
    "code": (
        Path(
            "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
        ),
    ),
    "cursor": (
        Path("/Applications/Cursor.app/Contents/Resources/app/bin/cursor"),
    ),
    "subl": (
        Path("/Applications/Sublime Text.app/Contents/SharedSupport/bin/subl"),
    ),
}
EDITOR_ALIASES = {
    "zed": "zed",
    "code": "code",
    "cursor": "cursor",
    "subl": "subl",
    "sublime_text": "subl",
}


def resolve_editor(name: str) -> str | None:
    for command in COMMAND_NAMES[name]:
        found = shutil.which(command)
        if found:
            return found
    if sys.platform == "darwin":
        for candidate in MACOS_COMMANDS[name]:
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return str(candidate)
    return None


def editor_from_environment() -> str | None:
    for variable in ("VISUAL", "EDITOR"):
        value = os.environ.get(variable, "").strip()
        if not value:
            continue
        try:
            command = shlex.split(value)[0]
        except (ValueError, IndexError):
            continue
        name = EDITOR_ALIASES.get(Path(command).name)
        if name and resolve_editor(name):
            return name
    return None


def detect_editors() -> dict[str, object]:
    available = [name for name in EDITOR_ORDER if resolve_editor(name)]
    preferred = editor_from_environment()
    if preferred is None and len(available) == 1:
        preferred = available[0]
    return {"preferred": preferred, "available": available}


def build_command(
    editor: str, executable: str, path: Path, line: int, column: int
) -> list[str]:
    position = f"{path}:{line}:{column}"
    if editor in {"code", "cursor"}:
        return [executable, "--goto", position]
    return [executable, position]


def open_source(
    path: Path, line: int, column: int, editor: str
) -> tuple[bool, str]:
    executable = resolve_editor(editor)
    if executable is None:
        return False, f"editor is not available: {editor}"
    command = build_command(editor, executable, path, line, column)
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError as exc:
        return False, str(exc)
    if result.returncode == 0:
        return True, ""
    return False, result.stderr.strip() or f"exit code {result.returncode}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("--line", type=int, default=1)
    parser.add_argument("--column", type=int, default=1)
    parser.add_argument("--editor", choices=EDITOR_ORDER)
    parser.add_argument(
        "--detect", action="store_true", help="Print detected editors as JSON"
    )
    args = parser.parse_args()

    if args.detect:
        print(json.dumps(detect_editors()))
        return 0
    if args.path is None:
        parser.error("path is required unless --detect is used")
    if args.line < 1 or args.column < 1:
        parser.error("line and column must be positive")

    path = args.path.resolve()
    if not path.is_file():
        print(f"Error: source file does not exist: {path}", file=sys.stderr)
        return 2

    detected = detect_editors()
    editor = args.editor or detected["preferred"]
    if not isinstance(editor, str):
        available = ", ".join(detected["available"]) or "none"
        print(
            f"Error: no preferred editor; available editors: {available}",
            file=sys.stderr,
        )
        return 2

    opened, error = open_source(path, args.line, args.column, editor)
    if not opened:
        print(f"Error: could not open {path}: {error}", file=sys.stderr)
        return 2
    print(f"Opened {path}:{args.line}:{args.column} in {editor}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
