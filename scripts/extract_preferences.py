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


# Topic taxonomy — used for auto-tagging
_TOPIC_KEYWORDS = {
    "harness": ["harness", "test", "verify", "check", "scaffold"],
    "memory": ["memory", "remember", "recall", "kg", "knowledge", "persist"],
    "eval": ["eval", "metric", "score", "judge", "gold", "accuracy", "audit"],
    "llm": ["llm", "prompt", "claude", "gemini", "gpt", "model", "afc"],
    "agent": ["agent", "mcp", "sub-agent", "multi-agent"],
    "arch": ["architecture", "layer", "substrate", "structure"],
    "workflow": ["plan", "rollback", "env-var", "flag", "depend", "build", "step"],
    "tooling": ["lint", "scaffold", "tool", "script", "audit", "code"],
}

def _infer_topics(title: str, statement: str) -> list[str]:
    """Best-effort topic tagging from title + statement keywords."""
    text = (title + " " + statement).lower()
    matched = []
    for topic, kws in _TOPIC_KEYWORDS.items():
        for kw in kws:
            if kw in text:
                matched.append(topic)
                break
    return matched or ["workflow"]  # fallback


def _slugify(s: str) -> str:
    """kebab-case slug."""
    s = re.sub(r"[^a-z0-9 -]+", "", s.lower())
    s = re.sub(r"\s+", "_", s.strip())
    s = re.sub(r"-+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "unnamed"


def _tokenize_for_sim(s: str) -> set:
    """Tokenize for Jaccard similarity (lowercase alphanumeric)."""
    # Drop very short tokens (stopword-ish noise)
    return {t for t in re.findall(r"\w+", s.lower()) if len(t) > 2}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _find_similar_existing(candidate: dict, memory_root: Path, threshold: float):
    """Returns (existing_path, similarity_score) if a similar memory file exists, else None."""
    matches = _find_similar_existing_top_k(candidate, memory_root, k=1, min_threshold=threshold)
    if matches:
        return (matches[0]["path"], matches[0]["similarity"])
    return None


def _find_similar_existing_top_k(candidate: dict, memory_root: Path, k: int = 5,
                                  min_threshold: float = 0.05) -> list[dict]:
    """Returns top-k existing memory files ranked by token overlap.

    Each match: {path, name, description, similarity}.
    Used as a cheap pre-filter before LLM-judge similarity check.
    """
    cand_text = candidate.get("title", "") + " " + candidate.get("statement", "")
    cand_tokens = _tokenize_for_sim(cand_text)
    if len(cand_tokens) < 3:
        return []

    matches = []
    for md_file in memory_root.rglob("*.md"):
        if md_file.name.startswith("_") or md_file.name.startswith("EXAMPLE_"):
            continue
        try:
            content = md_file.read_text(encoding="utf-8")[:2000]
        except Exception:
            continue
        name_match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
        desc_match = re.search(r"^description:\s*(.+)$", content, re.MULTILINE)
        name = name_match.group(1).strip() if name_match else md_file.stem
        desc = desc_match.group(1).strip() if desc_match else ""
        existing_tokens = _tokenize_for_sim(name + " " + desc)
        if len(existing_tokens) < 3:
            continue
        sim = _jaccard(cand_tokens, existing_tokens)
        if sim >= min_threshold:
            matches.append({"path": md_file, "name": name, "description": desc, "similarity": sim})

    matches.sort(key=lambda m: -m["similarity"])
    return matches[:k]


_LLM_JUDGE_SYSTEM = """You decide whether a CANDIDATE principle/preference is semantically duplicate of an EXISTING one. Return ONLY JSON.

Strict rule: mark as duplicate ONLY if the core concept is the same, even when worded differently. Different angles on related topics (e.g. "plan before building" vs "audit before delivering") are NOT duplicates — they're distinct rules.

Return: {"is_duplicate": bool, "duplicate_of": "<existing_name>" or null, "reason": "<one short sentence>"}"""


_LLM_JUDGE_USER_TMPL = """CANDIDATE
title: {cand_title}
statement: {cand_statement}

EXISTING memory files (top-{n} most similar by keyword overlap):
{existing_list}

Is the candidate a semantic duplicate of any existing file?"""


def llm_judge_duplicate(candidate: dict, top_k_existing: list[dict], model: str) -> dict:
    """LLM-judges whether candidate duplicates any of the top-k existing files.

    Returns {"is_duplicate": bool, "duplicate_of": str|None, "reason": str}.
    Falls back to is_duplicate=False on any error.
    """
    if not top_k_existing:
        return {"is_duplicate": False, "duplicate_of": None, "reason": "no similar existing"}

    existing_list = "\n".join(
        f"{i + 1}. {e['name']}: {e['description']}"
        for i, e in enumerate(top_k_existing)
    )
    user_msg = _LLM_JUDGE_USER_TMPL.format(
        cand_title=candidate.get("title", ""),
        cand_statement=candidate.get("statement", "")[:400],
        n=len(top_k_existing),
        existing_list=existing_list,
    )
    try:
        response = call_claude(model, _LLM_JUDGE_SYSTEM, user_msg, max_tokens=256)
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if not match:
            return {"is_duplicate": False, "duplicate_of": None, "reason": "no JSON in response"}
        data = json.loads(match.group(0))
        return {
            "is_duplicate": bool(data.get("is_duplicate", False)),
            "duplicate_of": data.get("duplicate_of"),
            "reason": data.get("reason", ""),
        }
    except Exception as e:
        return {"is_duplicate": False, "duplicate_of": None, "reason": f"error: {e}"}


def auto_write_memory_files(clusters: list[dict], memory_root: Path, min_confidence: float,
                            skip_similar_threshold: float = 0.5,
                            use_llm_judge: bool = False) -> dict:
    """Write each cluster above confidence threshold to memory/{type}/<title>.md.

    Dedup logic:
    - Token-Jaccard pre-filter finds top-k similar existing files.
    - If use_llm_judge: Sonnet judges whether candidate is a true semantic duplicate.
    - Else: any Jaccard >= skip_similar_threshold causes skip.

    Returns stats: {written, skipped_low_conf, skipped_similar, conflict, by_type, skipped_similar_pairs}.
    """
    stats = {
        "written": 0, "skipped_low_conf": 0, "skipped_similar": 0, "conflict": 0,
        "by_type": defaultdict(int), "skipped_similar_pairs": []
    }

    for c in clusters:
        if c["avg_confidence"] < min_confidence:
            stats["skipped_low_conf"] += 1
            continue

        # Find top-k similar existing files via token overlap (cheap pre-filter)
        top_k = _find_similar_existing_top_k(c, memory_root, k=5, min_threshold=0.05)

        skipped_reason = None
        existing_path = None
        score = 0.0

        if use_llm_judge and top_k:
            # Authoritative LLM-judge — semantic dup detection
            verdict = llm_judge_duplicate(c, top_k, MODEL_EXTRACT)
            if verdict["is_duplicate"]:
                skipped_reason = "llm_judge"
                # Find the actual file path matching duplicate_of
                dup_name = verdict.get("duplicate_of", "")
                for m in top_k:
                    if m["name"] == dup_name or dup_name in str(m["path"]):
                        existing_path = m["path"]
                        score = m["similarity"]
                        break
                if existing_path is None and top_k:
                    existing_path = top_k[0]["path"]
                    score = top_k[0]["similarity"]
                judge_reason = verdict.get("reason", "")
            else:
                judge_reason = None
        else:
            # Fallback to Jaccard threshold
            if top_k and top_k[0]["similarity"] >= skip_similar_threshold:
                skipped_reason = "jaccard"
                existing_path = top_k[0]["path"]
                score = top_k[0]["similarity"]
                judge_reason = f"token overlap {score:.2f} >= {skip_similar_threshold}"
            else:
                judge_reason = None

        if skipped_reason:
            stats["skipped_similar"] += 1
            stats["skipped_similar_pairs"].append({
                "candidate_title": c.get("title", ""),
                "candidate_statement": c.get("statement", ""),
                "candidate_confidence": c.get("avg_confidence", 0.0),
                "candidate_occurrences": c.get("occurrences", 0),
                "candidate_category": c.get("category", ""),
                "existing_path": str(existing_path.relative_to(memory_root.parent)).replace("\\", "/") if existing_path else "",
                "similarity": round(score, 3),
                "skip_method": skipped_reason,
                "judge_reason": judge_reason or "",
                "quotes": c.get("quotes", []),
            })
            continue

        category = c.get("category", "preference")
        # Map category → subdir
        subdir_map = {
            "principle": "principles",
            "preference": "preferences",
            "lesson": "lessons",
            "pattern": "patterns",
        }
        subdir = subdir_map.get(category, "preferences")
        target_dir = memory_root / subdir
        target_dir.mkdir(parents=True, exist_ok=True)

        slug = _slugify(c["title"])
        target_path = target_dir / f"{slug}.md"

        if target_path.exists():
            stats["conflict"] += 1
            # Skip — don't overwrite operator-curated content
            continue

        # Compose file content
        topics = _infer_topics(c["title"], c["statement"])
        applies_to = "[operator-self]" if category == "preference" else "[universal]"
        topics_str = ", ".join(topics)

        body_extra = ""
        if c["quotes"]:
            body_extra = "\n\n## Source quotes (from sessions)\n\n"
            for q in c["quotes"]:
                snippet = q.replace("\n", " ").strip()[:300]
                body_extra += f"> {snippet}\n\n"

        if category == "lesson":
            content = f"""---
name: {slug}
description: {c['statement']}
topics: [{topics_str}]
applies_to: {applies_to}
type: lesson
source: derived-from-sessions
source_count: {c['occurrences']}
source_confidence: {c['avg_confidence']:.2f}
date_added: {datetime.date.today().isoformat()}
---

# {c['title']}

{c['statement']}

## Why

(Derived from sessions — fill in the incident detail when convenient.){body_extra}
## How to apply

(Fill in when convenient.)
"""
        else:
            content = f"""---
name: {slug}
description: {c['statement']}
topics: [{topics_str}]
applies_to: {applies_to}
type: {category}
source: derived-from-sessions
source_count: {c['occurrences']}
source_confidence: {c['avg_confidence']:.2f}
date_added: {datetime.date.today().isoformat()}
---

# {c['title']}

{c['statement']}{body_extra}
"""

        target_path.write_text(content, encoding="utf-8")
        stats["written"] += 1
        stats["by_type"][subdir] += 1

    return stats


def _html_escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace('"', "&quot;").replace("'", "&#39;"))


