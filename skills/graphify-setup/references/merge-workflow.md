# Persistent Graphify merge and artifact rules

## Contents

- [When these rules apply](#when-these-rules-apply)
- [Copy-ready AGENTS.md guidance](#copy-ready-agentsmd-guidance)
- [Ordinary merge procedure](#ordinary-merge-procedure)
- [Recovery boundaries](#recovery-boundaries)

## When these rules apply

Use this reference when adding persistent Graphify working rules to a repository's `AGENTS.md`, or when a user asks to merge branches in a project that already uses Graphify. Keep the rules in `AGENTS.md` only, under the exact heading `## Graphify working rules`; never put them under exactly `## graphify`, which Graphify's installers own and rewrite wholesale. When Claude is used, `CLAUDE.md` imports them with `@AGENTS.md` (see the setup instructions) instead of repeating them. Do not create other harness-named context files. Preserve existing `AGENTS.md` and `CLAUDE.md` content (including an installer-written `## graphify` section, which you leave unedited) and merge equivalent guidance rather than duplicating it. Do not initialize Graphify solely to enable these merge rules; a direct, explicit setup request is different.

Add the guidance below to `AGENTS.md` without changing unrelated instructions. Keep routine updates and merge hooks bounded and deterministic. The full-build reference applies only to explicitly requested builds, not ordinary integration.

## Copy-ready AGENTS.md guidance

When `graphify-out/graph.json` exists, use `graphify query "<question>"` first for architecture, relationships, ownership, flow, and content questions. Use `graphify path` or `graphify explain` for focused exploration, then inspect exact source locations as needed. These working rules take precedence over any installer-written `## graphify` section, such as its "run `graphify update .` after modifying code" and "dirty graphify-out/ files are expected after hooks" lines.

Treat useful Graphify artifacts produced by a task as part of that task's work. Within `graphify-out/`, include only task-related changes to the tracked `graph.json`, `GRAPH_REPORT.md`, and `graph.html` (when it exists) in an authorized commit, staged by exact path; never include `manifest.json` (machine-local, gitignored, untracked), unrelated graph changes, caches, cost records, or machine-local sidecars. Graphify's auto-rebuild hooks (post-commit/post-checkout) are not kept, because they leave the tree dirty; refresh before committing instead: run `PYTHONHASHSEED=0 graphify update .` when the commit changes code the graph covers, then stage sources and the graph files together by exact path. Before `graphify update` or `graphify cluster-only`, check that the machine-local files `graphify-out/.graphify_labels.json` and `graphify-out/.graphify_labels.json.sig` both exist: without them Graphify silently replaces curated community names in `graph.json`, the report and the HTML, so stop and ask the user unless the graph has no non-placeholder names. If `update` refuses to overwrite, do not use `--force` or stage graph files; report the message and ask. Include task-related changes to the `.gitattributes` merge-driver entry when applicable. Do not add Graphify to a project that does not already use it unless the user explicitly requests setup. In an existing Graphify project, repair a missing merge-driver registration with `graphify hook install`, then remove the two Graphify git hooks it adds again, preserving other hooks and the merge driver: in the directory `git rev-parse --git-path hooks` prints (its parent when the directory is named `_`, as with Husky 9), delete the block from `# graphify-hook-start` through `# graphify-hook-end` in `post-commit` and from `# graphify-checkout-hook-start` through `# graphify-checkout-hook-end` in `post-checkout`, never run `graphify hook uninstall`, and require `graphify hook status` to show `merge driver: registered` and values starting with `not installed` for both hooks.

Do not hand-edit generated Graphify conflict markers or resolve `graph.json` by blanket-selecting `--ours` or `--theirs`. The registered Graphify union merge driver runs during `git merge`, before the merge commit, and handles only `graph.json`. Hooks are not conflict resolvers, and there is no post-merge hook.

Ordinary recovery uses one bounded deterministic refresh against the settled merge target. Keep both valid graph inputs available until recovery succeeds. Preserve/reuse valid extraction caches/chunks. Document/media changes do not authorize `/graphify --update`, LLM extraction, corpus-wide document/media reads, community relabeling, completeness audits, or repeated extraction/refresh cycles. A missing or checkout-specific manifest/cache does not authorize a whole-corpus semantic rebuild.

If semantic work is explicitly requested, scope it to actual task/source changes using merge/source deltas. Changed hashes or absolute checkout paths alone do not establish new content. Broader semantic rebuilding or enrichment is a separate explicitly requested task, not a merge-completion gate. Report semantic freshness limitations without claiming unverified parity or freshness.

Determine recovery scope from the existing merge's actual changed/deleted source paths and graph metadata/provenance. Cache hashes, absolute checkout-path differences, and the union's overall corpus do not add investigation scope.

Verify preservation mechanically against both valid union inputs, using graph node/edge IDs or provenance for affected paths. Reconcile actual deleted source paths against provenance. Preserve nodes/edges supported by surviving sources, including multi-source content. Do not blindly drop shared graph content or invent semantic replacements.

Do not re-read source bodies, inspect functions/queries, invoke codebase exploration/search/LSP, connect to databases, or run semantic completeness comparisons for recovery. Do not change application code merely to satisfy graph recovery. Reading exact source conflict hunks to resolve a real Git conflict remains permitted. Graph work must not expand that separate source-resolution task. These recovery boundaries override the general Graphify exploration guidance above.

If provenance is missing/ambiguous or deletion reconciliation cannot be mechanical, preserve inputs and the paused merge. Report the exact affected path and metadata blocker. Do not claim deletion correctness or silently widen scope. Broader semantic investigation requires separate explicit authorization.

A Graphify worker's contract must name its owned graph files, allowed recovery commands, mechanical completion checks, and excluded source/code/query work. The coordinator must stop/cancel an out-of-scope worker, not accept its expanded task or allow more rounds.

## Ordinary merge procedure

Use this recipe only for an authorized ordinary branch merge:

1. Before merging, check whether the project already uses Graphify. If not, skip this Graphify-specific procedure and proceed with the authorized ordinary merge without introducing Graphify. Otherwise run `graphify hook status`; inspect the tracked `.gitattributes` entry `graphify-out/graph.json merge=graphify` and the local Git driver registration. Require the state that step 4 of [Remove the auto-rebuild hooks](setup-project.md#remove-the-auto-rebuild-hooks) defines. If the driver is missing, run `graphify hook install`, then remove the two Graphify hooks again as that section describes; rerun status and verify driver registration. If the command is unavailable, locate the existing installation and use its actual executable path; do not treat a missing driver as a blocker when the install command can repair it. Include any task-related `.gitattributes` change in the authorized commit.
2. Run `git merge <branch>`. If it pauses with conflicts, keep the merge in progress and resolve source-code/document conflicts first.
3. If `graphify-out/graph.json` is conflicted, diagnose the driver's configuration and actual error, then merge both graph versions with the driver. Do not choose one side. Before regeneration, ensure the graph is valid JSON and contains no conflict markers.

   If markers remain in `graph.json`, do not update or cluster it. Recover clean versions from Git's unmerged index, not the conflict-marked working copy. For an ordinary merge where stages 1, 2, and 3 all exist:

   ```sh
   recovery_dir=$(mktemp -d)
   git show :1:graphify-out/graph.json > "$recovery_dir/base.json" &&
   git show :2:graphify-out/graph.json > "$recovery_dir/current.json" &&
   git show :3:graphify-out/graph.json > "$recovery_dir/other.json" &&
   graphify merge-driver "$recovery_dir/base.json" "$recovery_dir/current.json" "$recovery_dir/other.json" &&
   cp "$recovery_dir/current.json" graphify-out/graph.json
   ```

   The driver writes its result to `current.json`; copy it back only if the driver succeeds. Validate the resulting JSON before continuing, and stage the final regenerated graph later in step 6. Keep the temporary inputs until recovery succeeds; then remove only that temporary directory. If an index stage is missing (for example, add/add or modify/delete), or a stage contains invalid JSON, inspect that specific conflict and the installed driver's behavior; do not run the three-stage recipe blindly. If the driver fails, retain the paused merge and clean inputs, diagnose its actual error, and do not remove markers by hand or discard either graph. Regeneration must wait until graph input is valid.
4. For each conflicted derived file only (`GRAPH_REPORT.md`, `graph.html`), choose a valid temporary baseline with `git checkout --ours -- <exact-file-path>` or `--theirs` when that is the valid side. Regenerate derived files before staging. If a legacy tracked `manifest.json` conflicts, untrack it (`git rm --cached -- graphify-out/manifest.json`) and keep it gitignored instead of resolving it. Preserve reusable caches/chunks without forcing semantic extraction. Never apply this to `graph.json`, unrelated files, or the whole output directory.
5. While the merge remains paused and `graph.json` is valid (step 3), pass the [community-name guard](setup-project.md#community-name-guard) before running anything below. When the guard says stop, stop with the merge paused. Then run this sequence once against the settled sources and the unioned graph. First the code refresh, saving and comparing community names around it as guard step 4 describes:

   ```sh
   PYTHONHASHSEED=0 graphify update .
   ```

   `update` is a local code/AST refresh without an LLM. It preserves existing semantic nodes but cannot recreate semantic data discarded by choosing one side; do not use it as a substitute for retaining data from both valid union inputs. With a valid label pair it keeps unchanged community names and renames only changed communities by hub; without the pair it replaces every name with a hub name, which is why the guard comes first.

   Then regenerate the report without LLM community labeling. Copy `graph.json`, `GRAPH_REPORT.md` and `graph.html` (when present) to a temporary directory, save the names again, and run:

   ```sh
   PYTHONHASHSEED=0 graphify cluster-only . --no-label
   ```

   `cluster-only` also rewrites `graph.html`; do not run a separate `graphify export html`. When the label pair is missing, `--no-label` writes `Community N` for every community. Count placeholder names before and after, for example with `jq '[.nodes[] | (.community_name // empty) | select(test("^Community [0-9]+$"))] | length' graphify-out/graph.json`. If the count rose, restore the three copies, stage nothing from this step, and report the counts. Compare the saved names as in guard step 4 and report any that are gone.
6. Verify valid JSON, no conflict markers, the mechanical preservation/deletion checks above, and current deterministic derived artifacts. A graph union is not a base-aware deletion merge. Explicitly stage task-related tracked artifacts:

   ```sh
   git add -- graphify-out/graph.json graphify-out/GRAPH_REPORT.md
   ```

   Add `graphify-out/graph.html` only when it exists and is tracked, using the `if` check from [section 6 of the setup instructions](setup-project.md#6-refresh-before-commit-replaces-the-hooks) so a missing optional file cannot fail staging. Never stage `manifest.json`. Stage resolved source files separately.
7. Run `git diff --name-only --diff-filter=U` and require no unresolved files. With step 6 satisfied, recovery is complete. Stop recovery work and complete the authorized merge with `git merge --continue`. Do not perform optional work after acceptance or leave stale temporary derived baselines.

## Recovery boundaries

If deterministic recovery fails or proposes unexpectedly broad work, preserve inputs and the paused merge. Report the exact failed command/error or scope blocker. Do not silently escalate to more agents, full rebuilds, retry loops, repeated refreshes, or repeated reviews. Do not bypass failures with `--force`, hide invalid JSON or unresolved source conflicts, or discard graph content. Never commit or push without explicit authorization; preserve unrelated working-tree changes.