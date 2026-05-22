---
name: moradin-learn-from-sessions
description: Extract user preferences from accumulated Claude Code session history. One-time bootstrap that mines your past corrections, preferences, and lessons into reviewable candidates.
---

# moradin:learn-from-sessions

Mine your accumulated Claude Code session history for implicit preferences. Surfaces candidates for review; operator decides what becomes memory.

## When to invoke

`/moradin:learn-from-sessions [--since 180d] [--project <name>]`

Best run ONCE at first-time setup, then again periodically (monthly or quarterly) to catch new patterns. For per-session incremental capture, use `/moradin:ship` after each session.

## What you do

1. **Set up.** Confirm `ANTHROPIC_API_KEY` is in env. If not, ask operator to set it or use `--local-only` mode.

2. **Discover sessions.** Run `scripts/session_scanner.py --since 180 --count-only` to show operator how many sessions/turns will be scanned.

3. **Estimate cost.** Roughly $0.001 per turn for pre-filter + $0.01 per extracted candidate. For ~10k turns: typically $8-15.

4. **Confirm with operator** before running the expensive extraction.

5. **Run extraction.**
   ```bash
   python scripts/extract_preferences.py --since 180 --min-count 5 --min-sessions 3
   ```
   This:
   - Scans matching JSONL files
   - Pre-filters with regex (corrections / preferences / lessons signal patterns)
   - Classifies filtered turns with Haiku (cheap)
   - Extracts structured candidates with Sonnet (strong)
   - Clusters similar candidates
   - Applies stability thresholds (count ≥ 5, sessions ≥ 3, confidence ≥ 0.6)
   - Writes review file to `scratch/proposed_<date>.md`

6. **Surface results to operator.** Read the proposed file, summarize:
   - Total candidates that passed stability
   - Top 5 by occurrence count
   - Distribution: how many principle / preference / lesson candidates

7. **Walk operator through review (optional).** For each candidate ask:
   - ACCEPT → write to `memory/preferences/<title>.md` (or `principles/` or `lessons/` based on category)
   - EDIT → rewrite statement, then accept
   - REJECT → skip

8. **After approval session.** Run `python scripts/refresh_indexes.py` to update `_INDEX.md` files. Delete the review file.

## Tuning knobs

| Flag | Default | When to adjust |
|---|---|---|
| `--since N` | 180 days | Start with 180 to verify pipeline quality; expand to 365+ once trusted |
| `--min-count N` | 5 | Lower (3) if your corpus is small; raise (8-10) if you want only strongest signals |
| `--min-sessions N` | 3 | Same logic — diversity threshold |
| `--project <slug>` | (all) | Restrict to one project (e.g. `C--Users-yuezh-Documents-GodTech`) |
| `--dry-run` | off | Test the regex pre-filter without spending LLM dollars |

## Privacy

- All session reading is LOCAL (Python reads files on disk).
- LLM calls go to Anthropic API. Per Anthropic's commercial terms, API traffic is NOT used for training.
- If you need pure-local processing: set `MORADIN_LOCAL_ONLY=1` (requires Ollama installed; future enhancement).
- The script applies regex redaction for common secrets (API keys, emails, bearer tokens) before sending to LLM.

## Don't

- Don't run this without operator confirmation on the LLM spend.
- Don't auto-write extracted candidates to `memory/`. Operator reviews each.
- Don't include any candidate in `memory/` without first cleaning the title + statement.
- Don't run on a corpus you haven't redacted appropriately if it contains sensitive IP.

## Output

- `scratch/proposed_<date>.md` — reviewable candidates
- 0 or more new files in `memory/preferences/`, `memory/principles/`, or `memory/lessons/` after operator approval
- Updated `_INDEX.md` files
