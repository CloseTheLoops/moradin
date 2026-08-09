# Research: technology decisions & verification (Research + Decide stages)

_Commissioned 2026-08-09 for the Forge redesign. Agent-produced deep research._

## Key findings

1. **ADRs work, but the dominant failure mode is abandonment, not bad format.** A 2023 MSR study of GitHub (IEEE) found ADR adoption low but rising, ~50% of repos with ADRs contain only 1–5 records — teams pilot, then stop. Stale "Accepted" ADRs are worse than none. *Forge implication:* the decision log must be a **byproduct of the DECIDE stage, not a separate chore** — written automatically at decision time, each record carrying an event-based review trigger ("revisit if pricing changes / if we exceed N users"), not a calendar date.

2. **The minimal viable format is 5 fields.** Nygard's original (2011): title/status/context/decision/consequences. MADR adds "options considered" with pros/cons. Most real repos use plain Nygard. *Forge implication:* Nygard-lite plus one line per rejected option ("why not") — the why-nots prevent relitigating.

3. **"Boring technology" is a budget, not an aesthetic.** McKinley (2015): a team gets ~3 "innovation tokens"; new tech costs one because its failure modes are unknown-unknowns. *Stronger* in the AI era: boring stacks (Postgres, mainstream frameworks) are massively represented in training data, so AI agents build more reliably on them. *Forge implication:* default recommendations boring; DECIDE literally counts tokens — "you've already spent one on X."

4. **Community health must be read with time-decayed signals; stars are the least meaningful metric.** Use human commits in a rolling 90-day window, contributor concentration over the *last 12 months*, issue first-response time, release cadence. Bus-factor-1 is not automatically fatal (curl computes as 1); risk multiplier, not veto.

5. **Free-tier rug-pulls and usage-billing blowups are a documented, recurring pattern.** Heroku killed free tier Nov 2022; Railway mid-2023; **PlanetScale removed Hobby April 2024** with ~30 days notice; **Glitch ended app hosting July 2025**; Vercel repriced four times since 2024. Usage billing without caps: **Netlify $104,500 bill** for a free-tier static site under DDoS (Feb 2024, waived after HN storm); **Cara's $96,280 Vercel bill** on going viral (June 2024). *Forge implication:* "free tier + auto-scaling usage billing + no hard spend cap" is a **named risk category** the research agent must flag; pricing-change history in the last 24 months is a mandatory check.

6. **Choice overload is real under the Forge's exact conditions — show 3 options with a default.** Scheibehenne 2010 meta-analysis: mean effect near zero; Chernev 2015: overload *does* appear under choice-set complexity, task difficulty, preference uncertainty — a non-expert choosing a database, exactly. Maximizing is a trap for reversible choices (Iyengar/Wells/Schwartz 2006: maximizers got ~20% better outcomes, were less satisfied, second-guessed more). *Forge implication:* 3 options, one marked "recommended," satisfice on two-way doors.

7. **Fast deciders use MORE information, not less — research becomes procrastination when it stops being real-time.** Eisenhardt (AMJ 1989): fast decision-makers used more real-time information, considered more alternatives *simultaneously*; fast-deciding firms outperformed. Combined with one-way/two-way doors: classify by **exit cost**. Data model, payment provider, auth = expensive doors; a UI library behind an abstraction = cheap doors. *Forge implication:* RESEARCH gets a timebox scaled to door type; cheap-door decisions get minutes, not days.

8. **AI agents hallucinate the artifacts they recommend — verification is not optional.** USENIX Security '25 (Spracklen et al.): 19.7% of LLM-recommended packages didn't exist (205k unique fake names); 2026 re-run on frontier models still 4.6–6.1%. "Slopsquatting": an existing package with that name may be attacker-registered bait. *Forge implication:* every package, API, and model ID in an options report must pass a live existence check against the official registry/docs.

9. **Weighted decision matrices mostly launder predetermined choices.** Weights assigned after seeing options reverse-engineer the answer; the value is stating criteria *before* advocacy. *Forge implication:* DECIDE elicits the operator's constraints (budget, scale, skills) **before** showing options; skip fake-precision scoring.

## Proposed verification checklist for research agents

For every option in the report:

