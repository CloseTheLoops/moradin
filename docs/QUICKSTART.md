# Quickstart

Get Moradin running in 5 minutes.

## 1. Create your instance

On GitHub, navigate to the Moradin template repo and click **Use this template** → **Create a new repository**. Name it whatever (e.g., `moradin-mine`). Set it to **private** — your build knowledge and preferences will live in it.

Then clone locally:

```bash
git clone https://github.com/<your-username>/moradin-mine.git ~/Documents/moradin
cd ~/Documents/moradin
```

## 2. Open your agent in the workshop

```bash
claude    # or cursor . — anything that reads AGENTS.md
```

The agent loads `CLAUDE.md` (mirror of `AGENTS.md`) — the identity, the pipeline, and the design laws. It now knows how to forge.

## 3. Initialize

```
/moradin:init
```

One-time setup: verifies structure, builds empty indexes, points you at the front door.

## 4. Build something — the only command you need to remember

```
/moradin:forge
```

Name a project folder or a brand-new idea. Projects are created as **siblings** of Moradin (`~/Documents/my-app`), never inside it. First run calibrates how much process you want, then the pipeline guides you: define → measure → research → decide → build → close → review. Every stage updates a 3-line journal, so coming back weeks later starts with "here's where you are."

Small fix to an existing project? The dispatcher's quick path skips the ceremony. Changed your mind mid-build? Say so — the amendment route updates the plan instead of arguing with it.

## 5. Feed the memory (optional but compounding)

```
/moradin:capture https://github.com/some/repo    # absorb an external source
/moradin:recall "what do I know about X?"        # search everything you've saved
```

Lessons are captured automatically at every close; `retrospect` periodically promotes them to patterns and principles.

## Updating Moradin

```bash
./scripts/update.sh   # merges framework updates; your memory/ and projects/ stay yours
```

## Next steps

- [CONCEPTS](CONCEPTS.md) — the layers explained
- [The forge plan](forge_plan.md) — why the pipeline is shaped this way
- [CONTRIBUTING](CONTRIBUTING.md) · [FAQ](FAQ.md)
