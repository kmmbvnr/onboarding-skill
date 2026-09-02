# Create the onboarding plan

## 1. Intake

Ask for:

- the learner's role and expected work;
- relevant work or study experience;
- technologies they can use without help;
- technologies they have seen but cannot use;
- one outcome they want from onboarding;
- the optional onboarding message from the supervisor to the learner.

Do not ask for a complete skill inventory.
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

## 3. Check the local environment

Use [environment.md](environment.md). Select two to five checks from project
evidence. Ask the learner to run them one at a time. Record what works and what
blocks progress. Do not turn a tool or project failure into a learner failure.

If the environment is not fully ready, keep an independent safe branch open.
Do not lock the whole map when the learner can still inspect, trace, or use a
small lab.

## 4. Check only gating knowledge

Use two to four short checks when a missing prerequisite can block an early node. Ask the learner to explain, trace, predict, or run something. Do not use trivia.

An experienced learner can place out of a node with clear evidence. A beginner must get an early, low-risk win before a long trace.
Do not add a node for a tool basic or policy restatement when intake evidence
already shows that the learner can apply it to the goal.

## 5. Build the route

Create 5 to 9 nodes for the first chapter. Add later chapters after the learner
completes a real task. Each node must produce one observable result in 5 to 20
minutes. The hard limit is 25 minutes. Split longer work into checkpoints. Use
short codenames such as `FIRST-LIGHT`, `REQUEST-RIVER`, or `SAFE-HARBOR`.

Prefer this route:

1. a small visible win;
2. only the goal-specific prerequisite or trace;
3. a low-risk real change;
4. its focused test and review;
5. the next useful branch.

Put the first useful change in the first three nodes. Do not make the learner
finish a repository tour before the first change.

Add branches only when the role needs them. If a required library or technology is missing, add a small lab under `.onboarding/labs/<codename>/`. The lab must teach the idiomatic basics before the learner studies project-specific use.

Do not add a broad topic such as "Learn Django." State the next action instead.

## 6. Save and show

Create `.onboarding/state.json` as defined in [state.md](state.md). Add `.onboarding/` to `.git/info/exclude` when possible. Render and open the first map:

```bash
python3 <skill-directory>/scripts/render_map.py .onboarding/state.json --open
```

Do not wait for the user to ask you to open it. If the runtime blocks browser
launch, give the exact map path. Later renders refresh the open page.

Report:

- the first ready node;
- what the learner skipped and why;
- the largest unknown or risk;
- the map path.

Do not start the first lesson unless the user asks to continue.
