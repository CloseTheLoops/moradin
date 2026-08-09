---
name: forge_tool_defaults
description: Dated tool recommendations the Forge stage skills cite (analytics, error monitoring, uptime). Verified against vendor pricing pages 2026-08-09. Re-verify monthly via audit_references.py — skills must read this file, never hardcode these facts.
topics: [tooling, workflow]
applies_to: [universal]
type: reference
---
**Verified: 2026-08-09** against vendor pricing pages (sources in `docs/forge_research/02_metrics.md` and `05_qa_launch.md`). Skills cite this file by path. If this file is >60 days old, re-verify before recommending.

## Analytics (Measure stage)

| Default | When | Free tier (2026-08-09) | Caveat |
|---|---|---|---|
| **PostHog** | Product funnels — activation, retention, custom events | 1M events + 5K replays/mo, 1-yr retention, billing limits settable | UI is the most complex of the set |
| **Umami Cloud** | Light web metrics — traffic + a few goal events | Free Hobby plan (vendor-confirmed) | Exact limits (~100K events/mo, 3 sites, 6-mo retention) are **UNVERIFIED** third-party figures — re-check before quoting |
| Plausible | Operator wants simplest hosted UI and will pay | None — $9/mo after 30-day trial | No free tier; otherwise excellent posture |

**Avoid for this audience:** GA4 (consent-banner obligations in EEA, 2/14-month retention, hardest reports); Vercel Web Analytics Hobby (no custom events — cannot measure a Success Contract).

## Error monitoring + uptime (Build wires it, Close verifies it)

| Default | Free tier (2026-08-09) | Note |
|---|---|---|
| **Sentry** | 5k errors/mo, 1 uptime + 1 cron monitor, 30-day retention | Default; SDKs for everything |
| **UptimeRobot** | 50 monitors @ 5-min interval, email alerts | Most generous free uptime tier |
| GlitchTip | 1k events/mo hosted; self-host uncapped | Sentry-SDK compatible fallback |

**Dead — do not recommend:** Highlight.io (deprecated 2026-02-28, folded into LaunchDarkly).

**Minimum sensible setup: Sentry free + UptimeRobot free = $0/mo**, wired in the first deploy slice, verified in Close with a deliberate test error and a test downtime alert.

## The named risk category (Research stage flags this wherever found)

**Free tier + auto-scaling usage billing + no hard spend cap.** Documented: Netlify $104,500 bill on a free-tier static site (2024, waived after public outcry); Cara's $96,280 Vercel bill on going viral (2024); PlanetScale Hobby tier removed with ~30 days notice (2024); Heroku free tier killed (2022); Glitch hosting ended (2025); Vercel repriced 4× since 2024. Always record: does a hard spend cap exist, and what is the overage behavior — throttle or bill?
