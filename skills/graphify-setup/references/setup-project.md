# Installing Graphify in a project

Use the current official instructions at <https://docs.graphify.com/installation> and the installed CLI's own `--help` output. CLI support and destinations can change; do not assume flags, paths, or integrations from an older version.

## 1. Prepare the CLI

1. Check `uv --version`. If `uv` is absent, on macOS use `brew install uv` when Homebrew is available; otherwise (Linux or macOS without Homebrew) use the official installer `curl -LsSf https://astral.sh/uv/install.sh | sh`. If `uv` exists but errors for another reason, diagnose that failure instead of reinstalling it.
2. Follow the selected install method's actual shell/PATH instructions. Verify `uv --version` before continuing.
3. Install the official package `graphifyy` with `uv tool install graphifyy`. If already installed, reuse it. Run `graphify --help` in the current shell.
4. If `graphify` is not found, run `uv tool dir --bin`; add that returned directory to this session's `PATH`, not a guessed location. Run `uv tool update-shell` for future shells and follow its actual output. Retry `graphify --help` and require success. If found but fails, diagnose that error rather than changing `PATH`.
5. Read `graphify install --help` and the relevant platform/integration help before installing. Use documented commands only; never infer unsupported commands or options.

## 2. Select only explicitly requested available harnesses

The target set for this setup is OMP, Pi, Codex, and Claude. Determine which are available from the active harness plus local executable/config evidence. Report the available and unavailable targets, then ask the user which available targets to initialize. Offer `All`, meaning all detected available targets and never unavailable ones, or allow one or more named available targets. Do not install anything until the user explicitly selects targets. If no targets are available, report that as a blocker and do not run any platform install.

Do not install for unrelated platforms or rely on the CLI's bare install default as discovery: some versions default to one platform based on the operating system and do not detect installed assistants. Never run a bare `graphify install`; install only explicitly selected targets, never unselected targets.

Use Graphify's own availability discovery only if the installed version's help documents it and it can check the target set above without installing. Otherwise determine availability locally. After the user selects targets, install once per selected platform; the CLI accepts one platform per invocation, not a list or multiple distinct `--platform` flags. For every selected target confirm `--project` is supported before using it:

