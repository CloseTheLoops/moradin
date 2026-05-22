#!/usr/bin/env python3
"""Moradin memory audit / lint.

Checks every file under memory/ for:
  1. Required frontmatter fields (name, description, topics, applies_to, type)
  2. Topic tags from the allowed taxonomy (8 tags)
  3. Files unchanged > STALE_DAYS flagged
  4. Orphan files (not linked from _INDEX.md)

Exit code: 0 if no errors, 1 if errors.
License: MIT
"""

import argparse
import datetime
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

MORADIN_ROOT = Path(__file__).resolve().parent.parent
MEMORY_ROOT = MORADIN_ROOT / "memory"

ALLOWED_TOPICS = {"harness", "memory", "eval", "llm", "agent", "arch", "workflow", "tooling"}
REQUIRED_FRONTMATTER = {"name", "description", "topics", "applies_to", "type"}
STALE_DAYS = 180

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)


def parse_frontmatter(content):
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


def file_age_days(path):
    mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime)
    return (datetime.datetime.now() - mtime).days


def audit():
    """Run all checks. Returns {files_checked: int, issues: [{file, severity, msg}]}."""
    issues = []

    if not MEMORY_ROOT.exists():
        return {"files_checked": 0, "issues": []}

    files = [f for f in MEMORY_ROOT.rglob("*.md") if not f.name.startswith("_")]

    # Build set of indexed filenames (mentioned in any _INDEX.md)
    indexed_files = set()
    for index_file in MEMORY_ROOT.rglob("_INDEX.md"):
        try:
            content = index_file.read_text(encoding="utf-8")
            for match in re.finditer(r"[\w_-]+\.md", content):
                indexed_files.add(match.group())
        except Exception:
            pass

    for md_file in files:
        rel_path = str(md_file.relative_to(MORADIN_ROOT)).replace("\\", "/")
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception as e:
            issues.append({"file": rel_path, "severity": "error", "msg": f"read failed: {e}"})
            continue

        metadata, body = parse_frontmatter(content)

        # 1. Required frontmatter
        missing = REQUIRED_FRONTMATTER - set(metadata.keys())
        if missing:
            issues.append({
                "file": rel_path, "severity": "error",
                "msg": f"missing frontmatter fields: {sorted(missing)}"
            })

        # 2. Topic taxonomy
        topics = metadata.get("topics", [])
        if isinstance(topics, str):
            topics = [topics]
        bad_topics = set(topics) - ALLOWED_TOPICS
        if bad_topics:
            issues.append({
                "file": rel_path, "severity": "warn",
                "msg": f"unknown topics: {sorted(bad_topics)} (allowed: {sorted(ALLOWED_TOPICS)})"
            })
        if not topics:
            issues.append({
                "file": rel_path, "severity": "warn",
                "msg": "no topics tag"
            })

        # 3. Stale file
        age = file_age_days(md_file)
        if age > STALE_DAYS:
            issues.append({
                "file": rel_path, "severity": "info",
                "msg": f"stale: {age} days since last touch (threshold: {STALE_DAYS})"
            })

        # 4. Orphan check (only if a sibling _INDEX exists)
        parent_index = md_file.parent / "_INDEX.md"
        if parent_index.exists() and md_file.name not in indexed_files:
            issues.append({
                "file": rel_path, "severity": "warn",
                "msg": f"orphan: not linked from {parent_index.parent.name}/_INDEX.md"
            })

    return {"files_checked": len(files), "issues": issues}


def main():
    parser = argparse.ArgumentParser(description="Moradin memory audit (lint)")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    args = parser.parse_args()

    result = audit()

    if args.format == "json":
        print(json.dumps(result, indent=2))
        return 0

    print(f"Audited {result['files_checked']} files. Found {len(result['issues'])} issues.\n")
    by_severity = defaultdict(list)
    for issue in result["issues"]:
        by_severity[issue["severity"]].append(issue)

    for sev in ["error", "warn", "info"]:
        if by_severity[sev]:
            print(f"== {sev.upper()} ({len(by_severity[sev])}) ==")
            for issue in by_severity[sev]:
                print(f"  {issue['file']}: {issue['msg']}")
            print()

    return 1 if by_severity["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
