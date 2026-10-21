#!/usr/bin/env bash
# Automatic release: pick the next version, update VERSION and CHANGELOG.md,
# commit, tag, push, and publish a GitHub Release with the same notes.
#
#   release.sh            Release (GitHub Actions only).
#   release.sh --dry-run  Plan from the local checkout and print the version,
#                         release notes, and CHANGELOG.md diff. No fetch, no gh
#                         call, no change to the repository, no commit/tag/push/release.
#
# Version rules (VERSION is the repository version, tags are the release record):
#   - No version tag yet: release the version in VERSION (first release).
#   - VERSION is ahead of the latest tag: release VERSION as written.
#   - Otherwise: release the latest tag with its patch number plus one.
# Commits that only touch VERSION or CHANGELOG.md never count as changes, so a
# checkout with no other commit since the latest tag releases nothing.
#
# Failure recovery: the release commit and tag are pushed together (atomic),
# then the GitHub Release is created. If that last step fails, the next run
# publishes the missing Release for the latest tag before it plans anything new.
set -euo pipefail

BOT_NAME='github-actions[bot]'
BOT_EMAIL='41898282+github-actions[bot]@users.noreply.github.com'
SEMVER_RE='^[0-9]+\.[0-9]+\.[0-9]+$'
MAX_ATTEMPTS=5
RETRY=0
PREV_TAG=''
NEW_TAG=''
NEW_VERSION=''
OUT=''

die() {
  echo "::error::$*" >&2
  exit 1
}

repo_url() {
  if [ -n "${GITHUB_REPOSITORY:-}" ]; then
    echo "${GITHUB_SERVER_URL:-https://github.com}/$GITHUB_REPOSITORY"
  else
    git remote get-url origin | sed -E 's#^git@([^:]+):#https://\1/#; s#\.git$##'
  fi
}

# Highest vMAJOR.MINOR.PATCH tag, or nothing.
latest_tag() {
  git tag --list 'v[0-9]*' | { grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' || true; } |
    sort -t. -k1.2,1n -k2,2n -k3,3n | tail -n1
}

# True when $1 is a higher MAJOR.MINOR.PATCH than $2.
ver_gt() {
  [ "$1" != "$2" ] &&
    [ "$(printf '%s\n%s\n' "$1" "$2" | sort -t. -k1,1n -k2,2n -k3,3n | tail -n1)" = "$1" ]
}

# Strip leading and trailing blank lines from stdin.
trim_blank() {
  awk '{ l[NR] = $0 } NF { if (!first) first = NR; last = NR } END { for (i = first; i && i <= last; i++) print l[i] }'
}

# Print the body of the "## [$1](...)" section of the CHANGELOG.md on stdin.
section_notes() {
  awk -v h="## [$1](" 'index($0, h) == 1 { on = 1; next } on && /^## / { exit } on' | trim_blank
}

release_exists() {
  local out
  if out=$(gh api "repos/$GITHUB_REPOSITORY/releases/tags/$1" --silent 2>&1); then
    return 0
  fi
  case $out in
    *'HTTP 404'*) return 1 ;;
  esac
  die "Cannot check for a GitHub Release for $1: $out"
}

