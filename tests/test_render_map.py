from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from create_tour import make_state  # noqa: E402
from render_map import main, open_map, render, validate  # noqa: E402


class RenderMapTests(unittest.TestCase):
    def test_open_map_uses_system_opener_after_browser_handler_fails(self) -> None:
        with (
            patch("render_map.sys.platform", "darwin"),
            patch("render_map.webbrowser.open", return_value=False),
            patch(
                "render_map.subprocess.run",
                return_value=CompletedProcess(["open"], 0, "", ""),
            ) as run,
        ):
            opened, error = open_map(Path("/project/.onboarding/map.html"))

        self.assertTrue(opened)
        self.assertEqual(error, "")
        self.assertEqual(run.call_args.args[0][0], "open")

    def test_open_map_reports_both_failures(self) -> None:
        with (
            patch("render_map.sys.platform", "darwin"),
            patch("render_map.webbrowser.open", return_value=False),
            patch(
                "render_map.subprocess.run",
                return_value=CompletedProcess(["open"], 1, "", "not permitted"),
            ),
        ):
            opened, error = open_map(Path("/project/.onboarding/map.html"))

        self.assertFalse(opened)
        self.assertIn("default browser handler returned false", error)
        self.assertIn("not permitted", error)

    def test_cli_fails_when_open_was_requested_but_no_opener_worked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            state_path.write_text(
                json.dumps(make_state("en", Path("/project"))), encoding="utf-8"
            )
            with (
                patch(
                    "sys.argv", ["render_map.py", str(state_path), "--open"]
                ),
                patch("render_map.open_map", return_value=(False, "not permitted")),
            ):
                result = main()

        self.assertEqual(result, 2)

    def test_done_node_gets_reward_and_locked_node_does_not(self) -> None:
        state = make_state("ru", Path("/project"))
        state["nodes"][0]["status"] = "done"
        state["nodes"][1]["status"] = "ready"

        output = render(state)

        self.assertIn('data-reward="TOUR-START"', output)
        self.assertIn("Забрать награду", output)
        self.assertNotIn('data-reward="TOUR-LEAD"', output)
        self.assertIn('name="onboarding-build"', output)
        self.assertIn("location.reload()", output)

    def test_long_node_is_rejected(self) -> None:
        state = make_state("en", Path("/project"))
        state["nodes"][0]["estimated_minutes"] = 26

        with self.assertRaisesRegex(ValueError, "between 1 and 25"):
            validate(state)

    def test_chapter_markers_are_rendered_when_chapter_changes(self) -> None:
        state = make_state("en", Path("/project"))
        state["nodes"][0]["chapter"] = "First steps"
        state["nodes"][1]["chapter"] = "First steps"
        state["nodes"][2]["chapter"] = "Ship safely"

        validate(state)
        output = render(state)

        self.assertEqual(output.count('class="chapter-marker"'), 2)
        self.assertIn("First steps", output)
        self.assertIn("Ship safely", output)

    def test_empty_chapter_is_rejected(self) -> None:
        state = make_state("en", Path("/project"))
        state["nodes"][0]["chapter"] = ""

        with self.assertRaisesRegex(ValueError, "chapter must be non-empty text"):
            validate(state)

    def test_environment_blocker_is_validated_and_rendered(self) -> None:
        state = make_state("en", Path("/project"))
        state["environment"] = {
            "checked_at": "2026-09-02",
            "status": "partial",
            "working": ["Python 3.12 matches pyproject.toml"],
            "blockers": [
                {
                    "id": "TEST-DATABASE",
                    "scope": "project",
                    "summary": "The focused test cannot create its database.",
                    "evidence": "The migration failed before tests ran.",
                    "next_action": "Use the documented PostgreSQL test path.",
                    "waiting_for": "Project owner",
                    "blocks": ["TOUR-LEAD"],
                }
            ],
        }

        validate(state)
        output = render(state)

        self.assertIn('data-environment-status="partial"', output)
        self.assertIn("Environment partly ready", output)
        self.assertIn("Blockers: 1", output)

    def test_ready_environment_cannot_have_a_blocker(self) -> None:
        state = make_state("en", Path("/project"))
        state["environment"] = {
            "checked_at": "2026-09-02",
            "status": "ready",
            "working": [],
            "blockers": [
                {
                    "id": "MISSING-TOOL",
                    "scope": "machine",
                    "summary": "A required tool is missing.",
                    "evidence": "The version command was not found.",
                    "next_action": "Install the supported tool version.",
                    "waiting_for": "Learner",
                    "blocks": ["TOUR-LEAD"],
                }
            ],
        }

        with self.assertRaisesRegex(ValueError, "ready cannot have blockers"):
            validate(state)

    def test_blocker_cannot_reference_unknown_node(self) -> None:
        state = make_state("en", Path("/project"))
        state["environment"] = {
            "checked_at": "2026-09-02",
            "status": "partial",
            "working": ["Python works"],
            "blockers": [
                {
                    "id": "STAGING-ACCESS",
                    "scope": "access",
                    "summary": "Staging access is pending.",
                    "evidence": "The access request is open.",
                    "next_action": "Wait for platform team approval.",
                    "waiting_for": "Platform team",
                    "blocks": ["UNKNOWN-NODE"],
                }
            ],
        }

        with self.assertRaisesRegex(ValueError, "blocks unknown codename"):
            validate(state)

    def test_partial_environment_requires_an_unblocked_next_node(self) -> None:
        state = make_state("en", Path("/project"))
        state["nodes"][0]["status"] = "revisit"
        state["environment"] = {
            "checked_at": "2026-09-02",
            "status": "partial",
            "working": [],
            "blockers": [
                {
                    "id": "LOCAL-SERVICE",
                    "scope": "service",
                    "summary": "The required database is unavailable.",
                    "evidence": "The supported health check failed.",
                    "next_action": "Start the approved local database.",
                    "waiting_for": "Learner",
                    "blocks": ["TOUR-START"],
                }
            ],
        }

        with self.assertRaisesRegex(ValueError, "requires an unblocked available node"):
            validate(state)

    def test_blocked_environment_rejects_an_unblocked_next_node(self) -> None:
        state = make_state("en", Path("/project"))
        state["environment"] = {
            "checked_at": "2026-09-02",
            "status": "blocked",
            "working": [],
            "blockers": [
                {
                    "id": "LATER-ACCESS",
                    "scope": "access",
                    "summary": "Access for a later node is pending.",
                    "evidence": "The access request is open.",
                    "next_action": "Wait for approval.",
                    "waiting_for": "Platform team",
                    "blocks": ["TOUR-LEAD"],
                }
            ],
        }

        with self.assertRaisesRegex(ValueError, "has unblocked available nodes"):
            validate(state)


if __name__ == "__main__":
    unittest.main()
