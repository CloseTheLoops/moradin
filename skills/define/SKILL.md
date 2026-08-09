---
name: moradin-define
description: Stage 1 of the Forge — turn a raw idea into a capped one-page plan through a drafted interview. Who + problem first, then job story, riskiest assumption, walking skeleton, appetite cut, premortem. Writes .forge/plan.md and seeds the backlog.
---

# moradin:define

Turn "I have an idea" into a plan someone can build from — in 10–15 minutes at light level. Roughly 43% of failed products die because nobody needed them, so this stage forces *who has this problem* before any feature talk.

## When invoked

`/moradin:define` (dispatcher routes here) or directly with the idea: `/moradin:define "an app that ..."`

Requires `.forge/profile.md` (run `/moradin:forge` first if missing). Read `profile.md` and, if it exists, the current `plan.md` (amendment mode — supersede only the affected sections).

## The one interaction rule

**You draft, the operator corrects.** Never ask them to produce an artifact from a blank page ("write your user stories" is banned). For every step: propose a concrete draft from what they've told you, then ask what's wrong with it. Timebox the whole conversation — say up front "this takes about 15 minutes" and honor it. Good-enough v0 answers are explicitly fine; say so when they stall.

## The interview — light level (all profiles do these 6)

Work through in order. One step at a time, conversationally.

1. **Who + problem.** Draft: "*[specific person] struggles to [specific thing]*." Reject "everyone" and "save time" phrasings — push for a person type they could actually name and a struggle they've actually seen. This is the step most failed products skipped.
2. **Job story.** Draft: "*When [situation], I want to [motivation], so I can [outcome]*." One sentence. They edit.
3. **Riskiest assumption.** Ask: "What has to be true for anyone to use this? What's the ONE thing v1 must prove?" Also ask: "How do you know this problem exists?" If the honest answer is "I don't" — note it; milestone 0 becomes a validation test (the measure stage will set it up).
4. **Walking skeleton.** Ask: "Walk me through one successful use, step by step, as the user." Each step becomes a story. Cap at 7; if they list more, the extras go to the backlog.
5. **Appetite + the cut.** Ask: "How much time before something is usable — a weekend? Two weeks?" Then go step by step: in, or not-now, against that appetite. Binary only — no maybe-tiers. Everything cut is *parked in the backlog with its number*, not deleted; say that out loud, it makes cutting painless.
6. **Premortem.** Ask: "It's three weeks from now and you abandoned this. Why?" Draft one mitigation for the top answer. Milestone 1 = the skeleton works end-to-end.

## Full level adds (medium picks what's useful)

- 2–3 named user types; pick the primary.
- Directional outcome + 2–3 opportunities *before* discussing solutions (catches "I built my idea, then looked for a problem").
- Acceptance criteria per skeleton step ("how will you know this step works?").
- A non-goals section.
- Full premortem: 3–5 failure reasons, each mapped to a mitigation or a milestone.
- 2–3 milestones, each with its own appetite and a demoable outcome.

**Never, at any level:** RICE scores, opportunity-tree upkeep, Should/Could tiers, effort estimates.

## Write the outputs

1. `.forge/plan.md` from `templates/forge/plan.md` — **hard cap: 2 pages light / 5 pages full.** If the draft runs over, cut prose, not decisions. Every sentence should encode something the operator chose.
2. Seed `.forge/backlog.md` with every parked item (status `deferred`, one-line reason).
3. Update `.forge/journal.md`: stage done, one-line summary, next action — "Run `/moradin:measure` to set the success numbers before we research tools."

Then read the plan back in three sentences, plain language, and ask: "Is this the thing you meant?"
