---
name: close_every_loop
description: Every feature needs a consumer + an exit query that proves the loop ran end-to-end
topics: [workflow, harness]
applies_to: [universal]
type: principle
---

# Close every loop — no dead ends

Every feature emits data, but the data only matters if something CONSUMES it. Every loop needs a consumer + an exit query that proves the loop fired.

## Rationale

Building producer-only features creates phantom infrastructure: code that runs, writes data, and nobody reads. Months later, you notice the table has 50k rows and zero downstream queries. Was the producer ever right? You don't know — nothing consumes it.

The exit query is the proof. If you can't write a SQL or grep query that demonstrates "this feature ran and produced X within window Y," the feature isn't closed.

## How to apply

Before declaring a feature done, check:

1. **Who's the consumer?** Specifically. Not "future calibrator might use this" — a named consumer that exists today.
2. **What's the exit query?** A check you can run that returns proof the loop fired. Examples: `SELECT COUNT(*) FROM eval_runs WHERE worker='reader' AND run_ts > NOW() - 8d`. Or a grep.
3. **Is the exit query in CI / a watcher / a dashboard?** If not, the closure is verbal, not enforced.

If consumer doesn't exist, don't ship the producer. Build the consumer first.
