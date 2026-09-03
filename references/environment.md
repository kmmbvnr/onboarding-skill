# Check the local environment

Use this guide after intake and whenever a project command cannot run or fails.

## Establish a baseline

Build a finite readiness list from the learner's role and route. One check can
prove a category; do not test every similar command. Check every local category
needed for the first chapter:

- required runtime and package-manager versions;
- the supported dependency or environment command;
- one required local service, such as a database or queue;
- one focused test, build, or start command near the learner's goal.

Also identify external systems needed for normal work. Derive each system from
repository evidence, such as Git remotes, CI workflows, deployment files,
project documentation, and example environment variable names. Check only
role-relevant access.

Do not bundle source hosting, CI, staging, logs, chat, or deployment into one
yes-or-no question. For each unknown system, name the system, cite the evidence
path, explain which task needs it, and request one safe read-only check. Accept
"I do not know" and keep the requirement `unknown`. A bare yes is not enough to
prove critical access. Do not create records, push dummy changes, send test
messages, or deploy only to test access.

Request later access early when approval can take time. Do not delay the first
chapter while access for a later chapter is pending.

Ask the learner to run one check at a time. Do not request secrets. Do not
install software, start shared services, or change project configuration unless
the user asks.

Detect a graphical source editor as a convenience check:

```bash
python3 <skill-directory>/scripts/open_source.py --detect
```

Use `preferences.editor` when it already exists. Otherwise prefer `$VISUAL` or
`$EDITOR`. When detection finds exactly one supported graphical editor, store
it. When it finds several or none, ask the learner once which editor they use.
Do not install an editor. Editor availability is not a readiness blocker.

Record successful facts in `environment.working`. Record a blocker only when it
changes the safe next action.

Do not set environment status to `ready` while a role-required local capability
or external access is unverified. Record an unverified requirement as an
`unknown` blocker and link it to the nodes that will need it.

## Classify a blocker

- `machine`: a required local tool or compatible version is missing;
- `service`: a required local process is unavailable;
- `access`: permission, account, credential, or network access is missing;
- `project`: checked-in defaults, migrations, scripts, or documentation conflict;
- `unknown`: the evidence is not sufficient yet.

Do not label an environment blocker as a learner knowledge gap.

For each blocker, set `waiting_for` to the person, team, or learner action that
can resolve it. Set `blocks` to the exact node codenames that cannot continue.
Do not use a global blocker when only one branch is affected.

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

Keep independent nodes ready. Do not repeatedly select a node that waits for an
external action. Continue with a ready node whose codename is not in any
blocker's `blocks` list.

Use a small lab when a missing local dependency blocks project work but the
learner can still practice the required concept. Recheck a blocker when the
learner says the external action is complete. Remove it only after evidence
shows that the required access or command now works.
