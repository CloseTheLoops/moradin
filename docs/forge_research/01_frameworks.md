# Research: AI dev process frameworks (Spec Kit, Kiro, BMAD, Claude Code, Cursor)

_Commissioned 2026-08-09 for the Forge redesign. Agent-produced deep research; sources verified at fetch time._

## Key findings

1. **Every surviving framework converged on "right-sized process" during 2025–26 — validating Forge's calibrate stage, but it must be per-task, not per-project.** Kiro added "Quick Spec" mode that auto-generates all three artifacts without approval gates; BMAD v6 rebuilt its identity around "right-sized process — simpler changes bypass deeper planning entirely" plus a "Quick Spec Flow"; Anthropic's official guidance says outright: "If you could describe the diff in one sentence, skip the plan." Birgitta Böckeler's evaluation (martinfowler.com, Oct 2025) found Kiro turned a minor bug into 4 user stories with 16 acceptance criteria — "sledgehammer to crack a nut." **Forge should adopt:** calibration as a routing decision at *every* task entry (quick path vs. full pipeline), because a one-time project-level setting repeats the mistake all three tools had to patch.

2. **The #1 documented SDD failure is markdown review burden, not bad code.** Scott Logic's hands-on Spec Kit test (Nov 26, 2025): 2,577 lines of generated markdown for one feature, 3.5 hours of artifact review vs. 15 minutes for his normal approach, ~10x slower overall, agent runtime 33m vs 8m. Böckeler: "I'd rather review code than all these markdown files." Spec Kit Discussion #1784 (Sept 2025) is literally titled "SpecKit creates the illusion of work." **Forge should adopt:** hard size budgets on every `.forge/` artifact (e.g. one screen of text per stage) and generate prose only where a human decision is encoded — never template boilerplate.

