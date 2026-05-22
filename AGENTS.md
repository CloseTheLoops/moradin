# Moradin — Dev Workshop

I am Moradin. I am your dev brain. I do not run. I am opened.

## What I am

A directory of principles, patterns, references, lessons, and per-project state.
When you open Claude Code (or Cursor, Codex, Gemini) in my directory, that session
inherits my contents. You use that session to **build OTHER projects**. Edits go
to those target projects. I myself just accumulate knowledge over time.

I am NOT a running agent. I have no port, no scheduler, no daemon. I am inert
files on disk. I come alive only when an agent opens me.

## When you open me — what to do

1. Read this file (AGENTS.md) fully.
2. Read `memory/_INDEX.md` for the catalog of principles, patterns, references, lessons.
3. Read the per-content `_INDEX.md` files inside `memory/principles/`, `memory/patterns/`, `memory/references/`, `memory/lessons/`.
4. If the operator mentions a specific project (e.g. "GodTech", "trading"), read `projects/<name>/state.md` to know its current shape. THEN read that project's own CLAUDE.md or AGENTS.md if it has one.
5. Apply relevant principles. Reference relevant patterns. Use scripts in `scripts/` when appropriate.

## The 8 skills

Each is a SKILL.md-compliant skill in `skills/<verb>/SKILL.md`. The operator invokes via `/moradin:<verb>`.

| Verb | What it does |
|---|---|
| `init` | Initialize a Moradin workshop in current directory (for new users) |
| `capture` | Capture an external source as a reference. WebFetch URL → list ALL notable concepts unfiltered → write to `memory/references/<name>.md` |
| `recall` | Search memory and synthesize an answer with citations to source files |
| `audit` | Lint memory: contradictions, stale dates, orphan files. Propose fixes. |
| `stats` | Report counts: files per topic, per applies_to, average age, dead/active ratio |
| `build` | Structured build session against a target project. Read project state → apply principles + patterns → propose plan → execute → write session log |
| `ship` | End-of-session capture. Review work. Ask for lessons learned. Save them. Update session log + project state.md |
| `retrospect` | Review past sessions over a window. Identify recurring patterns. Propose what to promote from lessons → patterns or principles |

## Memory system

My memory has 4 content types. Each lives in its own subdirectory under `memory/`:

| Type | Lives in | Purpose | Lifecycle |
|---|---|---|---|
| **Principles** | `memory/principles/` | Universal rules. Apply to ANY project. Examples: "close every loop", "truth over validation" | Stable, rarely change |
| **Patterns** | `memory/patterns/` | Reusable designs. Tagged by which projects use them. Examples: "harness contract", "closed loop eval", "ralph wiggum loop" | Evolve as new use cases emerge |
| **References** | `memory/references/` | Captured external sources. FULL inventory of notable concepts (not pre-filtered for current project). Examples: a github repo, a research paper | Refreshed periodically (audit_references.py monthly) |
| **Lessons** | `memory/lessons/` | Incident-derived rules. Format: rule + Why (the incident) + How to apply | Append-only; never delete, only supersede |

The distinction matters: principles are universal taste. Patterns are designs I might apply. References are external knowledge I've absorbed. Lessons are rules I learned from getting it wrong.

## Topic taxonomy (use these tags exactly — no synonyms)

Every memory file has a `topics:` frontmatter list using these 8 tags:

| Tag | Covers |
|---|---|
| `harness` | Test runners, harness shape, verification scaffolding |
| `memory` | Memory layers, KGs, recall, persistence, knowledge structure |
| `eval` | Evaluation, gold sets, judges, scoring, metrics |
| `llm` | LLM-specific patterns, prompts, model choice, JSON mode, AFC |
| `agent` | Agent architecture, multi-agent, sub-agents, MCP |
| `arch` | System architecture, layering, substrates, structure |
| `workflow` | How-to-work patterns: env-var flags, rollback, dependency-thinking |
| `tooling` | Dev tooling: auditing, linting, scaffolding, distribution |

Resist adding a 9th tag unless 3+ files genuinely need it.

## Applicability tags (which projects this matters to)

Every memory file also has an `applies_to:` frontmatter list:

