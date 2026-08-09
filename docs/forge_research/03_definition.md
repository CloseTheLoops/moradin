# Research: product definition methods (Define stage)

_Commissioned 2026-08-09 for the Forge redesign. Agent-produced deep research._

## Key findings

1. **The dominant failure mode is skipping "who/problem," not skipping process.** CB Insights' postmortem datasets put "no market need" at 35% (2019 analysis of 101 postmortems), 42% (2021, 110+), and its 2024 update of 431 VC-backed shutdowns attributes ~43% to poor product-market fit. Nine of the top 20 failure reasons are customer-related; only two are money. *Forge implication: Define's first job is forcing "who has this problem and how do I know" before any feature talk.*

2. **MVP ballooning is a sequence problem, not a willpower problem.** The Riskiest Assumption Test critique of Lean Startup: classic build-measure-learn still starts with *build*, so founders overbuild before learning; RAT flips to learn/test-then-build. Practitioner accounts of scope creep consistently describe "a string of reasonable-sounding small additions." Common heuristic: 3–5 must-have features; beyond that "you're building version 1, not an MVP." *Forge implication: the MVP cut must be anchored to an explicit riskiest assumption and a hard constraint, or it will drift.*

3. **Method-by-method verdicts for solo/non-expert builders:**
   - **JTBD**: full JTBD/ODI is usually "functionally ornamental"; vague jobs ("save time") are its standard failure. The beginner-usable artifact is Klement/Intercom's **job story**: *When ___, I want to ___, so I can ___*. Take the sentence, skip the framework.
   - **Story mapping (Patton)**: replaces the "flat backlog… bag of context-free mulch" with a left-to-right user journey backbone, then slice horizontally — the top slice IS the MVP cut. The single best story-generation mechanism for beginners: "list the steps of one successful use" requires zero PM vocabulary. Skip the workshop apparatus; keep backbone-then-slice.
   - **Opportunity Solution Trees (Torres)**: keep one directional outcome + naming the opportunity before the solution; drop the maintained tree (labor model incompatible with solo builders — Torres herself flags the pre-launch variant).
   - **Shape Up**: **appetite** is the most portable concept in the survey — budget time and let scope flex, instead of estimating scope. Basecamp's own appendix says tiny teams should "throw out most of the structure" but keep appetite, shaping, knowns-vs-unknowns.
   - **Pre-mortem (Klein)**: the only method with controlled-study backing — prospective hindsight improves generation of correct reasons by ~30% (Mitchell/Russo/Pennington 1989; Klein HBR 2007). Cost: one question. Include always.
   - **MoSCoW**: fails when there's no hard deadline (Must-list expands); works only paired with a constraint (appetite). Use binary in/now-out; Should/Could adds nothing solo.
   - **RICE**: false precision; requires data a pre-launch beginner cannot have. Skip at every profile.

4. **Sequencing consensus: certainty-first, customer+problem together, solution late.** Maurya: fill the Lean Canvas in order of certainty — Customer Segment + Problem together first, solution only after value proposition. Torres converges independently. Since Forge users *arrive* with an idea, back the idea into who/problem before letting it forward into features. Beginner stalls are "intelligence applied too early": edge cases, tool choice, positioning refined before anything ships. *Forge implication: Define needs an appetite itself (timebox the conversation), draft-first interaction (Forge proposes, user corrects — never a blank page), explicit permission for good-enough v0 answers.*

5. **Existing AI tools validate the pipeline but warn about weight.** ChatPRD (100k+ users): guided prompts → structured PRD in ~20 minutes — closest flow analog, but outputs a document, not a build plan. Kiro and Spec Kit run requirements → design → tasks; recurring criticism is process weight ("a sea of markdown documents") and spec/code drift. BMAD is the cautionary tale: a real brownfield user reported a **500+ page brief** and ~$847/month token burn. *Forge implication: nobody has nailed calibrated, brevity-capped definition for non-experts — that's the open slot. Hard-cap plan.md length and question count.*

