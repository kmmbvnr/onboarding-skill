# Learn to use onboarding

Use this mode when the user asks for a tour, or when `$onboarding` runs outside a recognizable project.

A recognizable project has clear evidence such as `.git`, a package manifest, a build file, or source directories with project documentation. A generic folder name or one unrelated file is not enough.

## Create or continue

Use `.onboarding-demo/state.json`. Do not use `.onboarding/state.json` for the tour.

If tour state does not exist, run:

```bash
python3 <skill-directory>/scripts/create_tour.py --language <ru|en> --output-dir .onboarding-demo --open
```

For another user language, create the English state, translate display text and labels, then render it again. Keep codenames and JSON enum values unchanged.

Add `.onboarding-demo/` to `.git/info/exclude` when the directory is inside a Git project. Open the map without waiting for the user to ask. Then start `TOUR-START` without another question.

If tour state exists, continue its active, revisit, or next ready node.

## Nodes

- `TOUR-START`: Show how the map, status, and codename work.
- `TOUR-LEAD`: Explain that `$onboarding lead` creates a message from a supervisor to a new developer. Ask for one example expectation.
- `TOUR-MAP`: Explain that `$onboarding` in a project assesses the learner, inspects the repository, and creates `.onboarding/map.html`.
- `TOUR-NODE`: Let the user choose a codename from the map. Explain `$onboarding` versus `$onboarding CODENAME`.
- `TOUR-ASK`: Give one vague mentor question. Ask the user to add goal, expected result, observed result, and attempts. Then explain `$onboarding ask`.
- `TOUR-REPORT`: Ask when to use a daily report and when to use a final report. Show `$onboarding report` and `$onboarding report final`.
- `TOUR-DONE`: Ask the user to name the first action in a real project. Then tell them to change to the project root and run `$onboarding`.

Use the normal learning loop from [learn.md](learn.md). Keep each node under five minutes. Update the demo state and render `.onboarding-demo/map.html` after each node.

The tour demonstrates actions. It does not inspect the current directory as a software project, create a real learner plan, or contact a supervisor.
