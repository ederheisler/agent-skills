# Runtime initialization, full build, and verification

Read this reference after project installation for an explicitly requested initial full Graphify build. It does not govern routine updates or merge hooks. For those, use [the bounded merge workflow](merge-workflow.md), not full-project extraction or completeness checks. A missing or checkout-specific manifest/cache does not authorize a full build. Broader semantic rebuilding or enrichment requires a separate explicit request.

Within the authorized build scope, follow the installed Graphify `SKILL.md` for exact runtime initialization, corpus detection, extraction, exclusions, and final presentation. The installed skill and CLI help for the actual version take precedence over remembered commands, not over the requested scope.

## Run the complete build

1. Read the verified installed skill for the active host and initialize its runtime/output state exactly as documented.
2. Before starting, tell the user that a full graph build can take time, especially for large codebases.
3. Invoke the installed Graphify skill through the host agent's native skill-invocation mechanism for the repository. Do not send its invocation token as a shell command. Use the documented full-project invocation, not a subfolder. Perform semantic extraction in the active harness; do not require a separate API key or switch to headless CLI extraction.
4. Follow the installed workflow's order: run its documented corpus-detection step under the harness's direction, present and handle any size warning before extraction, then complete extraction and graph generation. Do not invent `graphify detect`; a reviewed skill version uses the Python corpus detector `graphify.detect.detect()`, but the installed version is authoritative. A warning is not a terminal-command failure.
5. The reviewed skill version warns above 500 files or 2,000,000 words. These are version-specific warning thresholds, not universal CLI limits. Preserve existing exclusions and the entire project-owned corpus.

## Handle a real file-count error

Only use this recovery when the installed skill's warning requires a decision or an actual terminal command reports a file-count error:

1. Inspect the directory tree recursively at all relevant depths. Use `tree -a -d` when available, otherwise `find . -type d`; do not use depth limits. Inspect candidate directories and distinguish bundled third-party/vendor code (including bundled Java or Node dependencies) and embedded frameworks from project-owned source.
2. Exclude only confirmed vendor/dependency/framework content, using the installed version's documented exclusion mechanism. Preserve prior exclusions. Do not delete files, exclude project code because it uses Java or Node, or narrow the build to an arbitrary subset.
3. After changing exclusions, rerun only the installed skill's corpus-detection step or the exact underlying command that failed—not the entire skill invocation. Let Graphify report the remaining count; do not manually recount. If it still exceeds 1,500 files, tell the user the full project may take longer, then continue extraction/build for the entire project-owned corpus. Do not ask again or narrow scope.
4. If a build command fails, inspect `graphify --help` and the failing subcommand's `--help` when supported. Use a documented recovery for the actual error. Do not invent a size-override flag or use `--force` just to bypass a warning; Graphify documents force for rescanning/shrink-guard cases, not as a file-count override. Complete the full build without silently dropping project-owned files or calling a partial graph complete.

## Verify and report

Confirm that the expected `graphify-out/graph.json`, `GRAPH_REPORT.md`, and `graph.html` exist and are current. Verify `graphify hook status` shows `post-commit: not installed`, `post-checkout: not installed`, and `merge driver: registered`; inspect `.gitignore` and use Git's ignore/tracking checks to confirm `manifest.json`, cache and cost files are ignored and untracked while the three graph products remain eligible for tracking. Preserve all unrelated changes.

Exercise the generated graph with:

```sh
graphify query "What are the main architectural hubs and surprising cross-module relationships?"
```

Follow the installed skill's final presentation guidance, including interesting findings; avoid duplicating its completion summary. Report actual blockers and whether the full project-owned corpus was completed. Do not commit or push without explicit authorization.