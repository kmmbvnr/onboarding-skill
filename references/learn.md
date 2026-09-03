# Run a learning node

## Select

Use `.onboarding-demo/state.json` for the self-tour or a `TOUR-*` codename. Use `.onboarding/state.json` for project onboarding.

Validate the state before you select a node. If an older map contains an
unfinished node longer than 25 minutes, split that node into short checkpoints.
Preserve completed nodes, session evidence, and claimed capability. Render the
migrated map before the lesson.

Build the set of waiting codenames from `environment.blockers[].blocks`. Do not
select one of those nodes while its blocker is open.

Select the requested codename. If there is no codename, select the first
unblocked `active` node, then the first unblocked `revisit` node, then the first
unblocked `ready` node. A node is ready only when all required nodes are `done`
or `skipped`.

If there is no project state, route to `plan`. If there is no tour state, route
to `tour`. If the requested node is locked or waits for an external action,
explain the specific prerequisite or blocker and offer the nearest unblocked
node.

## Teach

Inspect the relevant project files before the lesson. Do not assume that the
learner saw the paths in the HTML map. Repeat the exact path needed for the
current action in the chat.

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

Use two to four small checks across a beginner node. Prefer choices, ordering,
matching, or prediction before free recall. Reduce the support after correct
answers. End with one short retrieval that matches the node evidence.

For an experienced learner, use the compact loop:

1. State the node goal and its value to the learner's work.
2. Ask for a prediction or prior explanation.
3. Give one short action in the real project or lab.
4. Ask what the learner observed.
5. Give direct feedback. Explain one gap at a time.
6. Ask for a final retrieval, trace, run, or small change that matches the node evidence.

Do not paste the answer before the learner tries. A focused source excerpt is
context, not an answer leak, when the learner still has to predict its behavior
or connect it to the next step. Do not turn the session into a lecture. Use a
quiz only when it tests a decision or mental model.

Help the learner start the project and inspect errors. Confirm commands from project files before you suggest them.
When a command cannot run or fails, use [environment.md](environment.md). Keep
the command, exit result, and smallest useful error as evidence.

Guide source changes only when the node requires a real low-risk task. The learner makes the change. Do not edit product code unless the learner explicitly asks you to do it.

## Complete

Mark a node `done` only when the recorded evidence matches its `evidence` field.
A nonzero exit does not prevent `done` when the node goal was to run, observe,
or diagnose the command. Record the blocker separately.

Use `revisit` when the learner needs more knowledge or practice. Use a
`stopped` session and an environment blocker when the machine, service, access,
or project prevents the required result. Use `skipped` only when prior evidence
makes the node unnecessary. Never use `skipped` for a failed command.

When an external blocker appears, set an attempted node to `revisit` or an
unstarted node to `locked`. Record who or what resolves it and the exact blocked
codenames. Then continue an independent node. Set environment status to
`blocked` only when no useful unblocked node remains.

Append a short session record. Include the date, result, evidence, and one remaining gap. Set newly unlocked and unblocked nodes to `ready`. Render the map again. Do not open a new browser tab. The existing map refreshes itself.

The page shows a reward button only after the node status is `done`. The learner
claims the reward in the browser. Do not mark a node `done` to expose the button;
require the node evidence first.

End with:

- what the learner can now do;
- the next ready codename;
- one open question, if one exists.
