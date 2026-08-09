# Moradin v0.3 — The Forge

_v3 (final draft). Drafted 2026-08-09: research pass (5 agents, primary sources) → synthesis → adversarial gap-check (17 findings folded in). Status: awaiting operator approval. Review surface: `docs/FORGE_PLAN_v1.html`. Evidence base: `docs/forge_research/01–05`._

## The identity shift

Moradin today is a **library**: memory you consult while building elsewhere. v0.3 makes it a **forge**: a guided pipeline that takes anyone — including operators who build purely by prompting AI — from "I have an idea" to "I shipped a product," with the expert judgment encoded in the skills so the operator doesn't have to supply it. Memory (principles, patterns, lessons, references) becomes the stock the forge draws from and feeds back into.

The 2025–26 evidence says this niche is genuinely open: every spec-driven framework (Spec Kit, Kiro, BMAD) either buried users in markdown, got ignored by its own agents, or admitted non-devs can't actually run it. Nobody has shipped *calibrated, brevity-capped, verified* guidance for non-experts. That is the slot the Forge fills. [01, 03]

## Locked decisions (operator, 2026-08-09)

1. **Forge state lives in the target project** — a `.forge/` directory; projects are self-contained and portable.
2. **Backlog is local-first** — `backlog.md` now; GitHub-issues sync ships at launch.
3. **Stage skills + dispatcher** — `/moradin:forge` reads state and routes.
4. **Forge front door, memory behind** — no teardown; memory system stays underneath.
5. **Measure is its own stage after Define** — success criteria are defined before any tool research or code.

## Design laws (from the research — these override everything else)

1. **Right-size per task, not per project.** Kiro, BMAD, and Anthropic all had to patch in a "quick path" after users abandoned full pipelines for small changes. The dispatcher routes *every* entry. [01]
2. **Hard size budgets on every artifact.** Spec Kit generated 2,577 lines of markdown for one feature; review took 3.5h vs 15min. Every `.forge/` file is capped; prose exists only where a human decision is encoded. [01, 03]
3. **Non-negotiables are enforced by checks and hooks, not prose.** Agents demonstrably ignore markdown instructions (Cursor rules, Spec Kit tasks). Every slice defines a check the agent can *run*; the hard rules (no prod data, secrets never committed, checks before ticks) are installed as hooks in the target project (pre-commit secrets scan; PreToolUse block on prod connection strings; stop-hook running slice checks). Prose is reserved for what genuinely can't be a check. [01, 05]
4. **No summary chains.** Task Master lost 80% of a PRD by decomposing from summaries. Build slices cite the specific `plan.md` sections and decision IDs they implement, and slice generation re-reads the source files. [01]
5. **Specs are scaffolding, not source of truth.** The code is the product; Close reconciles `.forge/` against reality in both directions. [01]
6. **No persona agents.** BMAD's role-play made small projects 10–15× slower; its own v6 retreated. Specialized perspectives are prompts inside a stage, never separate agents with handoffs. [01]
7. **Context economy.** `.forge/` files load on demand per stage; the steering layer alone is always-resident. Fresh session at the Decide→Build boundary — and the skill tells the operator *literally how* in plain language ("type /clear, then type /moradin:build"). [01]
8. **The agent never touches production data.** Replit's agent deleted a live database during a code freeze; Gemini CLI destroyed files after an unverified `mkdir`. Dev/prod separation from slice one; verify-after-write; commit at every checkpoint. [05]
9. **Facts that rot live in memory, not in skills.** Tool defaults (analytics, monitoring, hosts) are recorded in a dated `memory/references/` file that skills cite and `audit_references.py` re-verifies monthly — never hardcoded in SKILL.md text, or the Forge eventually recommends a dead tier with full confidence (Highlight.io died *during our own research window*). [01, 05]

## The pipeline