3. **Agents ignore specs; markdown is advisory, not binding.** Böckeler observed spec-kit's research step correctly identify existing classes, then the implementing agent regenerated them as duplicates. HN commenters on that article: "it would forget to create or run tests, or even implement a task." Cursor's forum has recurring bug reports of agents violating explicit rules ("Stop and Confirm Rule" ignored, thread #147589), and rules failing silently when too long or in the legacy format. Anthropic's answer is architectural, not textual: "Give Claude a check it can run" — tests, build exit codes, stop hooks, adversarial review subagents in fresh context. **Forge should adopt:** make build checkpoints and the close-stage audit *executable* (tests, scripts, screenshot diffs), not re-reading `.forge/` files; treat every markdown instruction as something the agent will eventually drop.

4. **What users genuinely keep from these frameworks: small persistent steering context + a forced clarify/interview step.** Kiro's steering files (`product.md`, `tech.md`, `structure.md`, loaded always/fileMatch/manual) are its most-praised feature; EARS-style acceptance criteria are praised for forcing edge-case decisions to surface ("what happens when a webhook arrives twice"). HN user 42point2 on Spec Kit: "The constitution that's created as the first step is valuable in its own right." Anthropic's recommended big-feature workflow is an *interview*: "Interview me in detail using the AskUserQuestion tool… then write a complete spec to SPEC.md," then execute in a fresh session. **Forge should adopt:** run define as an interview that digs into edge cases, not a form to fill; and add a small always-loaded steering layer.

5. **Task decomposition through summarization loses information — Task Master's documented flaw.** claude-task-master (r/cursor darling, ~20k+ stars) has strong adoption, but Discussion #864: a full PRD expected to yield ~100 tasks produced 10, "over 80% of the information missing," because subtasks are generated from the parent task summary, not the original PRD. **Forge should adopt:** every build slice must cite the specific define/decide sections it implements, and slice generation must re-read the source artifact, never a chain of summaries.

6. **BMAD's multi-agent role ceremony was substantially rejected; v6 is a retreat.** Issue #2003 (Mar 2026) documents: small projects taking "10 to 15 times" longer, dev agents shipping "renamed commands instead of proper fixes, useless assertions… TODO stubs checked as resolved," and a core contradiction — it claims non-technical accessibility but its architecture step "requires decisions that neither group can reliably make." A developer who built a Claude-based alternative called it "brilliant but way too complex… fighting against Claude Code's natural abilities." **Forge should avoid:** persona role-play (analyst/PM/architect/QA agents) entirely; specialized *perspectives* can be prompts inside a stage, not separate agents with handoffs.

7. **Kiro's real-world track record cuts both ways.** Praise is real (shared artifact prevents drift on multi-day features; EARS forces decisions). But: usage caps within weeks of launch (The Register, Jul 2025), and TechTarget reported internal AWS use of Kiro/Q was implicated in at least two production outages — attributed to skipped review, i.e., spec ceremony did not substitute for verification. **Forge should adopt:** the three-artifact separation (what/how/steps) is sound; the lesson is that specs don't replace review of the *code*.

8. **The "waterfall in markdown" critique is the live 2026 debate — the defensible position is specs as disposable scaffolding, not source of truth.** Marmelab's "The Waterfall Strikes Back" (Nov 2025) and its HN thread; Böckeler warns spec-as-source combines "inflexibility and non-determinism," echoing Model-Driven Development's failure. Defenders' strongest counterargument: SDD ≠ waterfall *if* the spec updates through minutes-long feedback loops. Spec Kit itself added `/speckit.converge` (assess codebase against artifacts) to repair drift. **Forge should adopt:** `.forge/` files are working memory that the close stage reconciles against reality — never claim the spec is the product.

9. **Context economy is the binding constraint the heavyweight frameworks ignore.** Anthropic's best-practices doc is organized around one fact: "performance degrades as context fills," and "bloated CLAUDE.md files cause Claude to ignore your actual instructions." Frameworks that inject thousands of instruction lines (Spec Kit constitutions, BMAD orchestration) are the direct cause of finding #3. Windsurf made the opposite bet: workflows are ≤12k chars and "Cascade will never invoke a workflow automatically." **Forge should adopt:** load `.forge/` files on demand per stage (skills-style), keep only a tiny steering core always-resident, and recommend fresh sessions between define and build.

10. **The space consolidated fast in 2026 — design for churn.** Windsurf docs now redirect to devin.ai (Cognition acquisition); Anthropic's best-practices moved to code.claude.com with new machinery (goal conditions, stop hooks, agent teams); Google shipped Conductor for Gemini CLI (Dec 2025) — a near-clone of the spec/plan/tasks pattern; OpenSpec, Agent OS v2, and OSpec all pivot to "lightweight." Nobody has won; the durable common denominator is *markdown files in the repo + explicit phases + human gates* — exactly Forge's substrate.

## What our draft is missing

- **A persistent steering layer.** Our stages are pipeline artifacts (per-effort); Kiro's most-praised feature is *standing* project context: product.md / tech.md / structure.md, always loaded. `.forge/` needs an equivalent (~1 screen) distinct from stage outputs — otherwise session #2 re-derives everything.
- **Per-task calibration re-entry.** Calibrate appears once at pipeline start. Every framework was forced to add a quick path for small changes; Forge needs a standing rule: small task → skip to build.
- **Fresh-context handoffs.** Anthropic explicitly: finish the spec, start a clean session for implementation. The Forge should prescribe when to `/clear` between stages.
- **Executable checkpoints.** Draft says "vertical slices with checkpoints" — the evidence says checkpoints must be checks the agent can *run* (test, build, screenshot), or the close stage becomes finding #3.
- **Spec-to-slice traceability** (Task Master's loss bug): slices must cite source sections and re-read them.
- **A converge/drift-repair notion in close**: reconcile `.forge/` against actual code, both directions — Spec Kit added this late for a reason.

## What to NOT do (evidenced failures)

- **Multi-file artifact cascades per feature** — Scott Logic's 10x slowdown, 3.5h markdown review; "illusion of work."
- **Relying on written rules for compliance** — Cursor rules silently ignored; agents dropped spec'd tasks. Use hooks/checks.
- **Agent personas with handoffs** — BMAD issue #2003; abandoned by its own v6 direction.
- **Forcing the full pipeline on small changes** — the universally patched mistake (Kiro Quick Spec, BMAD Quick Flow, Anthropic's skip-the-plan rule).
- **Decomposing via summary chains** — 80% information loss (Task Master #864).
- **Claiming the spec is the source of truth** — MDD-redux critique; treat specs as scaffolding with a reconciliation step.
- **Assuming spec ceremony equals accessibility for non-devs** — BMAD's core contradiction: execution still demands technical judgment. For vibe coders, Forge's decide stage should offer *triage options* (accept default / defer / ask me in plain language), not architecture questions.

## Sources

- https://github.com/github/spec-kit — repo, v0.12.x, accessed Aug 2026
- https://github.com/github/spec-kit/discussions/1784 — "illusion of work," Sept 2025
- https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html — Böckeler, Oct 15, 2025
- https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html — Nov 26, 2025
- https://news.ycombinator.com/item?id=45610996 and https://news.ycombinator.com/item?id=45798473 — HN threads, Oct–Nov 2025
- https://marmelab.com/blog/2025/11/12/spec-driven-development-waterfall-strikes-back.html — Nov 12, 2025 (HN: item?id=45935763)
- https://kiro.dev/docs/specs/ and https://kiro.dev/docs/steering/ — accessed Aug 2026
- https://www.theregister.com/2025/07/21/aws_kiro_usage_cap/ — Jul 2025; https://www.techtarget.com/searchsoftwarequality/news/366639129/ — Kiro/Q outage report
- https://github.com/bmad-code-org/BMAD-METHOD and https://github.com/bmad-code-org/BMAD-METHOD/issues/2003 — issue Mar 15, 2026
- https://code.claude.com/docs/en/best-practices — Anthropic, current as of Aug 2026
- https://forum.cursor.com/t/agent-repeatedly-ignores-user-rules...147589 and .../cursor-ignoring-cursorrules/149505 — 2025–26
- https://docs.devin.ai/desktop/cascade/workflows — Windsurf (post-Cognition), accessed Aug 2026
- https://github.com/eyaltoledano/claude-task-master + discussions/864 — PRD info-loss report
- https://developers.googleblog.com/conductor-introducing-context-driven-development-for-gemini-cli/ — Dec 2025
- https://buildermethods.com/agent-os/v2; https://github.com/ClawPlays/ospec; https://www.softwarethug.com/posts/openspec-vs-spec-kit-vs-agent-os-compared/ — lightweight-SDD wave, 2025–26
