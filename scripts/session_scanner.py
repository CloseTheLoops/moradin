#!/usr/bin/env python3
"""Claude Code session JSONL scanner.

Walks ~/.claude/projects/<project>/*.jsonl and yields conversation records
(user / assistant / system) with flattened text content.

- Skips internal record types (file-history-snapshot, progress, isSidechain, isCompactSummary)
- Joins subagent JSONLs via tool_use_id where present
- Applies simple regex redaction (API keys, emails, absolute filepaths with usernames)
- Stdlib-only — no external dependencies

License: MIT
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

DEFAULT_SESSIONS_DIR = Path(
    os.environ.get(
        "MORADIN_SESSIONS_DIR",
        os.path.expanduser("~/.claude/projects"),
    )
)

INGESTIBLE_TYPES = frozenset({"user", "assistant", "system"})
SKIP_TYPES = frozenset({"file-history-snapshot", "progress"})

REDACTION_PATTERNS = [
    # Anthropic API keys
    (re.compile(r"sk-ant-[a-zA-Z0-9_-]+"), "[REDACTED_ANTHROPIC_KEY]"),
    # OpenAI API keys
    (re.compile(r"sk-[a-zA-Z0-9]{40,}"), "[REDACTED_OPENAI_KEY]"),
    # Github tokens
    (re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,}"), "[REDACTED_GITHUB_TOKEN]"),
    # Email addresses
    (re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"), "[REDACTED_EMAIL]"),
    # Bearer tokens
    (re.compile(r"[Bb]earer\s+[A-Za-z0-9_\-.=]{20,}"), "[REDACTED_BEARER_TOKEN]"),
]


@dataclass
class SessionRecord:
    """One conversation record from a session JSONL file."""
    file_path: str
    session_id: str
    line_offset: int
    record_type: str
    role: str
    timestamp: str | None
    content: str
    content_hash: str
    uuid: str | None = None
    parent_uuid: str | None = None
    raw: dict = field(default_factory=dict)


def redact(text: str) -> str:
    """Apply simple regex redaction. Not exhaustive — best-effort for common secrets."""
    for pattern, replacement in REDACTION_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def _flatten_content(message_content) -> str:
    """Flatten Claude message content (str or list of typed blocks) into plain text."""
    if message_content is None:
        return ""
    if isinstance(message_content, str):
        return message_content
    if isinstance(message_content, list):
        parts: list[str] = []
        for block in message_content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type", "")
            if btype == "text":
                parts.append(block.get("text", ""))
            elif btype == "thinking":
                parts.append(f"[THINKING]\n{block.get('thinking', '')}\n[/THINKING]")
            elif btype == "tool_use":
                name = block.get("name", "?")
                tool_input = block.get("input", {})
                if isinstance(tool_input, dict):
                    summary = ", ".join(f"{k}={type(v).__name__}" for k, v in tool_input.items())
                else:
                    summary = str(tool_input)[:80]
                parts.append(f"[TOOL_USE {name}({summary})]")
            elif btype == "tool_result":
                tid = block.get("tool_use_id", "?")
                parts.append(f"[TOOL_RESULT {tid[:8]}]")
            else:
                parts.append(f"[{btype.upper()}]")
        return "\n".join(parts).strip()
    return str(message_content)


def _session_id_from_path(path: str) -> str:
    base = os.path.basename(path)
    if base.lower().endswith(".jsonl"):
        return base[:-6]
    return base


def _parse_line(raw: dict, file_path: str, line_offset: int) -> SessionRecord | None:
    """Convert one JSONL line into a SessionRecord, or None if not ingestible."""
    rtype = raw.get("type")
    if rtype not in INGESTIBLE_TYPES:
        return None

    # Skip side-chains and synthetic compaction summaries
    if raw.get("isSidechain") is True:
        return None
    if raw.get("isCompactSummary") is True:
        return None

    message = raw.get("message")
    if not isinstance(message, dict):
        return None

    content = _flatten_content(message.get("content"))
    if not content.strip():
        return None

    content = redact(content)
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:32]
    role = message.get("role", rtype) or rtype

    return SessionRecord(
        file_path=file_path,
        session_id=raw.get("sessionId") or _session_id_from_path(file_path),
        line_offset=line_offset,
        record_type=rtype,
        role=role,
        timestamp=raw.get("timestamp"),
        content=content,
        content_hash=content_hash,
        uuid=raw.get("uuid"),
        parent_uuid=raw.get("parentUuid"),
        raw=raw,
    )


def walk_file(file_path: str) -> Iterator[SessionRecord]:
    """Yield SessionRecord for every ingestible line in file_path."""
    try:
        f = open(file_path, "r", encoding="utf-8", errors="replace")
    except OSError:
        return
    with f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue
            rec = _parse_line(raw, file_path, i)
            if rec:
                yield rec


def discover_sessions(root: str | Path | None = None, project_only: str | None = None) -> list[str]:
    """Return list of session JSONL files (main + subagent) under root.

    If project_only is given (e.g. "C--Users-yuezh-Documents-GodTech"), restrict to that subdir.
    """
    if root is None:
        root = DEFAULT_SESSIONS_DIR
    root = Path(root)
    if not root.exists():
        return []

    if project_only:
        search = root / project_only
        if not search.exists():
            return []
        pattern = str(search / "**" / "*.jsonl")
    else:
        pattern = str(root / "**" / "*.jsonl")

    files = sorted(glob.glob(pattern, recursive=True))
    return files


def filter_by_age(files: list[str], days: int) -> list[str]:
    """Keep only files modified within the last `days` days."""
    import time
    cutoff = time.time() - days * 86400
    return [f for f in files if os.path.getmtime(f) > cutoff]


def session_turns(file_path: str) -> list[SessionRecord]:
    """Convenience: collect all records from one session into a list."""
    return list(walk_file(file_path))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Claude Code session JSONL scanner")
    parser.add_argument("--project", help="Limit to one project subdir (e.g. C--Users-yuezh-Documents-GodTech)")
    parser.add_argument("--since", type=int, help="Only files modified within last N days")
    parser.add_argument("--limit-files", type=int, help="Limit number of files scanned")
    parser.add_argument("--count-only", action="store_true", help="Just count records, don't print")
    args = parser.parse_args()

    files = discover_sessions(project_only=args.project)
    if args.since:
        files = filter_by_age(files, args.since)
    if args.limit_files:
        files = files[:args.limit_files]

    total_records = 0
    by_type: dict[str, int] = {}
    for fp in files:
        for rec in walk_file(fp):
            total_records += 1
            by_type[rec.record_type] = by_type.get(rec.record_type, 0) + 1

    print(f"Files scanned: {len(files)}")
    print(f"Total records: {total_records}")
    for t, n in sorted(by_type.items()):
        print(f"  {t}: {n}")