def _write_conflicts_html(pairs: list[dict], output_path: Path) -> None:
    """HTML report of candidates skipped because a similar memory file exists.

    Operator-facing — review whether each skip was correct or whether the new
    formulation deserves to supersede the existing one.
    """
    def card(p: dict, idx: int) -> str:
        q_html = "\n".join(
            f'<blockquote>{_html_escape(q.replace(chr(10), " ").strip()[:300])}</blockquote>'
            for q in p.get("quotes", [])
        )
        return f'''
<div class="card">
  <div class="head">
    <span class="idx">#{idx}</span>
    <span class="title">{_html_escape(p['candidate_title'])}</span>
    <span class="sim">sim {p['similarity']:.2f}</span>
  </div>
  <div class="row"><strong>Candidate ({p['candidate_category']}):</strong> {_html_escape(p['candidate_statement'])}</div>
  <div class="row"><strong>Existing:</strong> <code>{_html_escape(p['existing_path'])}</code></div>
  <div class="row"><strong>Confidence:</strong> {p['candidate_confidence']:.2f}  ·  <strong>Occurrences:</strong> {p['candidate_occurrences']}</div>
  <div class="quotes">{q_html}</div>
  <div class="actions">
    <label class="opt"><input type="radio" name="d-{idx}" value="skip" checked> <span>SKIP (default)</span></label>
    <label class="opt"><input type="radio" name="d-{idx}" value="supersede"> <span>SUPERSEDE existing</span></label>
    <label class="opt"><input type="radio" name="d-{idx}" value="rewrite"> <span>REWRITE both</span></label>
  </div>
</div>'''

    cards_html = "\n".join(card(p, i + 1) for i, p in enumerate(pairs))
    generated = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Moradin -- skipped similar candidates</title>
