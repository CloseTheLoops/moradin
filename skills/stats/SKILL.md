---
name: moradin-stats
description: Report counts, coverage, and age distribution of memory.
---

# moradin:stats

Show a stats report on Moradin's memory.

## When invoked

`/moradin:stats`

Quick health snapshot. Useful for retrospectives or just curiosity.

## What you do

1. **Run the stats script:**
   ```
   python scripts/stats.py --format json
   ```

2. **Present the report:**
   - Total files
   - By type (principles, patterns, references, lessons)
   - By topic (harness, memory, eval, llm, agent, arch, workflow, tooling)
   - By applies_to (universal, godtech, trading, ...)
   - Age distribution (fresh ≤7d, recent ≤30d, aging ≤90d, old ≤180d, stale >180d)

3. **Highlight observations.** Examples:
   - "You have 12 patterns tagged `eval` but only 2 references — capture more eval sources?"
   - "8 files are stale (>180d). Worth running `/moradin:audit` to review."
   - "No memory tagged `trading` yet — you haven't started that project's slot."

4. **Don't propose changes.** Stats is read-only.

## Output

A clean text report with counts + observations.