```
/moradin:forge ─► reads .forge/journal.md first, then routes per task:
                  one-sentence change ─► QUICK PATH
                  "this changes the plan" ─► AMENDMENT
                  measure.md review date passed ─► REVIEW
                  new product/feature ─► full pipeline
                  first run ─► calibrate, then define

0 Calibrate ─► 1 Define ─► 2 Measure ─► 3 Research ─► 4 Decide ─► 5 Build ─► 6 Close ─► 7 Review ─┐
                  ▲                                                                               │
                  └──────────────────────── v2 re-entry / pivot ──────────────────────────────────┘
```

**Quick path** (small fixes; exists at every profile): checkpoint → one-sentence align → build → run the affected slices' existing checks + a secrets scan on the diff → tick. No plan, no full Close.

**Amendment** (operator changes their mind mid-pipeline — a pivot is not scope creep): dispatcher re-enters Define to supersede the affected `plan.md` sections and decision records, then regenerates only the affected slices. Spec stays a minutes-fresh scaffold, not a stale contract. [01]

### Stage 0 — Calibrate (inside the dispatcher, first run)

Plain-language interview: do you read the code, use git, run tests, want light or heavy guardrails? "I don't know what that is" counts as an answer. Sets a **Light / Medium / Full profile** in `.forge/profile.md`; confirmed in one sentence; re-run any time. The profile sizes *guidance depth*; it never removes safety items (see Close).

### Stage 1 — Define (`/moradin:define`)

An interview, not a form — the Forge drafts, the operator corrects; never a blank page. Certainty-first sequence (who + problem before solution): ~43% of failed products die from "no market need," not bad code. [03]

**Light (6 steps, 10–15 min):** who + problem in one sentence (reject "everyone"/"save time") → job story ("When ___, I want to ___, so I can ___") → riskiest assumption ("the ONE thing v1 must prove") → walking skeleton ("walk me through one successful use" — each step a story, cap 5–7) → appetite + binary cut ("a weekend or two weeks?" then in/not-now; not-now parked in backlog) → premortem-lite ("three weeks from now you abandoned this — why?" → one mitigation).

**Full adds:** named user types (pick primary) · directional outcome + 2–3 opportunities *before* solutioning (Torres — catches idea-first confirmation bias) · evidence check ("how do you know this problem exists?" — none ⇒ milestone 0 = validate) · acceptance criteria per story · non-goals · full premortem (3–5 reasons → mitigations) · 2–3 milestones with appetites.

Never at any profile: RICE, opportunity-tree upkeep, Should/Could tiers, effort estimates. [03]

- **Writes:** `.forge/plan.md` (≤2 pg Light / ≤5 pg Full) · seeds `.forge/backlog.md` · updates `journal.md`.

### Stage 2 — Measure (`/moradin:measure`)

Before researching tools or writing code: what does working look like, in numbers? Output: a one-page **Success Contract** (`.forge/measure.md`):