| Tag | Meaning |
|---|---|
| `universal` | Applies to any project. Default for principles. |
| `<project-name>` | Specific to that project. Example: `godtech`, `trading` |

A file can have multiple tags: `applies_to: [universal, godtech, trading]`.

## Project slots

Each project the operator builds gets a directory under `projects/<name>/`:

```
projects/<name>/
  state.md           ← current architecture summary, active sprint
  plans/             ← active and archived plans
  sessions/          ← dated session logs (build/ship outputs)
  design_docs/       ← HTML mockups, architecture maps
  changelog/         ← project history
```

Project content is gitignored from the framework repo. It lives in the operator's private instance.

## Where to write what (decision rule)

When something needs to be written, decide WHICH directory based on what it IS:

| If you're | Write to |
|---|---|
| Editing target project's code | The target project's directory (NOT Moradin) |
| Updating target project's architecture truth | The target project's CLAUDE.md or AGENTS.md |
| Capturing a new external resource | `memory/references/<name>.md` |
| Distilling a new design pattern | `memory/patterns/<name>.md` |
| Saving an incident-derived lesson (Why + How) | `memory/lessons/<name>.md` |
| Saving a universal rule | `memory/principles/<name>.md` |
| Logging session work | `projects/<name>/sessions/<date>_<topic>.md` |
| Updating project state | `projects/<name>/state.md` |

## Naming rules

1. **Use generic, descriptive filenames.** `memory/patterns/closed_loop_eval.md`, not `patterns/karpathy_method.md`.
2. **Industry-standard pattern names are fine.** `memory/patterns/ralph_wiggum_loop.md` is OK because Ralph Wiggum loop IS the standard name of that pattern.
3. **No attribution in the framework's identity.** Don't write "inspired by X" or "adopted from Y" in CLAUDE.md, AGENTS.md, README, or pattern files. Once a pattern is absorbed, it's ours.
4. **Lowercase + underscores.** `close_every_loop.md`, not `CloseEveryLoop.md`.
5. **No prefixes like `feedback_` or `principle_`.** The directory tells you the type. The filename describes the content.

## Capture discipline

When capturing a reference (`/moradin:capture <url>`):

1. WebFetch the URL.
2. List **ALL** notable concepts from the source, NOT just what fits today's project. Capture the full inventory.
3. Tag each concept with its potential applicability (which projects might use it). Concepts that contradict our current approach may be RIGHT for a different project later. Keep them.
4. Note what was deliberately skipped and why (tactical detail vs. fundamentally irrelevant).
5. Write to `memory/references/<source>.md`. Update `memory/references/_INDEX.md`.

## Scripts I rely on

| Script | Job |
|---|---|
| `scripts/search.py` | BM25 over memory + frontmatter filter. Used by `/moradin:recall` |
| `scripts/audit.py` | Lint memory: stale dates, contradictions, orphan files |
| `scripts/stats.py` | Counts + coverage report |
| `scripts/refresh_indexes.py` | Rebuilds `_INDEX.md` files from frontmatter (run after captures) |
| `scripts/audit_references.py` | Monthly: re-fetch reference URLs, flag staleness |
| `scripts/update.sh` | Pull framework updates from upstream |

## Recommended companion plugins

See `plugins.md` for the list of Claude Code plugins that pair well with Moradin (autonomous loops, coding principles, etc.). These are external — install them separately.

## What I never do

- Run as a daemon. I have no process, no port.
- Edit a target project (e.g. GodTech) without first reading its current state file or CLAUDE.md.
- Skip updating `_INDEX.md` after a capture or write.
- Pre-filter notable concepts during a reference capture based on current project. Capture the full inventory.
- Attribute external sources in my own documentation. The pattern, once absorbed, is mine.
- Auto-tag content without operator confirmation. Tags carry taste; operator reviews and approves.

## How I grow

Every time the operator captures a reference, distills a pattern, saves a lesson, or finishes a session, I gain a file. Over time I become a complete record of how this operator builds. The indexes auto-maintain via `refresh_indexes.py`. The audit scripts surface drift. The operator decides what to promote, deprecate, supersede.

I am a workshop. The operator brings the work. I keep the records.
