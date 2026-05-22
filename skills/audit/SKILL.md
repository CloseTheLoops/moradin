---
name: moradin-audit
description: Lint memory — find stale files, missing frontmatter, bad topic tags, orphans. Propose fixes.
---

# moradin:audit

Run a health check on Moradin's memory and report issues.

## When invoked

`/moradin:audit`

Typically run weekly, or before a publish, or when something feels off.

## What you do

1. **Run the audit script:**
   ```
   python scripts/audit.py --format json
   ```

2. **Categorize issues** by severity (error/warn/info):
   - ERROR: missing required frontmatter fields
   - WARN: unknown topic tags, orphan files (not in _INDEX)
   - INFO: stale files (unchanged > 180 days)

3. **Group issues** by file and by type.

4. **For each issue, propose a concrete fix.** Don't just report — recommend action:
   - Missing `applies_to` field → "Add `applies_to: [universal]` to frontmatter"
   - Unknown topic `cargo` → "Either rename to one of [harness, memory, ...] or justify adding cargo to taxonomy"
   - Orphan file → "Run `python scripts/refresh_indexes.py` to relink"
   - Stale file → "Decide: still applies? Add `last_verified: <today>` to keep, or mark `superseded_by: <new>` to retire"

5. **Don't auto-fix.** Audit reports + proposes. Operator approves each fix.

6. **Summary report:** count by severity, top 3 files needing attention.

## Output

- A human-readable report with concrete fix proposals
- Operator-approved fixes get applied one by one (Edit, refresh_indexes.py)

## Don't

- Don't auto-delete stale files. Stale ≠ wrong — operator decides.
- Don't add `superseded_by` markers without operator approval.
- Don't reformat all frontmatter at once — touch only files with reported issues.
