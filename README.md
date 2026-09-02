# Onboarding skill

`$onboarding` creates and runs a project-specific developer onboarding path.
It inspects the current repository, checks the learner's relevant experience,
and renders a local HTML learning map.

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

Each initial chapter has 5–9 nodes. A node must take no more than 25 minutes.
Long tasks are split into checkpoints with separate evidence.

## Evaluation

The `evals/` directory contains isolated behavioral tests for the skill. Eval
agents work in disposable copies of public repositories. They cannot see the
hidden oracle or the accepted solution.