# Decide what to release. Sets NEW_TAG (empty when there is nothing to release),
# NEW_VERSION and PREV_TAG, and writes $OUT/{VERSION,CHANGELOG.md,NOTES.md}.
plan() {
  local current prev commits url today compare src unreleased pre rest
  local major minor patch sha subject

  NEW_TAG=''
  [ -f VERSION ] || die 'VERSION file is missing'
  current=$(tr -d '[:space:]' <VERSION)
  [[ $current =~ $SEMVER_RE ]] || die "VERSION must be MAJOR.MINOR.PATCH, got '$current'"

  PREV_TAG=$(latest_tag)
  commits=$(git log --no-merges --full-history --format='%H%x09%s' \
    ${PREV_TAG:+"$PREV_TAG..HEAD"} -- . ':(exclude)VERSION' ':(exclude)CHANGELOG.md')
  [ -n "$commits" ] || return 0

  if [ -z "$PREV_TAG" ]; then
    NEW_VERSION=$current
  else
    prev=${PREV_TAG#v}
    if ver_gt "$current" "$prev"; then
      NEW_VERSION=$current
    else
      [ "$current" = "$prev" ] ||
        echo "::warning::VERSION ($current) is behind the latest tag $PREV_TAG; bumping from the tag" >&2
      IFS=. read -r major minor patch <<<"$prev"
      NEW_VERSION="$major.$minor.$((patch + 1))"
    fi
  fi
  NEW_TAG="v$NEW_VERSION"

  url=$(repo_url)
  today=$(date -u +%F)
  if [ -n "$PREV_TAG" ]; then
    compare="$url/compare/$PREV_TAG...$NEW_TAG"
  else
    compare="$url/commits/$NEW_TAG"
  fi

  # Split CHANGELOG.md into: text before the first "## " heading, the
  # "## Unreleased" body (consumed into this release), and older releases.
  src=CHANGELOG.md
  [ -f "$src" ] || src=/dev/null
  : >"$OUT/pre"
  : >"$OUT/unrel"
  : >"$OUT/rest"
  awk -v pre="$OUT/pre" -v unrel="$OUT/unrel" -v rest="$OUT/rest" '
    /^## / {
      if (state != "rest" && tolower($0) ~ /^##[[:space:]]+\[?unreleased\]?[[:space:]]*$/) { state = "unrel"; next }
      state = "rest"
    }
    state == "unrel" { print > unrel; next }
    state == "rest"  { print > rest;  next }
    { print > pre }
  ' "$src"

  unreleased=$(trim_blank <"$OUT/unrel")
  {
    if [ -n "$unreleased" ]; then
      printf '%s\n\n' "$unreleased"
    fi
    printf '### Commits\n\n'
    while IFS=$'\t' read -r sha subject; do
      printf '%s\n' "- $subject ([\`${sha:0:7}\`]($url/commit/$sha))"
    done <<<"$commits"
    printf '\nFull changelog: %s\n' "$compare"
  } >"$OUT/NOTES.md"

  pre=$(trim_blank <"$OUT/pre")
  rest=$(trim_blank <"$OUT/rest")
  {
    printf '%s\n\n' "${pre:-# Changelog}"
    printf '## [%s](%s) - %s\n\n' "$NEW_VERSION" "$url/releases/tag/$NEW_TAG" "$today"
    cat "$OUT/NOTES.md"
    if [ -n "$rest" ]; then
      printf '\n%s\n' "$rest"
    fi
  } >"$OUT/CHANGELOG.md"
  printf '%s\n' "$NEW_VERSION" >"$OUT/VERSION"
}

# Publish the Release for an existing tag if it has none.
reconcile() {
  local tag notes
  tag=$(latest_tag)
  [ -n "$tag" ] || return 0
  if release_exists "$tag"; then
    return 0
  fi
  echo "GitHub Release for $tag is missing; publishing it from the CHANGELOG.md recorded at the tag."
  notes=$(git show "$tag:CHANGELOG.md" 2>/dev/null | section_notes "${tag#v}" || true)
  [ -n "$notes" ] ||
    die "Tag $tag has no GitHub Release and no '## [${tag#v}](...)' section in its CHANGELOG.md; publish it manually or delete the tag."
  printf '%s\n' "$notes" >"$OUT/existing-notes.md"
  gh release create "$tag" --verify-tag --title "$tag" --notes-file "$OUT/existing-notes.md" --latest ||
    die "Could not publish the GitHub Release for existing tag $tag; rerun this workflow."
}

# One full release pass on the latest main. Sets RETRY=1 when main moved while pushing.
attempt() {
  local base

  git fetch --quiet --force --tags origin '+refs/heads/main:refs/remotes/origin/main'
  git checkout --quiet -B main origin/main

  reconcile

  plan
  if [ -z "$NEW_TAG" ]; then
    echo "Nothing to release: no commits since ${PREV_TAG:-the start} other than VERSION/CHANGELOG.md updates."
    return 0
  fi
  echo "Releasing $NEW_TAG (previous tag: ${PREV_TAG:-none})"

  base=$(git rev-parse HEAD)
  cp "$OUT/VERSION" VERSION
  cp "$OUT/CHANGELOG.md" CHANGELOG.md
  git add VERSION CHANGELOG.md
  git -c user.name="$BOT_NAME" -c user.email="$BOT_EMAIL" commit --quiet -m "chore(release): $NEW_TAG"
  git -c user.name="$BOT_NAME" -c user.email="$BOT_EMAIL" tag -a "$NEW_TAG" -m "$NEW_TAG"

  # Atomic: the release commit and its tag land together or not at all.
  if git push --atomic origin HEAD:refs/heads/main "refs/tags/$NEW_TAG"; then
    gh release create "$NEW_TAG" --verify-tag --title "$NEW_TAG" --notes-file "$OUT/NOTES.md" --latest ||
      die "$NEW_TAG is committed and tagged but its GitHub Release was not published; rerun this workflow (or push to main) to publish it."
    return 0
  fi

  git tag -d "$NEW_TAG" >/dev/null
  git fetch --quiet origin '+refs/heads/main:refs/remotes/origin/main'
  [ "$(git rev-parse refs/remotes/origin/main)" != "$base" ] ||
    die "Push of $NEW_TAG was rejected although main did not move; check branch protection and token permissions."
  RETRY=1
}

main() {
  local dry_run=0 i
  case "${1:-}" in
    '') ;;
    --dry-run) dry_run=1 ;;
    *) die 'usage: release.sh [--dry-run]' ;;
  esac

  cd "$(git rev-parse --show-toplevel)"
  OUT=$(mktemp -d)
  trap 'rm -rf "$OUT"' EXIT

  if [ "$dry_run" = 1 ]; then
    plan
    if [ -z "$NEW_TAG" ]; then
      echo "Dry run: nothing to release since ${PREV_TAG:-the start}."
      return 0
    fi
    echo "Dry run: would release $NEW_TAG (previous tag: ${PREV_TAG:-none})"
    printf '\n== VERSION ==\n%s\n' "$(cat "$OUT/VERSION")"
    printf '\n== Release notes ==\n'
    cat "$OUT/NOTES.md"
    printf '\n== CHANGELOG.md diff ==\n'
    diff -u "$([ -f CHANGELOG.md ] && echo CHANGELOG.md || echo /dev/null)" "$OUT/CHANGELOG.md" || true
    return 0
  fi

  [ "${GITHUB_ACTIONS:-}" = true ] || die 'refusing to release outside GitHub Actions; use --dry-run locally'

  for ((i = 1; i <= MAX_ATTEMPTS; i++)); do
    RETRY=0
    attempt
    [ "$RETRY" = 1 ] || return 0
    echo "main moved during the release; starting over on the new main ($i/$MAX_ATTEMPTS)"
  done
  die "main kept moving for $MAX_ATTEMPTS attempts; rerun this workflow."
}

# Single line so bash has read the whole script before main can replace it on disk.
main "$@"; exit
