#!/usr/bin/env python3
"""Moradin memory stats — counts + coverage report.

License: MIT
"""

import argparse
import datetime
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

MORADIN_ROOT = Path(__file__).resolve().parent.parent
MEMORY_ROOT = MORADIN_ROOT / "memory"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)


def parse_frontmatter(content):
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}
    fm_text = match.group(1)
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
    return metadata


def collect_stats():
    if not MEMORY_ROOT.exists():
        return {
            "total_files": 0,
            "by_type": {},
            "by_topic": {},
            "by_applies_to": {},
            "age_distribution": {},
        }

    files = [f for f in MEMORY_ROOT.rglob("*.md") if not f.name.startswith("_")]

    by_type = Counter()
    by_topic = Counter()
    by_applies_to = Counter()
    age_buckets = Counter()
    now = datetime.datetime.now()

    for md_file in files:
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        metadata = parse_frontmatter(content)

        t = metadata.get("type", "unknown")
        by_type[t] += 1

        topics = metadata.get("topics", [])
        if isinstance(topics, str):
            topics = [topics]
        for topic in topics:
            by_topic[topic] += 1

        applies_to = metadata.get("applies_to", [])
        if isinstance(applies_to, str):
            applies_to = [applies_to]
        for at in applies_to:
            by_applies_to[at] += 1

        mtime = datetime.datetime.fromtimestamp(md_file.stat().st_mtime)
        age_days = (now - mtime).days
        if age_days <= 7:
            age_buckets["fresh (≤7d)"] += 1
        elif age_days <= 30:
            age_buckets["recent (≤30d)"] += 1
        elif age_days <= 90:
            age_buckets["aging (≤90d)"] += 1
        elif age_days <= 180:
            age_buckets["old (≤180d)"] += 1
        else:
            age_buckets["stale (>180d)"] += 1

    return {
        "total_files": len(files),
        "by_type": dict(by_type),
        "by_topic": dict(by_topic),
        "by_applies_to": dict(by_applies_to),
        "age_distribution": dict(age_buckets),
    }


def main():
    parser = argparse.ArgumentParser(description="Moradin memory stats")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    args = parser.parse_args()

    stats = collect_stats()

    if args.format == "json":
        print(json.dumps(stats, indent=2))
        return

    print(f"Moradin memory stats")
    print(f"====================\n")
    print(f"Total files: {stats['total_files']}\n")

    def print_counter(title, d):
        if not d:
            print(f"{title}: (none)\n")
            return
        print(f"{title}:")
        for k, v in sorted(d.items(), key=lambda x: -x[1]):
            print(f"  {k:20s} {v}")
        print()

    print_counter("By type", stats["by_type"])
    print_counter("By topic", stats["by_topic"])
    print_counter("By applies_to", stats["by_applies_to"])
    print_counter("Age distribution", stats["age_distribution"])


if __name__ == "__main__":
    main()
