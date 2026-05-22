---
name: moradin-ship
description: End-of-session capture. Review work, extract lessons, update project state.
---

# moradin:ship

Wrap up a build session. The "save what we learned" verb.

## When invoked

`/moradin:ship`

At the end of a build session, before closing Claude Code.

## What you do

1. **Review the session.** What was the task? What changed? Look at the session log.

2. **Ask the operator:**
   - "Any lessons learned worth saving? (something that worked or failed that you'd apply next time)"
   - "Any new pattern emerged that wasn't in `memory/patterns/`?"
   - "Should we update the project's `state.md`?"

3. **For each lesson the operator describes:**
   - Write to `memory/lessons/<name>.md` using `templates/lesson.template.md`
   - Frontmatter: name, description, topics, applies_to, type=lesson
   - Body: the rule + **Why:** (the incident or success) + **How to apply:** (when this fires)

4. **For each new pattern:**
   - Write to `memory/patterns/<name>.md` using `templates/pattern.template.md`
   - Confirm with operator before writing

5. **Update project state if needed:**
   - `projects/<project>/state.md` reflects current architecture
   - If state changed (e.g. new module, removed component), update it

6. **Update indexes:** Run `python scripts/refresh_indexes.py`.

7. **Summary:**
   - Lessons saved: X
   - Patterns saved: X
   - State updated: yes/no
   - Session log: `projects/<project>/sessions/<date>.md`

## Don't

- Don't save lessons the operator didn't explicitly identify. Ask, don't auto-extract.
- Don't update `state.md` unless architecture actually changed.
- Don't promote a one-time observation to a principle. Lessons → patterns happens via `/moradin:retrospect` after multiple occurrences.

## Output

- 0-N new `memory/lessons/*.md` files
- 0-N new `memory/patterns/*.md` files (if patterns emerged)
- Optionally: updated `projects/<project>/state.md`
- Updated indexes
