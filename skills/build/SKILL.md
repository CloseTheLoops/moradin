---
name: moradin-build
description: Stage 5 of the Forge — turn plan + decisions into a checklist of vertical slices, then build them one at a time: checkpoint, align, build, run the slice's executable check, tick. Dev data only. Scope creep goes to the backlog, never silently in.
---

# moradin:build

The building stage. Slices, not layers — one feature working end-to-end at a time, each proven by a check the agent can *run*, because agents demonstrably drop instructions they merely read.

## When invoked

`/moradin:build` — requires `.forge/plan.md` and `.forge/decisions.md`. **Start builds in a fresh session** (tell the operator literally: "type /clear, then /moradin:build") and re-read the `.forge/` files — never work from a summary of them.

## Step 1 — Generate the checklist (first run)

From plan + decisions, write `.forge/checklist.md` (template: `templates/forge/checklist.md`, cap 1 screen):

- **Vertical slices** — each one a runnable end-to-end piece ("hear the events", "the ping"), never all-database-then-all-frontend. 5–8 slices typical.
- Each slice cites its sources: `plan.md §sections · decisions #ids`. Generate slices by re-reading those sections, not from memory — summary chains lose most of a plan.
- Each slice defines its **check up front**: a command or concrete action plus what a good result looks like. If a check can't be stated, the slice is too vague — split it.
- **`[you]` tasks** — the human-only work (create accounts, paste API keys, set spend caps in dashboards, point DNS): written as plain-language walkthroughs, placed in the slice that needs them, and *verified by the agent* before the dependent step proceeds. Expect research to have over-specified some — kill any that pre-flight proves unnecessary.

## Step 2 — The slice loop

Per slice, in order:

1. **Checkpoint** — commit first ("saving a point we can rewind to").
2. **Align** — one short statement: what's about to be built and what's assumed. Wait for a nod (interactive); a standing "keep going" from the operator covers routine slices, but stop for anything surprising.
3. **Build** — against dev data only, never production; verify-after-write on anything destructive.
4. **Run the check** — live, now. A failed or *surprising* check is information: fix, or amend the plan's constants and note why in the checklist ([[verify_data_shape_not_just_existence]] — first contact with each external API is a data-shape pre-flight; expect it to correct a threshold).
5. **Tick + checkpoint** — update `checklist.md` with a one-line finding, commit, update `journal.md`.

## Hard rules

- **Scope creep → backlog.** Mid-slice ideas get an id and a one-line note in `backlog.md`, not silent inclusion. A changed *mind* is the dispatcher's amendment route, not a bigger slice.
- **API pre-flight** before building infrastructure around any external service: one real call, real payload, response recorded.
- **The first deploy slice wires the instruments:** error monitoring + uptime (per `memory/references/forge_tool_defaults.md`) and the Success Contract's named analytics events — verified with a deliberate test error, not assumed.
- **Secrets in `.env`** (gitignored) from the first key onward; where the tool supports hooks, install a pre-commit secrets scan now, not at close.
- **Windows/non-admin sessions:** background processes via `Start-Process` with `-u` + file redirect (jobs swallow buffered output); autostart via HKCU Run, not schtasks ([[windows_nonadmin_automation]]).

## Resuming

`checklist.md` + `journal.md` are the resume point. A returning session reads them, states where things stand in one sentence, and continues at the first unticked step — no re-explaining, no regenerating done work.
