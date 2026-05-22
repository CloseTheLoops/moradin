# Preferences schema

Preferences are **personal taste** — rules about how YOU like to work that others might disagree with. Distinct from principles (universal rules worth defending) and lessons (incident-derived).

## When to use this type vs others

| Type | Use when |
|---|---|
| `principle` | A rule you'd advocate for to any builder. Universal. ("Close every loop") |
| **`preference`** | **A rule about YOU specifically. Others may rightfully disagree. ("Prefer terse responses over verbose explanations")** |
| `pattern` | A reusable design. Project-agnostic or project-specific. ("Harness contract") |
| `lesson` | Derived from a specific incident. Has Why + How-to-apply. ("AFC amplification incident") |
| `reference` | Captured external source. ("Mem0 architecture") |

If unsure: lean preference for "how I like to work," principle for "how things should be."

## Required frontmatter

```yaml
---
name: short_kebab_name
description: One-line statement of the preference
topics: [tag1, tag2]
applies_to: [operator-self]            # preferences default to self-applicable
type: preference
---
```

## Optional frontmatter

```yaml
source: derived-from-sessions          # if extracted by learn-from-sessions
source_count: 12                       # how many session occurrences supported this
source_confidence: 0.85                # extraction confidence at proposal time
date_added: 2026-05-22
superseded_by: newer_preference_name   # if retired
```

## Body structure

```markdown
# <Preference stated clearly, as a directive>

<1-2 sentence elaboration.>

## Why

<Your personal reason for this preference. Be honest — taste doesn't need universal justification.>

## How to apply

<When this fires. Example situations.>

## Counter-cases

<When this preference DOESN'T apply. Edge cases where you'd override.>
```

## Examples (illustrative)

| Preference name | Statement |
|---|---|
| `terse_responses` | Prefer terse, dense responses over verbose explanations |
| `no_emoji_in_code` | No emojis in code comments unless explicitly asked |
| `confirm_before_destructive` | Ask before destructive actions (delete, drop, force-push) |
| `surgical_edits_only` | Edit only what's requested; don't refactor unrelated code |
| `markdown_tables_over_lists` | Prefer markdown tables when content has 2+ dimensions |

## File naming

Lowercase + underscores. State as the PREFERENCE, not the source.

- ✓ `terse_responses.md`
- ✓ `no_mock_databases.md`
- ✗ `feedback_terse.md` (no `feedback_` prefix)
- ✗ `claude_should_be_terse.md` (too specific to one tool)
