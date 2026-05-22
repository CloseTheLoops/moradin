---
name: moradin-capture
description: Capture an external source (URL, repo, paper) as a reference in memory/references/. Full unfiltered concept inventory.
---

# moradin:capture

Capture an external source as a reference. **Capture EVERYTHING notable, not just what fits the current project.** Project-specific filtering happens later at distillation time.

## When invoked

`/moradin:capture <url>` (or `/moradin:capture <description>` if not URL)

The operator saw something interesting and wants to record it permanently.

## What you do

1. **WebFetch the URL** (or read source if local). Read README + key sections.

2. **List ALL notable concepts** in your reply. Don't pre-filter for current project relevance. Show the operator a full inventory of what's in the source:
   - Concept A: [one paragraph]
   - Concept B: [one paragraph]
   - Concept C: [one paragraph]
   - ...

3. **For each concept, propose tags:**
   - `topics`: from the 8-tag taxonomy (harness, memory, eval, llm, agent, arch, workflow, tooling)
   - `applies_to`: which projects might use it (universal, godtech, trading, future)

4. **Ask the operator to confirm or edit the tags.** Don't auto-write — get a green light.

5. **Note what you deliberately skipped** — tactical setup details, deeply specific code, or items fundamentally irrelevant.

6. **Write the reference file** at `memory/references/<source_name>.md` using `templates/reference.template.md` as scaffold. Include:
   - Frontmatter: name, description, topics, applies_to, type=reference, url, captured (date), last_verified (date)
   - Body: "What it is" + "Notable concepts" (full inventory) + "What I deliberately skipped"

7. **Update indexes.** Run `python scripts/refresh_indexes.py` so `_INDEX.md` reflects the new file.

8. **Confirm to operator** with the file path.

## Capture discipline (the rule that protects against losing useful concepts)

The big failure mode: filtering concepts at capture time based on current project. **Don't.** Concepts that don't fit GodTech today may fit trading next month. Capture full inventory.

## Don't

- Don't summarize away interesting-but-tangential concepts. Capture them.
- Don't auto-assign tags without operator confirmation.
- Don't write attribution like "inspired by X" — once captured, the concepts are ours.
- Don't capture a reference if we've already captured the same source — update the existing file instead.

## Output

- New file at `memory/references/<source_name>.md`
- Updated `memory/references/_INDEX.md` (and top-level `memory/_INDEX.md`)
