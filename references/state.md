# Local state

Use `.onboarding/state.json` as the source of truth. Use UTF-8 JSON with two-space indentation.

Required top-level fields:

```json
{
  "version": 1,
  "language": "two-letter user language code",
  "labels": {
    "filter_all": "",
    "filter_ready": "",
    "filter_active": "",
    "filter_done": "",
    "filter_revisit": "",
    "details": "",
    "why": "",
    "evidence": "",
    "requires": "",
    "none": "",
    "nodes": "",
    "minutes": "",
    "footer": ""
  },
  "theme": {
    "ink": "#263225",
    "muted": "#657060",
    "paper": "#fffdf2",
    "background_top": "#dff4a0",
    "background_bottom": "#acd465",
    "path": "#f7dc98",
    "accent": "#ec5652",
    "done": "#4b9460",
    "locked": "#aeb5aa",
    "revisit": "#8067ae",
    "logo": ""
  },
  "project": {"name": "", "root": "", "goal": ""},
  "learner": {"role": "", "experience": [], "placed_out": []},
  "nodes": [],
  "sessions": []
}
```

Each node requires:

```json
{
  "codename": "FIRST-LIGHT",
  "title": "Start the project",
  "summary": "Run the supported local path and identify each process.",
  "why": "You need a repeatable environment before you change code.",
  "kind": "setup",
  "target": "operate",
  "status": "ready",
  "requires": [],
  "estimated_minutes": 25,
  "icon": "🚀",
  "image": "",
  "evidence": "The learner starts the project and explains the main processes.",
  "project_paths": ["README.md"]
}
```

`estimated_minutes` must be from 1 to 25. Prefer 5 to 20. Split longer work into
separate nodes with separate evidence.

Allowed values:

- `kind`: `orientation`, `check`, `setup`, `trace`, `lab`, `task`, `review`.
- `target`: `recognize`, `operate`, `modify`.
- `status`: `locked`, `ready`, `active`, `done`, `revisit`, `skipped`.

Codenames must be unique uppercase words joined with hyphens. Dependencies must use codenames. Do not store secrets, environment values, or private tokens.

Write every `labels` value in the user's language. The `footer` tells the user to open a node and use its command.

Set `theme` from project-owned visual assets and color tokens. Use CSS hex colors. Paths in `theme.logo` and node `image` are relative to `.onboarding/map.html`. Use an empty string when there is no suitable image.

Each session record requires `date`, `codename`, `result`, `evidence`, and `gap`. The result is `done`, `revisit`, or `stopped`.
