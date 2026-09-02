# Assess the learner from project evidence

Use a short adaptive assessment. Do not ask the learner to inventory the whole
stack.

## Start with a small intake

Before project inspection, ask only for:

- the role and expected work;
- one concrete work or study task they completed, and how much help they used;
- the desired onboarding outcome and the optional supervisor message.

Wait for the reply. Do not ask which items from a long technology list the
learner knows.

## Derive requirements from the repository

After intake, inspect only evidence near the role and first useful task. Build
an internal checklist with:

- the required capability or system;
- the repository path that proves it is relevant;
- the task or node that needs it;
- a safe way to verify it;
- `verified`, `unknown`, `missing`, or `not-needed`.

Use manifests, project instructions, documented commands, Git remotes, CI
workflows, deployment configuration, and example environment variable names.
Do not read secret values or real environment files.

## Check access concretely

Do not ask one grouped question such as "Do you have GitHub, CI, staging, logs,
and chat access?" The learner can answer yes without knowing what each item
means.

For each role-relevant system that is still unknown:

1. Name the exact system.
2. Cite the repository path that shows why it is needed.
3. State the near-term task that needs it.
4. Ask for one safe, read-only check.

Example: "`.github/workflows/test.yml` uses GitHub Actions. Can you open the
latest Actions run for this repository? Answer: yes, no, or I do not know."

Do not accept a bare yes as proof of critical access. Use read-only evidence or
keep the item `unknown`. "I do not know" is a valid answer. Record it as an
environment unknown, not as a learner failure. Do not create dummy issues,
pushes, deployments, or messages to test access.

Check safe machine facts directly when the agent can do so. Ask the learner
only for facts that the agent cannot verify.

## Check knowledge with small evidence

Do not ask "What is your level in Django, React, PostgreSQL, and Docker?" It
hides uneven knowledge and rewards confident self-rating.

Select only two to four capabilities that gate the first useful task. Derive
them from the files and libraries close to that task. Check one capability at a
time with a small action:

- explain a 10–20 line code path;
- predict a command or function result;
- choose or run one focused test;
- compare a small diff and state its effect.

Use the evidence to place out an experienced learner or add one small lab for a
missing prerequisite. Do not quiz every dependency. Defer non-gating libraries
until the learner reaches the branch that uses them.

Treat "I know the theory but have not used it" as a practical gap. Do not send
that learner directly into a large project file. Add a short bridge before the
first project trace:

1. explain the technology's job in this project;
2. show one minimal idiomatic example;
3. let the learner predict and change the example in a small lab;
4. move to the matching project code.

Use one to three nodes of 5 to 15 minutes. Skip or shorten the bridge when the
learner produces equivalent practical evidence.

Stop the initial assessment when the first chapter is tailored and the learner
has a safe next action. Continue assessment just in time during later nodes.
