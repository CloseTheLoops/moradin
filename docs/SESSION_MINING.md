# Session mining

Moradin can extract your implicit preferences from accumulated Claude Code session history. This document explains what that means, how it works, and how to use it.

## What it does

Your Claude Code sessions are stored at `~/.claude/projects/<project>/<session-uuid>.jsonl`. Every time you've corrected Claude ("no, do it this way"), expressed a preference ("I prefer X"), or taught a lesson ("we got burned by Y") â€” those signals are in your history.

The `learn-from-sessions` skill reads these files locally, identifies high-signal turns, asks an LLM to extract structured candidates, clusters similar candidates, applies stability thresholds, and writes a reviewable file. You approve each candidate; approved ones become real memory entries.

## Why preferences are a separate memory type

Moradin's 5 memory types:

| Type | Description |
|---|---|
| **Principles** | Universal rules. You'd advocate them to anyone. |
| **Patterns** | Reusable designs. |
| **References** | Captured external sources. |
| **Lessons** | Incident-derived rules with Why + How. |
| **Preferences** | Your personal taste. Others might disagree. |

Preferences live separately because they're personal. They guide YOUR workshop, but they're not universal truths.

## Two modes

### Mode A â€” One-time bootstrap (`/moradin:learn-from-sessions`)

Process all your existing sessions (or a time-windowed subset). Run once to bootstrap your `memory/preferences/` from accumulated history. Typical cost: $8-15 for ~10k turns.

```bash
# Via the skill (preferred)
/moradin:learn-from-sessions --since 180

# Or directly
python scripts/extract_preferences.py --since 180 --min-count 5 --min-sessions 3
```

### Mode B â€” Per-session incremental (via `/moradin:close`)

After each session ends, `/moradin:close` can process just that session's turns and add to a candidate pool. Cross-session aggregation happens later via `/moradin:retrospect`.

```bash
# At end of a session
/moradin:close

# Periodically review accumulated candidates
/moradin:retrospect --review-candidates
```

(Mode B is a Phase 2 feature; Phase 1 ships Mode A only.)

## Pipeline (Mode A)

```
~/.claude/projects/<project>/*.jsonl
     â†“ session_scanner.py â€” parse + redact + flatten
high-signal user turns (after regex pre-filter)
     â†“ Haiku (cheap classifier) â€” keep correction/preference/lesson, drop noise
filtered candidates
     â†“ Sonnet (strong extractor) â€” structured output per turn
extracted candidates ({title, statement, category, confidence, source})
     â†“ Cluster (substring + token overlap)
candidate clusters with occurrence counts
     â†“ Stability filter (count â‰¥ 5, sessions â‰¥ 3, confidence â‰¥ 0.6)
review queue â†’ scratch/proposed_<date>.md
     â†“ Operator review (ACCEPT / EDIT / REJECT each)
memory/preferences/, memory/principles/, or memory/lessons/
```

## Tuning

| Knob | Default | Effect |
|---|---|---|
| `--since N` | 180 days | How far back to look. Start small; expand once you trust the pipeline. |
| `--min-count N` | 5 | How many times a pattern must appear before it's a candidate. Lower = more candidates, more noise. |
| `--min-sessions N` | 3 | Pattern must span â‰¥ N distinct sessions. Filters one-off bursts. |
| `--project <name>` | (all) | Restrict to one project's session dir |
| `--dry-run` | off | Show what the regex pre-filter would catch without LLM calls |

## Cost expectations

Roughly:
- ~$0.001 per turn pre-filtered (Haiku)
- ~$0.01 per extracted candidate (Sonnet)
- 10k turns of 180d history â†’ ~$8-15

You'll see the cost estimate from the dry-run; confirm before the full run.

## Privacy

| Concern | How handled |
|---|---|
| Sessions contain code + IP | All file reading is local. Only the FLATTENED + REDACTED turn text goes to LLM. |
| Anthropic stores API traffic? | Per Anthropic commercial terms, API traffic is NOT used for training. ZDR available for enterprise. |
| Secrets in sessions | Regex redaction strips Anthropic/OpenAI/GitHub tokens, emails, bearer tokens before sending to LLM. Not exhaustive â€” review redaction output if needed. |
| Want fully local? | Set `MORADIN_LOCAL_ONLY=1` and have Ollama + Qwen 2.5 14B installed (Phase 2 feature; not in v1) |

## What to expect

- Your first run on real data will produce some real preferences (often 5-15 that you immediately recognize as "yes, that's me") plus some misses (correctly low-confidence stuff that gets filtered out).
- Don't aim for 100% accuracy â€” aim for "useful." Even 10 well-captured preferences is a strong starting workshop layer.
- Re-run quarterly or semi-annually. Preferences evolve; the workshop should too.

## Limitations

- Pre-filter regex is in English; sessions in other languages will need pattern adjustment
- Cluster matching is simple substring + token overlap (not embeddings) â€” may not group semantically-equivalent-but-differently-worded candidates. Embedding-based clustering is a Phase 2+ enhancement.
- Single-session corrections won't surface (deliberately â€” see stability thresholds)

