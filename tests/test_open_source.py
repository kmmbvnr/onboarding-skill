from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from open_source import build_command, detect_editors, open_source  # noqa: E402


class OpenSourceTests(unittest.TestCase):
    def test_zed_uses_path_line_column(self) -> None:
        command = build_command(
            "zed", "/Applications/Zed.app/Contents/MacOS/cli", Path("/p/a.py"), 12, 3
        )

        self.assertEqual(
            command,
            ["/Applications/Zed.app/Contents/MacOS/cli", "/p/a.py:12:3"],
        )

    def test_vscode_uses_goto(self) -> None:
        command = build_command("code", "/usr/bin/code", Path("/p/a.py"), 9, 1)

        self.assertEqual(command, ["/usr/bin/code", "--goto", "/p/a.py:9:1"])

    def test_single_available_editor_becomes_preferred(self) -> None:
        available = {"zed": "/zed", "code": None, "cursor": None, "subl": None}
        with (
            patch("open_source.resolve_editor", side_effect=available.get),
            patch.dict("open_source.os.environ", {}, clear=True),
        ):
            result = detect_editors()

        self.assertEqual(result, {"preferred": "zed", "available": ["zed"]})

    def test_open_source_invokes_editor_without_a_shell(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "a.py"
            path.touch()
            with (
                patch("open_source.resolve_editor", return_value="/zed"),
                patch(
                    "open_source.subprocess.run",
                    return_value=CompletedProcess(["/zed"], 0, "", ""),
                ) as run,
            ):
                opened, error = open_source(path, 7, 2, "zed")

        self.assertTrue(opened)
        self.assertEqual(error, "")
        self.assertEqual(run.call_args.args[0], ["/zed", f"{path}:7:2"])
        self.assertNotIn("shell", run.call_args.kwargs)


if __name__ == "__main__":
    unittest.main()