## Proposed Define-stage flow (Light vs Full)

Both profiles: Forge drafts every artifact and asks the user to correct it (never open-ended "write your user stories"); output is one plan.md with a hard length cap (~2 pages Light, ~5 Full).

**Light (6 steps, target 10–15 min):**
1. **Who + problem, together** (Maurya): "Finish this: *[specific person] struggles to [specific thing]*." Reject "everyone"/"save time" phrasing.
2. **Job story** (Klement): Forge drafts *When ___, I want to ___, so I can ___*; user edits.
3. **Riskiest assumption** (RAT): "What has to be true for anyone to use this? What's the ONE thing v1 must prove?"
4. **Walking skeleton** (Patton): "Walk me through one successful use, step by step." Each step becomes a story; cap ~5–7.
5. **Appetite + cut** (Shape Up + binary MoSCoW): "How much time before something is usable — a weekend, two weeks?" Then in/not-now for each skeleton step against that appetite. Not-now list is written down (parking, not deleting).
6. **Premortem-lite + milestone** (Klein): "It's three weeks from now and you abandoned this — why?" → one mitigation. Milestone 1 = skeleton works end-to-end.

**Full adds (12–14 steps, ~45 min):**
- 2–3 named user types; pick the primary (persona-lite).
- **Directional outcome + 2–3 opportunities** before solutioning (Torres pre-launch variant).
- "How do you know this problem exists?" — evidence check; if none, flag validation as milestone 0 (the 42% failure mode).
- Acceptance criteria per story ("how will you know this step works?").
- Explicit **non-goals** section.
- Full premortem: 3–5 failure reasons → each mapped to a mitigation or milestone.
- 2–3 milestones, each with an appetite and a demoable outcome; a single success metric.

**Never, at any profile:** RICE scoring, opportunity tree maintenance, betting tables, Should/Could tiers, effort estimates.

## Sources

- CB Insights failure reports — https://www.cbinsights.com/research/report/startup-failure-reasons-top/ ; https://www.cbinsights.com/research/startup-failure-post-mortem/
- Basecamp, *Shape Up*, "Adjust to Your Size" — https://basecamp.com/shapeup/4.1-appendix-02
- "Why Shape Up might not be for you" — https://www.leadinginproduct.com/p/you-are-not-37signals (2024)
- Torres, discovery in early-stage startups — https://www.producttalk.org/discovery-in-startups/
- Klement, job stories — https://jtbd.info/designing-features-using-job-stories-41d20fc7ade6 ; Intercom — https://www.intercom.com/blog/accidentally-invented-job-stories/
- JTBD limitations — https://shahmm.medium.com/exploring-the-limitations-of-the-jobs-to-be-done-framework-ebd387fd12e0
- Klein, premortem HBR 2007 — http://homepages.se.edu/cvonbergen/files/2013/01/Performing-a-Project-Premortem.pdf ; Veinott/Klein ISCRAM 2010 — https://idl.iscram.org/files/veinott/2010/1049_Veinott_etal2010.pdf
- Maurya, Lean Canvas fill order — https://medium.com/lean-stack/what-is-the-right-fill-order-for-a-lean-canvas-f8071d0c6c8c
- RAT — https://mindsea.com/riskiest-assumption-test/
- Fowler site, SDD tools — https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html (2025)
- BMAD issue #446 (500+ page brief) — https://github.com/bmad-code-org/BMAD-METHOD/issues/446
- ChatPRD — https://www.chatprd.ai/
- Analysis paralysis threads — https://www.indiehackers.com/post/analysis-paralysis-the-tyranny-of-choice-and-the-problem-with-perfection-96126774fb ; https://news.ycombinator.com/item?id=17710707
- Patton via Mind the Product — https://www.mindtheproduct.com/getting-started-with-user-story-mapping-jeff-patton/
