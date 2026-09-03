# Run a learning node

## Select

Use `.onboarding-demo/state.json` for the self-tour or a `TOUR-*` codename. Use `.onboarding/state.json` for project onboarding.

Validate the state before you select a node. If an older map contains an
unfinished node longer than 25 minutes, split that node into short checkpoints.
Preserve completed nodes, session evidence, and claimed capability. Render the
migrated map before the lesson.

Also migrate a node from `active` or `locked` to `waiting` when the learner has
completed every available action and progress now depends only on CI, review,
approval, or a reply. Record `waiting_for`, `check_after`, and one read-only
`check_action`. Do not ask a quiz whose intended answer is only "wait".

Before node selection, inspect waiting nodes. When `check_after` is today or in
the past, perform its read-only check once if current access permits it. Do not
sleep or poll. If the external event is still pending, move `check_after` to the
next reasonable work date and continue onboarding. If it creates a learner
action, change the node to `ready` or `revisit` and remove `wait`.

Build the set of waiting codenames from `environment.blockers[].blocks` and
nodes whose status is `waiting`. Do not select them while the dependency is
open.

Select the requested codename. If there is no codename, select the first
unblocked `active` node, then the first unblocked `revisit` node, then the first
unblocked `ready` node. A node is ready only when all required nodes are `done`
or `skipped`.

If there is no project state, route to `plan`. If there is no tour state, route
to `tour`. If the requested node is locked or waits for an external action,
explain the specific prerequisite or blocker and offer the nearest unblocked
node.

Audit dependencies when a node starts waiting. Remove the waiting node from a
later node's `requires` when that later action does not need the external
result. Keep the last real prerequisite instead. Set the independent node to
`ready` when its remaining requirements are complete.

## Teach

Use [teaching.md](teaching.md) to select the support level for the current
concept. Do not use the learner's general seniority as proof that they know a
specific language or tool.

Inspect the relevant project files before the lesson. Do not assume that the
learner saw the paths in the HTML map. Repeat the exact path needed for the
current action in the chat.

Before the first source excerpt, read `preferences.editor`. If it is absent,
run the editor detection from [environment.md](environment.md). Save one
unambiguous result. If several editors are available, ask the learner once.
When the learner names an editor, use it immediately and save the preference.

Open the exact source location before you discuss it:

```bash
python3 <skill-directory>/scripts/open_source.py \
  --editor <editor> --line <line> --column <column> <absolute-file>
```

Request GUI permission and retry when required. Do not claim that the file is
open until the command succeeds. If no supported editor is available, continue
with the clickable link and excerpt. Do not block learning. Opening the editor
does not replace showing the focused excerpt in chat.

For a beginner or a learner with theory but no practice, guide discovery:

1. Select one small concept or one adjacent transition in the project flow.
2. Open the relevant file yourself with a file-reading tool.
3. Give a clickable absolute file link with a line number. Show only the
   relevant 5–20 lines, or a short safe summary when the source contains
   sensitive data.
4. Ask one decision question with three or four answer choices. Include an "I
   am not sure" choice. Wait for the answer.
5. Give short feedback, then show the next file or action.

Introduce at most one new project file per learner turn. A node can contain
several `project_paths`, but reveal them one at a time. Do not say "read these
files and send a trace" as one action.

Use three to five small checks across an `unknown` or `theory-only` concept.
Ask one per message and state progress, such as "Question 2 of 4." Prefer
choices, ordering, matching, or a filled example with one blank before free
recall. Reduce the support after correct answers. End with one short retrieval
that matches the node evidence.

For an experienced learner, use the compact loop:

1. State the node goal and its value to the learner's work.
2. Ask for a prediction or prior explanation.
3. Give one short action in the real project or lab.
4. Ask what the learner observed.
5. Give direct feedback. Explain one gap at a time.
6. Ask for a final retrieval, trace, run, or small change that matches the node evidence.

If the learner says that they do not know a concept used by the active node,
stop the compact loop. Switch to the teach-first loop. Explain the concept
before another prediction or command.

Do not paste the answer before the learner tries. A focused source excerpt is
context, not an answer leak, when the learner still has to predict its behavior
or connect it to the next step. Do not turn the session into a lecture. Use a
quiz only when it tests a decision or mental model.

Help the learner start the project and inspect errors. Confirm commands from project files before you suggest them.
When a command cannot run or fails, use [environment.md](environment.md). Keep
the command, exit result, and smallest useful error as evidence.

Before the learner's first product-code change in a module, teach its local
code-quality path. Use documented contribution rules, formatter or linter
configuration, CI, and a small nearby source example. State which rules a tool
checks and which rules a reviewer checks. Ask one concrete choice, comparison,
or fix-the-snippet question at a time. Then let the learner run the smallest
documented formatter, linter, or static check that covers the target. Do not
teach generic style trivia or claim that one nearby example is a project rule.

Guide source changes only when the node requires a real low-risk task. The learner makes the change. Do not edit product code unless the learner explicitly asks you to do it.

## Complete

Mark a node `done` only when the recorded evidence matches its `evidence` field.
A nonzero exit does not prevent `done` when the node goal was to run, observe,
or diagnose the command. Record the blocker separately.

Do not close a node by asking the learner to say "understood" or to repeat a
sentence that the coach just supplied. Before completion, use a fresh small
example, choice, trace, or learner action that requires the same mental model.
If the learner says they still lack the overall context, return to the
execution story and keep the node active.

Use `revisit` when the learner needs more knowledge or practice. Use a
`stopped` session and an environment blocker when the machine, service, access,
or project prevents the required result. Use `skipped` only when prior evidence
makes the node unnecessary. Never use `skipped` for a failed command.

When a machine, service, access, or project blocker appears, set an attempted
node to `revisit` or an unstarted node to `locked`. Record who or what resolves
it and the exact blocked codenames. Set environment status to `blocked` only
when no useful unblocked node remains.

When the learner completed their part but CI, review, approval, or a reply is
pending, keep the completed node `done` and set the response-dependent node to
`waiting`. Do not call it active or an environment failure. Record the next
check and continue an independent node. The skill checks waits only when it is
invoked; it does not promise background monitoring.

Append a short session record. Include the date, result, evidence, and one remaining gap. Set newly unlocked and unblocked nodes to `ready`. Render the map again. Do not open a new browser tab. The existing map refreshes itself.

The page shows a reward button only after the node status is `done`. The learner
claims the reward in the browser. Do not mark a node `done` to expose the button;
require the node evidence first.

End with:

- what the learner can now do;
- the next ready codename;
- one waiting item and its next check, when one exists;
- one open question, if one exists.
