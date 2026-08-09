---
name: moradin-measure
description: Stage 2 of the Forge — write the Success Contract before any tool research or code. One metric that matters with a kill threshold, max 3 supporting signals, an anti-vanity list, the traffic question, and instrumentation named up front. Writes .forge/measure.md.
---

# moradin:measure

Before researching tools or writing code: what does *working* look like, in numbers? Without this, you ship blind and every metric you pick later will be one that flatters you. Takes ~10 minutes.

## When invoked

`/moradin:measure` — requires `.forge/plan.md` (run `/moradin:define` first if missing). Read `plan.md` and `profile.md`. Draft everything from the plan; the operator corrects. Same rule as define: never a blank page.

## Build the Success Contract

Work through in order, one at a time:

1. **Stage label.** From the plan's evidence answer: no evidence the problem exists → stage is **validation**. Evidence but not shipped → **launch**. Already has users → **growth**. Say which and why in one sentence.

2. **The one metric that matters.** Draft it from the riskiest assumption — the metric should measure *exactly the thing v1 must prove*. Rules:
   - A **rate or ratio**, never a cumulative total ("% of signups who do X within 7 days", not "total signups"). Totals only go up; they flatter and inform nothing.
   - A **target** ("30%") *and* a **kill/pivot threshold with a sample size** ("under 10% after 100 signups"). The threshold is what turns the number into a decision instead of a decoration. Say plainly: "if we hit this line, we change course — agreeing on that now is the whole point."

3. **The traffic question.** "Where do the first 20 users come from — concretely?" A subreddit they post in, a community they're in, friends in the target group, an audience they have. **"Nowhere yet" is a legitimate answer** — it means milestone 0 is a validation test (landing page + the concrete channel hunt), because a metric with no visitors is theater.

4. **Supporting signals — max 3.** Each with a target and a "measured by." Good candidates: a return-rate (do people come back within a week?), the funnel step before the main metric, and the zero-instrumentation fallback below. Refuse a fourth; tracking everything is how measurement gets abandoned.

5. **The anti-vanity list.** Write down what will NOT count as success: total signups, page views, followers, stars. This list is what the operator re-reads on a bad week.

6. **Two horizons.** Launch week = an activation check (did people who arrived do the core thing? Under ~20% usually means broken onboarding, not a bad idea). Month 3 = retention or revenue. Different questions at different times — one static dashboard is the wrong shape.

7. **Instrumentation, named now.** Pick the tool from `memory/references/forge_tool_defaults.md` (don't hardcode from memory — that file is dated and re-verified). Name the 1–3 custom events. They get built during the build stage, not bolted on after. The zero-setup fallback that always works: at week 4, ask 10 users "how would you feel if you could no longer use this?" — 40%+ saying "very disappointed" is the strongest product signal there is.

8. **Review date: +30 days.** The dispatcher watches it. Metrics expire — a pre-launch waitlist number becomes a vanity number the day you launch.

## Validation gate

If stage = validation (no evidence, or no traffic answer): the contract's first metric is **pre-build** — e.g. "≥5% of visitors from [the named channel] join the waitlist AND ≥5 people say they'd pay." Milestone 0 in the plan becomes that test. Route outcomes explicitly, now, in writing:
- **Pass** → proceed to research/build with the assumption validated.
- **Fail** → back to define to pivot the idea (amendment), or stop cleanly. Both are wins over building the wrong thing for two months. Write which threshold triggers which.

## Confirm via the review page — never a chat wall

Numbers the operator must decide on get a **clickable page, not prose** (`operator_review_as_html`). Generate `.forge/measure_review.html`: a single-file, dark, interactive page that explains each number in plain language ("out of every 10 alerts, how many should be real?"), offers each as 2–3 clickable options with the draft marked, states the stop line's meaning honestly, and has an **Export my choices** button producing a small JSON blob. The operator clicks, exports, pastes it back. Chat is for the conversation; the page is for the decision.

## Write the outputs (after the export comes back)

1. `.forge/measure.md` from `templates/forge/measure.md`, using the exported numbers — **hard cap: 1 page.**
2. If milestone 0 changed, update `plan.md`'s milestones (supersede, don't silently edit).
3. Update `.forge/journal.md` — next action: "Run `/moradin:research` to pick the tools" (or, until that skill ships: "research stage arrives in Phase 2 — ask for a manual research pass").

Close with the two honesty questions, plainly: "If these numbers came true, would you call it working? If they came in under the stop line, would you actually stop?"
