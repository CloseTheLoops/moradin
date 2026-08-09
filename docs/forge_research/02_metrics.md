# Research: success metrics for solo builders (Measure stage)

_Commissioned 2026-08-09 for the Forge redesign. Agent-produced deep research; pricing verified against vendor pages on the date noted._

## Key findings

1. **The famous frameworks are mostly wrong-sized for solo builders; only "One Metric That Matters" (OMTM) and stage-based thinking fit.** North Star Metric, per Amplitude's own playbook co-author John Cutler, is deliberately *not* directly actionable ("If you can move your North Star directly, it's probably not a good North Star") — it exists to align teams around input metrics, which presumes a team. Google HEART was published as "Measuring the User Experience on a **Large Scale**" (Rodden, Hutchinson, Fu, CHI 2010) — its Happiness dimension needs survey volume a week-old indie app doesn't have. AARRR (Dave McClure, 2007) is a useful funnel vocabulary but has a documented failure mode: acquisition-first focus, which prompted the RARRA reordering (Petit/Papp, 2017) putting retention first because acquiring into a leaky bucket just accelerates churn. OKRs carry real rollout overhead (one documented case: 18 months to integrate) and even proponents concede poor fit for tiny/early teams. Lean Analytics (Croll & Yoskovitz, 2013) is the one framework explicitly designed around stage: pick ONE metric per stage (Empathy → Stickiness → Virality → Revenue → Scale) and graduate on evidence. **Forge implication:** teach AARRR only as *vocabulary*, use Lean Analytics stages as the *selector*, output one OMTM — not a North Star program, not OKRs.

2. **The core failure mode to design against is vanity metrics — and it's stage-relative.** Croll/Yoskovitz: "Vanity metrics always go up — actionable metrics drive decisions" (total signups, page views, downloads, followers). MicroConf's guidance for bootstrappers repeats the same warning and adds a second trap: tracking everything → analysis paralysis or abandonment. Critically, "yesterday's north star becomes tomorrow's vanity metric" — total waitlist signups is a *valid* metric pre-build and a vanity metric post-launch. **Forge implication:** the artifact must carry an expiry/review date and a stage label, and the skill should actively reject cumulative "total X" metrics as the primary number.

3. **Pre-build validation has usable pass/fail thresholds, but signup counts overstate demand.** Median landing-page conversion is **6.6%** across industries (Unbounce, 41,000 pages / 464M visitors, Q4 2024). Waitlist pages: roughly **2–5% typical, 8–20% strong, 25%+ elite** (Flowjam/LaunchList aggregations; ranges vary by traffic quality — treat as soft). CB Insights' classic finding that **42% of startups fail from no market need** is the motivation for smoke-testing at all. But indie-hacker practice (Indie Hackers threads, 2021–2025) consistently notes email signups ≠ willingness to pay; the stronger pre-build signals are pre-orders, "willing-to-pay beta tester" conversations, and fake-door clicks on a price. Post-use, the Sean Ellis test (**≥40% "very disappointed"**, from ~100-startup analysis) remains the standard PMF gate in 2025-2026 material. **Forge implication:** Measure stage should force a *pre-build* metric (e.g. "≥5% of targeted visitors join waitlist, and ≥5 people say they'd pay") before the tool-research stage unlocks.

4. **What successful solo builders measure changes sharply: week 1 = activation, month 3 = retention + revenue.** Week-1 practice: signups, signup→activation rate (% reaching the "aha" action within 7 days — under ~20% signals broken onboarding), and qualitative support/feedback themes. Month-3 practice: D30/month-3 retention (~34% month-3 retention cited as a median for surviving products — single-source, treat as anecdote) and, for anything paid, MRR. Rob Walling's bootstrapper guidance (MicroConf / *The SaaS Playbook*): MRR as the north star plus 5–10 directly-correlated input metrics (trial→paid, churn, demos). **Forge implication:** the artifact needs two time horizons — a launch-week check and a month-3 check — with different metrics, not one static dashboard spec.

