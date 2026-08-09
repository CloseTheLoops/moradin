---
name: moradin-close
description: Stage 6 of the Forge — the loose-ends stage. Evidence-derived security core, closed-loop audit, converge, and the four-question retro whose lessons flow back into Moradin memory. Core/Extended keys to release significance, never to operator profile.
---

# moradin:close

Every item here traces to a documented disaster that hit builders exactly like this project's operator. The profile never shrinks this list — **scoping keys to release significance**: first public launch or personal data involved ⇒ Extended; otherwise Core.

## When invoked

`/moradin:close` — after a milestone ships, before ending a project phase. Reads all of `.forge/`.

## Core (every ship, 30–60 min, agent-driven)

1. **Secrets** — scan the *entire git history*, not just HEAD. Any hit: **rotate the key**, never just delete the line (most keys leaked years ago are still live). Confirm nothing secret sits in client-delivered code.
2. **Logged-out probe** — from outside the app (curl/incognito, no session): attempt to read and write every endpoint, table, and storage bucket. Expect denial everywhere. This one check would have prevented the era's worst vibe-coded breaches.
3. **Database rules** — row-level security / access rules on every table, verified with the platform's own linter where one exists.
4. **A way back** — automatic backup on, and **one real restore performed** into a scratch location. An untested backup is a hope, not a backup.
5. **Spend caps** — billing alerts + hard caps on every metered API the project touches; note any service that *cannot* cap as a standing risk.
6. **Monitoring heartbeat** — error tracker receives a deliberate test error; uptime check answers.
7. **Production smoke test** — the golden path (arrive → core action → data persists), in production, as a stranger.
8. **Contact route** — a working way for a user to reach the operator; doubles as the data-deletion request path.
9. **Personal data?** — if the app stores any: privacy policy + terms generated and linked, deletion route actually works.
10. **Closed-loop audit** — every plan item and backlog entry is `done` or `deferred` with a reason. Nothing dangles unlabeled.
11. **Converge** — reconcile `.forge/` files against the actual code, both directions: constants the build amended go into the plan; code that drifted from a decision gets flagged (supersede or fix).
12. **Retro, four questions** — what shipped · what broke or surprised · what would we do differently · what's explicitly deferred.

## Extended (first public launch / bigger releases / PII)

Rate limiting on auth + expensive endpoints · dependency audit and unused-dep removal · TODO/mock/dead-code sweep (AI codebases accumulate stubs that look finished) · legacy-data purge (old buckets, dev databases, seeded PII — old data breaches as well as new) · **prompt-injection trifecta review** whenever an LLM feature exists (does anything read untrusted content while holding private data and an outbound channel? agent credentials read-only) · adversarial code review by a fresh-context subagent over the full diff · cost audit of every service signed up during build, cancel the unused · README verified from a clean clone · platform-trust check (verify auth yourself even on platforms that "handle it").

## Moradin-side outputs (how the forge gets smarter)

- Session log → `projects/<name>/sessions/<date>_<topic>.md`; update `projects/<name>/state.md`.
- Retro answers that generalize → `memory/lessons/` (rule + Why-incident + How-to-apply), then `scripts/refresh_indexes.py`.
- Update the target project's `CLAUDE.md` steering (stack, commands, ops) so the next session inherits truth.
- `.forge/journal.md` → shipped status + "next: /moradin:review fires at the contract's review date."
