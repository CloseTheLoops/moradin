# Memory frontmatter schema

Every file under `memory/{principles,patterns,references,lessons}/` MUST have YAML frontmatter at the top.

## Required fields (all memory types)

```yaml
---
name: short_kebab_case_name
description: One sentence — what this file is. Shown in _INDEX.md listings.
topics: [tag1, tag2]
applies_to: [universal]
type: principle | pattern | reference | lesson
---
```

| Field | Type | Notes |
|---|---|---|
| `name` | string (kebab-case) | Matches filename (without .md). Lowercase + underscores. |
| `description` | string | One sentence. Surfaced in catalog views. |
| `topics` | list | From the 8-tag taxonomy. See below. |
| `applies_to` | list | Which projects this matters to. `universal` for cross-project. |
| `type` | string | One of: principle, pattern, reference, lesson |

## Topic taxonomy (8 fixed tags)

| Tag | Covers |
|---|---|
| `harness` | Test runners, harness shape, verification scaffolding |
| `memory` | Memory layers, KGs, recall, persistence, knowledge structure |
| `eval` | Evaluation, gold sets, judges, scoring, metrics |
| `llm` | LLM-specific patterns, prompts, model choice, JSON mode |
| `agent` | Agent architecture, multi-agent, sub-agents, MCP |
| `arch` | System architecture, layering, substrates, structure |
| `workflow` | How-to-work patterns, env-var flags, rollback, dependency-thinking |
| `tooling` | Dev tooling: auditing, linting, scaffolding, distribution |

## Applicability tags

| Tag | Meaning |
|---|---|
| `universal` | Applies to any project. Default for principles. |
| `<project-name>` | Specific to one project (e.g. `godtech`, `trading`) |

## Optional fields (per-type)

### references/

```yaml
url: https://github.com/.../...     # source URL (required for references)
captured: 2026-01-15                # date first captured
last_verified: 2026-01-15           # date last re-checked
```

### patterns/ and lessons/

```yaml
version: 1                          # increment if substantively revised
superseded_by: newer_pattern_name   # if this is retired in favor of newer
```

## Body structure

After frontmatter, write markdown body. Conventions per type:

| Type | Body should include |
|---|---|
| `principle` | The rule + brief rationale |
| `pattern` | The design + when to use + when NOT to use |
| `reference` | "What it is" + "Notable concepts" (full inventory) + "What I deliberately skipped" |
| `lesson` | The rule + **Why:** (incident) + **How to apply:** (when this fires) |

## File naming

- Lowercase + underscores: `close_every_loop.md`, NOT `CloseEveryLoop.md`
- Descriptive, not citation-style: `autonomous_iteration.md` OR `ralph_wiggum_loop.md` (industry-standard names OK), NOT `karpathy_method.md`
- No prefixes like `feedback_` or `principle_` — the directory tells you the type
