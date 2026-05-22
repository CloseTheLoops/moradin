# FAQ

## Is Moradin a memory system like Mem0 or Zep?

No. Moradin is a workshop — a directory of markdown files that an agent loads when opened. Mem0 and Zep are runtime memory layers that AGENTS query during conversation. Different problems.

You can use both: a runtime agent uses Mem0 for within-session memory; you use Moradin in your dev sessions to accumulate build knowledge across projects.

## Is Moradin a knowledge base / second brain?

Close, but with a workshop focus. Most "second brain" tools (Karpathy LLM Wiki, claude-obsidian, etc.) are designed for accumulating knowledge from READING. Moradin is designed for accumulating taste from BUILDING — principles, patterns, lessons from your actual work.

## Why markdown? Why not a database?

Markdown is portable, version-controllable, human-readable, and works in any editor. The 8 SKILL.md skills + 5 scripts maintain it. At <500 files (typical for a personal workshop), BM25 search over markdown is fast enough.

If your workshop grows past 200 files and search slows, consider adding vector search via Mem0 / Zep as a sublayer.

## Why no fancy KG / temporal validity / supersession infrastructure?

It's a workshop for one operator, not a runtime agent serving thousands. The Karpathy LLM Wiki pattern + audit scripts handle 95% of what we need. Heavier infrastructure (Graphiti, Mem0's hybrid stores) is overkill until you have >500 files and need cross-reference queries.

If you need supersession: add `superseded_by: <newer_file>` to frontmatter. Audit script flags. Simple.

## Can I use Moradin with Cursor / Codex / Gemini, not just Claude Code?

Yes. The workshop's brain lives in `AGENTS.md` (the Linux Foundation cross-tool standard). `CLAUDE.md` is a copy/symlink. Any agent that respects `AGENTS.md` or `CLAUDE.md` will load the workshop on session start.

Skills are written in the `SKILL.md` format from [agentskills.io](https://agentskills.io), which is adopted across major agents.

## How do I keep my Moradin private but the framework public?

The framework is at `closetheloops/moradin` (public, MIT). Your instance is a fork or template-clone at `<your-username>/moradin-yz` (private). Your memory/, projects/, and scratch/ are gitignored from the framework remote.

When the framework updates, `./scripts/update.sh` merges upstream changes without touching your content.

## What if a pattern conflicts with a principle?

Principles win. They're universal rules. Patterns are designs that should align with principles. If a pattern violates a principle, either:
1. The pattern is wrong (fix it).
2. The principle has an exception for this case (document the exception in the principle file).
3. The principle is wrong (rare — generally don't change principles lightly).

## How big should my memory get?

| Stage | Files |
|---|---|
| New install | ~5-10 (1-2 principles, 1-2 patterns, 0-2 references, 0 lessons) |
| 1 month in | ~30-50 |
| 6 months in | ~80-150 |
| 1 year in | ~150-300 |
| 2 years+ | 300-500 |

At ~500 files, consider audit-driven cleanup. At ~1000, Moradin's pure-grep search may slow — add a vector layer.

## Can I open-source my workshop?

Sure. Either:
1. Make your instance repo public.
2. PR generalizable patterns back to the framework repo as `EXAMPLE_*.md`.

Both work. The framework/content split means you can choose what to share.

## Why "Moradin"?

Dwarven god of creation in D&D. Builders, craftsmen, smiths. The metaphor fits a workshop. Low collision with existing tools (no other major project under this name in the AI agent space).

## What if I never start a second project?

Moradin still helps with the one project. You'll accumulate principles, patterns, lessons across sessions. The cross-project benefit is a bonus, not a requirement.
