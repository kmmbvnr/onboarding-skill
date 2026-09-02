# Check the local environment

Use this guide after intake and whenever a project command cannot run or fails.

## Establish a baseline

Choose two to five checks from project files. Prefer:

- required runtime and package-manager versions;
- the supported dependency or environment command;
- one required local service, such as a database or queue;
- one focused test, build, or start command near the learner's goal.

Ask the learner to run one check at a time. Do not request secrets. Do not
install software, start shared services, or change project configuration unless
the user asks.

Record successful facts in `environment.working`. Record a blocker only when it
changes the safe next action.

## Classify a blocker

- `machine`: a required local tool or compatible version is missing;
- `service`: a required local process is unavailable;
- `access`: permission, account, credential, or network access is missing;
- `project`: checked-in defaults, migrations, scripts, or documentation conflict;
- `unknown`: the evidence is not sufficient yet.

Do not label an environment blocker as a learner knowledge gap.

## Interpret a failed command

Use the node's evidence contract, not the exit code alone.

- If the goal was to run, observe, or diagnose a command, mark the node `done`
  when that evidence is complete. Save the failure as a blocker.
- If the goal required a passing result, append a `stopped` session and set the
  node to `revisit`. Save the blocker and its next action.
- Never set a node to `skipped` because a command failed.

Example: a focused test exits during database creation. A "capture the local
baseline" node can be `done` when the learner ran the correct command and
identified the database mismatch. A "make the test pass" node is not `done`.

## Keep progress possible

Set environment status to:

- `ready` when the required path works;
- `partial` when a blocker exists but another safe branch is available;
- `blocked` when no safe project action can continue;
- `unknown` before the baseline is complete.

Keep independent nodes ready. Use a small lab when a missing local dependency
blocks project work but the learner can still practice the required concept.