5. **Published benchmarks skew optimistic (survivorship bias) — cite ranges, not points.** Consumer app retention medians (Adjust-derived, 2025-2026): **D1 25–26%, D7 11–13%, D30 5–7%**; but the median *catalog* app retains **under 4% by D30**, i.e., published benchmarks over-represent winners. Category spread is huge (social D30 15–20% vs e-commerce 3–6%). SaaS conversion: freemium→paid **3–5% good, 8–12% great** (Userpilot/First Page Sage); opt-in free trial ~**8–18%**, credit-card-required trial ~**31–49%** (1Capture 10K-company analysis; ChartMogul's SaaS Conversion Report is the most transparent primary source). All third-party aggregations — flag as directional. **Forge implication:** ship a small benchmarks reference table with explicit "top-quartile vs median vs catalog-median" caveats, and default guidance of "beat your own last month" over "hit the industry number."

6. **Instrumentation is effectively free at solo-builder scale, but defaults matter for non-technical operators.** Verified against vendor pages 2026-08-09: PostHog's free tier (1M events + 5K session replays/mo) is the most generous but its UI is the most complex; Umami Cloud's Hobby plan is free (vendor FAQ confirms; the 100K events / 3 sites / 6-month retention figures come from third-party 2026 sources — **unverified against vendor, re-check**); Vercel Web Analytics Hobby gives 50K events/mo but only a 1-month reporting window and **no custom events** — pageviews only, so it can't measure activation. GA4 is free but the worst fit for this audience: 2/14-month event-data retention, consent-mode requirements for EEA traffic, compliance overhead. Plausible has **no free tier** (30-day trial, then $9/mo, 10K pageviews) but the simplest mental model. **Forge implication:** default to one privacy-first tool with custom-event support (PostHog for product metrics, Umami for lighter web metrics), installed as a one-snippet step the Forge can scaffold.

## Proposed Measure-stage output artifact

A one-page **Success Contract** (`measure.md` in the project), written before any tool research:

```
# Success Contract — <product>  (stage: validation | launch | growth)
Written: <date>   Review due: <date +30d>

## The one metric that matters
Metric: e.g. "% of signups who create their first X within 7 days"
Target: 30%   |   Kill/pivot threshold: <10% after 100 signups
Measured by: PostHog custom event `first_x_created` / signup count

## Supporting signals (max 3)
1. Weekly returning users (D7 retention) — target 15% — PostHog retention view
2. Waitlist→signup conversion — target 25% — email tool + PostHog
3. "Very disappointed" score (ask 10 users at week 4) — target 40% — manual survey

## What we will NOT count as success
Total signups, page views, social followers, stars.

## Instrumentation checklist
[ ] analytics snippet installed  [ ] 1-3 custom events named + firing  [ ] weekly 10-min review scheduled
```

Justification: one OMTM with a stage label (findings 1, 2); an explicit kill threshold — Lean Analytics' "draw a line in the sand" — turns the number into a decision, which is what separates actionable from vanity (finding 2); max three supporting signals prevents the over-measurement failure MicroConf documents (finding 4); the anti-metrics section guards against the dominant failure mode (finding 2); the "measured by" column forces instrumentation to be decided *before* code exists, so events get named during the build rather than bolted on; the 30-day review date operationalizes "yesterday's north star becomes tomorrow's vanity metric." The Sean Ellis question gives non-technical builders one metric that needs zero instrumentation.

## Instrumentation comparison table

| Tool | Free tier (verified 2026-08-09) | Custom events (needed for activation) | Setup for vibe-coded app | Privacy/GDPR |
|---|---|---|---|---|
| **PostHog** | 1M events/mo + 5K replays, 1-yr retention free, billing limits settable | Yes, core feature | 1 snippet or npm; UI is complex | EU hosting option; cookieless config possible |
| **Umami Cloud** | Free Hobby plan (vendor-confirmed); ~100K events/mo, 3 sites, 6-mo retention (3rd-party, unverified) | Yes | 1 script tag, simplest OSS option | No cookies, GDPR-friendly; self-host free (MIT) |
| **Plausible** | **None** — 30-day trial, then $9/mo (10K pageviews, 1 site, 3-yr retention) | Yes (goals) | 1 script tag, simplest hosted UI | No cookies, EU-hosted, no consent banner |
| **GA4** | Free (sampling >10M events; 2–14 mo event retention) | Yes, steep learning curve | Snippet easy; *reports* are hard | Consent banner in EEA; Consent Mode v2; worst posture here |
| **Simple Analytics** | Free plan: 30-day history, 5 sites, fair-use pageviews | Yes (events, fully on paid tiers) | 1 script tag | No cookies, EU, GDPR-clean |
| **Vercel Analytics** | Hobby: 50K events/mo, 1-mo window, collection pauses at cap | **No** on Hobby (Pro only) | Zero-effort if already on Vercel | Cookieless, privacy-friendly |

Best default: **PostHog** if the product needs activation/retention funnels; **Umami** if only traffic + a couple of goal events. Avoid GA4 for this audience; Vercel Hobby cannot measure the Success Contract.

## Sources (all checked 2026-08-09)

- Rodden/Hutchinson/Fu, CHI 2010 — https://research.google/pubs/measuring-the-user-experience-on-a-large-scale-user-centered-metrics-for-web-applications/
- Lean Analytics OMTM — https://leananalyticsbook.com/one-metric-that-matters/ ; Maurya commentary — https://medium.com/lean-stack/lean-analytics-the-one-metric-that-matters-and-other-provocations-fd3006aab17
- Amplitude North Star (Cutler) — https://amplitude.com/blog/good-bad-north-star-metric ; https://amplitude.com/north-star-hub
- AARRR vs RARRA — https://www.mindtheproduct.com/aarrr-vs-rarra-pirate-metrics-explained/
- OKR fit criticism — https://ritmoo.io/blog/why-okrs-are-a-terrible-fit-for-startups ; https://www.whatmatters.com/articles/using-okrs-to-scale-a-cautionary-tale
- MicroConf — https://microconf.com/latest/saas-lean-analytics ; https://microconf.com/latest/saas-key-metrics
- Sean Ellis 40% test — https://www.fitsignal.com/blog/sean-ellis-40-percent-test
- Landing page/waitlist benchmarks — https://landerlab.io/blog/landing-page-conversion-rate (Unbounce 6.6% median) ; https://www.flowjam.com/blog/waitlist-landing-page-examples-10-high-converting-pre-launch-designs-how-to-build-yours
- Retention benchmarks — https://vmobify.com/blog/app-retention-benchmarks ; https://mwm.ai/glossary/retention ; https://www.pushwoosh.com/blog/increase-user-retention-rate/
- SaaS conversion — https://chartmogul.com/reports/saas-conversion-report/ ; https://www.1capture.io/blog/free-trial-conversion-benchmarks-2025 ; https://userpilot.com/blog/saas-average-conversion-rate/
- Activation practice — https://www.revenuecat.com/blog/growth/activation-metrics ; https://www.lowcode.agency/glossary/activation-rate-in-startup-metrics
- Indie validation — https://www.indiehackers.com/post/validate-your-idea-with-a-landing-page-before-you-validate-your-product-917cce77e0 ; https://thegood.com/insights/smoke-testing/
- Pricing pages (fetched directly): https://posthog.com/pricing ; https://plausible.io/#pricing ; https://www.simpleanalytics.com/pricing ; https://vercel.com/docs/analytics/limits-and-pricing ; Umami: https://docs.umami.is/docs/cloud/faq

**Uncertainty flags:** waitlist-conversion "benchmarks" come from waitlist-tool vendors (conflict of interest); retention medians carry survivorship bias; Umami exact free-tier limits unverified on vendor page; "34% month-3 retention" is single-source anecdote.
