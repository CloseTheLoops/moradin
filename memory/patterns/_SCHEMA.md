# Patterns schema

Patterns are **reusable designs** — concrete approaches that apply across multiple uses. Tagged by topic and which projects use them.

## Required frontmatter

```yaml
---
name: short_kebab_name
description: One-line statement of the pattern
topics: [tag1, tag2]
applies_to: [universal, godtech]     # patterns can be universal OR project-specific
type: pattern
---
```

## Optional frontmatter

```yaml
version: 1                           # increment if substantively revised
superseded_by: newer_pattern_name    # if retired
```

## Body structure

```markdown
# <Pattern name>

<1-2 sentence summary of what the pattern is.>

## Shape

<The actual design — code structure, file layout, contract, whatever defines the pattern.>

## When to use

<Criteria — what makes this pattern apply.>

## When NOT to use

<Anti-criteria — when this pattern is wrong.>

## Example

<A concrete instance, or pointer to one in `projects/<name>/`.>
```

## What goes here vs. elsewhere

| Goes here | Goes elsewhere |
|---|---|
| "The 5-step closed-loop eval contract" | Universal rule "close every loop" → `principles/` |
| "Per-tenant layered structure (Ingest → Brain → Agent → Substrate)" | Specific GodTech layout → `projects/godtech/state.md` |
| "Ralph Wiggum loop — autonomous iteration via stop hook" | "Used Ralph for re-extraction" → `lessons/` |

## File naming

Lowercase + underscores. Industry-standard names are fine.

- ✓ `harness_contract.md`
- ✓ `closed_loop_eval.md`
- ✓ `ralph_wiggum_loop.md` (industry-standard name)
- ✓ `per_tenant_layered.md`
- ✗ `karpathy_wiki.md` (don't attribute)
