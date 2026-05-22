---
name: moradin-recall
description: Search memory and synthesize an answer with citations to source files.
---

# moradin:recall

Search Moradin's memory and answer a question with citations.

## When invoked

`/moradin:recall <question>` 

or `/moradin:recall <question> --topic <tag>` for topic-filtered search.

## What you do

1. **Tokenize the question.** Identify key terms.

2. **Run BM25 search:**
   ```
   python scripts/search.py "<question>" [--topic <tag>] [--applies-to <tag>] --limit 10
   ```

3. **Read the top results** (typically 5-10 files). For each, read both frontmatter and body.

4. **Synthesize an answer** that:
   - Directly addresses the question
   - Cites EACH source file by path (e.g. `memory/patterns/closed_loop_eval.md`)
   - Distinguishes between principles (universal rules), patterns (designs), references (external knowledge), and lessons (incident-derived)
   - Honest about gaps: if memory doesn't have the answer, say so

5. **Optional: file the synthesis back.** If the synthesis itself is valuable, ask the operator: "This synthesis is valuable — file it back as a new pattern or lesson?"

## Citation format

Always cite specific files. Don't say "your memory has principles about closed loops" — say "see `memory/principles/close_every_loop.md`."

## Topic filter

If the operator's question is clearly within one topic (e.g. "what do I know about evals?"), use `--topic eval` to focus the search.

If unsure: search without filter first; let BM25 surface relevant docs.

## Don't

- Don't synthesize without reading the actual files. Search results give you hits — read them before answering.
- Don't make up content. If the memory doesn't say it, say "memory doesn't cover this."
- Don't filter results silently. If you skip a hit, explain why.

## Output

- A synthesized answer with file-path citations
- Optionally: a new file in `memory/patterns/` or `memory/lessons/` if the synthesis is filed back
