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

Inspect the relevant project files before the lesson. Then use this loop:

1. State the node goal and its value to the learner's work.
2. Ask for a prediction or prior explanation.
3. Give one short action in the real project or lab.
4. Ask what the learner observed.
5. Give direct feedback. Explain one gap at a time.
6. Ask for a final retrieval, trace, run, or small change that matches the node evidence.

Do not paste the answer before the learner tries. Do not turn the session into a lecture. Use a quiz only when it tests a decision or mental model.

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
