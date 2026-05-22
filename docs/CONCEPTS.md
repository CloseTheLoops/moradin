# Concepts

Moradin's design in 5 layers.

## Layer 1 — The workshop (this directory)

Moradin is a folder, not a service. It has no port, no daemon, no scheduler. Just files. When an agent opens it, the agent's session inherits the workshop. When the agent closes, Moradin is inert again.

## Layer 2 — Memory (4 content types)

The `memory/` directory holds 4 kinds of knowledge:

| Type | Lives in | Purpose | Examples |
|---|---|---|---|
| **Principles** | `memory/principles/` | Universal rules — apply to ANY project | "close every loop" · "truth over validation" |
| **Patterns** | `memory/patterns/` | Reusable designs, tagged by which projects use them | "harness contract" · "ralph wiggum loop" · "closed loop eval" |
| **References** | `memory/references/` | Captured external sources, full unfiltered concept inventory | A GitHub repo · a paper · a docs page |
| **Lessons** | `memory/lessons/` | Incident-derived rules with Why + How-to-apply | "check our code first" · "dedup at storage layer" |

The promotion path:
- Lesson → Pattern when applied 3+ times
- Pattern → Principle when generalizes beyond one project

Promotions happen via `/moradin:retrospect`.

## Layer 3 — Skills (8 verbs)

Skills are SKILL.md-compliant files in `skills/<verb>/SKILL.md`. The operator invokes via `/moradin:<verb>`:

| Verb | What |
|---|---|
| init | Set up a fresh workshop |
| capture | Capture an external source as a reference |
| recall | Search memory + synthesize with citations |
| audit | Lint memory: stale, missing fields, bad tags, orphans |
| stats | Counts + coverage report |
| build | Structured build session against a target project |
| ship | End-of-session: save lessons, update state |
| retrospect | Review past sessions, propose promotions |

## Layer 4 — Projects (per-project state)

Each project Moradin helps build gets a slot under `projects/<name>/`:

```
projects/<name>/
  state.md         ← current architecture, active sprint
  plans/           ← active + archived plans
  sessions/        ← dated session logs from build work
  design_docs/     ← HTML mockups, architecture maps
  changelog/       ← project history
```

Projects are entirely the operator's content — gitignored from the framework remote. Lives only in the operator's private instance.

## Layer 5 — Scripts (stdlib utilities)

`scripts/` holds stdlib-only Python utilities Moradin's skills call:

| Script | Job |
|---|---|
| `search.py` | BM25 over memory with frontmatter filter |
| `audit.py` | Lint memory: 4 checks |
| `stats.py` | Counts + coverage report |
| `refresh_indexes.py` | Rebuild `_INDEX.md` files from frontmatter |
| `audit_references.py` | Monthly: re-fetch refs, flag staleness |
| `update.sh` | Pull framework updates from upstream |

No external dependencies — all stdlib. Easy to fork, easy to vendor elsewhere.

## Operator review surfaces are HTML

When a script outputs something the operator has to SCAN, REVIEW, or DECIDE ON, render it as HTML — not markdown. Markdown is for storage, git diffs, grep, and LLM-readable content. HTML is for actually reading + acting.

Why: a 1500-line markdown file with 100 review candidates is friction the operator won't fight through. The same content as HTML (cards + filter search + checkboxes + export-decisions button) is reviewable in 5-10 minutes.

Pattern: review-emitting scripts write BOTH formats in the same function.

| Output type | Format |
|---|---|
| Memory files (principles, patterns, references, lessons, preferences) | markdown |
| Schema files, templates | markdown |
| Session logs | markdown |
| **Review queues** (proposed preferences, audit reports, retrospect output) | **HTML** (+ markdown alongside) |
| **Stats dashboards** | **HTML** (+ JSON alongside) |
| Design docs / explainers | HTML |

Reference implementation: `scripts/extract_preferences.py` writes both `proposed_<date>.md` and `proposed_<date>.html`. The HTML has dark theme, sticky toolbar, per-card radio buttons for ACCEPT/EDIT/REJECT, and an export-to-JSON button.

## The framework vs content split

This is the most important design choice. The Moradin GitHub repository ships an **empty shell**:
- All directories
- All scripts
- All SKILL.md files
- All templates and schemas
- Example content (committed, prefixed `EXAMPLE_`)

But NOT:
- Your actual principles, patterns, references, lessons (gitignored)
- Your project content (gitignored)
- Your memory files (live in your private fork or untracked)

This means:
- The framework can be open-source even if your content is private.
- You can update the framework (`./scripts/update.sh`) without affecting your content.
- Sharing patterns publicly is opt-in: PR a sanitized pattern back upstream.
