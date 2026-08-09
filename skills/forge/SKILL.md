---
name: moradin-forge
description: The Forge dispatcher. Reads a project's .forge/ state, tells the operator where they are, and routes to the right stage — full pipeline for new things, quick path for small changes, amendment when the plan changes. First run calibrates.
---

# moradin:forge

The front door of the pipeline. You never guess what to do next in a forge project — this command reads the state and routes.

## When invoked

`/moradin:forge` or `/moradin:forge <what the operator wants to do>`

## Step 1 — Find the target project

The forge runs against a **target project directory** — always a SIBLING of the Moradin folder, never inside it (nesting tangles git and pollutes context). If the conversation already names it, use it. Otherwise ask: "Which project folder are we working in? (Give me a path, or a name and I'll create a new folder next to Moradin.)" For a brand-new project, create the sibling directory and `git init` it — explain in one sentence that git is the save-point system everything else relies on.

## Step 2 — Read the journal first

Read `.forge/journal.md` in the target project. It is 3 lines: current stage, last action, next action.

- **No `.forge/` directory** → first run. Go to Step 3 (Calibrate).
- **Journal exists** → tell the operator where they are in one sentence ("You're mid-research; last time we compared databases. Next: run /moradin:decide.") Then route via Step 4.

Load other `.forge/` files only when the route needs them — never all at once.

## Step 3 — Calibrate (first run only)

Before asking anything: if this workshop has `memory/preferences/` content, read its `_INDEX.md` and pre-fill what's already known about how this operator works. Confirm pre-filled answers in one line ("I know you try the app rather than read diffs — still true?") instead of re-asking.

Then a short plain-language interview for the gaps, a few questions at a time — never a wall. "I don't know what that is" is a real answer and means "not yet."

1. What are you building here, in a sentence or two?
2. When AI writes code for you — do you read it, skim it, or just try the app?
3. Do you use git? Branches? Pull requests?
4. Are there tests? Do you run them?
5. How do you find out something broke?
6. Ever wished you could rewind the project to yesterday? What happened?
7. How much process do you want — light guardrails, or fuller structure that catches more?

Pick a level and confirm it in one sentence, no jargon ("Sounds like light — I'll keep steps few and explain anything new. Good?"). The operator can override.

| Level | Signals |
|---|---|
| **light** | doesn't read diffs · no branches · no tests · wants speed |
| **medium** | uses git · some tests · reads diffs sometimes |
| **full** | comfortable with branches/PRs/tests · wants the whole thing |

Then: create `.forge/` from `templates/forge/` (journal, profile, backlog now; other files are created by their stages), fill `profile.md`, and route to `/moradin:define`.

The level sizes guidance depth only. It never removes safety steps.

## Step 4 — Route

| Situation | Route |
|---|---|
| Change describable in one sentence, plan unaffected | **Quick path** (below) |
| "This changes what we're building" | **Amendment** (below) |
| `measure.md` review date has passed | Review stage — say so first |
| Otherwise | The next stage named in the journal |

Stages: define → measure → research → decide → build → close → review. Each is `/moradin:<stage>`.

All seven stage skills exist. If a listed skill is ever missing in a copy of this workshop, say so plainly and offer a best-effort manual version instead of pretending the command exists.

## Quick path — small fixes, any level

No plan, no full close. In order:

1. **Checkpoint** — commit first (a point we can rewind to).
2. **Align** — one sentence: what you're about to change and what you assume. Wait for a nod.
3. **Build it** — dev data only, never production.
4. **Check** — run the affected slices' existing checks from `checklist.md` (if none apply, verify by using the app), and scan the diff for secrets before committing.
5. **Tick** — commit, note it in `backlog.md` if it closed an item, update the journal.

If mid-way it stops being one sentence — stop and say so. It's an amendment or a new pipeline entry, not a bigger quick fix.

## Amendment — the operator changed their mind

A pivot is not scope creep; don't bolt it onto the backlog. Instead:

1. Say back what's changing, in one sentence, and confirm.
2. Re-enter `/moradin:define` scoped to the affected sections — supersede those parts of `plan.md` (and mark affected records in `decisions.md` as superseded; never edit them in place).
3. Regenerate only the affected slices in `checklist.md`. Untouched work stays untouched.
4. Update the journal.

## Backlog ↔ GitHub issues (optional, for projects with a remote)

If the target project has a GitHub remote and `gh` is authenticated, offer once: "want your backlog mirrored to GitHub issues?" If yes, note `github_sync: on` in `profile.md` and from then on:

- **`backlog.md` is the source of truth for content**; issues mirror it. New backlog item → `gh issue create` (title = item title, body = note + backlog id, label `forge`). Item `done`/`deferred` → close the issue with a one-line comment.
- **Issues are an inbox**: at each dispatch, `gh issue list --label forge` — issues created directly on GitHub (ideas from a phone) get pulled *into* `backlog.md` as `idea`, then follow the normal flow.
- On conflict (edited both places), `backlog.md` wins; say so and update the issue.
- Never sync `.forge/` files themselves to issues — the backlog is the only shared surface.

## Always, before finishing

Rewrite `.forge/journal.md` — stage, what just happened, and the next action in plain language with the exact command. The journal is how the operator resumes after three weeks away; write it for that person.
