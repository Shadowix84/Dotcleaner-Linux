#!/bin/sh
#
# dotcleaner installer - installs the "dotcleaner" command.
#
#   curl -fsSL https://raw.githubusercontent.com/Shadowix84/Dotcleaner-Multi-Software/main/install.sh | sh
#
# Uninstall:
#   curl -fsSL https://raw.githubusercontent.com/Shadowix84/Dotcleaner-Multi-Software/main/install.sh | sh -s -- --uninstall
#
# Environment:
#   PREFIX=/usr/local      install to $PREFIX/bin (default /usr/local)
#   DOTCLEANER_SRC=FILE    install this local file instead of downloading it

set -eu

URL="https://raw.githubusercontent.com/Shadowix84/Dotcleaner-Multi-Software/main/dotcleaner.sh"
PREFIX=${PREFIX:-/usr/local}
BIN_DIR="$PREFIX/bin"
DEST="$BIN_DIR/dotcleaner"

say() { printf '%s\n' "$*"; }
die() { printf 'Error: %s\n' "$*" >&2; exit 1; }

# Use sudo only when the install folder cannot be written as the current user
if mkdir -p "$BIN_DIR" 2>/dev/null && [ -w "$BIN_DIR" ]; then
  NEED_SUDO=0
else
  NEED_SUDO=1
fi

as_needed() {
  if [ "$NEED_SUDO" -eq 0 ]; then
    "$@"
  elif command -v sudo >/dev/null 2>&1; then
    sudo "$@"
  else
    die "$BIN_DIR is not writable (try: PREFIX=\$HOME/.local sh install.sh)"
  fi
}

if [ "$NEED_SUDO" -eq 1 ] && command -v sudo >/dev/null 2>&1; then
  say "Administrator password may be needed to write to $BIN_DIR"
fi

if [ "${1:-}" = "--uninstall" ]; then
  if [ -e "$DEST" ]; then
    as_needed rm -f "$DEST"
    say "dotcleaner removed from $DEST"
  else
    say "dotcleaner is not installed in $DEST"
  fi
  exit 0
fi

TMP=$(mktemp "${TMPDIR:-/tmp}/dotcleaner.XXXXXX")
trap 'rm -f "$TMP"' EXIT

if [ -n "${DOTCLEANER_SRC:-}" ]; then
  cp "$DOTCLEANER_SRC" "$TMP"
elif command -v curl >/dev/null 2>&1; then
  curl -fsSL "$URL" -o "$TMP" || die "download failed: $URL"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$TMP" "$URL" || die "download failed: $URL"
else
  die "curl or wget is required"
fi

# Sanity checks before installing anything
head -n 1 "$TMP" | grep -q '^#!/bin/sh' || die "the downloaded file is not the dotcleaner script"
sh -n "$TMP" || die "the downloaded script has a syntax error"
VERSION=$(sh "$TMP" --version) || die "the downloaded script does not run"

as_needed mkdir -p "$BIN_DIR"
as_needed cp "$TMP" "$DEST"
as_needed chmod 755 "$DEST"

say "Installed: $VERSION -> $DEST"
case ":$PATH:" in
  *":$BIN_DIR:"*) say "Run it with: dotcleaner" ;;
  *) say "Note: $BIN_DIR is not in your PATH. Run it with: $DEST" ;;
esac
