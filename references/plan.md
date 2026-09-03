# Create the onboarding plan

## 1. Intake

Ask for:

- the learner's role and expected work;
- one concrete work or study task they completed, and how much help they used;
- one outcome they want from onboarding and the optional onboarding message
  from the supervisor.

Do not ask for a technology inventory before you inspect the project.
Ask at most three short questions in one message. Combine related items.
Do not infer the answers from the issue or the repository. Wait for the learner's
reply before you inspect the project or create state.

## 2. Inspect the project

Read project instructions, the main documentation, and files close to the
learner's goal. Detect the stack, start commands, tests, contribution flow,
delivery clues, and one representative product flow. Use recent history when it
is available. Do not read the repository from top to bottom. Stop when you have
enough evidence to build the route.

Inspect the names and metadata of project-owned visual assets first. Read at
most one small token or style file. Do not dump a large SVG or image as text.
Use the evidence to define the map theme. Prefer an existing project asset when
it helps explain a node. Do not copy art from an unrelated product. Use a
neutral theme when the project has no visual system.

Separate evidence from inference. Record unknown company facts as unknown.

Use [assessment.md](assessment.md) after inspection. Derive access and knowledge
checks from repository evidence. Do not use a generic stack questionnaire.

## 3. Check the local environment

Use [environment.md](environment.md). Check each local capability needed for the
first chapter. Identify all role-relevant external access and request
long-lead access before it blocks a later chapter. Ask the learner to run checks
one at a time. Record what works and what blocks progress. Do not turn a tool or
project failure into a learner failure.

If the environment is not fully ready, keep an independent safe branch open.
Do not lock the whole map when the learner can still inspect, trace, or use a
small lab.

## 4. Check only gating knowledge

Use [assessment.md](assessment.md). Use two to four short checks when a missing
prerequisite can block an early node. Ask the learner to explain, trace,
predict, or run something. Do not use trivia or broad self-ratings.

An experienced learner can place out of a node with clear evidence. A beginner must get an early, low-risk win before a long trace.
Do not add a node for a tool basic or policy restatement when intake evidence
already shows that the learner can apply it to the goal.

## 5. Build the route

Create a visible route of 3 to 5 named chapters. A normal production project
should start with 12 to 24 nodes. Use fewer than 12 only when the role and
project are genuinely narrow, and explain why. Do not add filler to reach a
number.

Make the first chapter detailed and immediately usable. Give it 5 to 9 nodes.
Later chapters are visible route landmarks. Keep them locked and revise their
details after evidence from the first real task. Each node must still name one
observable result in 5 to 20 minutes. The hard limit is 25 minutes. Split
longer work into checkpoints. Use short codenames such as `FIRST-LIGHT`,
`REQUEST-RIVER`, or `SAFE-HARBOR`.

Prefer this route:

1. a small visible win;
2. only the goal-specific prerequisite or trace;
3. a first-task action, when an approved task exists;
4. its focused test and review;
5. the next useful branch.

Put the first useful work action in the first three nodes. Do not make the
learner finish a repository tour before useful work.

Do not invent a product change for onboarding. A real change needs a work
source: a supervisor task, an assigned or selected issue, a confirmed bug, a
failing test with an agreed expectation, or an explicit project TODO. Put that
reference in the node's `project_paths`. "Find an inconsistency and fix it" is
not a valid task.

When no approved work item exists, do not create a generic `FIRST-PATCH` node.
Keep product changes locked until the learner or supervisor supplies a task.
Continue with safe setup, a product-flow trace, focused tests, or a lab that
does not change product code.

Cover the actual work loop, not only the first issue. Use project evidence to
include the relevant parts of local operation, one product flow, a safe change,
focused tests and review, delivery, and observation. Include the change only
when an approved work item exists. Omit parts that the role does not use.

Add branches only when the role needs them. If a required library or technology is missing, add a small lab under `.onboarding/labs/<codename>/`. The lab must teach the idiomatic basics before the learner studies project-specific use. A lab is practice, not a fabricated product task.

When the learner reports theory without practice for a gating technology, add
a one-to-three-node bridge before a large project trace: its purpose in this
project, one minimal example, and one small learner change. Do not replace this
bridge with "read these project files."

Avoid one fully linear chain when an access request can take time. Link each
open blocker only to the nodes it prevents. Keep at least one useful independent
node ready when project evidence allows it.

Do not add a broad topic such as "Learn Django." State the next action instead.

## 6. Save and show

Create `.onboarding/state.json` as defined in [state.md](state.md). Add `.onboarding/` to `.git/info/exclude` when possible. Render and open the first map:

```bash
python3 <skill-directory>/scripts/render_map.py .onboarding/state.json --open
```

Do not wait for the user to ask you to open it. If the runtime blocks browser
launch, request GUI permission and retry with the absolute map path and the
platform opener: `open` on macOS, `xdg-open` on Linux, or `start` on Windows.
Do not merely offer to open the map. Only after the opener itself fails can you
report the error and give the exact clickable map path. Later renders refresh
the open page.

Report:

- the first ready node;
- what the learner skipped and why;
- the largest unknown or risk;
- the map path.

Do not start the first lesson unless the user asks to continue.
