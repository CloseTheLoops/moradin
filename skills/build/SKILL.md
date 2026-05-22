---
name: moradin-build
description: Structured build session against a target project. Apply Moradin's principles + patterns to a real task.
---

# moradin:build

Run a structured build session. The workshop's core verb.

## When invoked

`/moradin:build <project> <task>`

Example: `/moradin:build godtech "add a worker harness to Life Agent"`

## What you do

1. **Load context from Moradin:**
   - Read `memory/_INDEX.md` to see what's available
   - Read `memory/principles/` (the universal rules)
   - Read relevant `memory/patterns/` (by topic — for harness task, load patterns tagged `harness`)
   - Read `memory/references/` if external knowledge is relevant

2. **Load context from target project:**
   - Read `projects/<project>/state.md` — current architecture summary
   - Read `<target-project-path>/CLAUDE.md` or `AGENTS.md` — the project's own context
   - Read the specific files relevant to the task

3. **Propose a plan.** Reference the patterns + principles you'll apply by file path. Don't just say "I'll add a harness" — say "I'll apply `memory/patterns/harness_contract.md` to add a worker harness following the 5-step closed loop."

4. **Wait for operator approval** before executing. Show the plan, ask for go/edit.

5. **Execute** — edit the target project's files (NOT Moradin's files, unless explicitly capturing a new pattern that emerged).

6. **Write a session log** at `projects/<project>/sessions/<YYYY-MM-DD>_<topic>.md`:
   - What was the task
   - What patterns/principles were applied
   - What files changed
   - What worked, what was tricky

## Don't

- Don't edit Moradin's `memory/` during a build session (unless capturing a new lesson via `/moradin:ship`).
- Don't skip reading the target project's CLAUDE.md — that's the runtime truth.
- Don't apply patterns blindly. Verify each pattern actually fits the specific task.
- Don't execute without operator approval of the plan.

## Output

- Files changed in the target project
- New session log at `projects/<project>/sessions/`
- Optionally: updated project `state.md` if architectural state changed
