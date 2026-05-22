# Recommended companion plugins

Moradin pairs well with these Claude Code plugins. Install them separately — they're not bundled.

| Plugin | What it gives you | Install | Required? |
|---|---|---|---|
| [karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | 4 universal coding principles (Think Before · Simplicity First · Surgical Changes · Goal-Driven). Acts as default principles for any project. | `/plugin marketplace add multica-ai/andrej-karpathy-skills` + `/plugin install karpathy-skills` | Optional but recommended |
| [ralph-wiggum](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) (Anthropic) | Autonomous iteration loop — Stop hook re-feeds prompt until completion. See `memory/patterns/ralph_wiggum_loop.md` for when to use. | Built into Anthropic's official plugin marketplace | Optional |
| Obsidian (optional UI) | Visual graph + backlinks + Web Clipper for the memory directory. Moradin is pure markdown, so Obsidian opens the vault as-is. | Install Obsidian desktop app, "Open folder as vault" → point at Moradin directory | Optional |

## How to use

These plugins are completely independent of Moradin. They don't ship with the framework. The operator installs whichever ones suit their workflow.

When a Moradin skill needs functionality from a companion plugin (e.g. `/moradin:build` may suggest using Ralph loop for a mechanical task), it references the plugin's command but doesn't require it to be installed — the operator decides.

## Adding more

If you find a Claude Code plugin that pairs well with Moradin, add it here via PR. Criteria:

- MIT or Apache-2 licensed
- Actively maintained
- Solves a problem Moradin doesn't (no overlap with Moradin's 8 skills)
- Discoverable on a major catalog (anthropics/claude-plugins-official, claudemarketplaces.com)
