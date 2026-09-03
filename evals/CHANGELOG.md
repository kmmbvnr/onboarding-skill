# Eval-driven changes

## 2026-09-03 — external waits and project-specific code style

- Source: human review of the Wesnoth PR handoff.
- Evidence: after the learner opened the PR, the coach marked `REVIEW-LOOP`
  active and asked a quiz whose correct answer was to wait. It did not label the
  step as externally owned or continue the independent route. A later review
  also exposed a project-specific naming convention that the route had not
  taught or checked.
- Change: add a visible `waiting` node with owner, next date, and one read-only
  check. Due waits are checked once per invocation and never selected as a
  lesson. Rewire unrelated downstream nodes around the wait. Before the first
  code change, teach and exercise rules from contribution docs, formatter or
  linter configuration, CI, and nearby target code.
- Validation: twenty-two deterministic tests and skill validation pass. Tests
  cover required wait metadata, invalid dates, map output without an action
  button, and an independent ready node beside a waiting node.

## 2026-09-03 — refresh on return and wrap detail labels

- Source: human and browser review of the Wesnoth onboarding map.
- Evidence: a learner returned from the agent to a `file://` map and waited for
  the ten-second refresh interval. The Russian label `Доказательство` was wider
  than the fixed 70-pixel detail column and overlapped its value.
- Change: check for a new render immediately on window focus or restored page
  visibility, with the interval as a fallback. Stack detail labels above their
  values and allow long text to wrap. State explicitly that the model writes
  state from the reference and never invents map HTML.
- Validation: nineteen deterministic tests pass. Browser review at the Wesnoth
  card width shows each label above its value with no overlap. A dispatched
  focus event caused an immediate map-check request between interval requests.

## 2026-09-03 — open source at the teaching line

- Source: human review of the Wesnoth teaching interaction.
- Evidence: the coach named `machine.py:212`, but the learner had to ask it to
  open that location in Zed. The `zed` command was absent from `PATH` although
  Zed's bundled macOS CLI was installed. The learner also had to ask explicitly
  for examples and did not know which tutor actions were available.
- Change: detect a preferred graphical editor, save it in local state, and use
  a fixed helper to open the exact file, line, and column. Detect both PATH
  commands and standard macOS app CLI paths. Keep the source excerpt in chat.
  Explain once that the learner can interrupt for examples, simpler wording,
  hints, file opening, repetition, or a pacing change.
- Follow-up evidence: the coach tried to close `BASELINE-RUN` by asking the
  learner to restate its supplied sentence. The learner still did not know the
  execution path or the purpose of `PendingLuaString`.
- Follow-up change: explain a short execution story and separate code, control,
  and data state. Do not accept "understood" or immediate parroting as node
  evidence.
- Validation: local detection finds the bundled Zed CLI even though `zed` is
  absent from `PATH`. Skill validation and seventeen deterministic tests pass.
  A fresh behavioral trace remains pending.

## 2026-09-03 — teach before testing an unknown concept

- Source: human review of `BASELINE-RUN` in the Wesnoth trial.
- Evidence: after the learner said they did not know Lua, the coach introduced
  "long-bracket string", asked for a syntax prediction, and supplied a compound
  shell reproduction without first explaining Lua strings or the command.
- Change: select support per concept. "I do not know" activates a teach-first
  loop with a definition, minimal and contrasting examples, a safe coach
  demonstration, a choice check, and one learner variation. Put the bridge
  before the first action that uses the unfamiliar syntax. First orient the
  learner to the parent subsystem. Use three to five one-at-a-time checks and a
  faded-support ladder inspired by the existing Rundrill teaching contract.
- Validation: skill validation and twelve deterministic tests pass. A fresh
  behavioral trace remains pending.

## 2026-09-03 — guided code discovery for beginners

- Source: human review of the first `EVENT-RIVER` lesson.
- Evidence: a theory-only learner was told to read several source files and
  produce a five-transition trace. The paths existed in the HTML map but were
  absent from the coach message.
- Change: the coach opens and shows one focused excerpt at a time, repeats the
  clickable path in chat, and uses two to four choice-based checks before short
  free recall. A beginner's first trace is split into small adjacent hops.
- Validation: skill validation and twelve deterministic tests pass. A fresh
  behavioral trace remains pending.

## 2026-09-03 — opening the first map is a required action

- Source: repeated human trial in Together.
- Evidence: the coach rendered `.onboarding/map.html`, then said that the
  browser did not open. It did not retry with the macOS `open` command.
- Change: the renderer falls back to the platform opener and returns a nonzero
  status when opening still fails. The coach must request GUI permission and
  retry. It can report only the path after the opener itself fails.
- Validation: twelve state, renderer, and browser-opening tests pass. Skill
  validation passes.

## 2026-09-02 — full route and repository-derived assessment

- Source: human review of a generated project plan.
- Evidence: the map stopped after seven nodes. Intake grouped GitHub, CI,
  staging, logs, and chat into one yes-or-no question. It also grouped four
  technologies into one broad self-rating.
- Change: show 3–5 chapters and normally 12–24 evidence-based nodes. Keep only
  the nearest 5–9 nodes detailed. Derive access checks from repository paths and
  use two to four small capability checks for the first task. Treat theory-only
  experience as a practical gap and add a short example-to-project bridge. Do
  not invent a product change when no approved work item exists.
- Validation: nine state and renderer tests pass. Current Together state remains
  valid and unchanged. Skill validation passes.

## 2026-09-02 — access readiness does not freeze the route

- Source: product-owner clarification after the Together trial.
- Requirement: onboarding must prove that required local commands work and
  role-relevant systems are accessible.
- Change: check near-term local capabilities, request long-lead access early,
  and link each external blocker to exact node codenames and `waiting_for`.
- Route rule: while an external action is pending, continue the first useful
  unblocked node. Mark the whole environment blocked only when no useful branch
  remains.
- Validation: seven state and renderer tests pass. Current Together state remains
  valid and unchanged. Skill validation passes.

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
