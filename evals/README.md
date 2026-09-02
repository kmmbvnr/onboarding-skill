# Onboarding evals

The eval runner pairs an onboarding coach with a simulated learner in a
disposable repository. The coach can write onboarding state. Only the learner
may change product code.

Each case pins a public repository to a commit before a real issue was solved.
The runner creates a new Git history from that snapshot. Agents cannot inspect
the accepted solution. A hidden test runs after the conversation.

Prepare the first case without calling agents:

```sh
python3 evals/run_case.py \
  evals/cases/django-modern-rest-1225 \
  --persona junior \
  --repo-cache /path/to/django-modern-rest \
  --prepare-only
```

Run the skill arm:

```sh
python3 evals/run_case.py \
  evals/cases/django-modern-rest-1225 \
  --persona junior \
  --repo-cache /path/to/django-modern-rest
```

Check only the coach's first response before a longer run:

```sh
python3 evals/run_case.py \
  evals/cases/django-modern-rest-1225 \
  --persona junior \
  --repo-cache /path/to/django-modern-rest \
  --smoke-first-turn
```

Use `--arm baseline` to replace `$onboarding` with a generic read-only mentor.
Results are written under `evals/runs/` and are ignored by Git.

The runner does not edit the skill. The final review contains a proposed
change. Apply a proposal only after it improves repeated runs and does not
regress existing cases.
