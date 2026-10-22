# Runtime initialization, full build, and verification

Read this reference for an explicitly requested initial full Graphify build, after sections 2 to 5 of [the setup instructions](setup-project.md) are complete. It does not govern routine updates or merge hooks. For those, use [the bounded merge workflow](merge-workflow.md), not full-project extraction or completeness checks. A missing or checkout-specific manifest/cache does not authorize a full build. Broader semantic rebuilding or enrichment requires a separate explicit request.

Within the authorized build scope, follow the installed Graphify `SKILL.md` for exact runtime initialization, corpus detection, extraction, exclusions, and final presentation. The installed skill and CLI help for the actual version take precedence over remembered commands, not over the requested scope.

## Before any extraction

All of these must hold. If one does not, finish that setup section first: extraction before the ignore rules exist writes untracked machine-local output, and extraction must not be repeated later.

1. The installed skill was verified read-only (setup section 2).
2. `graphify hook status` passes the check in [Remove the auto-rebuild hooks](setup-project.md#remove-the-auto-rebuild-hooks).
3. The ignore rules are in place and their Git checks pass (setup section 4).
4. The persistent working rules are written (setup section 5).

## Run the complete build

Run it once, for the active host only. Do not initialize or extract from a second installed copy of the skill.

1. Choose the one copy to read and invoke: the skill that the active host's own skill listing shows under the bare name `graphify`, at the path it reports. Expect `.claude/skills/graphify/SKILL.md` in Claude Code and `.agents/skills/graphify/SKILL.md` in Pi and Codex. OMP discovers both directories; when both are installed its docs rank the Claude copy above the `agents` copy, so the bare `graphify` it lists is normally the `.claude` copy. Read that file and initialize its runtime/output state exactly as documented. Never read one copy and invoke another.
2. Before starting, tell the user that a full graph build can take time, especially for large codebases.
3. Invoke that same listed `graphify` skill through the host agent's native skill-invocation mechanism for the repository. Do not send its invocation token as a shell command. Use the documented full-project invocation, not a subfolder.
4. Perform semantic extraction in the active harness. Do not require an API key, switch to headless CLI extraction, or take the installed skill's `GEMINI_API_KEY`/`GOOGLE_API_KEY` provider branch (`extract_corpus_parallel(backend="gemini")`) even when a key is set: it sends the corpus to a third-party API. Use the host-agent branch.
5. Follow the installed workflow's order: run its documented corpus-detection step under the harness's direction, present and handle any size warning before extraction, then complete extraction and graph generation. Do not invent `graphify detect`; a reviewed skill version uses the Python corpus detector `graphify.detect.detect()`, but the installed version is authoritative. A warning is not a terminal-command failure.
6. The reviewed skill version warns above 500 files or 2,000,000 words. These are version-specific warning thresholds, not universal CLI limits. Preserve existing exclusions and the entire project-owned corpus. Do not override Graphify's sensitive-file skipping (`skipped_sensitive`): report the skipped file names as the installed skill instructs.

## Handle a real file-count error

Only use this recovery when the installed skill's warning requires a decision or an actual terminal command reports a file-count error:

1. Inspect the directory tree recursively at all relevant depths. Use `tree -a -d` when available, otherwise `find . -type d`; do not use depth limits. Inspect candidate directories and distinguish bundled third-party/vendor code (including bundled Java or Node dependencies) and embedded frameworks from project-owned source.
2. Exclude only confirmed vendor/dependency/framework content, using the installed version's documented exclusion mechanism. Preserve prior exclusions. Do not delete files, exclude project code because it uses Java or Node, or narrow the build to an arbitrary subset.
3. After changing exclusions, rerun only the installed skill's corpus-detection step or the exact underlying command that failed, not the entire skill invocation. Let Graphify report the remaining count; do not manually recount. If it still exceeds 1,500 files, tell the user the full project may take longer, then continue extraction/build for the entire project-owned corpus. Do not ask again or narrow scope.
4. If a build command fails, inspect `graphify --help` and the failing subcommand's `--help` when supported. Use a documented recovery for the actual error. Do not invent a size-override flag or use `--force` just to bypass a warning; Graphify documents force for rescanning/shrink-guard cases, not as a file-count override. Complete the full build without silently dropping project-owned files or calling a partial graph complete.

## Verify and report

Confirm that `graphify-out/graph.json` and `GRAPH_REPORT.md` exist and are current. `graph.html` is optional: Graphify skips or removes it when HTML is disabled or no useful community view exists. Report whether it was written, and never fail the build for its absence. Verify `graphify hook status` passes the hook check above. Inspect `.gitignore` and use Git's ignore/tracking checks to confirm `manifest.json`, cache and cost files are ignored and untracked while the graph products that exist remain eligible for tracking. Report any other untracked `graphify-out/` file the ignore rules do not cover, and do not stage it. Preserve all unrelated changes.

Exercise the generated graph with:

```sh
graphify query "What are the main architectural hubs and surprising cross-module relationships?"
```

Follow the installed skill's final presentation guidance, including interesting findings; avoid duplicating its completion summary. Report actual blockers and whether the full project-owned corpus was completed. Do not commit or push without explicit authorization.
