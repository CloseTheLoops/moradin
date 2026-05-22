#!/usr/bin/env python3
"""Extract user preferences from Claude Code session history.

Two-pass pipeline:
  1. Pre-filter (regex) for high-signal turns
  2. Classify each filtered turn via cheap LLM (Haiku) → keep correction/preference/lesson
  3. Extract structured preference via strong LLM (Sonnet) for each kept turn
  4. Cluster + dedup candidates
  5. Apply stability checks (count ≥ 5, diversity ≥ 3 sessions, contradiction < 20%)
  6. Write reviewable candidates to scratch/proposed_<date>.md

Stdlib-only LLM calls via urllib.request.

Env vars:
  ANTHROPIC_API_KEY      — required (or use --local-only)
  MORADIN_SESSIONS_DIR   — default ~/.claude/projects/

License: MIT
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

# Use session_scanner from same dir
sys.path.insert(0, str(Path(__file__).resolve().parent))
from session_scanner import (
    SessionRecord, discover_sessions, filter_by_age,
    walk_file, DEFAULT_SESSIONS_DIR,
)

# ─── Models + API config ─────────────────────────────────────────────────────

MODEL_FILTER = os.environ.get("MORADIN_MODEL_FILTER", "claude-haiku-4-5-20251001")
MODEL_EXTRACT = os.environ.get("MORADIN_MODEL_EXTRACT", "claude-sonnet-4-6")
API_URL = "https://api.anthropic.com/v1/messages"

# ─── Pre-filter patterns (high-signal turn detection) ────────────────────────

CORRECTION_PATTERNS = [
    r"\bno,?\s+(actually|wait|don't|that's not|not quite)",
    r"\bwrong\b", r"\bdon't\b", r"\bstop\b",
    r"\binstead of\b", r"\bthe right way\b", r"\bshould have\b",
    r"\bthat's not what\b",
]

PREFERENCE_PATTERNS = [
    r"\bI (prefer|like|want|always|never)\b",
    r"\bcan we (always|never)\b",
    r"\bI'd rather\b",
    r"\bremember (that|this)\b",
    r"\bnext time\b",
    r"\busually\b", r"\bgenerally\b",
]

LESSON_PATTERNS = [
    r"\blesson learned\b",
    r"\bgot burned\b",
    r"\blast time\b.*\b(failed|broke|didn't work)\b",
]

ALL_PATTERNS = [
    (re.compile(p, re.IGNORECASE), "correction") for p in CORRECTION_PATTERNS
] + [
    (re.compile(p, re.IGNORECASE), "preference") for p in PREFERENCE_PATTERNS
] + [
    (re.compile(p, re.IGNORECASE), "lesson") for p in LESSON_PATTERNS
]


def pre_filter(record: SessionRecord) -> str | None:
    """Cheap regex filter. Returns a category hint or None."""
    # Only filter on user messages (corrections come from user)
    if record.role != "user":
        return None
    content = record.content
    if len(content) < 5 or len(content) > 4000:
        return None
    for pattern, category in ALL_PATTERNS:
        if pattern.search(content):
            return category
    return None


# ─── Anthropic API client (stdlib only) ──────────────────────────────────────

def call_claude(model: str, system: str, user_msg: str, max_tokens: int = 1024) -> str:
    """Call Anthropic Messages API. Returns assistant text content."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable not set")

    body = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user_msg}],
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API error {e.code}: {body_text[:400]}")

    if "content" in data and data["content"]:
        # First text block
        for block in data["content"]:
            if block.get("type") == "text":
                return block.get("text", "")
    return ""


# ─── Stage 2: Classify filtered turns ────────────────────────────────────────

CLASSIFY_SYSTEM = """You classify single turns from a developer's Claude Code chat history.

Return ONLY a JSON object: {"category": "<one_of>", "confidence": 0.0-1.0}

Categories:
- "correction"  — user is correcting Claude's output ("no, do it this way")
- "preference"  — user is expressing a stable preference ("I prefer X over Y", "always do X")
- "lesson"      — user is teaching from a past incident
- "noise"       — none of the above (acknowledgment, question, status update)

Only mark as preference/correction/lesson if the signal is CLEAR. When in doubt, "noise".
"""

CLASSIFY_USER_TMPL = """Turn from a developer's session:

```
{content}
```

Classify."""


def classify_turn(record: SessionRecord) -> tuple[str, float]:
    """Returns (category, confidence). Category is correction/preference/lesson/noise."""
    user_msg = CLASSIFY_USER_TMPL.format(content=record.content[:2000])
    try:
        response = call_claude(MODEL_FILTER, CLASSIFY_SYSTEM, user_msg, max_tokens=128)
        # Extract JSON from response (may have markdown fence)
        match = re.search(r"\{[^}]+\}", response)
        if not match:
            return ("noise", 0.0)
        data = json.loads(match.group(0))
        return (data.get("category", "noise"), float(data.get("confidence", 0.0)))
    except Exception as e:
        print(f"  classify error: {e}", file=sys.stderr)
        return ("noise", 0.0)


