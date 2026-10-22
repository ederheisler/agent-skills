---
name: graphify-setup
description: Installs Graphify in a repository for Claude Code, OMP, Pi, and Codex, completes the full project graph build, migrates existing setups to the clean-tree workflow, and recovers graph artifacts during merges. Use when asked to set up Graphify and build the repository graph, migrate an existing Graphify setup, or merge branches that conflict on Graphify files.
author: Eder Heisler
version: "1.8"
---

# Graphify Setup

Do the requested Graphify work end to end; do not stop after describing commands or installing the CLI. Use the installed CLI's `--help` and the current official Graphify instructions; never invent commands or flags. Preserve existing configuration, hooks, instructions, and unrelated changes.

## Gates for every mode

- Never commit or push without explicit authorization.
- Within `graphify-out/`, commit only `graph.json`, `GRAPH_REPORT.md`, and `graph.html` (optional: only when the file exists), by exact path. Never stage `manifest.json`, caches, cost records, `.graphify_*` sidecars, or dated `YYYY-MM-DD/` backup folders. Commit other setup files (`.gitignore`, `.gitattributes`, `AGENTS.md`, `CLAUDE.md`, installed skill and config directories) only when the authorization names them. Ignore the installer's broad `git add` hint.
- Graphify's auto-rebuild git hooks (`post-commit`, `post-checkout`) are not kept. Only the `graph.json` merge driver stays; the graph is refreshed before each commit instead ([refresh](references/setup-project.md#6-refresh-before-commit-replaces-the-hooks)).
- Before any `graphify update` or `graphify cluster-only`, pass the [community-name guard](references/setup-project.md#community-name-guard): without Graphify's machine-local label files these commands silently replace curated community names. Stop and ask when the guard says so.
- Do not run `graphify hook uninstall` (it also removes the merge driver) or a bare `graphify install`. Never add `--force` on your own: when a Graphify command refuses, report its message and ask.
- Semantic extraction runs once, through the active host agent. Never use a headless, API-key, or provider-key substitute.
- Routine integration (merges, updates) is one bounded deterministic refresh that reuses valid semantic data and caches. Missing or checkout-specific state, or an installed skill that suggests broader extraction, does not authorize a semantic rebuild; the [merge workflow](references/merge-workflow.md) scope and stop conditions govern.

## Choose the mode

- **Migration**: the repository already uses Graphify (`graphify-out/graph.json` exists) and the user asks to set it up again, update it, or apply the new workflow. Do not reinstall skills, ask for harness selection, or run a full build. Run only [the migration steps](references/setup-project.md#7-migrate-an-existing-setup), then verify and report. For an additional harness, run only section 2 of the setup instructions for that target.
- **Merge**: persistent merge rules, or merging branches in a repository that already uses Graphify. Follow [the merge workflow](references/merge-workflow.md) and only its mechanical completion checks. Keep the merge paused until it says recovery is complete. Broader semantic investigation, rebuilding, or enrichment needs separate explicit authorization.
- **Initial setup**: an explicit request to set up Graphify and build the graph. Follow the steps below.

## Initial setup

1. Check that the active repository is the requested target. Inspect existing Graphify state before changing it, and read `AGENTS.md` and, when present, `CLAUDE.md`.
2. Follow [project setup instructions](references/setup-project.md) in order: CLI (1), targets and install (2), integration and git hooks (3), ignore rules (4), persistent rules (5). Claude Code maps to `claude`; OMP, Pi, and Codex share one `agents` install. Default to Claude alone when only it is available, Claude plus the available OMP/Pi/Codex targets when several are, or those targets alone. Show the default and the unavailable targets, and let the user change it. Install only the confirmed selection.
3. After each install only verify, read-only, that the printed `SKILL.md` exists. Do not initialize or run the installed skill yet. Preserve existing Graphify skill customizations.
4. Persistent rules live in `AGENTS.md` under `## Graphify working rules`. Claude Code gets them through a `CLAUDE.md` that imports `@AGENTS.md`. Create no other harness-named context files.
5. Only after steps 2 to 4, with hooks removed and ignore rules verified, run the full build once with [runtime, build, and verification instructions](references/full-build.md). Handle warnings and errors without dropping project-owned source or calling a partial build complete.
6. Verify the graph artifacts, hook status, ignore and tracking behavior, and a real `graphify query`. Follow the installed skill's final findings presentation and report actual blockers.
