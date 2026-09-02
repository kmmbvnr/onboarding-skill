# Eval-driven changes

## 2026-09-02 — failed command is evidence, not a skip

- Source: human review of the Together onboarding trial.
- Evidence: the learner ran the correct focused test and supplied the complete
  database-creation failure. The coach used `skipped` because the test did not
  pass, although the node evidence asked for the run and traceback.
- Change: add a local-environment baseline, store working facts and typed
  blockers, and define completion from the node evidence contract rather than
  the command exit code.
- Rule: a failed command can complete a diagnosis node. It cannot make a node
  `skipped`. A passing-result node uses `stopped` plus `revisit` when an external
  blocker prevents completion.
- Validation: four renderer and state tests pass. Skill validation passes.

## 2026-09-02 — short game loop and earned rewards

- Source: human trial in `/Users/kmmbvnr/Workspace/Together`.
- Evidence: the generated map had 13 nodes. Ten nodes were estimated at 35–150
  minutes. The first real patch was node 12. The CSS stretched one rounded path
  element through the full page, which rendered as a long oval.
- Change: limit the first chapter to 5–9 nodes, cap nodes at 25 minutes, put a
  useful change in the first three nodes, render a repeating curved trail, and
  open the first map automatically.
- Reward rule: only `done` nodes expose the reward button. The verified status
  stays in `state.json`; the learner's claim stays in browser storage.
- Validation: renderer unit tests pass, skill validation passes, and the new
  desktop map was inspected in Chrome. Full learner comparison runs remain
  pending.

## 2026-09-02 — intake before inspection

- Case: `django-modern-rest-1225`, junior, skill arm.
- Trace: `20260902T085941503728Z-junior-skill`.
- Result: aborted after two learner actions because the route was already
  inefficient.
- Evidence: the coach created state with an empty learner profile. It then
  required Git status and an AI policy summary although the persona already
  knew Git and project contribution basics were not the first task blocker.
  The first coach turn used 292,172 input tokens.
- Candidate change: require intake before inspection, limit visual inspection,
  and omit demonstrated tool or policy basics from the route.
- Validation: smoke run `20260902T090825147062Z-junior-skill` asked three
  intake questions, used `continue`, made no product change, and did not inspect
  the repository. The turn used 52,038 input tokens. Full comparison runs are
  still pending.
