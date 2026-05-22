# Moradin

> A workshop for accumulating build-taste across projects. Cross-tool dev brain.

Moradin is a directory on your machine — a workshop. You open Claude Code (or Cursor, Codex, Gemini) in it. That session inherits your principles, patterns, references, lessons, and per-project state. You then use that session to **build other projects**. Moradin itself just accumulates knowledge.

It is **not** a running agent. No port, no scheduler, no daemon. Just markdown files + Python scripts. Dormant when you're not using it. Comes alive when an agent opens the directory.

## Quickstart

```bash
# Use the GitHub template button to create your private instance, then:
git clone https://github.com/<your-username>/<your-moradin-fork>.git ~/Documents/moradin
cd ~/Documents/moradin
claude   # or `cursor .` or whichever agent you use
```

In your first session:

```
/moradin:init                       # set up workshop, optionally create first project slot
/moradin:capture <url>              # capture an external source
/moradin:recall "what do I know about X?"   # search memory
/moradin:build <project> <task>     # structured build session
/moradin:ship                       # end-of-session, save lessons
```

## What's inside

```
moradin/
  AGENTS.md / CLAUDE.md          ← workshop brain (loaded every session)
  .claude-plugin/                ← Claude Code plugin manifest
  skills/                        ← 8 SKILL.md-compliant verbs
  scripts/                       ← stdlib-only Python utilities
  memory/                        ← THE memory layer
    principles/                  ← universal rules
    patterns/                    ← reusable designs
    references/                  ← captured external sources (full inventory)
    lessons/                     ← incident-derived rules
  projects/                      ← per-project state, plans, sessions, design docs
  templates/                     ← scaffolds for new files
  examples/                      ← demo content (committed)
  plugins.md                     ← recommended companion plugins
  docs/                          ← QUICKSTART, CONCEPTS, CONTRIBUTING, FAQ
```

## The 8 skills

| Verb | What it does |
|---|---|
| `init` | Initialize a fresh workshop |
| `capture` | Capture an external source as a reference (full unfiltered concept inventory) |
| `recall` | Search memory + synthesize an answer with citations |
| `audit` | Lint memory: stale, missing fields, bad tags, orphans |
| `stats` | Counts + coverage report |
| `build` | Structured build session against a target project |
| `ship` | End-of-session: save lessons, update state |
| `retrospect` | Review past sessions, propose promotions to patterns/principles |

## Key design decisions

- **Framework vs content split.** The repository ships an empty shell + tools + workflows. Each user fills it with their own content. Their `memory/` is gitignored from the framework remote.
- **Capture full inventory, distill per-project.** References capture EVERYTHING notable from a source, not pre-filtered. Patterns extract project-specific designs later.
- **Topic taxonomy is small + stable.** 8 tags (harness, memory, eval, llm, agent, arch, workflow, tooling). Resist adding more.
- **Cross-tool.** Uses `AGENTS.md` (Linux Foundation standard) as source of truth, with `CLAUDE.md` as a copy/symlink. Works in Claude Code, Cursor, Codex, Gemini.
- **Standards-compliant.** Skills use the [agentskills.io](https://agentskills.io) `SKILL.md` format. Plugin manifest follows Anthropic's spec.
- **No attribution in framework identity.** Patterns are absorbed and become ours. Industry-standard names (Ralph Wiggum loop, etc.) are fine as filenames.

## Updating from upstream

When the Moradin framework updates, pull changes without losing your personal content:

```bash
./scripts/update.sh
```

This merges upstream framework changes via `-X ours` so your `memory/` and `projects/` stay intact.

## License

MIT — see `LICENSE`.

## Documentation

- [QUICKSTART](docs/QUICKSTART.md) — set up in 5 minutes
- [CONCEPTS](docs/CONCEPTS.md) — the 5 layers explained
- [CONTRIBUTING](docs/CONTRIBUTING.md) — how to add skills, file PRs
- [FAQ](docs/FAQ.md) — common questions
- [plugins.md](plugins.md) — recommended companion plugins
