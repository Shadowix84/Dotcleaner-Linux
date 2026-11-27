#!/bin/sh
#
# Tidies the GitHub releases (run by GitHub Actions: tidy-releases.yml and release.yml):
#   - titles every release "Dotcleaner x.y.z — <short title>", from the CHANGELOG heading
#     "## [x.y.z] — date — <short title>";
#   - adds a notice "This is an old version" with a link to the latest release at the top
#     of every release except the latest one (and removes it from the latest one);
#   - keeps the "What's new" part of each release equal to its CHANGELOG section, so a
#     correction made in the CHANGELOG reaches the release page too.
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

# changes VERSION -> the CHANGELOG section of VERSION (without its heading)
changes() {
  [ -f CHANGELOG.md ] || return 0
  awk -v v="[$1]" '/^## \[/ { if (p) exit; if (index($0, v)) { p = 1; next } } p' CHANGELOG.md |
    awk 'NF { n = NR } { line[NR] = $0 } END { s = 1; while (s <= n && line[s] == "") s++; for (i = s; i <= n; i++) print line[i] }'
}

# sync_changes BODY VERSION -> BODY whose "## ✨ What's new..." part is the CHANGELOG section
sync_changes() {
  DC_CHANGES=$(changes "$2")
  if [ -z "$DC_CHANGES" ]; then printf '%s\n' "$1"; return 0; fi
  export DC_CHANGES
  printf '%s\n' "$1" | awk '
    skip && (/^## / || /^<details>/) { skip = 0 }
    skip { next }
    /^## .*What.s new/ { print; print ""; print ENVIRON["DC_CHANGES"]; print ""; skip = 1; next }
    { print }'
}

if [ "${1:-}" = "--self-test" ]; then
  REPO=owner/repo
  b=$(add_notice "Notes")
  [ "$(add_notice "$b")" = "$b" ] || { echo "notice added twice"; exit 1; }
  [ "$(remove_notice "$b")" = "Notes" ] || { echo "notice not removed"; exit 1; }
  t=$(mktemp -d "${TMPDIR:-/tmp}/tidy.XXXXXX")
  printf '## [9.9.9] — 2026-01-01 — Test\n\n- new text\n\n## [9.9.8] — 2026-01-01\n- old\n' >"$t/CHANGELOG.md"
  b=$(printf '## ⬇️ Download\n\nx\n\n## ✨ What'"'"'s new in 9.9.9\n\n- old text\n- more\n\n<details>\ny\n</details>')
  want=$(printf '## ⬇️ Download\n\nx\n\n## ✨ What'"'"'s new in 9.9.9\n\n- new text\n\n<details>\ny\n</details>')
  [ "$(cd "$t" && sync_changes "$b" 9.9.9)" = "$want" ] || { rm -rf "$t"; echo "What's new not synced"; exit 1; }
  [ "$(cd "$t" && sync_changes "$want" 9.9.9)" = "$want" ] || { rm -rf "$t"; echo "sync not stable"; exit 1; }
  rm "$t/CHANGELOG.md"
  [ "$(cd "$t" && sync_changes "$b" 9.9.9)" = "$b" ] || { rm -rf "$t"; echo "body changed without CHANGELOG"; exit 1; }
  rm -rf "$t"
  echo "self-test ok"
  exit 0
fi

[ -n "$REPO" ] || { echo "set GITHUB_REPOSITORY=owner/repo" >&2; exit 2; }
latest=$(gh api "repos/$REPO/releases/latest" -q .tag_name)
gh api "repos/$REPO/releases?per_page=100" -q '.[] | "\(.id) \(.tag_name)"' | while read -r id tag; do
  body=$(gh api "repos/$REPO/releases/$id" -q .body)
  body=$(sync_changes "$body" "${tag#v}")
  if [ "$tag" = "$latest" ]; then body=$(remove_notice "$body"); else body=$(add_notice "$body"); fi
  title=$(release_title "${tag#v}")
  jq -n --arg n "$title" --arg b "$body" '{name: $n, body: $b}' |
    gh api -X PATCH "repos/$REPO/releases/$id" --input - >/dev/null
  echo "$tag: $title$([ "$tag" = "$latest" ] && echo '  (latest)')"
done
