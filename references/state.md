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
  "environment": {
    "checked_at": "YYYY-MM-DD",
    "status": "unknown",
    "working": [],
    "blockers": []
  },
  "nodes": [],
  "sessions": []
}
```

New project plans include `environment`. Existing states and self-tours can
omit it. Allowed status values are `unknown`, `ready`, `partial`, and `blocked`.

Project state can include a local preference:

```json
"preferences": {"editor": "zed"}
```

Supported editor names are `zed`, `code`, `cursor`, and `subl`. Detect the
preference once. Do not store arbitrary commands or global editor settings.

Each blocker requires:

```json
{
  "id": "TEST-DATABASE",
  "scope": "project",
  "summary": "The documented test command cannot create its database.",
  "evidence": "The command exited before tests ran because migration 0036 uses ArrayField on SQLite.",
  "next_action": "Run the supported PostgreSQL test path or clarify SQLite support.",
  "waiting_for": "Project owner decision",
  "blocks": ["FIRST-PATCH"]
}
```

Allowed blocker scopes are `machine`, `service`, `access`, `project`, and
`unknown`. Store tool versions and successful checks in `working`. Do not store
tokens, environment values, or other secrets.

`waiting_for` names the person, team, or learner action that can resolve the
blocker. `blocks` contains only node codenames that cannot continue. Other ready
nodes stay available. Remove a blocker after a new check proves it resolved.

Each node requires:

```json
{
  "codename": "FIRST-LIGHT",
  "chapter": "Run the project",
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

Use `waiting` when the learner completed the available action and the node now
depends only on an external event. A waiting node also requires:

```json
"status": "waiting",
"wait": {
  "waiting_for": "Repository maintainers and CI",
  "check_after": "2026-09-04",
  "check_action": "Check the PR checks and new review comments once."
}
```

`check_after` uses `YYYY-MM-DD`. Update it after each unresolved check. Do not
add `wait` to another status. A waiting node is visible, but it is not an active
lesson and does not block an independent branch.

`chapter` is optional for old state files and self-tours. New project plans set
it on every node. Use 3 to 5 short chapter names and keep nodes from the same
chapter adjacent. The map shows a chapter marker when the name changes.

`estimated_minutes` must be from 1 to 25. Prefer 5 to 20. Split longer work into
separate nodes with separate evidence.

Allowed values:

- `kind`: `orientation`, `check`, `setup`, `trace`, `lab`, `task`, `review`.
- `target`: `recognize`, `operate`, `modify`.
- `status`: `locked`, `ready`, `active`, `waiting`, `done`, `revisit`, `skipped`.

Codenames must be unique uppercase words joined with hyphens. Dependencies must use codenames. Do not store secrets, environment values, or private tokens.

Write every `labels` value in the user's language. The `footer` tells the user to open a node and use its command.

Set `theme` from project-owned visual assets and color tokens. Use CSS hex colors. Paths in `theme.logo` and node `image` are relative to `.onboarding/map.html`. Use an empty string when there is no suitable image.

Each session record requires `date`, `codename`, `result`, `evidence`, and `gap`. The result is `done`, `revisit`, or `stopped`.

`done` means the node evidence was produced. It does not mean every command
returned zero. `stopped` means an external blocker prevented the required
result. `skipped` is a node status, not a session result; use it only for prior
evidence or a node that is no longer needed.

Environment blockers describe missing local capability, service, access, or a
project problem. Do not use them for normal CI, review, approval, or reply
latency after the learner has completed their action. Use a waiting node.
