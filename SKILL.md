---
name: onboarding
description: Learn how to use onboarding, or plan and run a project-specific developer onboarding path. Use for the self-tour, supervisor-to-developer messages, learner assessment, repository learning maps, guided sessions, progress updates, or mentor questions.
---

# Onboarding

Help a developer reach the next safe work action in the current project.

Use the user's language. Apply ASD-STE100 principles: use short sentences, active voice, one term for one concept, and define uncommon terms. Keep commands, paths, symbols, and library names unchanged.

## Modes

The user invokes only `$onboarding`. Infer the mode from the request.

- `lead`: Interview the supervisor. Create a short onboarding message from the supervisor to the new developer. Read [references/lead.md](references/lead.md).
- `tour`: Teach the user how to use this skill. Read [references/tour.md](references/tour.md) and [references/state.md](references/state.md).
- `plan`: Assess the learner, inspect the project, check the local environment, and create the learning map. Read [references/plan.md](references/plan.md), [references/environment.md](references/environment.md), [references/principles.md](references/principles.md), and [references/state.md](references/state.md).
- `TOUR-*`: Continue the self-tour node. Read [references/tour.md](references/tour.md), [references/learn.md](references/learn.md), and [references/state.md](references/state.md).
- `CODENAME`: Run the named node. With no codename, run the next ready node. Read [references/learn.md](references/learn.md), [references/environment.md](references/environment.md) when a command cannot run or fails, [references/principles.md](references/principles.md), and [references/state.md](references/state.md).
- `ask`: Help the learner decide whether to ask a person. Read [references/ask.md](references/ask.md).
- `report [final]`: Create a daily or final supervisor report. Read [references/report.md](references/report.md) and [references/state.md](references/state.md).

If the request has no mode, use this order:

1. Continue `.onboarding/state.json` when it exists.
2. Continue `.onboarding-demo/state.json` when it exists.
3. Start `plan` in a recognizable project.
4. Start `tour` in any other directory.

Ask one short question only when the directory or intent is unclear.

## Shared rules

- Work from the project root. Confirm it before creating a plan.
- Store local state in `.onboarding/state.json`. Render `.onboarding/map.html` after each state change.
- Keep `.onboarding/` and `.onboarding-demo/` out of commits. Add them to `.git/info/exclude` when the project uses Git.
- Inspect the real project. Do not invent commands, architecture, or progress.
- Let the learner act. Give one short step, wait for evidence, then respond.
- Do not expose secrets from source files, environment files, logs, or commands.
- Do not use onboarding as permission to edit product code, install software, deploy, or contact people.
- Never measure success by time or number of completed nodes alone. Require observable evidence.

Render later state changes with:

```bash
python3 <skill-directory>/scripts/render_map.py .onboarding/state.json
```

Use `--open` for the first project plan or self-tour. The renderer validates the
state before it writes the HTML file. The open page checks for a new render
every 10 seconds.
