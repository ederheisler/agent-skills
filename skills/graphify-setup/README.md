# graphify-setup

Agent skill that sets up [Graphify](https://pypi.org/project/graphifyy/) in a repository, migrates an existing setup to a clean-tree workflow, and handles graph merges.

## Install

```sh
npx skills add ederheisler/agent-skills --skill graphify-setup -g
npx skills update graphify-setup
```

## What it does

- **Initial setup**: installs the `graphifyy` CLI and the project-scoped Graphify skill. Claude Code gets the `claude` install; OMP, Pi, and Codex share one `agents` install (`.agents/skills/`, which all three discover). It registers the `graph.json` merge driver, removes the auto-rebuild git hooks, adds ignore rules, writes the working rules to `AGENTS.md` under `## Graphify working rules`, and makes `CLAUDE.md` import `@AGENTS.md`. Only then does it run the full build once, through the active host agent.
- **Migration mode**: for repositories that already use Graphify. Removes the auto-rebuild git hooks (keeps the merge driver), gitignores and untracks `graphify-out/manifest.json`, updates `AGENTS.md`, and makes `CLAUDE.md` import `@AGENTS.md` when Claude is used. No reinstall, no full build.
- **Merge workflow**: bounded, deterministic recovery when a merge conflicts on Graphify artifacts. Community names are curated and live in tracked `graph.json`, but Graphify only reuses them from machine-local label files that a fresh clone lacks. Before `update` or `cluster-only` the skill checks for those files and stops to ask when they are missing and the graph carries names. It reports any name that disappears afterwards, including hub renames Graphify announces; it cannot guarantee names survive a structural change.

## Workflow it enforces

- Within `graphify-out/`, commit only `graph.json`, `GRAPH_REPORT.md`, and `graph.html` (when it exists), by exact path. `manifest.json` is machine-local and never committed. Other setup files (`.gitignore`, `.gitattributes`, `AGENTS.md`, `CLAUDE.md`, installed skill directories) are committed only when you name them.
- No `post-commit`/`post-checkout` hooks: they leave the tree dirty after every commit and branch switch. Hooks are removed from the directory `git rev-parse --git-path hooks` reports, so Husky and linked worktrees work.
- Refresh before committing: pass the community-name check, run `PYTHONHASHSEED=0 graphify update .` (local, no LLM), then commit sources and graph files together. If `update` refuses to overwrite, it does not use `--force`; it reports and asks.

## Migrate an existing repository

Send this to your agent in the repository:

```
Use the `graphify-setup` skill in migration mode on this repository. Graphify is already set up here, so do not reinstall skills, ask about harnesses, or run a full build. Follow section 7 of `references/setup-project.md`. Verify everything yourself. Do not commit or push. Report the status and staged changes.
```

## Layout

| File | Purpose |
|---|---|
| `SKILL.md` | Entry point, safety gates, and modes |
| `references/setup-project.md` | CLI install, harness selection and install, hooks, ignore rules, refresh, migration |
| `references/full-build.md` | Full initial build and verification |
| `references/merge-workflow.md` | Persistent `AGENTS.md` rules and merge recovery |

The skill never commits or pushes without explicit authorization.
