# Success Contract — <product>
<!-- Cap: 1 page. Written BEFORE tool research or code. The Review stage reads this and acts on it. -->
Stage: <validation | launch | growth> · Written: <YYYY-MM-DD> · Review due: <date +30d>

## The one metric that matters
Metric: <e.g. "% of signups who do their first X within 7 days" — never a cumulative "total X">
Target: <number> · Kill/pivot threshold: <number + sample size, e.g. "<10% after 100 signups">
Measured by: <named event/tool, e.g. PostHog event `first_x_created` ÷ signups>

## Where do the first 20 users come from — concretely?
<real channel(s). "Nowhere yet" is a valid answer — it makes milestone 0 a validation test.>

## Supporting signals (max 3)
1. <signal> — target <n> — measured by <...>
2. <signal> — target <n> — measured by <...>

## What we will NOT count as success
Total signups · page views · followers · stars · <anything cumulative>

## Two horizons
Launch week: <activation-type check, e.g. "≥20% of signups reach the aha action">
Month 3: <retention/revenue-type check>

## Instrumentation checklist
[ ] analytics snippet installed (see memory/references/forge_tool_defaults.md)
[ ] 1–3 custom events named above actually fire
[ ] weekly 10-minute review scheduled
<!-- Zero-instrumentation fallback: at week 4 ask 10 users "how would you feel if you could no
     longer use this?" — ≥40% "very disappointed" is the strongest signal there is. -->
