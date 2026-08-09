---
name: moradin-review
description: Stage 7 of the Forge — the loop-closer that consumes the Success Contract. Pulls actual numbers, compares them to the targets and the kill line, and routes explicitly: continue, pivot, or stop cleanly. Also the v1→v2 re-entry point.
---

# moradin:review

The stage that makes the Success Contract mean something. A kill line nobody reads is decoration; this stage reads it.

## When invoked

`/moradin:review` — the dispatcher offers it when `.forge/measure.md`'s review date has passed, when the contract's sample size is reached, or whenever the operator returns asking "how's it going?" Reads `measure.md`, `backlog.md`, `journal.md`.

## Step 1 — Pull the actuals

From the instrumentation the build wired (the analytics events, the outcome log, the stats query — whatever the contract's "measured by" column names). Present them **against the contract, side by side**, in plain language: metric, target, actual, kill line, sample size so far. If the sample is still too small for the kill line, say so and schedule the next look — don't judge early.

## Step 2 — Route, explicitly

- **Continue** — at or trending toward target: pick the next milestone from the backlog (statuses `idea`/`deferred` are the menu), re-enter the pipeline at build (or research, if the milestone needs new decisions).
- **Pivot** — kill line hit but the *problem* still looks real: the idea changes, not just the code. Route through the dispatcher's amendment into define; supersede the affected plan sections and decisions; write a lesson about what the numbers taught.
- **Stop** — kill line hit and the thesis is dead: close the project cleanly (run `/moradin:close` Core), capture the lesson, mark the journal `stopped: <why>`. Say it straight: **a clean kill is the process succeeding** — two months not spent building the wrong thing is the win the contract bought.

The routing is the operator's call — present the numbers and a recommendation, then wait. Never soften a kill-line breach into "let's keep tweaking"; that's the failure mode the contract exists to prevent.

## Step 3 — Refresh the contract

Whatever the route, the contract updates: new stage label if the product graduated (validation → launch → growth), metrics re-drawn for the new stage (yesterday's north star is tomorrow's vanity metric), fresh targets, fresh review date (+30d), and the anti-vanity list re-checked. Supersede sections, don't silently edit — the old contract is the record of what we believed.

## Step 4 — Journal

`journal.md` gets the verdict in one line ("reviewed 2026-09-08: precision 24% vs 20% target → continue, milestone 2") and the next action with its command. This is also the v1→v2 re-entry point: a shipped project comes back through here, never by starting a new plan from scratch.
