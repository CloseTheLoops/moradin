---
name: moradin-decide
description: Stage 4 of the Forge — turn the research options into locked decisions. Constraints elicited before options shown, choices made by clicking the options page, every choice recorded as a compact decision record with why-nots and event-based revisit triggers. Accepted decisions are never relitigated, only superseded.
---

# moradin:decide

Choices get made once, with reasons, and stay made — so the build never re-argues the database at midnight. The operator clicks; the records write themselves.

## When invoked

`/moradin:decide` — requires `.forge/research/` output. If the research stage didn't already produce the options page, build it now from the research files.

## Step 1 — Constraints before options

Before showing anything, confirm the operator's constraints in one short exchange: monthly budget ceiling, expected scale ("just me" is a fine answer), and what they already know how to use. Criteria stated *after* seeing options get bent to justify a favorite — locking them first is the whole discipline.

## Step 2 — The options page

Generate (or reuse) the single-file interactive HTML report and publish it for the operator:

- **One card per decision.** 2–3 options; the recommended one pre-selected and tagged. Never more — choice overload hits non-experts under exactly these conditions.
- **Per option:** one-line what-it-is · cost now and at 10× scale · spend cap yes/no · exit cost in days · a "pick this if…" sentence · risk lines (repricing history, single-maintainer, UNVERIFIED flags) in a warning treatment.
- **Non-dev triage on every card:** accepting the default is always a first-class choice; "explain this in plain language" is a legitimate export value that routes back to a conversation, not a failure.
- **One export button** for the whole page → JSON blob pasted back into chat.

Style/mechanics follow the project's existing review pages (dark, single file, no external requests, clipboard export with textarea fallback).

## Step 3 — Lock the records

For each exported choice, append a record to `.forge/decisions.md` (~15 lines, from `templates/forge/decisions.md`):

- Numbered title · date · `Status: accepted` · door type with concrete exit ("two-way, exit ≈ 1 day: pg_dump → any host") · innovation token yes/no
- **Context** (2–3 sentences: what forced this, the operator's stated constraints)
- **Decision** (one sentence, active voice) · **Why** (2–3 bullets tied to those constraints)
- **Rejected** — every option not chosen, one line each on why not. The why-nots are what prevent relitigating.
- **Verified** — source URL + fetch date, spend-cap status
- **Revisit when** — event triggers only ("pricing changes", ">10k users", "PumpPortal goes down"). Never calendar dates; stale decision logs die of scheduled reviews nobody does.

## Step 4 — Binding, and the one way out

An `accepted` record is never edited and never re-argued. Changing course = a **new record** with `supersedes: NNN` (the old one gets `superseded-by: NNN`) — normally via the dispatcher's amendment route when the operator's mind changes mid-build. If the operator asks to revisit a decision casually, point at the record's why-nots first; if they still want the change, supersede cleanly.

## Step 5 — Hand off

Update `.forge/journal.md` — next: "/moradin:build — the checklist gets generated from plan + these decisions" (until that skill ships: "build stage arrives in Phase 3 — ask for a manual build pass"). If any export came back "defer," it goes to the backlog with a reason, and the build must not depend on it.