| Available target | Graphify platform |
| --- | --- |
| Claude | `claude` |
| Codex | `codex` |
| Pi | `pi` |
| OMP | `agents` (the generic Agent-Skills location, compatible with OMP's `.agent[s]/skills` provider; Graphify has no OMP-specific platform) |

For example, the explicit project-scoped commands are `graphify install --project --platform claude`, `graphify install --project --platform codex`, `graphify install --project --platform pi`, and `graphify install --project --platform agents`. Run only the commands for explicitly selected targets and only when the installed CLI lists that platform. Never pass `--platform omp`. If an installed CLI lacks a needed target, report the gap and use only a documented compatible platform mapping.

Before each install, inspect the destination printed by the installer or determined from its current documentation. If the destination already contains a Graphify skill, read/reuse it and avoid overwriting custom changes unknowingly. Preserve unrelated configuration and existing hooks. After each successful install, use the printed destination; verify its `SKILL.md` exists before reading it. Read each newly installed skill and follow its initialization and extraction instructions. Diagnose install failures or missing files from actual output; do not invent a separate initialization command.

## 3. Verify platform integration

Inspect each install's output for platform-specific registrations. For the selected platform, consult its installed `graphify --help`/subcommand help and official instructions. Run a documented project-scoped integration command only when the Graphify integration is actually missing; preserve unrelated settings and hooks, avoid duplicate Graphify entries, and verify the result. Skill-only platforms need no invented extra integration. Do not read or create harness-named context files; persistent repository guidance belongs in the generic `AGENTS.md`.

Independently install and verify the Graphify merge driver, then remove the auto-rebuild hooks. The `post-commit` and `post-checkout` hooks rebuild after the commit, always leave `graph.json`, the report and the HTML dirty, and dirty the tree again on branch switches, which causes pull/merge rework. The deterministic refresh before each commit (section 6) replaces them.

```sh
graphify hook install
```

`graphify hook install` registers the `graphify-out/graph.json merge=graphify` driver and writes `.gitattributes`, but also installs the two hooks. Remove only those hooks afterwards: delete `.git/hooks/post-commit` and `.git/hooks/post-checkout` when each contains only the `# graphify-hook-start … # graphify-hook-end` block; otherwise remove only that block and keep the rest. Do not run `graphify hook uninstall`: it also removes the merge driver and `.gitattributes` entry. Then run `graphify hook status` and require `post-commit: not installed`, `post-checkout: not installed`, and `merge driver: registered`. If the project already has the hooks installed, apply the same removal. Preserve existing non-Graphify Git hooks and hook-manager configuration.

## 4. Exclude machine-local output before building

Add these exact ignore patterns once, preserving existing `.gitignore` rules:

```gitignore
# Graphify local caches, intermediates, and costs
.graphify_cache/
graphify-out/**/cache/
graphify-out/**/.graphify_cache/
graphify-out/**/cost.json
graphify-out/**/.graphify_*
graphify-out/**/.needs_update
graphify-out/**/needs_update
# manifest.json is keyed by file mtimes: different on every machine and run
graphify-out/manifest.json

# Graphify automatic dated backups of the previous graph (one folder per day)
graphify-out/20*/
```

Commit allowlist: only `graph.json`, `GRAPH_REPORT.md` and `graph.html` are ever committed, staged by exact path. Everything else in `graphify-out/` is ignored and never staged, including `manifest.json`, the dated backup folders `graphify-out/YYYY-MM-DD/` (Graphify copies the previous semantic or curated graph there before overwriting it), caches, `.graphify_*` files, cost records, and sidecars. Never `git add graphify-out`, `git add -A`, or `git add .`. If dated backup folders are already tracked, leave them tracked and untouched unless the user asks to untrack them.

Keep `graphify-out/graph.json`, `graphify-out/GRAPH_REPORT.md`, and `graphify-out/graph.html` eligible for version control. If `manifest.json` or confirmed cache/cost files are tracked, remove only those exact paths from Git's index (for example, `git rm --cached -- graphify-out/manifest.json`); verify their local copies remain. Never untrack the three graph products or delete local caches. Untracking is staged, not committed, until the user authorizes a commit.

## 5. Add generic persistent working rules

Read `AGENTS.md` if present, preserve its content, and avoid duplicate Graphify guidance. Add or update the Graphify query, generated-artifact, and merge/recovery rules from [the merge workflow](merge-workflow.md). Do not add platform-specific instructions to a harness-named context file. If `AGENTS.md` is absent, create only the generic file needed for the requested persistent rules.

Do not commit or push setup changes unless the user explicitly authorizes it. Preserve unrelated working-tree changes.

## 6. Refresh before commit (replaces the hooks)

When an authorized commit changes code the graph covers, run the refresh first, then commit sources and graph products together so the tree stays clean:

```sh
PYTHONHASHSEED=0 graphify update .
git add -- <changed sources> graphify-out/graph.json graphify-out/GRAPH_REPORT.md graphify-out/graph.html
```

`update` is deterministic, local, no-LLM and takes about 2 seconds. Skip the refresh for commits that change nothing the graph covers. Doc/media semantic re-extraction is a separate explicit request. After a pull or merge, a conflicted report or HTML is regenerated with the same command, not hand-merged.

## 7. Migrate an existing setup

For a repository that already uses Graphify. No skill install, no harness selection, no full build, no LLM work. Preserve unrelated changes and never commit or push without authorization.

1. Confirm `graphify-out/graph.json` exists and `graphify --help` works. Run `graphify hook status` and record the starting state.
2. Remove the auto-rebuild hooks, keeping the merge driver, exactly as in section 3. Do not run `graphify hook uninstall`. If the merge driver is not registered, run `graphify hook install` first, then remove the two hooks. Remove only Graphify's own hook content; keep other hooks.
3. Ensure `.gitattributes` contains `graphify-out/graph.json merge=graphify` (the install writes it).
4. In `.gitignore`, add the missing lines from section 4, in particular `graphify-out/manifest.json`. Preserve existing rules.
5. If `graphify-out/manifest.json` is tracked, run `git rm --cached -- graphify-out/manifest.json`. The local file stays. Leave it staged, not committed.
6. Make sure `AGENTS.md` carries the current rules from [the merge workflow](merge-workflow.md): the three-file allowlist, no manifest, no auto-rebuild hooks, refresh before commit. Replace the old wording instead of duplicating it.
7. Verify: `graphify hook status` shows `post-commit: not installed`, `post-checkout: not installed`, `merge driver: registered`; `git check-ignore -v graphify-out/manifest.json` matches; `git ls-files graphify-out` lists no manifest; a real `graphify query` works. Report the before/after state and the staged and unstaged changes. Do not stage graph regeneration the migration did not cause.