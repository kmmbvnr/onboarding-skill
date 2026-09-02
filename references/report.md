# Report onboarding status

Read `.onboarding/state.json`. Use recorded evidence. Do not infer competence from elapsed time or node count.

Do not create a supervisor report from `.onboarding-demo/state.json`. The demo is a private tutorial. If project state does not exist, explain this boundary and continue `TOUR-REPORT` when the user is in the self-tour.

Ask the learner to confirm two facts before you write:

- Is there a blocker or question that the supervisor must resolve?
- Did any completed work or evidence occur outside the recorded sessions?

Do not include secrets, private feedback, raw quiz errors, or unsupported claims. Use `environment.blockers` when it exists. Separate machine, service, access, and project blockers from learning gaps. Use the learner's language and ASD-STE100 principles.
For each open blocker, name `waiting_for`, the blocked codenames, and the next
action. Do not report the whole onboarding as blocked while another useful node
is available.

## Daily report

Use sessions for the current date. Save `.onboarding/reports/YYYY-MM-DD.md`.

```markdown
# Onboarding status — YYYY-MM-DD

Goal:
Verified today:
- <capability and evidence>

Can now:
- <work action>

Blockers or open questions:
- <item, owner, and needed action>

Next:
- <codename and outcome>

Supervisor action: <one action or None>
```

Keep it under 180 words.

## Final report

Use all nodes and sessions. Save `.onboarding/reports/final-YYYY-MM-DD.md`.

```markdown
# Onboarding result — YYYY-MM-DD

Role and target:
Ready for normal work:
- <area, target level, and evidence>

Needs supervision:
- <area and safe boundary>

Remaining blockers or gaps:
- <item and next action>

Suggested next work:
- <small real task or ownership area>

Onboarding process feedback:
- <missing access, document, command, or explanation>
```

Use `recognize`, `operate`, and `modify` targets as evidence levels. Keep it under 350 words.

Show the saved report to the learner. Do not send it or mark it approved.
