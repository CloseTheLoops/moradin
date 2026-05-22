# Quickstart

Get Moradin running in 5 minutes.

## 1. Create your instance

On GitHub, navigate to the Moradin template repo and click **Use this template** → **Create a new repository**. Name it whatever (e.g., `moradin-yz`). Set it to **private** if you want your build knowledge private.

Then clone locally:

```bash
git clone https://github.com/<your-username>/moradin-yz.git ~/Documents/moradin
cd ~/Documents/moradin
```

## 2. Open Claude Code in your workshop

```bash
claude
```

Claude Code loads `CLAUDE.md` (which mirrors `AGENTS.md`) — that's the workshop's brain. Claude now knows it's in your workshop, knows the 8 skills, and is ready.

## 3. Initialize

```
/moradin:init
```

Claude walks you through:
- Verifying directory structure
- Optionally creating your first project slot
- Optionally capturing your first principle

## 4. Capture your first reference

Saw an interesting repo or article? Capture it:

```
/moradin:capture https://github.com/some/repo
```

Claude fetches the source, lists all notable concepts, asks you to confirm tags, then writes `memory/references/<source>.md`.

## 5. Build something

When you want to work on a project:

```
/moradin:build <project> "task description"
```

Claude reads relevant principles + patterns from `memory/`, reads the project's `state.md`, proposes a plan, executes after your approval. Writes a session log.

## 6. Ship at end of session

Before closing:

```
/moradin:ship
```

Claude asks what you learned. Saves any lessons. Updates project state.

## 7. Search anytime

```
/moradin:recall "what do I know about X?"
```

Claude searches memory and synthesizes an answer with citations.

## Optional: install companion plugins

See [plugins.md](../plugins.md) for recommended Claude Code plugins that pair well with Moradin.

## Updating Moradin

When the framework updates:

```bash
./scripts/update.sh
```

This merges upstream framework changes while preserving your `memory/` and `projects/`.

## Next steps

- [CONCEPTS](CONCEPTS.md) — understand the 5 layers
- [CONTRIBUTING](CONTRIBUTING.md) — how to extend Moradin
- [FAQ](FAQ.md) — common questions
