from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from create_tour import make_state  # noqa: E402
from render_map import render, validate  # noqa: E402


class RenderMapTests(unittest.TestCase):
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
                }
            ],
        }

        with self.assertRaisesRegex(ValueError, "ready cannot have blockers"):
            validate(state)


if __name__ == "__main__":
    unittest.main()