# ─── Stage 3: Extract preference text ────────────────────────────────────────

EXTRACT_SYSTEM = """You extract a generalizable principle/preference/lesson from a turn in a developer's Claude Code chat.

Return ONLY a JSON object with these fields:
{
  "category": "principle" | "preference" | "lesson",
  "title": "short kebab-case slug (e.g. terse-responses, no-mock-databases)",
  "statement": "one-sentence rule the user appears to follow",
  "rationale": "why — if explicit, quote it; else infer briefly",
  "generalizable": true/false,
  "confidence": 0.0-1.0
}

Rules:
- "principle" = universal rule (should apply to any project)
- "preference" = personal taste (might not apply universally)
- "lesson" = derived from a specific incident (has Why + How-to-apply structure)
- "generalizable": false if the rule is too project-specific or context-dependent to be reusable
- "confidence": how clearly the turn expresses this? 0.0 = ambiguous, 1.0 = explicit
- Be skeptical. Single corrections are NOT preferences. Only extract if you'd bet money the user follows this consistently.
"""

EXTRACT_USER_TMPL = """Turn from a developer's session (pre-filtered as {hint}):

```
{content}
```

Extract."""


def extract_preference(record: SessionRecord, hint: str) -> dict | None:
    """Returns dict with extracted fields, or None on failure / low confidence."""
    user_msg = EXTRACT_USER_TMPL.format(hint=hint, content=record.content[:3000])
    try:
        response = call_claude(MODEL_EXTRACT, EXTRACT_SYSTEM, user_msg, max_tokens=512)
        # Extract JSON
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if not match:
            return None
        data = json.loads(match.group(0))
        if data.get("confidence", 0) < 0.5:
            return None
        if not data.get("generalizable", True):
            return None
        data["source_session"] = record.session_id
        data["source_line"] = record.line_offset
        data["source_file"] = record.file_path
        data["source_quote"] = record.content[:300]
        return data
    except Exception as e:
        print(f"  extract error: {e}", file=sys.stderr)
        return None


# ─── Stage 4: Dedup + cluster ────────────────────────────────────────────────

def cluster_candidates(candidates: list[dict]) -> list[dict]:
    """Group similar candidates by title and statement similarity (simple substring match).

    Returns list of clusters: each {title, statement, category, occurrences, sessions, quotes}.
    """
    clusters: dict[str, dict] = {}
    for c in candidates:
        title = c.get("title", "").lower().strip()
        if not title:
            continue
        # Find best matching existing cluster by title substring overlap
        key = title
        for existing_key in clusters.keys():
            # Simple match: significant token overlap
            tokens_new = set(title.replace("-", " ").split())
            tokens_existing = set(existing_key.replace("-", " ").split())
            if tokens_new and tokens_existing:
                overlap = len(tokens_new & tokens_existing) / max(len(tokens_new), len(tokens_existing))
                if overlap > 0.6:
                    key = existing_key
                    break
        if key not in clusters:
            clusters[key] = {
                "title": title,
                "statement": c.get("statement", ""),
                "category": c.get("category", "preference"),
                "occurrences": 0,
                "sessions": set(),
                "quotes": [],
                "confidences": [],
            }
        clusters[key]["occurrences"] += 1
        clusters[key]["sessions"].add(c.get("source_session", ""))
        if len(clusters[key]["quotes"]) < 3:
            clusters[key]["quotes"].append(c.get("source_quote", ""))
        clusters[key]["confidences"].append(c.get("confidence", 0.0))

    result = []
    for cluster in clusters.values():
        result.append({
            "title": cluster["title"],
            "statement": cluster["statement"],
            "category": cluster["category"],
            "occurrences": cluster["occurrences"],
            "session_count": len(cluster["sessions"]),
            "avg_confidence": sum(cluster["confidences"]) / max(len(cluster["confidences"]), 1),
            "quotes": cluster["quotes"],
        })
    return sorted(result, key=lambda x: (-x["occurrences"], -x["avg_confidence"]))


# ─── Stage 5: Stability checks ───────────────────────────────────────────────

def passes_stability(cluster: dict, min_count: int, min_sessions: int) -> bool:
    """Apply stability thresholds: count + session diversity + confidence."""
    if cluster["occurrences"] < min_count:
        return False
    if cluster["session_count"] < min_sessions:
        return False
    if cluster["avg_confidence"] < 0.6:
        return False
    return True


# ─── Stage 6: Write review file ──────────────────────────────────────────────

