---
name: moradin-research
description: Stage 3 of the Forge — verified deep research on the project's open technology decisions. Generates its own questions from the plan, fans out verification agents with the expert method encoded, and delivers a clickable options report. Every claim checked against a live source today.
---

# moradin:research

Replace "just search and hope" with directed, verified research. The operator doesn't supply the expert prompting — it lives here. Takes minutes for cheap decisions, longer only where being wrong is expensive.

## When invoked

`/moradin:research` — requires `.forge/plan.md` and `.forge/measure.md` (run define/measure first). Read both, plus `profile.md` and `memory/references/forge_tool_defaults.md` (if that file is >60 days old, re-verify anything you use from it).

## Step 1 — Generate the questions, confirm the list

Derive the open decisions from the plan yourself (stack, hosting, data sources, auth/payments/AI services, anything the skeleton needs that doesn't exist yet). Present the list in one short message — "here's what I think needs researching, anything to add or cut?" — and wait for the nod. Don't research questions nobody asked.

## Step 2 — Classify each decision by door type

- **Expensive door** (data model, payment provider, auth, core data dependency — costly to exit): full verification, a background agent per decision.
- **Cheap door** (UI library, log storage, host for a $0 experiment — an afternoon to reverse): minutes of checking, 2 options, no agent fan-out needed.

Timebox accordingly and say which is which. More research on a cheap door is procrastination.

## Step 3 — Verify (the checklist every option must pass)

No claim from memory — every fact fetched today, with URL + date recorded:

1. **Existence:** official registry/docs page fetched for every package, API, endpoint, and model ID named. (LLMs hallucinate packages; slopsquatting is a real attack.)
2. **Data shape:** for any API whose *fields* will drive a threshold or decision, make one real call with a real payload and record a sample response. Existence + price ≠ semantics — this is the check that catches "$0 means pre-migration" surprises. ([[verify_data_shape_not_just_existence]])
3. **Pricing:** vendor's live pricing page — free-tier limits, card required?, **hard spend cap available?**, overage behavior (throttle vs bill).
4. **Pricing history:** repricings/tier removals/acquisitions in the last 24 months → risk line. Flag the named risk category wherever found: *free tier + usage billing + no hard cap*.
5. **Maintenance:** last human commit ≤90 days, a release in 12 months, contributor concentration over the last 12 months (never lifetime, never stars).
6. **Adoption trend + responsiveness:** download-trend direction over 12 months; median time-to-first-response on recent issues.
7. **Lock-in:** the concrete exit path (export format, protocol, substitute) and migration effort in days — this sets the door type honestly.
8. **UNVERIFIED labeling:** anything that resisted verification is included with the flag, never silently.

Bias: **boring by default** — mainstream stacks are also what AI agents build most reliably on. Track innovation tokens: each unproven-tech pick spends one; flag the second.

## Step 4 — Write the outputs

1. `.forge/research/<topic>.md` per decision — **cap: 1 screen each.** What was recommended, the 2–3 options with verified facts, what was ruled out in one line each, sources with dates.
2. **The options report page** — a single-file interactive HTML (this is the decide stage's input; see that skill for the card format). One card per decision: 2–3 options, recommended one pre-selected, per-option fact rows (cost now and at 10×, spend-cap status, exit cost, "pick this if…"), risk lines in warning color, one export button for all decisions at once.
3. Update `.forge/journal.md` — next: "/moradin:decide — open the options page, click, export."

Never: more than 3 options per decision (choice overload is real for non-experts) · a recommendation whose critical claim wasn't verified today · burying a risk in prose instead of a labeled risk line.
