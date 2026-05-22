# Contributing

How to extend Moradin.

## Add a new skill

1. Create a directory under `skills/<verb>/` (kebab-case).
2. Inside, write `SKILL.md` with this frontmatter:
   ```yaml
   ---
   name: moradin-<verb>
   description: One-line description of what the skill does
   ---
   ```
3. Body: explain when to invoke, what the skill does step-by-step, what NOT to do, what output to expect.
4. Register the skill in `.claude-plugin/plugin.json` under `skills`.
5. Test by opening Claude Code in Moradin and invoking `/moradin:<verb>`.

Keep skills focused — one verb, one purpose. If your skill is doing 3 things, split it.

## Add a new script

1. Write the script in `scripts/<name>.py` (stdlib-only — no external deps).
2. Add a docstring at the top:
   ```python
   """One-line description.
   
   Longer explanation if needed.
   
   License: MIT
   """
   ```
3. Test it works from the Moradin root: `python scripts/<name>.py`.
4. If a Moradin skill should call this script, reference it in the relevant `SKILL.md`.

## Add a new topic tag

Resist this. The 8-tag taxonomy (harness, memory, eval, llm, agent, arch, workflow, tooling) is small + stable on purpose.

If you NEED a 9th tag:
1. Propose it in an issue: what 3+ files would use it? What goes wrong if it falls under an existing tag?
2. If approved, update `memory/_SCHEMA.md` taxonomy table.
3. Update `scripts/audit.py` `ALLOWED_TOPICS` set.
4. Update `AGENTS.md` topic taxonomy section.

## Add a template

If you find yourself writing the same structure repeatedly, add a template:

1. Create `templates/<name>.template.md`.
2. Use `REPLACE` markers for fields the user fills in.
3. Reference the template in the relevant skill (e.g. `/moradin:capture` uses `templates/reference.template.md`).

## Sharing patterns upstream

If a pattern you've written in your private Moradin instance is generalizable, PR it as an example:

1. Sanitize: remove project-specific names, generalize.
2. Rename `your_pattern.md` → `EXAMPLE_pattern_your_pattern.md`.
3. Put it in `examples/`.
4. Open a PR.

Patterns that aren't operator-specific (i.e., don't reference your company / your data) are good candidates.

## PR guidelines

- One change per PR (one skill, one script, one fix).
- Update the relevant `_SCHEMA.md` or docs if behavior changes.
- Test against an empty memory AND a memory with example fixtures.
- No external dependencies in `scripts/` — stdlib-only.
