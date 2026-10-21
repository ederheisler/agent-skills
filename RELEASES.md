# Release schema

This file is the authoritative release schema for this repository. The repository uses [Semantic Versioning](https://semver.org/) with tags named `vX.Y.Z`.

## Baseline

`1.2.0` is the published baseline (tag `v1.2.0`). The latest `vX.Y.Z` tag on GitHub is the source of truth. The root [`VERSION`](VERSION) file only mirrors it and is updated automatically.

## What releases

Only a change to the content of `skills/**` releases. This includes `SKILL.md`, readmes, references, and every other file under a skill. Skills are prose, so a wording change is a skill change. The commit prefix does not matter: `docs:` or `chore:` on a skill file still releases.

These do not release and do not create a tag:

- Root docs: `README.md`, `RELEASES.md`, `CHANGELOG.md`.
- `VERSION`.
- CI files under `.github/`.
- The automatic metadata commit.

The workflow compares `skills/**` at the push with `skills/**` at the latest tag. If there is no net difference, it does nothing. This includes changes that were made and then reverted. The workflow can run on every push to `main`, but a run with no net skill change ends without a new version, tag, or release.

## Bump size

Each commit that touches `skills/**` since the latest tag sets a bump. The highest bump wins. Commits that touch only root files are ignored, even if their header says `feat!:`.

| Bump | Commit | Example | Result from `1.2.0` |
|---|---|---|---|
| Major | `type!:` or `type(scope)!:` header, or a `BREAKING CHANGE:` or `BREAKING-CHANGE:` trailer in the body | `feat(wtf)!: rename command` | `2.0.0` |
| Minor | `feat:` or `feat(scope):` | `feat(wtf): add option` | `1.3.0` |
| Patch | Anything else, including fixes and messages with no prefix | `fix: correct wording` | `1.2.1` |

A higher bump resets the lower numbers. Patch is the default, so nobody must choose a version by hand.

## Pushes in a queue

If several pushes wait, they share one release. The highest bump of all their skill commits is used, measured from the latest tag.

## What the workflow publishes

When a skill change is found, the workflow:

1. Calculates the next version.
2. Updates `VERSION` and `CHANGELOG.md` in an automatic commit.
3. Pushes the commit and the `vX.Y.Z` tag together.
4. Creates the GitHub Release with the changelog notes.

If a run fails, a later run recovers from the latest tag.

## What is not used

- No manual release step.
- No comparison of per-skill versions. Each skill keeps its own version in its own metadata, independent of the repository version.
- No npm publication or npm dependency.

## Effect on installs

The `skills` CLI updates from the content of each installed skill, not from `VERSION`, tags, or Releases. A normal install follows the source branch. An install pinned to a tag or other ref stays on that ref. Tags and Releases are for tracking and pinning.
