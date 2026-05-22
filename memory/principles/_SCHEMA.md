# Principles schema

Principles are **universal rules** that apply to ANY project. Stable; rarely change.

## Required frontmatter

```yaml
---
name: short_kebab_name
description: One-line statement of the rule
topics: [tag1, tag2]
applies_to: [universal]              # principles are usually universal
type: principle
---
```

## Body structure

```markdown
# <Rule stated clearly>

<1-2 sentence elaboration of the rule.>

## Rationale

<Why this rule exists. What goes wrong without it.>

## How to apply

<When this rule fires. Example situations.>
```

## What goes here vs. elsewhere

| Goes here | Goes elsewhere |
|---|---|
| "Close every loop — every feature needs consumer + exit query" | Specific harness design → `patterns/` |
| "Truth over validation" | "Daniel is a contact not a peptide" → not memory at all |
| "Never delete, always supersede" | "Mem0 uses supersession" → `references/mem0.md` |
| "Plan before code for non-trivial work" | "Used Ralph loop for the CURSED compiler" → `lessons/` |

## File naming

Lowercase + underscores. Stated as the RULE, not the source.

- ✓ `close_every_loop.md`
- ✓ `truth_over_validation.md`
- ✓ `never_delete_supersede.md`
- ✗ `feedback_close_every_loop.md` (don't prefix)
- ✗ `karpathy_principles.md` (don't attribute)
