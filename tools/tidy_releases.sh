#!/bin/sh
#
# Tidies the GitHub releases (run by GitHub Actions: tidy-releases.yml and release.yml):
#   - titles every release "Dotcleaner x.y.z — <short title>", from the CHANGELOG heading
#     "## [x.y.z] — date — <short title>";
#   - adds a notice "This is an old version" with a link to the latest release at the top
#     of every release except the latest one (and removes it from the latest one).
# Safe to run again: the notice is added only once.
#
# Needs: gh (logged in with GH_TOKEN), jq, GITHUB_REPOSITORY=owner/repo, run from the repo root.

set -eu
REPO=${GITHUB_REPOSITORY:-}
MARKER='<!-- old-version -->'

# release_title VERSION -> "Dotcleaner x.y.z — <short title>"
release_title() {
  _sub=$(grep -m1 "^## \[$1\]" CHANGELOG.md | awk -F ' — ' 'NF >= 3 { print $3 }') || _sub=''
  if [ -n "$_sub" ]; then printf 'Dotcleaner %s — %s' "$1" "$_sub"; else printf 'Dotcleaner %s' "$1"; fi
}

# add_notice BODY -> BODY with the old-version notice on top (once)
add_notice() {
  case $1 in
    *"$MARKER"*) printf '%s' "$1" ;;
    *) printf '%s\n> [!WARNING]\n> **This is an old version.** Download the latest one here: **[latest release](https://github.com/%s/releases/latest)**.\n\n%s' \
         "$MARKER" "$REPO" "$1" ;;
  esac
}

# remove_notice BODY -> BODY without the notice (marker line + the 3 lines after it)
remove_notice() {
  printf '%s\n' "$1" | awk -v m="$MARKER" '$0 == m { skip = 3; next } skip > 0 { skip--; next } { print }'
}

if [ "${1:-}" = "--self-test" ]; then
  REPO=owner/repo
  b=$(add_notice "Notes")
  [ "$(add_notice "$b")" = "$b" ] || { echo "notice added twice"; exit 1; }
  [ "$(remove_notice "$b")" = "Notes" ] || { echo "notice not removed"; exit 1; }
  echo "self-test ok"
  exit 0
fi

[ -n "$REPO" ] || { echo "set GITHUB_REPOSITORY=owner/repo" >&2; exit 2; }
latest=$(gh api "repos/$REPO/releases/latest" -q .tag_name)
gh api "repos/$REPO/releases?per_page=100" -q '.[] | "\(.id) \(.tag_name)"' | while read -r id tag; do
  body=$(gh api "repos/$REPO/releases/$id" -q .body)
  if [ "$tag" = "$latest" ]; then body=$(remove_notice "$body"); else body=$(add_notice "$body"); fi
  title=$(release_title "${tag#v}")
  jq -n --arg n "$title" --arg b "$body" '{name: $n, body: $b}' |
    gh api -X PATCH "repos/$REPO/releases/$id" --input - >/dev/null
  echo "$tag: $title$([ "$tag" = "$latest" ] && echo '  (latest)')"
done
