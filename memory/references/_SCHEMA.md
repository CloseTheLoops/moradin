# References schema

References are **captured external sources** — github repos, papers, articles, docs. Full inventory of notable concepts, NOT pre-filtered for current project.

## Required frontmatter

```yaml
---
name: short_kebab_name
description: One-line description of the source
topics: [tag1, tag2, tag3]           # often multi-tagged (source covers many concepts)
applies_to: [universal, godtech, trading]   # which projects might use this
type: reference
url: https://github.com/.../...
captured: 2026-01-15
last_verified: 2026-01-15
---
```

## Body structure

```markdown
# <Source name>

## What it is

<One paragraph — what the source is, who made it.>

## Notable concepts (full inventory, NOT pre-filtered)

### A. <Concept name>
<One paragraph.>
Applicability: <which projects this could apply to>

### B. <Concept name>
<One paragraph.>
Applicability: <which projects this could apply to>

### C. <Concept name>
<One paragraph.>
Applicability: <which projects might apply this — INCLUDING ones that contradict current approach. Note the contrast.>

...

## What I deliberately skipped

- <Tactical detail, lookup-later items>
- <Deeply specific to their project, not generalizable>
```

## The capture discipline

The big rule: **capture ALL notable concepts, not just what fits today's project.** Concepts that don't fit GodTech today may fit trading next month. Tag them with potential applicability and keep them.

If a concept contradicts our current approach, capture it anyway. Note the philosophical contrast. It may be the right call for a different project.

## File naming

Lowercase + underscores. Descriptive of the source.

- ✓ `hermes_agent.md`
- ✓ `mem0.md`
- ✓ `zep_graphiti.md`
- ✓ `openai_evals.md`
- ✗ `nous_research_hermes.md` (don't include the company; use the project name)
