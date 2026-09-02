# Onboarding skill

`$onboarding` creates and runs a project-specific developer onboarding path.
It inspects the current repository, checks the learner's relevant experience,
and renders a local HTML learning map.

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

## Evaluation

The `evals/` directory contains isolated behavioral tests for the skill. Eval
agents work in disposable copies of public repositories. They cannot see the
hidden oracle or the accepted solution.
