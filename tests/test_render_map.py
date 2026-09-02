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


if __name__ == "__main__":
    unittest.main()
