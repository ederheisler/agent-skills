# Installing Graphify in a project

Use the current official instructions at <https://docs.graphify.com/installation> and the installed CLI's own `--help` output. CLI support and destinations change between versions; do not assume flags, paths, or integrations from an older version. Facts below were checked against Graphify 0.9.72; compare them with the installer's printed output and adapt if the installed version differs.

## Contents

- [1. Prepare the CLI](#1-prepare-the-cli)
- [2. Select targets and install](#2-select-targets-and-install)
- [3. Integration and git hooks](#3-integration-and-git-hooks)
  - [Remove the auto-rebuild hooks](#remove-the-auto-rebuild-hooks)
- [4. Exclude machine-local output before building](#4-exclude-machine-local-output-before-building)
- [5. Add persistent working rules](#5-add-persistent-working-rules)
- [6. Refresh before commit (replaces the hooks)](#6-refresh-before-commit-replaces-the-hooks)
  - [Community-name guard](#community-name-guard)
- [7. Migrate an existing setup](#7-migrate-an-existing-setup)

## 1. Prepare the CLI

1. Check `uv --version`. If `uv` is absent, on macOS use `brew install uv` when Homebrew is available; otherwise (Linux or macOS without Homebrew) use the official installer `curl -LsSf https://astral.sh/uv/install.sh | sh`. If `uv` exists but errors for another reason, diagnose that failure instead of reinstalling it.
2. Follow the selected install method's actual shell/PATH instructions. Verify `uv --version` before continuing.
3. Install the official package `graphifyy` with `uv tool install graphifyy`. If already installed, reuse it. Run `graphify --help` in the current shell.
4. If `graphify` is not found, run `uv tool dir --bin` and add the returned directory to this session's `PATH`, not a guessed location. Retry `graphify --help` and require success. `uv tool update-shell` edits the user's shell profile outside this repository: tell the user and run it only after they approve. If `graphify` is found but fails, diagnose that error rather than changing `PATH`.
5. Read `graphify install --help` before installing. Use documented commands only.

## 2. Select targets and install

The target set is Claude Code, OMP, Pi, and Codex. Determine which are available from the active harness plus local evidence (for example `command -v claude omp pi codex`). Report the available and unavailable targets, propose the default below, and let the user change it. Never include an unavailable or unselected target. If none is available, report that blocker and run no install. Install nothing until the user confirms a selection.

Default selection:

- Only Claude is available: Claude.
- Claude and at least one of OMP, Pi, Codex are available: Claude plus the other available targets.
- Only OMP, Pi, and/or Codex are available: those targets.

Map the confirmed targets to Graphify platforms and install once per platform, not once per harness. The CLI takes one `--platform` per invocation. A bare `graphify install` defaults to an OS-dependent platform without detecting assistants, so never run it.

| Confirmed target | Graphify platform | Project skill destination |
| --- | --- | --- |
| Claude | `claude` | `.claude/skills/graphify/` |
| OMP, Pi, Codex (any subset) | `agents`, one install | `.agents/skills/graphify/` |

`.agents/skills` is the one location all three discover: Codex scans it from the working directory to the repository root (OpenAI Codex skills docs); Pi lists `.agents/skills/` as a project skills location; OMP's `agents` provider loads it. Do not run `--platform codex` or `--platform pi`: `codex` also writes a `## graphify` section into `AGENTS.md` and `.codex/hooks.json`, and `pi` writes `.pi/agent/skills/`, which Pi's docs do not list as a project location (they list `.pi/skills/`). Graphify has no OMP platform; never pass `--platform omp`.

Run from the repository root, only for confirmed platforms, and only when `graphify install --help` lists the platform and `--project`:

```sh
graphify install --project --platform claude
graphify install --project --platform agents
```

Side effects observed in 0.9.72:

- `claude`: `.claude/skills/graphify/` (`SKILL.md`, `references/`, `.graphify_version`); `.claude/CLAUDE.md` (a `# graphify` skill registration); `CLAUDE.md` (a `## graphify` section); `.claude/settings.json` (Claude Code PreToolUse hooks; an existing file that changes is kept as `settings.json.graphify-bak`).
- `agents`: `.agents/skills/graphify/` only.
- Both: when a differing `SKILL.md` is replaced, the installer keeps one `SKILL.md.bak` of the previous copy.

Before the first install over an existing Graphify skill directory, copy its `SKILL.md` outside the repository (for example under `$TMPDIR`): the installer keeps only one rolling `SKILL.md.bak`, so a second install overwrites the backup of the original. The installer replaces the destination; afterwards compare it with the copy, re-apply real local customizations, or report them. Do not stage the `.bak` and `.graphify-bak` backups.

After each install, verify read-only that the printed destination `SKILL.md` exists and is non-empty, and that `references/` exists when the installer printed a `references` line. Do not follow that skill or run its initialization or extraction yet: that happens once, after sections 3 to 5, in [the full build](full-build.md). Diagnose install failures from actual output; never invent an initialization command.

## 3. Integration and git hooks

Inspect each install's output for the registrations it made (list above). `graphify install --project --platform claude` already runs `graphify claude install`; run a documented integration command only when a registration listed above is actually missing, preserve unrelated settings and hooks, and avoid duplicate Graphify entries. The Claude PreToolUse hook in `.claude/settings.json` is a Claude Code tool hook, not a git hook, and stays.

Register the merge driver, then remove the auto-rebuild git hooks that the same command also installs. The `post-commit` and `post-checkout` hooks rebuild after the commit, always leave `graph.json`, the report and the HTML dirty, and dirty the tree again on every branch switch, which causes pull/merge rework. The refresh before each commit (section 6) replaces them.

```sh
graphify hook install
```

This registers `merge.graphify.driver` in git config, writes `graphify-out/graph.json merge=graphify` to `.gitattributes`, and installs both hooks (appending to an existing hook file). Its output prints each hook file path.

### Remove the auto-rebuild hooks

Do this after every `graphify hook install`, and for hooks that already exist in a repository you are migrating.

1. Locate the hook files. Use the paths `graphify hook install` printed. When no install ran, run `git rev-parse --git-path hooks` from the repository root; it honors `core.hooksPath` and linked worktrees, so the files may not be under `.git/hooks`. When the directory's name is `_` (Husky 9), Graphify uses the parent directory, because the editable hooks live there.
2. In `post-commit`, delete the lines from `# graphify-hook-start` through `# graphify-hook-end` inclusive. In `post-checkout`, delete the lines from `# graphify-checkout-hook-start` through `# graphify-checkout-hook-end` inclusive. When `graphify hook install` appended to an existing hook file it inserted one blank separator line before the block; delete that line too, so a tracked hook file shows no stray diff. Delete the file only if just a shebang line and blank lines remain; otherwise keep all other content, any hook-manager configuration, and the rest of the hook unchanged.
3. Do not run `graphify hook uninstall`: it also removes the merge driver and the `.gitattributes` entry.
4. Run `graphify hook status`. Require `merge driver: registered`, and for each of `post-commit` and `post-checkout` a value that starts with `not installed`. The suffix `(hook exists but graphify not found)` is correct when another hook's content was kept. Any other value (`installed`, `installed (out of date ...)`, `partially registered ...`) means the removal or registration is incomplete: fix it and recheck.

## 4. Exclude machine-local output before building

Add these exact ignore patterns once, preserving existing `.gitignore` rules, before any extraction or build:

```gitignore
# Graphify local caches, intermediates, and costs
.graphify_cache/
graphify-out/**/cache/
graphify-out/**/.graphify_cache/
graphify-out/**/cost.json
graphify-out/**/.graphify_*
graphify-out/**/.needs_update
graphify-out/**/needs_update
graphify-out/**/.graph.html.stale
graphify-out/**/.graph.tmp.json
graphify-out/**/.vocab.txt
# manifest.json is keyed by file mtimes: different on every machine and run
graphify-out/manifest.json

# Graphify automatic dated backups of the previous graph (one folder per day)
graphify-out/20*/
```

Verify with Git: `git check-ignore -v -- graphify-out/manifest.json` must match, and `git check-ignore -v -- graphify-out/graph.json graphify-out/GRAPH_REPORT.md graphify-out/graph.html` must print nothing. If an existing rule ignores `graphify-out/` or one of the products, report the matching rule and ask before changing it; do not delete rules or add negations on your own.

Commit scope, when the user authorizes a commit:

- Within `graphify-out/`, commit only `graph.json`, `GRAPH_REPORT.md` and `graph.html` (when it exists), staged by exact path. Never stage anything else there: `manifest.json`, the dated backup folders `graphify-out/YYYY-MM-DD/` (Graphify copies the previous semantic or curated graph there before overwriting it), caches, `.graphify_*` files, cost records, and sidecars. Never `git add graphify-out`, `git add -A`, or `git add .`. If dated backup folders are already tracked, leave them tracked and untouched unless the user asks to untrack them.
- Setup also changes `.gitignore`, `.gitattributes`, `AGENTS.md`, `CLAUDE.md`, and the installed skill and config directories (`.claude/`, `.agents/`). Commit those only when the authorization names them, and stage them by exact path. Ignore the installer's printed broad `git add` hint.
- Keep the three graph products eligible for version control. If `manifest.json` or confirmed cache/cost files are tracked, remove only those exact paths from Git's index (for example `git rm --cached -- graphify-out/manifest.json`) and verify their local copies remain. Never untrack the graph products or delete local caches. Untracking is staged, not committed, until the user authorizes a commit.

## 5. Add persistent working rules

Read `AGENTS.md` and `CLAUDE.md` if present and preserve their content. Put the rules from [the merge workflow](merge-workflow.md#copy-ready-agentsmd-guidance) into `AGENTS.md` once, under the exact heading `## Graphify working rules`. Never put them under exactly `## graphify`: Graphify owns that heading in `AGENTS.md` and `CLAUDE.md` and replaces the whole section whenever an installer runs. If `AGENTS.md` is absent, create it with only these rules. Merge equivalent existing Graphify guidance into that section instead of duplicating it.

Leave an installer-written `## graphify` section (the Claude install adds one to `CLAUDE.md`) unedited; a reinstall rewrites it. The working rules say that they take precedence over it.

By default Claude Code reads `AGENTS.md` only when no `CLAUDE.md` exists (Claude Code memory docs), and the Claude install creates one. When Claude is a selected target, make sure `CLAUDE.md` contains the line `@AGENTS.md` (Claude Code's import syntax): create it with just that line if absent, otherwise add the line at the top only when missing. Do not copy the rules into `CLAUDE.md`, so there is one source of truth. If `CLAUDE.md` holds a hand-copied duplicate of the working rules, replace that duplicate with the import and keep everything else, including the installer's `## graphify` section. Do not create other harness-named context files.

Do not commit or push setup changes unless the user explicitly authorizes it. Preserve unrelated working-tree changes.

## 6. Refresh before commit (replaces the hooks)

When an authorized commit changes code the graph covers, pass the community-name guard, run the refresh, then commit sources and graph products together so the tree stays clean. Skip all of it for commits that change nothing the graph covers.

### Community-name guard

Run this before every `graphify update` or `graphify cluster-only`, here and in [the merge workflow](merge-workflow.md#ordinary-merge-procedure). When Graphify re-clusters (`cluster-only`, or `update` when the topology changed) it takes community names only from the machine-local, gitignored pair `graphify-out/.graphify_labels.json` and `graphify-out/.graphify_labels.json.sig`, not from the tracked `graph.json`; only its HTML-only reconcile reads the names persisted in `graph.json`. Without that pair, `update` replaces every curated name in `graph.json`, the report and the HTML with hub-derived names (such as `a.py`), and `cluster-only --no-label` replaces them with `Community N`. Neither command warns (observed in 0.9.72 on a scratch project). A fresh clone, a new worktree, and CI lack the pair.

1. If both files exist, continue. Graphify checks each community against its signature, keeps unchanged names, and renames a changed community by its hub, printing `community set changed since labeling ... renamed N community(ies) by their hub`.
2. If either file is missing, count the names that would be lost (`jq`, or any equivalent JSON query). If `graphify-out/graph.json` does not exist yet, there is no graph and nothing to lose: skip the query and continue. If the count is 0, continue.

   ```sh
   jq '[.nodes[] | (.community_name // empty) | select(test("^Community [0-9]+$") | not)] | length' graphify-out/graph.json
   ```

3. Otherwise stop before running the command, change nothing, and ask the user to restore both files together from a checkout that has them, or to approve hub-derived names. Never write the pair from `graph.json` names: without the `.sig` file Graphify trusts names by community count alone, and in a scratch test it kept a name on a community whose members had moved.
4. Around each command, save the distinct names and compare afterwards:

   ```sh
   names=$(mktemp -d)
   jq -r '[.nodes[] | .community_name // empty] | unique | .[]' graphify-out/graph.json > "$names/before.txt"
   # run the command, then:
   jq -r '[.nodes[] | .community_name // empty] | unique | .[]' graphify-out/graph.json > "$names/after.txt"
   LC_ALL=C comm -23 "$names/before.txt" "$names/after.txt"
   ```

   The last command prints names that were present and are now gone. Report them, and Graphify's `renamed N` message, for each command (`update`, and `cluster-only` in the merge workflow). Hub renames on a valid pair are Graphify's own validated behavior: report them, do not undo them.

### Refresh and stage

```sh
PYTHONHASHSEED=0 graphify update .
git add -- <changed sources> graphify-out/graph.json graphify-out/GRAPH_REPORT.md
if [ -f graphify-out/graph.html ] && git ls-files --error-unmatch -- graphify-out/graph.html >/dev/null 2>&1; then
  git add -- graphify-out/graph.html
fi
```

`update` is deterministic, local, and no-LLM. `PYTHONHASHSEED=0` keeps clustering stable on versions that do not pin it themselves. Doc/media semantic re-extraction is a separate explicit request. After a pull or merge, regenerate a conflicted report or HTML with the same command, not by hand.

`graph.html` is optional: Graphify skips or removes it when HTML is disabled or no useful community view exists. A routine commit stages it only when it exists and is already tracked, so a missing file cannot fail staging and an untracked one is not added. The initial setup commit adds it when the build wrote it.

If `update` refuses (it prints `Refusing to overwrite`, or exits non-zero), do not add `--force` or set `GRAPHIFY_FORCE=1`, and do not stage graph files from that run. Report the exact message and ask the user how to proceed.

## 7. Migrate an existing setup

For a repository that already uses Graphify. No skill install, no harness selection, no full build, no LLM work. Preserve unrelated changes and never commit or push without authorization.

1. Confirm `graphify-out/graph.json` exists and `graphify --help` works. Run `graphify hook status` and record the starting state.
2. Remove the auto-rebuild hooks, keeping the merge driver, as in [Remove the auto-rebuild hooks](#remove-the-auto-rebuild-hooks). If the merge driver is not registered, run `graphify hook install` first, then remove the two hooks. Keep other hooks.
3. Ensure `.gitattributes` contains `graphify-out/graph.json merge=graphify` (the install writes it).
4. In `.gitignore`, add the missing lines from section 4, in particular `graphify-out/manifest.json`, and run its Git ignore checks. Preserve existing rules.
5. If `graphify-out/manifest.json` is tracked, run `git rm --cached -- graphify-out/manifest.json`. The local file stays. Leave it staged, not committed.
6. Make sure `AGENTS.md` carries the current rules from [the merge workflow](merge-workflow.md#copy-ready-agentsmd-guidance) under `## Graphify working rules`: the three-product allowlist, no manifest, no auto-rebuild hooks, refresh before commit. Replace the old wording instead of duplicating it, and leave any installer-written `## graphify` section unedited. If Claude is used in this repository (a `CLAUDE.md` exists or `claude` is available), make sure `CLAUDE.md` imports `@AGENTS.md` as in section 5.
7. Verify: `graphify hook status` passes the check in [Remove the auto-rebuild hooks](#remove-the-auto-rebuild-hooks); `git check-ignore -v graphify-out/manifest.json` matches; `git ls-files graphify-out` lists no manifest; a real `graphify query` works. Report the before/after state and the staged and unstaged changes. Do not stage graph regeneration the migration did not cause.
