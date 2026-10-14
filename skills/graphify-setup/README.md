# graphify-setup

Agent skill that sets up [Graphify](https://pypi.org/project/graphifyy/) in a repository, migrates an existing setup to a clean-tree workflow, and handles graph merges.

## Install

```sh
npx skills add ederheisler/agent-skills --skill graphify-setup -g
npx skills update graphify-setup
```

## What it does

- **Initial setup**: installs the `graphifyy` CLI, installs the Graphify skill for Claude when it is available (default), or for Claude plus the agents-standard harnesses (OMP, Pi, Codex) when several are available, adds ignore rules, registers the `graph.json` merge driver, runs a full build, and makes `CLAUDE.md` import `@AGENTS.md` so Claude Code sees the same persistent rules.
- **Migration mode**: for repositories that already use Graphify. Removes the auto-rebuild git hooks (keeps the merge driver), gitignores and untracks `graphify-out/manifest.json`, updates `AGENTS.md`, and makes `CLAUDE.md` import `@AGENTS.md` when Claude is used. No reinstall, no full build.
- **Merge workflow**: bounded, deterministic recovery when a merge conflicts on Graphify artifacts.

## Workflow it enforces

- Commit only `graph.json`, `GRAPH_REPORT.md` and `graph.html`, by exact path. `manifest.json` is machine-local and never committed.
- No `post-commit`/`post-checkout` hooks: they leave the tree dirty after every commit and branch switch.
- Refresh before committing: `PYTHONHASHSEED=0 graphify update .` (about 2 s, no LLM), then commit sources and graph files together.

## Migrate an existing repository

Send this to your agent in the repository:

```
Use the `graphify-setup` skill in migration mode on this repository. Graphify is already set up here, so do not reinstall skills, ask about harnesses, or run a full build. Follow section 7 of `references/setup-project.md`. Verify everything yourself. Do not commit or push. Report the status and staged changes.
```

## Layout

| File | Purpose |
|---|---|
| `SKILL.md` | Entry point and modes |
| `references/setup-project.md` | CLI install, harness selection, hooks, ignore rules, refresh, migration |
| `references/full-build.md` | Full initial build and verification |
| `references/merge-workflow.md` | Persistent `AGENTS.md` rules and merge recovery |

The skill never commits or pushes without explicit authorization.