- **One metric that matters** — stage-labeled (validation / launch / growth), with a target *and a kill/pivot threshold* — the threshold is what turns the number into a decision. [02]
- **Max 3 supporting signals**, each with target + "measured by."
- **Anti-vanity list**: what we will NOT count as success (total signups, page views, followers).
- **Two horizons**: launch-week (activation) and month-3 (retention/revenue).
- **The traffic question**: "where do the first 20 users come from, *concretely*?" An answer of "nowhere yet" triggers the validation gate — metrics without a source of visitors are unmeasurable theater.
- **Instrumentation named now** so events are built during Build: defaults come from the dated tool reference (currently PostHog for funnels / Umami for light web metrics — Umami's exact limits still flagged UNVERIFIED; GA4 avoided for this audience; Sean Ellis "very disappointed" question as the zero-instrumentation fallback). [02]
- **Review date (+30d)** — read by the dispatcher, which offers the Review stage when it passes.
- **Validation gate:** no evidence from Define, or no traffic answer ⇒ the contract's first metric is *pre-build* (e.g. "≥5% of targeted visitors join the waitlist AND ≥5 people say they'd pay") and milestone 0 becomes a landing-page test. Gate outcomes are explicit: pass ⇒ proceed to product build; fail ⇒ Review-style decision (pivot the idea via Amendment, or stop cleanly). [02, 03]

### Stage 3 — Research (`/moradin:research`)

Reads `plan.md` + `measure.md`, **generates its own research questions**, confirms which matter, then researches with the expert method encoded:

- **Timebox scaled to door type**: expensive doors (data model, auth, payments) get real research; cheap doors get minutes. [04]
- **Verification checklist per option — all 8 checks, no claim from memory**: live existence check on every package/API/model ID (19.7% of LLM package recommendations were hallucinated; slopsquatting is real) · vendor pricing page fetched today (limits, spend caps, overage behavior) · pricing-change history over 24 months · maintenance signals (human commits ≤90d, releases ≤12mo, last-12-month contributor concentration — never stars) · adoption-trend direction over 12 months · issue responsiveness (median first response; critical issues untriaged >30d flagged) · lock-in probe (concrete exit path, migration days) · anything unverifiable labeled **UNVERIFIED**. [04]
- **Named risk category** flagged wherever found: free tier + auto-scaling usage billing + no hard spend cap (Netlify $104k, Cara $96k, PlanetScale/Heroku/Glitch rug-pulls). [04]
- **Boring-by-default**: mainstream stacks are what AI agents build most reliably on; the report tracks innovation tokens. [04]

- **Writes:** `.forge/research/<topic>.md` · one HTML options report (per `operator_review_as_html`) · updates `journal.md`.

### Stage 4 — Decide (`/moradin:decide`)

Constraints first (budget / scale / skills elicited *before* options are shown — post-hoc weights launder predetermined answers). Then per decision: **exactly 3 options + 1 recommended default**, each with cost now and at 10×, spend-cap status, exit cost in days, and a "pick this if…" sentence. Every decision offers non-dev triage: **accept the default / defer / explain in plain language**. [01, 04]

Each choice appends a **Nygard-lite record** to `.forge/decisions.md`: context (2–3 sentences) · decision (1 sentence) · why (2–3 bullets tied to stated constraints) · rejected options with one-line why-nots · door type · innovation token spent · verified-on date · **"revisit when" event triggers** (pricing changes, >N users — never calendar dates). Binding enforced by status: `accepted` is not relitigated except by explicit supersession (or Amendment). [04]

### Stage 5 — Build (`/moradin:build`, rewritten)

Plan + decisions become `.forge/checklist.md`: **vertical slices**, each citing its plan sections + decision IDs and defining its **executable check** up front. Per slice: checkpoint (commit — "save a point to rewind to") → align (plain-language statement of what's about to be built + assumptions; wait, or log-and-proceed in auto) → build against dev data only → **run the slice's check** → tick + checkpoint.

**Operator setup tasks** — the human-only work no framework acknowledges: creating hosting/DB/analytics/monitoring accounts, pasting API keys into env vars, setting spend caps in vendor dashboards, buying/pointing a domain. These become explicit `[you]` items in `checklist.md`, written as plain-language walkthroughs ("you do this; I verify it") — and the agent verifies each before the dependent slice proceeds. A non-dev never strands on an auth wall the agent can't cross.

Hard rules (hook-enforced where possible, Law 3): scope creep → backlog item; API pre-flight (real key, real payload, standalone) before building around any external service; first deploy slice wires monitoring (currently Sentry free + UptimeRobot free = $0) and the Success Contract's analytics events; fresh session at build start, re-reading `.forge/` state. [01, 02, 05]

### Stage 6 — Close (`/moradin:close`, absorbs `ship`)

Checklist items are evidence-derived from documented 2025 incidents. [05] **Scoping rule:** the Core/Extended split keys to *release significance* (first public launch or PII involved ⇒ Extended), never to operator profile — the incidents all happened to Light-profile builders. The trifecta check is unconditional whenever an LLM feature exists.

**Core (every ship, 30–60 min, AI-driven):** secrets scan over full git history — any hit *rotated*, never deleted (70% of 2022's leaked keys were still live in 2025) · **logged-out probe** of every endpoint/table/bucket, expecting denial (Tea; Lovable CVE-2025-48757) · database rules verified with the platform's own linter · backup on + **one real restore performed** · spend caps + billing alerts on every metered API · monitoring receives a deliberate test error · production smoke test of the golden path · **working contact/feedback route verified** (also the data-deletion request path) · **collects personal data? ⇒ privacy policy + terms + deletion route generated** · **closed-loop audit**: every plan item and backlog entry done or explicitly deferred with a reason · **converge**: reconcile `.forge/` against actual code, both directions · four-question retro (shipped / broke / differently / deferred).

**Extended (first public launch / bigger releases):** rate limiting on auth + expensive endpoints · dependency audit + unused-dep removal · TODO/mock/dead-code sweep · legacy-data purge (old buckets, dev DBs, seeded PII) · prompt-injection trifecta review (untrusted content + private data + outbound channel; agent creds read-only) · **adversarial code-review pass** — fresh-context subagent over the full diff (Kiro's outages came from skipped review; specs don't substitute) · cost audit of every service signed up during build · README verified from a clean clone · platform-trust check (verify auth yourself even on "handled" platforms).

**Moradin-side outputs:** session log to `projects/<name>/sessions/` + `projects/<name>/state.md` updated (keeps `retrospect` and `learn-from-sessions` fed after `ship` retires) · lessons → `memory/lessons/`.

### Stage 7 — Review (`/moradin:review`) — the loop-closer

The stage that consumes the Success Contract. Runs when the operator returns, when the dispatcher sees `measure.md`'s review date has passed, or on demand:

1. Pull actuals from the instrumentation wired in Build; compare against the contract's targets and kill threshold.
2. Route on the result, explicitly: **continue** (targets trending — pick next milestone from backlog, re-enter Build) · **pivot** (kill threshold hit but the problem still real — Amendment back through Define) · **stop** (kill threshold hit, thesis dead — close the project cleanly, capture the lesson; a clean kill is a success of the process, not a failure of the operator).
3. Update the contract for the new stage (validation → launch → growth; yesterday's north star is tomorrow's vanity metric) with a fresh review date. [02]

This is also the v1→v2 re-entry: shipped projects re-enter the pipeline here, not at Define.

## `.forge/` state spec (in the target project)

| File | Written by | Holds | Cap |
|---|---|---|---|
| `journal.md` | Every stage | Current stage · last action · next action, in plain language — read FIRST by the dispatcher; the 3-week-absence resume point | 3 lines |
| `profile.md` | Calibrate | Working style, profile level | ⅓ screen |
| `plan.md` | Define | Who/problem, job story, riskiest assumption, skeleton, cut, milestones | 2 pg L / 5 pg F |
| `measure.md` | Measure | Success Contract (incl. traffic answer, review date) | 1 page |
| `backlog.md` | All stages | id · title · status (idea/planned/building/done/deferred) · note | grows |
| `research/<topic>.md` | Research | Options, verification results, sources | 1 screen each |
| `decisions.md` | Decide | Nygard-lite records, append-only | ~15 lines each |
| `checklist.md` | Build | Slices: source refs, executable check, `[you]` setup tasks, status | 1 screen |

**Steering layer:** the target project's own `CLAUDE.md`/`AGENTS.md` (always loaded by the tool) is the standing context — product one-liner, stack, commands, conventions. The forge creates it if missing; Close keeps it current. No duplicate steering file. [01]

**Hooks:** the forge installs its non-negotiables into the target project's hook config (pre-commit secrets scan; prod-connection-string block; slice-check stop-hook) during the first Build. [01, 05]

## Changes to the Moradin repo

| Area | Change |
|---|---|
| `skills/forge/` | **New** — dispatcher: journal-first routing, quick path, amendment, calibration |
| `skills/define/` `measure/` `research/` `decide/` `close/` `review/` | **New** — stage skills |
| `skills/build/` | **Rewritten** — slice loop, `[you]` setup tasks, hook installation |
| `skills/ship/` | **Retired** — session capture moves into close |
| `capture` `recall` `audit` `stats` `retrospect` `learn-from-sessions` | **Kept** — memory-maintenance layer; retrospect now feeds on close's session logs |
| `skills/init/` | **Updated** — presents the forge as the front door |
| `templates/` | **Add** — journal, profile, plan, measure, backlog, decisions, checklist templates |
| `memory/references/forge_tool_defaults.md` | **New** — dated tool recommendations (analytics, monitoring, hosts) cited by skills; refreshed by `audit_references.py` (Law 9) |
| `docs/forge_research/` | **Added** — evidence base 01–05 |
| `CLAUDE.md` / `AGENTS.md` / `README.md` | **Rewritten** — forge identity |

## Build order

- **Phase 1 — Foundation.** ✅ Built + dogfooded 2026-08-09 (memecoin-scout: idea → live product in one day; session log + 2 lessons harvested).
- **Phase 2 — Research engine.** ✅ Built 2026-08-09: research (now a 9-check list — data-shape verification added from the dogfood lesson) + decide (constraints-first, clickable options page, supersede-only records). Dogfood pending on the next real decision set.
- **Phase 3 — Build, close, review.** ✅ Built 2026-08-09: build rewritten (slice loop, executable checks, data-shape pre-flight, [you] tasks), close (evidence-derived Core/Extended + retro-to-lessons), review (continue/pivot/stop), ship retired. Dogfood pending: run close + review on memecoin-scout after its 24h window.
- **Phase 4 — Launch polish.** Identity docs + README, GitHub-issues sync, shareable packaging (zip/plugin) with FEEDBACK.md, calibration reading `memory/preferences/`.

Each phase ends with a dogfood pass on a real project before the next begins.

## Interaction surface (decided 2026-08-09)

Moradin stays **agent-native**: a plug-in to whatever agent the operator already uses (Claude Code, Hermes, Cursor, Gemini CLI — the SKILL.md format is the portability layer), never a hosted website. No server, no accounts, no synced state; the files stay on the operator's disk and their agent drives.

The **adaptive UI** is the HTML layer on top: stage skills generate local, single-file, interactive pages — cards, radio/checkbox selections, a sticky toolbar, an **export button** that produces a small JSON/text blob the operator hands back to the agent (paste or file). Selection-based moments get clickable surfaces; everything else stays conversational. This extends `operator_review_as_html` from review-only to review-and-choose.

**First shipped surface: the Measure stage's Success Contract page** (built 2026-08-09 during the memecoin-scout dogfood, now standard in the measure skill) — dogfooding proved the need same-day: a chat read-back of contract numbers didn't land; a clickable page did. **Phase 2 pilot: the Decide stage options report** — purely selection-based (3 options + a default per decision): click your choices across all decisions, export once, the agent writes the decision records. Later candidates: define plan read-back (accept/edit per section), close checklist, review stage's continue/pivot/stop. Claude-artifact live capabilities can come at launch for claude.ai users, but the local-file version is the contract — it must work identically for a Hermes or Cursor operator.

## Open items

- **Naming** — stage verbs provisional; confirm before Phase 1.
- **GitHub sync mechanics** — `backlog.md` ↔ issues via `gh`; truth direction on conflict. Launch-phase.
- **Distribution** — plugin vs copy-in zip.
- **Auto mode** — `auto` argument in v0.3 or v0.4; if shipped: never auto-merges, stops on enumerated blockers.
- **Benchmarks table** — honest-ranges reference (with survivorship caveats) as a memory reference.
- **Hook portability** — hooks are Claude Code-native; degrade gracefully (prose + checks only) on other tools.

## Evidence base

`docs/forge_research/01_frameworks.md` · `02_metrics.md` · `03_definition.md` · `04_decisions.md` · `05_qa_launch.md` — primary-source URLs with verification dates. Bracketed numbers cite these. Gap-check pass: 17 findings (3 critical) folded into this version — notably the Review stage, the quick-path definition, `[you]` operator setup tasks, `journal.md`, the amendment route, hook enforcement, legal basics, the traffic question, and release-significance scoping for Close.
