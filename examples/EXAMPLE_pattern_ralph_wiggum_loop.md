---
name: ralph_wiggum_loop
description: Autonomous iteration loop — re-feed the same prompt to a coding agent until completion criteria met
topics: [harness, workflow, tooling]
applies_to: [universal]
type: pattern
version: 1
---

# Ralph Wiggum loop — autonomous iteration

A `while true` loop that re-feeds the same prompt file to a coding agent until a verifiable completion criterion is met. State accumulates in files + git, not the agent's context window.

## Shape

```bash
while true; do
  cat PROMPT.md | claude-code
  # Stop hook intercepts Claude's exit attempt and re-feeds the prompt
  if [[ -f COMPLETION_MARKER ]]; then break; fi
done
```

Or use Anthropic's official ralph-wiggum plugin which implements the Stop-hook pattern automatically.

Key properties:
- **State on disk, not in context.** Each iteration sees the modified files + git history from previous runs.
- **Failures feed back as context.** When the agent fails, it reads its own error output on the next iteration.
- **Completion is verifiable.** A test suite passes, a marker file appears, a SQL query returns the expected row.

## When to use

| ✓ Use Ralph when | ✗ Don't use Ralph when |
|---|---|
| Greenfield project, clear spec | Existing codebase / refactor (Ralph will fight your patterns) |
| Deterministic completion criterion (tests pass, output matches) | Spec is vague or completion fuzzy |
| Can run unattended for hours | Operator needs to approve each step |
| Batch operation: large refactor, test coverage, documentation | Single-decision task — Ralph's overhead dominates |
| Mechanical, repeatable work | Creative or judgment-heavy decisions |

## Example

Geoffrey Huntley built a programming language compiler over 3 months of unattended Ralph loop. YC hackathon teams shipped 6+ repos overnight for $297. The pattern works at scale when the spec is tight and the test is honest.

For our use: candidate for big mechanical migrations, generating test fixtures, batch documentation updates across a codebase. NOT for design decisions or architecture work.
