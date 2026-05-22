# Lessons schema

Lessons are **incident-derived rules** — what we learned from getting something right or wrong. Append-only; never delete, only supersede.

## Required frontmatter

```yaml
---
name: short_kebab_name
description: One-line statement of the rule
topics: [tag1, tag2]
applies_to: [universal, godtech]
type: lesson
---
```

## Optional frontmatter

```yaml
date: 2026-01-15                     # when the incident happened
superseded_by: newer_lesson_name     # if retired
```

## Body structure

```markdown
# <Rule stated as a clear directive>

## Why

<The incident or success that taught this. Be specific. "When we tried X, Y happened, because Z." Don't summarize too much — the story is the load-bearing part.>

## How to apply

<When this rule fires. What to check. What to avoid.>
```

## What goes here vs. elsewhere

| Goes here | Goes elsewhere |
|---|---|
| "Mock the DB → mock and prod diverged → broken migration" | Universal rule "test against real DB" → `principles/` once it generalizes |
| "AFC default-enabled → 10x HTTP amplification" | "Use stdlib-only JSON mode" → `patterns/` after we standardize |
| "Trying to refactor mid-flight made the merge worse" | "Plan before code" → `principles/` |

## File naming

Lowercase + underscores. State as the RULE, not the incident.

- ✓ `check_code_first.md` (not `incident_blamed_google_was_us.md`)
- ✓ `dedup_at_storage_layer.md`
- ✓ `verify_audit_agents.md`
- ✗ `lesson_from_2026_03_15.md` (date doesn't belong in name)
- ✗ `feedback_check_code_first.md` (no `feedback_` prefix)

## Promotion path

Lesson → Pattern: when the same lesson gets applied 3+ times, consider promoting to a pattern (copy to `memory/patterns/`, keep lesson file).

Lesson → Principle: when a lesson generalizes beyond one project, consider promoting to `memory/principles/`.

Promotion happens via `/moradin:retrospect`.
