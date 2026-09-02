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

## 2. Inspect the project

Read project instructions and the main documentation. Detect the stack, start commands, tests, contribution flow, delivery clues, and one representative product flow. Use recent history when it is available. Do not read the repository from top to bottom.

Inspect the project's logo, color tokens, styles, and owned images. Use them to define the map theme. Prefer an existing project asset when it helps explain a node. Do not copy art from an unrelated product. Use a neutral theme when the project has no visual system.

Separate evidence from inference. Record unknown company facts as unknown.

## 3. Check only gating knowledge

Use two to four short checks when a missing prerequisite can block an early node. Ask the learner to explain, trace, predict, or run something. Do not use trivia.

An experienced learner can place out of a node with clear evidence. A beginner must get an early, low-risk win before a long trace.

## 4. Build the route

Create 7 to 15 nodes. Each node must produce one observable result. Use short codenames such as `FIRST-LIGHT`, `REQUEST-RIVER`, or `SAFE-HARBOR`.

Prefer this route:

1. product purpose;
2. local start and checks;
3. one vertical system flow;
4. contribution and review loop;
5. delivery and observation;
6. a low-risk real task;
7. scoped ownership.

Add branches only when the role needs them. If a required library or technology is missing, add a small lab under `.onboarding/labs/<codename>/`. The lab must teach the idiomatic basics before the learner studies project-specific use.

Do not add a broad topic such as "Learn Django." State the next action instead.

## 5. Save and show

Create `.onboarding/state.json` as defined in [state.md](state.md). Add `.onboarding/` to `.git/info/exclude` when possible. Render `.onboarding/map.html`.

Report:

- the first ready node;
- what the learner skipped and why;
- the largest unknown or risk;
- the map path.

Do not start the first lesson unless the user asks to continue.
