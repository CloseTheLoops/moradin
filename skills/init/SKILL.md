---
name: moradin-init
description: Initialize a Moradin workshop in the current directory. Run once per instance.
---

# moradin:init

Use this skill to set up a fresh Moradin workshop. Typically run once per instance, right after cloning the template.

## When invoked

`/moradin:init`

The operator just cloned the template (or used "Use this template" on GitHub). This skill walks them through first-time setup.

## What you do

1. **Verify structure.** Check that `memory/{principles,patterns,references,lessons}/`, `projects/`, `templates/`, `examples/` exist. If any are missing, create them.

2. **Initialize indexes.** Run `python scripts/refresh_indexes.py` to create empty `_INDEX.md` files.

3. **Ask the operator:**
   - "Do you have an existing project you want Moradin to help build? If yes, tell me its name and where it lives."
   - "If yes, I'll create `projects/<name>/state.md` and link it."

4. **Optional first content.**
   - "Want to capture your first principle? (universal rules that apply to any project)"
   - If yes, walk through writing one to `memory/principles/` using `templates/principle.template.md`.

5. **Point them at the front door.** Explain in two sentences: "The main way to use Moradin is `/moradin:forge` — open a session, name a project folder or a brand-new idea, and it guides you from there, start to finish. Everything else (capture, recall, audit) is the memory layer that makes each project smarter than the last."

6. **Summarize what's set up.** List the directories, the first project slot if created, the first principle if any — and end with the `/moradin:forge` pointer.

## Don't

- Don't pre-fill memory with content. Moradin starts empty. The operator fills it.
- Don't write to GodTech or any other target project during init.
- Don't auto-tag the first principle without asking the operator to confirm tags.

## Output

- Updated `_INDEX.md` files (empty initially)
- Optional `projects/<name>/state.md` if operator gave a project
- Optional `memory/principles/<first>.md` if operator gave a principle
