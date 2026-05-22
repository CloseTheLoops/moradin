#!/usr/bin/env python3
"""Moradin memory search.

BM25 over memory/ markdown files with frontmatter filtering (topics, applies_to).
Stdlib-only — no external dependencies.

License: MIT
"""

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

MORADIN_ROOT = Path(__file__).resolve().parent.parent
MEMORY_ROOT = MORADIN_ROOT / "memory"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)


def parse_frontmatter(content):
    """Parse simple YAML-ish frontmatter. Returns (metadata dict, body str)."""
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}, content
    fm_text, body = match.group(1), match.group(2)
    metadata = {}
    for line in fm_text.split("\n"):
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
        metadata[k] = v
    return metadata, body


def tokenize(text):
    """Lowercase alphanumeric tokenizer."""
    return re.findall(r"\w+", text.lower())


def scan_memory():
    """Walk memory/ dirs, return list of doc records.

    Skips files starting with _ (schemas, indexes).
    """
    docs = []
    if not MEMORY_ROOT.exists():
        return docs
    for md_file in MEMORY_ROOT.rglob("*.md"):
        if md_file.name.startswith("_"):
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Warning: failed to read {md_file}: {e}", file=sys.stderr)
            continue
        metadata, body = parse_frontmatter(content)
        tokens = tokenize(body)
        docs.append({
            "path": str(md_file.relative_to(MORADIN_ROOT)).replace("\\", "/"),
            "metadata": metadata,
            "body": body,
            "tokens": tokens,
        })
    return docs


def bm25_score(query_tokens, doc, doc_freqs, total_docs, avgdl, k1=1.5, b=0.75):
    """BM25 score for one document against a query."""
    if not doc["tokens"]:
        return 0.0
    dl = len(doc["tokens"])
    doc_counter = Counter(doc["tokens"])
    score = 0.0
    for q in query_tokens:
        f = doc_counter.get(q, 0)
        if f == 0:
            continue
        df = doc_freqs.get(q, 0)
        idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1)
        norm = f * (k1 + 1) / (f + k1 * (1 - b + b * dl / avgdl))
        score += idf * norm
    return score


def matches_filter(metadata, topic_filter, applies_to_filter):
    """Check optional frontmatter filters."""
    if topic_filter:
        topics = metadata.get("topics", [])
        if isinstance(topics, str):
            topics = [topics]
        if topic_filter not in topics:
            return False
    if applies_to_filter:
        applies = metadata.get("applies_to", [])
        if isinstance(applies, str):
            applies = [applies]
        if applies_to_filter not in applies:
            return False
    return True


def search(query, topic=None, applies_to=None, limit=10):
    """Search memory. Returns list of {path, score, topics, applies_to, snippet}."""
    docs = scan_memory()
    if not docs:
        return []
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    doc_freqs = Counter()
    for doc in docs:
        for t in set(doc["tokens"]):
            doc_freqs[t] += 1
    avgdl = sum(len(d["tokens"]) for d in docs) / len(docs)

    results = []
    for doc in docs:
        if not matches_filter(doc["metadata"], topic, applies_to):
            continue
        score = bm25_score(query_tokens, doc, doc_freqs, len(docs), avgdl)
        if score > 0:
            results.append({
                "path": doc["path"],
                "score": round(score, 4),
                "topics": doc["metadata"].get("topics", []),
                "applies_to": doc["metadata"].get("applies_to", []),
                "snippet": doc["body"][:200].replace("\n", " "),
            })
    results.sort(key=lambda r: -r["score"])
    return results[:limit]


def main():
    parser = argparse.ArgumentParser(
        description="Moradin memory search — BM25 over markdown with frontmatter filter."
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument("--topic", help="Filter by topic tag (harness, memory, eval, llm, agent, arch, workflow, tooling)")
    parser.add_argument("--applies-to", dest="applies_to", help="Filter by applies_to tag (universal, godtech, trading, ...)")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    results = search(args.query, args.topic, args.applies_to, args.limit)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
