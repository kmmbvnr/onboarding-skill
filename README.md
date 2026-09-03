# Onboarding skill

`$onboarding` creates and runs a project-specific developer onboarding path.
It inspects the current repository, checks the learner with small project-based
actions, and renders a local HTML learning map. Access checks name the exact
system and repository evidence. The skill does not use grouped yes-or-no
inventories.

The first map opens in the user's default browser. It uses short learning
nodes, refreshes after state changes, and offers a local reward only after the
agent verifies a node as done.

## Install

Link this directory into your agent skills directory:

```sh
ln -s /path/to/onboarding-skill ~/.agents/skills/onboarding
```

## Use

Run the skill from a project directory:

```text
$onboarding lead
$onboarding plan
$onboarding
$onboarding ask
$onboarding report
```

Use `$onboarding tour` outside a project to learn the workflow.

The skill stores learner state in `.onboarding/`. It keeps the self-tour state
in `.onboarding-demo/`. Both directories stay local to the project.

The initial map shows 3–5 chapters. A normal production project starts with
12–24 nodes, while the nearest 5–9 nodes form the detailed first chapter. A node
must take no more than 25 minutes. Long tasks are split into checkpoints with
separate evidence.

The first chapter also records a small local-environment baseline. A failed
command can still complete a diagnostic node; machine and project blockers are
tracked separately from learner progress.

The baseline covers local commands and role-relevant external access. A pending
access request blocks only the nodes that need it. The learner continues on an
independent branch while another person or team completes the request.

The skill does not invent product work. A real code change must refer to a
supervisor task, issue, confirmed bug, agreed failing test, or explicit TODO.

For a beginner, the coach shows one focused source excerpt at a time and uses
short choice-based checks. It does not assign a batch of files as the first
action.

## Evaluation

The `evals/` directory contains isolated behavioral tests for the skill. Eval
agents work in disposable copies of public repositories. They cannot see the
hidden oracle or the accepted solution.
