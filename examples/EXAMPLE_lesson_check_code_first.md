---
name: check_code_first
description: When symptoms look like an external service is broken, verify our own code isn't the cause first
topics: [workflow, tooling]
applies_to: [universal]
type: lesson
date: 2026-05-20
---

# Check our own code before blaming the service

When something looks broken externally — "the API is throttling us", "the database is overloaded", "the LLM is hallucinating" — verify our own code first. Bias toward "external problem" delays root-cause discovery.

## Why

During PART 7 of a major build, we lost ~3 hours blaming Google's Gemini API for what turned out to be 4 of 6 of our own issues:

1. "Google project throttle" — actually JSON truncation from `max_output_tokens=4000` cutting responses mid-content.
2. "503 storm = backend overloaded" — partly real, mostly our parse failures.
3. "Per-project ceiling ~17 r/s" — actually AFC amplifying each call 10x.
4. "Worker stall = rate review" — actually as_completed slowdown at 397k futures (Python issue).

The pattern: cost rises without progress → "throttle" symptoms → blame service. But the actual fault was in OUR code 4 of 6 times. AFC config, max_output_tokens vs response size, futures-loop iteration, lock contention, dedup queries — all checkable in 30 seconds.

## How to apply

When something looks externally broken, run this checklist BEFORE escalating to "service issue":

1. **AFC / automatic function calling enabled?** If using google-genai SDK, AFC defaults ON and amplifies calls 10x.
2. **`max_output_tokens` vs response size?** If LLM responses are getting truncated, parse failures look like model failures.
3. **Futures loop iteration order?** as_completed slows at large N. Check telemetry honesty.
4. **Lock contention?** Check thread/process locks if throughput stalls.
5. **Dedup queries?** SELECT before INSERT can be slow if missing indexes.

Only after the checklist comes up clean: escalate to service issue.

The discipline: **check first, blame second.**
