---
name: moradin-retrospect
description: Review past sessions, identify recurring patterns, propose what to promote from lessons → patterns or principles.
---

# moradin:retrospect

Review past work across a time window. Identify what's worth promoting.

## When invoked

`/moradin:retrospect [<project>] [<window>]`

Examples:
- `/moradin:retrospect godtech 2w` — review GodTech sessions in last 2 weeks
- `/moradin:retrospect` — review all projects, all time

## What you do

1. **Gather session logs.** Read `projects/<project>/sessions/*.md` (or all projects). Filter by date if window specified.

2. **Read recent lessons** under `memory/lessons/`. Especially ones cited multiple times in sessions.

3. **Identify recurring patterns:**
   - Did the same lesson get applied 3+ times? → candidate for promotion to a pattern.
   - Did the same pattern get applied across multiple projects? → candidate for promotion to a universal principle.
   - Did the same kind of mistake keep happening? → candidate for a new principle.

4. **Propose promotions to operator:**
   - "Lesson `check_code_first.md` was cited in 4 sessions. Promote to principle?"
   - "Pattern `harness_contract.md` applied to GodTech 3x and proposed for trading. Already widely used — consider locking the spec."
   - "I notice you've hit the same Verifier-bypass issue 3 times. Make it a principle?"

5. **For each approved promotion:**
   - If lesson → pattern: copy to `memory/patterns/`, update frontmatter (type=pattern), keep original lesson file as reference
   - If pattern → principle: copy to `memory/principles/`, update frontmatter (type=principle), keep pattern

6. **Identify decay candidates:**
   - Patterns not referenced in any session for 90+ days
   - References whose source URL changed materially (run `scripts/audit_references.py`)

7. **Update indexes** and produce a retrospective summary.

## Don't

- Don't auto-promote without operator approval.
- Don't delete files during retrospective. Mark with `superseded_by:` if a newer version exists.
- Don't propose promotion based on a single occurrence. Wait for the 3rd.

## Output

- Retrospective summary (counts, recurring themes, promotion candidates)
- 0-N new files in `memory/patterns/` or `memory/principles/` (after operator approval)
- 0-N files marked `superseded_by:` in their frontmatter