<style>
*{{box-sizing:border-box}}body{{margin:0 auto;max-width:1100px;padding:24px 36px 80px;font-family:-apple-system,sans-serif;background:#0a0e14;color:#d4dae3;line-height:1.5}}
h1{{font-family:'Courier New',monospace;color:#e8a917;font-size:20px;margin:0 0 6px}}
.stamp{{font-family:'Courier New',monospace;font-size:11px;color:#5a6577;margin-bottom:18px}}
.lede{{background:#12171f;border-left:4px solid #f59e0b;padding:12px 16px;font-size:13px;margin-bottom:24px;border-radius:0 4px 4px 0}}
.card{{background:#12171f;border:1px solid #1e2a3a;border-left:4px solid #f59e0b;border-radius:6px;padding:14px 18px;margin-bottom:10px}}
.head{{display:flex;gap:10px;align-items:center;margin-bottom:8px}}
.idx{{font-family:'Courier New',monospace;color:#5a6577;font-size:11px;min-width:32px}}
.title{{font-family:'Courier New',monospace;color:#d4dae3;font-size:13px;font-weight:700;flex:1}}
.sim{{font-family:'Courier New',monospace;font-size:11px;color:#f59e0b;background:rgba(245,158,11,0.15);padding:2px 8px;border-radius:3px}}
.row{{font-size:12px;margin:4px 0;color:#d4dae3}}.row strong{{color:#06b6d4;font-family:'Courier New',monospace;font-size:11px}}
.row code{{background:#1a2030;padding:1px 6px;border-radius:3px;font-size:11px;color:#94a3b8}}
.quotes blockquote{{margin:4px 0;padding:5px 10px;border-left:2px solid #1e2a3a;color:#94a3b8;font-size:11px;font-style:italic}}
.actions{{display:flex;gap:14px;margin-top:10px;padding-top:8px;border-top:1px dashed #1e2a3a;flex-wrap:wrap}}
.opt{{display:inline-flex;gap:5px;align-items:center;font-family:'Courier New',monospace;font-size:11px;cursor:pointer;padding:3px 8px;border-radius:3px}}
.opt:hover{{background:#1a2030}}.opt input{{accent-color:#e8a917}}
</style></head><body>
<h1>SKIPPED -- similar existing memory found</h1>
<div class="stamp">Generated {generated}</div>
<div class="lede">
These candidates were extracted but NOT written because a memory file with similar (title+description) already exists.
Default = SKIP (existing wins). Override only if the new formulation is meaningfully better; choose SUPERSEDE (mark old as superseded by new) or REWRITE (operator manually merges both into one).
</div>
{cards_html}
</body></html>'''
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def write_review_html(stable: list[dict], all_clusters: list[dict], output_path: Path, stats: dict, min_count: int, min_sessions: int) -> None:
    """Write the review queue as an interactive HTML page.

    Operator-facing: checkboxes for ACCEPT/EDIT/REJECT per candidate, export button
    that downloads a JSON of all decisions. Dark theme matches other Moradin HTMLs.
    """
    def render_card(c: dict, idx: int, stable_flag: bool) -> str:
        title = _html_escape(c["title"])
        statement = _html_escape(c["statement"])
        category = _html_escape(c.get("category", ""))
        weak_badge = '' if stable_flag else '<span class="badge weak">WEAK</span>'
        quotes_html = "\n".join(
            f'<blockquote>{_html_escape(q.replace(chr(10), " ").strip()[:300])}</blockquote>'
            for q in c["quotes"]
        )
        return f'''
<div class="card {'stable' if stable_flag else 'weak'}" data-idx="{idx}" data-title="{title}">
  <div class="card-head">
    <span class="idx">#{idx}</span>
    <span class="title">{title}</span>
    {weak_badge}
    <span class="cat cat-{category}">{category}</span>
  </div>
  <div class="statement">{statement}</div>
  <div class="meta">
    <span><strong>Occurrences:</strong> {c['occurrences']}</span>
    <span><strong>Sessions:</strong> {c['session_count']}</span>
    <span><strong>Confidence:</strong> {c['avg_confidence']:.2f}</span>
  </div>
  <div class="quotes">{quotes_html}</div>
  <div class="actions">
    <label class="opt"><input type="radio" name="decision-{idx}" value="accept"> <span>ACCEPT</span></label>
    <label class="opt"><input type="radio" name="decision-{idx}" value="edit"> <span>EDIT</span></label>
    <label class="opt"><input type="radio" name="decision-{idx}" value="reject"> <span>REJECT</span></label>
    <label class="opt"><input type="radio" name="decision-{idx}" value="" checked> <span>(skip)</span></label>
  </div>
</div>'''

    stable_html = "\n".join(render_card(c, i + 1, True) for i, c in enumerate(stable))
    weak = [c for c in all_clusters if c not in stable]
    weak_html = "\n".join(render_card(c, len(stable) + i + 1, False) for i, c in enumerate(weak))

    generated = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Moradin -- Proposed preferences review</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin:0 auto; max-width:1100px; padding:24px 36px 80px; font-family:-apple-system,BlinkMacSystemFont,sans-serif; background:#0a0e14; color:#d4dae3; line-height:1.5; }}
  h1 {{ font-family:'Courier New',monospace; color:#e8a917; font-size:22px; margin:0 0 4px; letter-spacing:0.5px; }}
  h2 {{ font-family:'Courier New',monospace; color:#e8a917; font-size:15px; margin:30px 0 12px; padding-bottom:6px; border-bottom:1px solid #1e2a3a; letter-spacing:0.3px; }}
  .stamp {{ font-family:'Courier New',monospace; font-size:11px; color:#5a6577; margin-bottom:18px; }}
  .stats {{ background:#12171f; border-left:4px solid #06b6d4; padding:12px 16px; font-size:12px; color:#94a3b8; font-family:'Courier New',monospace; margin-bottom:18px; }}
  .stats .row {{ display:flex; gap:24px; flex-wrap:wrap; }}
  .stats .row span {{ display:inline-block; }}
  .stats .row strong {{ color:#e8a917; }}
  .lede {{ background:#12171f; border-left:4px solid #e8a917; padding:12px 16px; font-size:13px; color:#d4dae3; margin-bottom:24px; border-radius:0 4px 4px 0; }}
  .toolbar {{ position:sticky; top:0; background:#0a0e14; padding:10px 0; z-index:10; border-bottom:1px solid #1e2a3a; margin-bottom:14px; display:flex; gap:10px; align-items:center; flex-wrap:wrap; }}
  .toolbar input[type=text] {{ flex:1; background:#1a2030; border:1px solid #1e2a3a; color:#d4dae3; padding:6px 10px; border-radius:4px; font-size:12px; font-family:'Courier New',monospace; min-width:200px; }}
  .toolbar button {{ background:#1a2030; border:1px solid #1e2a3a; color:#d4dae3; padding:6px 12px; border-radius:4px; font-family:'Courier New',monospace; font-size:11px; cursor:pointer; }}
  .toolbar button:hover {{ border-color:#e8a917; color:#e8a917; }}
  .toolbar button.primary {{ background:#e8a917; color:#0a0e14; border-color:#e8a917; font-weight:700; }}
  .toolbar button.primary:hover {{ background:#f59e0b; }}
  .toolbar .count {{ font-family:'Courier New',monospace; font-size:11px; color:#94a3b8; }}
  .card {{ background:#12171f; border:1px solid #1e2a3a; border-radius:6px; padding:14px 18px; margin-bottom:10px; transition:border-color 0.15s; }}
  .card.stable {{ border-left:4px solid #10b981; }}
  .card.weak {{ border-left:4px solid #5a6577; opacity:0.88; }}
  .card:hover {{ border-color:#e8a917; }}
  .card.hide {{ display:none; }}
  .card-head {{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-bottom:8px; }}
  .idx {{ font-family:'Courier New',monospace; color:#5a6577; font-size:11px; min-width:32px; }}
  .title {{ font-family:'Courier New',monospace; color:#d4dae3; font-size:13px; font-weight:700; }}
  .badge {{ display:inline-block; padding:2px 7px; border-radius:3px; font-family:'Courier New',monospace; font-size:10px; font-weight:700; letter-spacing:0.3px; }}
  .badge.weak {{ background:rgba(108,122,137,0.25); color:#94a3b8; }}
  .cat {{ display:inline-block; padding:2px 7px; border-radius:3px; font-family:'Courier New',monospace; font-size:10px; font-weight:700; letter-spacing:0.3px; }}
  .cat-principle {{ background:rgba(232,169,23,0.20); color:#e8a917; }}
  .cat-preference {{ background:rgba(168,85,247,0.20); color:#a855f7; }}
  .cat-lesson {{ background:rgba(16,185,129,0.18); color:#10b981; }}
  .statement {{ font-size:13px; color:#d4dae3; margin:6px 0 10px; }}
  .meta {{ font-size:11px; color:#94a3b8; font-family:'Courier New',monospace; margin-bottom:10px; display:flex; gap:18px; }}
  .meta strong {{ color:#06b6d4; }}
  .quotes blockquote {{ margin:4px 0; padding:6px 10px; border-left:2px solid #1e2a3a; color:#94a3b8; font-size:12px; font-style:italic; background:rgba(26,32,48,0.4); }}
  .actions {{ display:flex; gap:14px; margin-top:10px; padding-top:10px; border-top:1px dashed #1e2a3a; flex-wrap:wrap; }}
  .opt {{ display:inline-flex; gap:5px; align-items:center; font-family:'Courier New',monospace; font-size:11px; cursor:pointer; padding:3px 8px; border-radius:3px; }}
  .opt:hover {{ background:#1a2030; }}
  .opt input {{ accent-color:#e8a917; }}
  .opt input[value=accept] + span {{ color:#10b981; }}
  .opt input[value=edit] + span {{ color:#06b6d4; }}
  .opt input[value=reject] + span {{ color:#ef4444; }}
  .footnote {{ font-size:11px; color:#5a6577; font-style:italic; margin-top:24px; }}
</style>
</head>
<body>

<h1>MORADIN -- PROPOSED PREFERENCES</h1>
<div class="stamp">Generated {generated} -- review queue from session extraction</div>

<div class="stats">
  <div class="row">
    <span><strong>Sessions:</strong> {stats['sessions_scanned']}</span>
    <span><strong>Turns:</strong> {stats['turns_scanned']}</span>
    <span><strong>Pre-filtered:</strong> {stats['turns_filtered']}</span>
    <span><strong>Classified (Haiku):</strong> {stats['turns_classified_signal']}</span>
    <span><strong>Extracted (Sonnet):</strong> {stats['candidates_extracted']}</span>
    <span><strong>Clusters:</strong> {stats['clusters_formed']}</span>
    <span><strong>Stable (count&gt;={min_count}, sessions&gt;={min_sessions}):</strong> {len(stable)}</span>
  </div>
</div>

<div class="lede">
  For each candidate: pick ACCEPT (sounds like me), EDIT (close but needs tweak), or REJECT (not me / one-off). Skip the ones you're unsure about.
  When done, click <strong>Export decisions</strong> -- downloads a JSON of your choices that you (or Claude) can use to write the final memory files.
</div>

<div class="toolbar">
  <input type="text" id="filter" placeholder="filter by title or text..." oninput="filterCards()">
  <button onclick="showOnly('stable')">Show stable only</button>
  <button onclick="showOnly('all')">Show all</button>
  <button onclick="showOnly('decided')">Show decided</button>
  <button class="primary" onclick="exportDecisions()">Export decisions</button>
  <span class="count" id="count"></span>
</div>

<h2>STABLE ({len(stable)})</h2>
{stable_html if stable_html else '<p style="color:#94a3b8;font-size:12px;">No candidates passed stability thresholds. Try lower thresholds via --min-count.</p>'}

<h2>WEAK SIGNALS ({len(weak)})</h2>
<p style="font-size:12px;color:#94a3b8;">Below stability threshold but extracted. Skim -- some may be real preferences clustering missed.</p>
{weak_html}

<p class="footnote">Cached candidates at <code>scratch/_candidates_*.json</code>. Re-cluster cheaply via <code>python scripts/extract_preferences.py --from-cache &lt;cache.json&gt; --min-count N</code>.</p>

<script>
function filterCards() {{
  const q = document.getElementById('filter').value.toLowerCase();
  let visible = 0;
  document.querySelectorAll('.card').forEach(c => {{
    const text = c.innerText.toLowerCase();
    const match = !q || text.includes(q);
    c.classList.toggle('hide', !match);
    if (match) visible++;
  }});
  document.getElementById('count').innerText = visible + ' visible';
}}

function showOnly(mode) {{
  document.querySelectorAll('.card').forEach(c => {{
    if (mode === 'all') c.classList.remove('hide');
    else if (mode === 'stable') c.classList.toggle('hide', !c.classList.contains('stable'));
    else if (mode === 'decided') {{
      const radios = c.querySelectorAll('input[type=radio]');
      let decided = false;
      radios.forEach(r => {{ if (r.checked && r.value) decided = true; }});
      c.classList.toggle('hide', !decided);
    }}
  }});
  filterCards();  // re-apply text filter
}}

function exportDecisions() {{
  const decisions = [];
  document.querySelectorAll('.card').forEach(c => {{
    const idx = c.dataset.idx;
    const title = c.dataset.title;
    let decision = '';
    c.querySelectorAll('input[type=radio]').forEach(r => {{ if (r.checked && r.value) decision = r.value; }});
    if (decision) decisions.push({{ idx, title, decision }});
  }});
  const blob = new Blob([JSON.stringify(decisions, null, 2)], {{type: 'application/json'}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'moradin_decisions_' + new Date().toISOString().slice(0,10) + '.json';
  a.click();
  URL.revokeObjectURL(url);
  alert('Exported ' + decisions.length + ' decisions. Save this JSON and tell Claude to write the approved files.');
}}

filterCards();
</script>

</body>
</html>'''
    output_path.write_text(html, encoding="utf-8")


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
    parser.add_argument("--auto-accept", action="store_true",
                        help="Skip HTML review; auto-write all candidates above --auto-confidence to memory/{type}/")
    parser.add_argument("--auto-confidence", type=float, default=0.70,
                        help="Min confidence for --auto-accept (default 0.70)")
    parser.add_argument("--skip-similar-threshold", type=float, default=0.5,
                        help="Token-Jaccard threshold for skipping similar (default 0.5; ignored if --skip-similar-llm-judge)")
    parser.add_argument("--skip-similar-llm-judge", action="store_true",
                        help="Use LLM-judge (Sonnet) for semantic dedup against existing memory. Adds ~$0.01/candidate.")
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
        if args.auto_accept:
            memory_root = Path(__file__).resolve().parent.parent / "memory"
            print(f"Auto-accepting candidates with confidence >= {args.auto_confidence}...")
            write_stats = auto_write_memory_files(clusters, memory_root, args.auto_confidence,
                                                   args.skip_similar_threshold, args.skip_similar_llm_judge)
            print(f"Wrote {write_stats['written']} files")
            print(f"  Skipped (low confidence): {write_stats['skipped_low_conf']}")
            print(f"  Skipped (similar exists): {write_stats['skipped_similar']}")
            print(f"  Skipped (filename exists): {write_stats['conflict']}")
            print(f"  By type:")
            for t, n in write_stats["by_type"].items():
                print(f"    {t}: {n}")
            # Write conflicts HTML
            if write_stats["skipped_similar"] > 0:
                conflicts_path = Path(__file__).resolve().parent.parent / "scratch" / f"conflicts_{datetime.date.today().isoformat()}.html"
                _write_conflicts_html(write_stats["skipped_similar_pairs"], conflicts_path)
                print(f"  Conflicts report: {conflicts_path}")
            return

        output_path = Path(args.output) if args.output else Path(__file__).resolve().parent.parent / "scratch" / f"proposed_{datetime.date.today().isoformat()}.md"
        write_review_file(stable, clusters, output_path, stats, args.min_count, args.min_sessions)
        html_path = output_path.with_suffix(".html")
        write_review_html(stable, clusters, html_path, stats, args.min_count, args.min_sessions)
        print(f"Clusters: {len(clusters)}, Stable: {len(stable)}")
        print(f"Review (md):   {output_path}")
        print(f"Review (html): {html_path}")
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
    if args.auto_accept:
        memory_root = Path(__file__).resolve().parent.parent / "memory"
        print()
        print(f"Auto-accepting candidates with confidence >= {args.auto_confidence}...")
        write_stats = auto_write_memory_files(clusters, memory_root, args.auto_confidence)
        print(f"Wrote {write_stats['written']} files")
        print(f"  Skipped (low confidence): {write_stats['skipped_low_conf']}")
        print(f"  Skipped (file exists):    {write_stats['conflict']}")
        print(f"  By type:")
        for t, n in write_stats["by_type"].items():
            print(f"    {t}: {n}")
        print(f"Cached candidates: {cache_path}")
        return

    write_review_file(stable, clusters, output_path, stats, args.min_count, args.min_sessions)
    html_path = output_path.with_suffix(".html")
    write_review_html(stable, clusters, html_path, stats, args.min_count, args.min_sessions)
    print()
    print(f"Review file (markdown): {output_path}")
    print(f"Review file (HTML):     {html_path}  <-- recommended for review")
    print(f"Cached candidates:      {cache_path} (use --from-cache to re-cluster cheaply)")


if __name__ == "__main__":
    main()