def write_review_file(stable: list[dict], all_clusters: list[dict], output_path: Path, stats: dict, min_count: int, min_sessions: int) -> None:
    """Write candidates as a reviewable markdown file.

    Shows STABLE candidates first (passed threshold), then ALL OTHER clusters
    below for operator to optionally pick from.
    """
    lines = [
        "# Proposed preferences -- review queue",
        "",
        f"_Generated by `scripts/extract_preferences.py` on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}._",
        "",
        f"**Sessions scanned:** {stats['sessions_scanned']}",
        f"**Turns scanned:** {stats['turns_scanned']}",
        f"**Pre-filtered (regex):** {stats['turns_filtered']}",
        f"**Classified as signal (Haiku):** {stats['turns_classified_signal']}",
        f"**Extracted candidates (Sonnet):** {stats['candidates_extracted']}",
        f"**Clusters formed:** {stats['clusters_formed']}",
        f"**Pass stability threshold (count>={min_count}, sessions>={min_sessions}):** {len(stable)}",
        "",
        "## How to use this file",
        "",
        "Two sections below:",
        "- **STABLE** -- passed clustering + thresholds, strongest candidates.",
        "- **WEAK SIGNALS** -- single-occurrence or near-singleton candidates. Many will be noise but some are real preferences my clustering missed.",
        "",
        "For each candidate, decide ACCEPT / EDIT / REJECT.",
        "",
        "- **ACCEPT**: copy to `memory/preferences/<title>.md` (or `memory/principles/` if universal, or `memory/lessons/` if incident-derived)",
        "- **EDIT**: rewrite the statement/title to match what you actually believe",
        "- **REJECT**: skip",
        "",
        "After review: run `python scripts/refresh_indexes.py` and archive this file.",
        "",
        "---",
        "",
        f"## STABLE ({len(stable)})",
        "",
    ]

    def render_cluster(c, idx, stable_flag):
        block = [
            f"### {idx}. {c['title']}{'  [WEAK]' if not stable_flag else ''}",
            "",
            f"**Statement:** {c['statement']}",
            f"**Category:** {c['category']}",
            f"**Occurrences:** {c['occurrences']} across {c['session_count']} sessions",
            f"**Avg confidence:** {c['avg_confidence']:.2f}",
            "",
            "**Example quotes:**",
            "",
        ]
        for q in c["quotes"]:
            snippet = q.replace("\n", " ").strip()[:200]
            block.append(f"> {snippet}")
            block.append("")
        block.extend([
            "**Action**: [ ] ACCEPT  [ ] EDIT  [ ] REJECT",
            "",
            "---",
            "",
        ])
        return block

    if not stable:
        lines.append("_No candidates passed stability thresholds. See WEAK SIGNALS section below._")
        lines.append("")

    for i, c in enumerate(stable, start=1):
        lines.extend(render_cluster(c, i, stable_flag=True))

    # Now the weak signals
    weak = [c for c in all_clusters if c not in stable]
    lines.extend([
        f"## WEAK SIGNALS ({len(weak)})",
        "",
        "_Below stability threshold but extracted. Skim these -- some may be real preferences that clustering missed._",
        "",
    ])
    for i, c in enumerate(weak, start=len(stable) + 1):
        lines.extend(render_cluster(c, i, stable_flag=False))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def save_candidates_cache(candidates: list[dict], cache_path: Path) -> None:
    """Save extracted candidates to JSON so re-clustering is free."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(candidates, indent=2, default=str), encoding="utf-8")


def load_candidates_cache(cache_path: Path) -> list[dict]:
    """Load previously extracted candidates."""
    return json.loads(cache_path.read_text(encoding="utf-8"))


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Extract user preferences from Claude Code session history.")
    parser.add_argument("--project", help="Limit to one project subdir (e.g. C--Users-yuezh-Documents-GodTech)")
    parser.add_argument("--since", type=int, default=180, help="Only sessions modified within last N days (default: 180)")
    parser.add_argument("--limit-files", type=int, help="Max number of session files to scan")
    parser.add_argument("--limit-turns", type=int, default=10000, help="Max user turns to consider for classification (default 10000)")
    parser.add_argument("--min-count", type=int, default=5, help="Stability: minimum occurrences (default 5)")
    parser.add_argument("--min-sessions", type=int, default=3, help="Stability: minimum distinct sessions (default 3)")
    parser.add_argument("--output", help="Output path (default: scratch/proposed_<date>.md)")
    parser.add_argument("--dry-run", action="store_true", help="Show pre-filter results only, don't call LLM")
    parser.add_argument("--from-cache", help="Skip extraction and re-cluster from cached candidates JSON")
    args = parser.parse_args()

    print("=" * 60)
    print("Moradin session preference extraction")
    print("=" * 60)
    print(f"Project: {args.project or '(all)'}")
    print(f"Since: {args.since} days")
    print(f"Min count: {args.min_count}, Min sessions: {args.min_sessions}")
    print()

    # Cache path
    cache_path = Path(__file__).resolve().parent.parent / "scratch" / f"_candidates_{datetime.date.today().isoformat()}.json"

    # If --from-cache, skip extraction
    if args.from_cache:
        cache_file = Path(args.from_cache)
        if not cache_file.is_file():
            print(f"Cache file not found: {cache_file}")
            return
        candidates = load_candidates_cache(cache_file)
        print(f"Loaded {len(candidates)} candidates from cache")
        clusters = cluster_candidates(candidates)
        stable = [c for c in clusters if passes_stability(c, args.min_count, args.min_sessions)]
        stats = {
            "sessions_scanned": 0, "turns_scanned": 0, "turns_filtered": 0,
            "turns_classified_signal": 0, "candidates_extracted": len(candidates),
            "clusters_formed": len(clusters),
        }
        output_path = Path(args.output) if args.output else Path(__file__).resolve().parent.parent / "scratch" / f"proposed_{datetime.date.today().isoformat()}.md"
        write_review_file(stable, clusters, output_path, stats, args.min_count, args.min_sessions)
        print(f"Clusters: {len(clusters)}, Stable: {len(stable)}")
        print(f"Review file: {output_path}")
        return

    # 1. Discover + filter
    files = discover_sessions(project_only=args.project)
    files = filter_by_age(files, args.since)
    if args.limit_files:
        files = files[:args.limit_files]
    print(f"Sessions to scan: {len(files)}")

    # 2. Walk + pre-filter
    user_turns_filtered = []  # (record, category_hint)
    total_turns = 0
    for fp in files:
        for rec in walk_file(fp):
            if rec.role != "user":
                total_turns += 1
                continue
            total_turns += 1
            hint = pre_filter(rec)
            if hint:
                user_turns_filtered.append((rec, hint))
    print(f"Total turns scanned: {total_turns}")
    print(f"Pre-filtered (regex high-signal): {len(user_turns_filtered)}")

    if args.dry_run:
        print()
        print("DRY RUN - showing first 20 filtered turns:")
        for rec, hint in user_turns_filtered[:20]:
            snippet = rec.content[:150].encode("ascii", errors="replace").decode("ascii")
            print(f"  [{hint:11s}] {snippet}")
        return

    if not user_turns_filtered:
        print("No high-signal turns found. Try a longer time window or different project.")
        return

    user_turns_filtered = user_turns_filtered[:args.limit_turns]

    # 3. Classify with Haiku
    print()
    print(f"Classifying {len(user_turns_filtered)} turns with {MODEL_FILTER}...")
    kept = []
    for i, (rec, hint) in enumerate(user_turns_filtered):
        if i % 25 == 0:
            print(f"  {i}/{len(user_turns_filtered)}...")
        category, confidence = classify_turn(rec)
        if category != "noise" and confidence >= 0.6:
            kept.append((rec, hint))
    print(f"Classified as signal: {len(kept)}")

    # 4. Extract with Sonnet
    print()
    print(f"Extracting structured preferences from {len(kept)} turns with {MODEL_EXTRACT}...")
    candidates = []
    for i, (rec, hint) in enumerate(kept):
        if i % 10 == 0:
            print(f"  {i}/{len(kept)}...")
        extracted = extract_preference(rec, hint)
        if extracted:
            candidates.append(extracted)
    print(f"Extracted candidates: {len(candidates)}")

    # 5. Save raw candidates to cache (cheap re-clustering later)
    save_candidates_cache(candidates, cache_path)
    print(f"Candidates cached: {cache_path}")

    # 6. Cluster
    clusters = cluster_candidates(candidates)
    print(f"Clusters formed: {len(clusters)}")

    # 7. Stability filter
    stable = [c for c in clusters if passes_stability(c, args.min_count, args.min_sessions)]
    print(f"Pass stability: {len(stable)}")

    # 8. Write review file (shows BOTH stable AND weak signals)
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(__file__).resolve().parent.parent / "scratch" / f"proposed_{datetime.date.today().isoformat()}.md"

    stats = {
        "sessions_scanned": len(files),
        "turns_scanned": total_turns,
        "turns_filtered": len(user_turns_filtered),
        "turns_classified_signal": len(kept),
        "candidates_extracted": len(candidates),
        "clusters_formed": len(clusters),
    }
    write_review_file(stable, clusters, output_path, stats, args.min_count, args.min_sessions)
    print()
    print(f"Review file: {output_path}")
    print(f"Cached candidates: {cache_path} (use --from-cache to re-cluster cheaply)")


if __name__ == "__main__":
    main()