1. **Existence check:** fetch the official registry page (npm/PyPI) for every package name; official docs for every API endpoint and model ID. No claim from memory. Record URL + fetch date.
2. **Pricing check:** fetch the vendor's live pricing page today. Record: free-tier limits, credit-card requirement, whether **hard spend caps exist**, overage behavior (throttle vs. bill).
3. **Pricing-history check:** search "<vendor> pricing change" over the last 24 months. Any repricing, tier removal, or acquisition → risk line.
4. **Maintenance check:** last *human* commit ≤ 90 days; ≥ 1 release in last 12 months; changelog updated; no sunset announcement. Contributor concentration over last 12 months, not lifetime.
5. **Adoption trend:** download/usage trend direction over 12 months — direction beats magnitude; never cite stars as evidence.
6. **Responsiveness:** median time-to-first-response on recent issues; critical issues untriaged > 30 days is a flag.
7. **Lock-in probe:** name the concrete exit path (data export format, open protocol, self-host option, nearest substitute); estimate migration effort in days.
8. **Provenance discipline:** every factual claim carries a source URL + date; anything unverifiable is labeled **UNVERIFIED**, never silently included.

## Proposed decision-log format

One `decisions/NNN-slug.md` per decision (or one `DECISIONS.md` appended):

```markdown
# 007: Postgres on Neon for the app database
Date: 2026-08-09 | Status: accepted        (later: superseded-by: 019)
Door: two-way (exit ≈ 1 day: pg_dump → any Postgres host)
Innovation token spent: no

## Context
2-3 sentences: what forced this decision, key constraints (budget, scale, skills).

## Decision
One sentence, active voice.

## Why
- 2-3 bullets, tied to the operator's stated constraints.

## Rejected
- Supabase — one line why not.
- SQLite/Turso — one line why not.

## Verified
Pricing page + limits as of 2026-08-09 (URL). Spend cap: yes/no.

## Revisit when
Event triggers only: "pricing changes", ">10k users", "need multi-region".
```

Binding-until-reopened is enforced by status: the skill refuses to relitigate an `accepted` record unless the operator explicitly supersedes it.

## Options report format (for the DECIDE stage)

- **Exactly 3 options + 1 recommended default** (more only if the operator asks).
- Per option: one-line what-it-is; **cost now and at 10x scale**; spend-cap yes/no; maintenance signals (90-day commits, release cadence, response time); exit cost in days; door type; **"pick this if…"** sentence; known incidents/repricings; verified-on date.
- Close with: recommendation + why (mapped to pre-stated constraints), and one line listing what was ruled out before the top 3.

## Sources

- Nygard — https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions (2011)
- ADR templates — https://adr.github.io/adr-templates/ ; MADR paper https://ceur-ws.org/Vol-2072/paper9.pdf (2018)
- MSR ADR study — https://ieeexplore.ieee.org/document/10155430/ (2023); ECSA action research https://rebekkaa.github.io/files/2024_ECSA.pdf (2024)
- ADR staleness — https://www.javacodegeeks.com/2026/05/the-reason-most-architecture-decision-records-get-written-and-never-read-is-architectural-not-cultural.html (May 2026)
- McKinley — https://mcfunley.com/choose-boring-technology (2015)
- Open-source health metrics — https://nesbitt.io/2026/05/09/the-mismeasure-of-open-source.html (May 2026); https://dasroot.net/posts/2026/02/github-star-counts-meaning-project-popularity/ (Feb 2026)
- Netlify $104.5k — https://serverlesshorrors.com/all/netlify-104k/ ; https://news.ycombinator.com/item?id=39520776 (Feb 2024)
- Cara $96k — https://www.infoq.com/news/2024/06/vercel-serverless-scale-expenses ; https://news.ycombinator.com/item?id=40612981 (June 2024)
- Heroku — https://help.heroku.com/RSBRUH58/removal-of-heroku-free-product-plans-faq (2022); Railway — https://www.saaspricepulse.com/blog/railway-pricing-history (2023); PlanetScale — https://www.srvrlss.io/provider/planetscale/ (April 2024); Glitch — https://www.theregister.com/2025/05/23/glitch_app_hosting_gone/ (May 2025); Vercel — https://bex.co/blog/2026/08/04/vercel-four-repricings-hosted-platform-bill-shock (Aug 2026)
- Choice overload — https://academic.oup.com/jcr/article-abstract/37/3/409/1827647 (2010); https://myscp.onlinelibrary.wiley.com/doi/abs/10.1016/j.jcps.2014.08.002 (2015)
- Maximizers — https://business.columbia.edu/sites/default/files-efs/pubfiles/874/874.pdf (2006)
- Eisenhardt — https://journals.aom.org/doi/abs/10.5465/256434 (1989)
- Package hallucinations — https://www.usenix.org/publications/loginonline/we-have-package-you-comprehensive-analysis-package-hallucinations-code (USENIX 2025); https://arxiv.org/abs/2605.17062 (2026)
- Weighted-matrix critique — https://www.decision-mastery.com/articles/weighted-decision-making ; https://airfocus.com/blog/weighted-decision-matrix-prioritization/
