#!/bin/sh
#
# dotcleaner — remove the junk files macOS leaves on the SD cards of
# emulation handhelds (R36S, Anbernic, Miyoo, Retroid, TrimUI...):
# ._* files, .DS_Store, .Spotlight-V100, .Trashes, .fseventsd, __MACOSX...
#
# Plain POSIX sh: runs on macOS, Linux and on the consoles themselves (BusyBox).
#
# https://github.com/Shadowix84/Dotcleaner-Linux
# MIT License — Copyright (c) 2026 Shadowix84

set -u

VERSION="1.2.0"
PROG=${0##*/}

# --- What gets removed (edit here to add more) -------------------------------
# Files, at any depth
JUNK_FILES='._* .DS_Store .apdisk'
# Folders, at any depth (removed with everything inside)
JUNK_DIRS='.Spotlight-V100 .Trashes .fseventsd .TemporaryItems .DocumentRevisions-V100 .AppleDouble .AppleDB .AppleDesktop __MACOSX'
# Windows files, only with -w / --windows
WINDOWS_FILES='Thumbs.db ehthumbs.db desktop.ini'

# --- Options -----------------------------------------------------------------
DRY_RUN=0
ASSUME_YES=0
CLEAN_WINDOWS=0
EJECT=0
VERBOSE=0
QUIET=0
KEEP_TRASH=0
SHOW_HELP=0
FORCE=0

# --- Language: English by default, French with --lang fr ---------------------
# (or DOTCLEANER_LANG=fr in the environment)
set_lang() {
  case $1 in
    en|EN|en_*|en-*) FR=0 ;;
    fr|FR|fr_*|fr-*) FR=1 ;;
    *) return 1 ;;
  esac
}
FR=0
set_lang "${DOTCLEANER_LANG:-en}" || FR=0

# t "English text" "Texte français" -> prints the text in the user's language
t() {
  if [ "$FR" -eq 1 ]; then printf '%s' "$2"; else printf '%s' "$1"; fi
}

# n_items N -> "1 item" / "5 items" (French: "1 élément" / "5 éléments")
n_items() {
  if [ "$1" -le 1 ]; then t "$1 item" "$1 élément"; else t "$1 items" "$1 éléments"; fi
}

# n_deleted N -> "1 item deleted" / "5 items deleted" (French agreement)
n_deleted() {
  if [ "$1" -le 1 ]; then t "$1 item deleted" "$1 élément supprimé"
  else t "$1 items deleted" "$1 éléments supprimés"; fi
}

# --- Output helpers ----------------------------------------------------------
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C_BOLD=$(printf '\033[1m'); C_DIM=$(printf '\033[2m')
  C_RED=$(printf '\033[31m'); C_GRN=$(printf '\033[32m')
  C_YEL=$(printf '\033[33m'); C_OFF=$(printf '\033[0m')
else
  C_BOLD='' C_DIM='' C_RED='' C_GRN='' C_YEL='' C_OFF=''
fi

say()  { if [ "$QUIET" -eq 0 ]; then printf '%s\n' "$*"; fi; }
warn() { printf '%s\n' "${C_YEL}$*${C_OFF}" >&2; }
err()  { printf '%s\n' "${C_RED}$(t 'Error:' 'Erreur :') $*${C_OFF}" >&2; }

usage() {
  if [ "$FR" -eq 1 ]; then
    cat <<EOF
dotcleaner $VERSION — supprime les fichiers parasites de macOS sur les cartes SD
des consoles d'émulation (R36S, Anbernic, Miyoo, Retroid, TrimUI…)

Utilisation : $PROG [options] [CHEMIN...]

Sans CHEMIN, la liste des cartes branchées s'affiche pour en choisir une.

Options :
  -n, --dry-run     simulation : affiche ce qui serait supprimé, ne supprime rien
  -y, --yes         ne pas demander de confirmation
  -w, --windows     supprimer aussi les fichiers Windows (Thumbs.db, desktop.ini)
  -k, --keep-trash  ne pas toucher à la corbeille de la carte (.Trashes)
      --force       accepter aussi un disque Mac (APFS/HFS+), refusé par défaut
  -e, --eject       éjecter la carte à la fin (macOS)
  -v, --verbose     afficher chaque élément supprimé
  -q, --quiet       n'afficher que les erreurs
      --lang LANGUE langue des messages : en (défaut) ou fr
  -h, --help        afficher cette aide
  -V, --version     afficher la version

Supprimé : fichiers ._*, .DS_Store, .apdisk et dossiers .Spotlight-V100,
.Trashes, .fseventsd, .TemporaryItems, .DocumentRevisions-V100,
.AppleDouble, .AppleDB, .AppleDesktop, __MACOSX.
Jamais touché : vos ROM, sauvegardes, BIOS et tous les autres fichiers.

Exemples :
  $PROG                          choisir la carte dans une liste
  $PROG -n /Volumes/EASYROMS     voir ce qui serait supprimé, sans rien toucher
  $PROG -y -e /Volumes/SHARE     nettoyer puis éjecter, sans question
EOF
  else
    cat <<EOF
dotcleaner $VERSION — removes the junk files macOS leaves on the SD cards
of emulation handhelds (R36S, Anbernic, Miyoo, Retroid, TrimUI...)

Usage: $PROG [options] [PATH...]

Without PATH, the mounted cards are listed so you can pick one.

Options:
  -n, --dry-run     preview: show what would be deleted, delete nothing
  -y, --yes         do not ask for confirmation
  -w, --windows     also remove Windows files (Thumbs.db, desktop.ini)
  -k, --keep-trash  leave the card's Trash (.Trashes) untouched
      --force       also accept a Mac disk (APFS/HFS+), refused by default
  -e, --eject       eject the card when done (macOS)
  -v, --verbose     list every deleted item
  -q, --quiet       only print errors
      --lang LANG   message language: en (default) or fr
  -h, --help        show this help
  -V, --version     show the version

Removed: ._* files, .DS_Store, .apdisk and the folders .Spotlight-V100,
.Trashes, .fseventsd, .TemporaryItems, .DocumentRevisions-V100,
.AppleDouble, .AppleDB, .AppleDesktop, __MACOSX.
Never touched: your ROMs, saves, BIOS and every other file.

Examples:
  $PROG                          pick the card from a list
  $PROG -n /Volumes/EASYROMS     preview what would be deleted
  $PROG -y -e /Volumes/SHARE     clean then eject, no questions
EOF
  fi
}

die_usage() {
  err "$1"
  printf '%s\n' "$(t "Try: $PROG --help" "Essayez : $PROG --help")" >&2
  exit 2
}

# --- Core --------------------------------------------------------------------

# junk_find ROOT MODE
#   MODE = print  -> print every junk item
#          delete -> delete every junk item
#          size   -> disk usage (KB) of every junk item
# Never follows symlinks and never leaves the card's filesystem (-xdev).
# Two passes (folders, then files) on purpose: BusyBox find, used by most
# console firmwares, silently ignores "-exec ... {} +" inside \( \).
junk_find() {
  _jf_root=$1 _jf_mode=$2
  _jf_files=$JUNK_FILES
  if [ "$CLEAN_WINDOWS" -eq 1 ]; then _jf_files="$_jf_files $WINDOWS_FILES"; fi

  set -f  # the '._*' pattern must reach find untouched
  # shellcheck disable=SC2086  # $_jf_or is meant to vanish when empty
  {
    set -- "$_jf_root" -xdev
    # With -k the card's Trash is skipped entirely, content included
    if [ "$KEEP_TRASH" -eq 1 ]; then set -- "$@" -type d -name .Trashes -prune -o; fi

    # Pass 1: junk folders (pruned, so their content is not listed twice)
    set -- "$@" -type d \(
    _jf_or=''
    for _jf_n in $JUNK_DIRS; do set -- "$@" $_jf_or -name "$_jf_n"; _jf_or='-o'; done
    set -- "$@" \) -prune
    _jf_run "$@"

    # Pass 2: junk files, outside the junk folders
    set -- "$@" -o -type f \(
    _jf_or=''
    for _jf_n in $_jf_files; do set -- "$@" $_jf_or -name "$_jf_n"; _jf_or='-o'; done
    set -- "$@" \)
    _jf_run "$@"
  }
  set +f
}

# _jf_run FIND-ARGS... -> runs find with the action of $_jf_mode
_jf_run() {
  case $_jf_mode in
    print)  find "$@" -print ;;
    delete) find "$@" -exec rm -rf {} + ;;
    size)   find "$@" -exec du -sk {} + ;;
  esac
}

# trash_count ROOT -> number of user files waiting in the card's Trash
trash_count() {
  find "$1" -xdev -path '*/.Trashes/*' -type f ! -name '._*' ! -name .DS_Store 2>/dev/null |
    awk 'END { print NR }'
}

# Reads paths on stdin, prints: appledouble ds_store system windows total
classify() {
  W="$WINDOWS_FILES" awk -F/ '
    BEGIN { n = split(ENVIRON["W"], w, " "); for (i = 1; i <= n; i++) win[w[i]] = 1 }
    {
      f = $NF
      if (f ~ /^\._/)            a++
      else if (f == ".DS_Store") d++
      else if (f in win)         x++
      else                       s++
    }
    END { printf "%d %d %d %d %d\n", a, d, s, x, a + d + s + x }'
}

# human_size KB -> "12.3 MB" (or "12,3 Mo" in French)
human_size() {
  awk -v k="$1" -v fr="$FR" 'BEGIN {
    if (fr) { u1 = "Ko"; u2 = "Mo"; u3 = "Go" } else { u1 = "KB"; u2 = "MB"; u3 = "GB" }
    if (k < 1024)         s = sprintf("%d %s", k, u1)
    else if (k < 1048576) s = sprintf("%.1f %s", k / 1024, u2)
    else                  s = sprintf("%.2f %s", k / 1048576, u3)
    if (fr) sub(/\./, ",", s)
    print s
  }'
}

# list_items ROOT -> junk items, relative to ROOT, sorted
list_items() {
  junk_find "$1" print 2>/dev/null | sort | P="$1/" awk '{
    p = ENVIRON["P"]
    if (index($0, p) == 1) $0 = substr($0, length(p) + 1)
    print "    " $0
  }'
}

# Folders that must never be cleaned as a whole
is_forbidden() {
  case $1 in
    /|/Applications|/Library|/System|/System/Volumes/Data|/Users|/Volumes|\
    /bin|/boot|/dev|/etc|/home|/media|/mnt|/opt|/private|/private/etc|\
    /private/tmp|/private/var|/proc|/root|/run|/run/media|/sbin|/sys|/tmp|\
    /usr|/var)
      return 0 ;;
  esac
  if [ -n "${HOME:-}" ] && _home=$(cd "$HOME" 2>/dev/null && pwd -P); then
    if [ "$1" = "$_home" ]; then return 0; fi
  fi
  return 1
}

# fs_type PATH -> filesystem type (apfs, hfs, msdos, exfat, ext4, vfat...), or nothing
fs_type() {
  if [ "$(uname -s 2>/dev/null)" = Darwin ]; then
    _ft_dev=$(stat -f %Sd "$1" 2>/dev/null) || return 0
    mount | awk -v d="/dev/$_ft_dev" '$1 == d { sub(/.*\(/, ""); sub(/[,)].*/, ""); print; exit }'
  else
    stat -f -c %T "$1" 2>/dev/null || true
  fi
}

# Mac disks (APFS, HFS+) are not console cards: consoles cannot read them, and
# there .Spotlight-V100, .fseventsd or .DocumentRevisions-V100 hold real data.
is_mac_disk() {
  case $(fs_type "$1") in
    apfs|hfs|hfsplus|hfs+) return 0 ;;
  esac
  return 1
}

eject_volume() {
  if [ "$(uname -s 2>/dev/null)" != Darwin ]; then
    warn "  $(t '--eject only works on macOS: unmount the card from your file manager.' "--eject ne fonctionne que sur macOS : démontez la carte depuis votre gestionnaire de fichiers.")"
    return 0
  fi
  case $1 in
    /Volumes/?*) _rest=${1#/Volumes/}; _vol=/Volumes/${_rest%%/*} ;;
    *)
      warn "  $(t "$1 is not on an external card, nothing to eject." "$1 n'est pas sur une carte externe, rien à éjecter.")"
      return 0 ;;
  esac
  if diskutil eject "$_vol" >/dev/null 2>&1; then
    say "  ${C_GRN}$(t "$_vol ejected, you can remove the card." "$_vol éjecté, vous pouvez retirer la carte.")${C_OFF}"
  else
    warn "  $(t "Could not eject $_vol (a file may still be open)." "Impossible d'éjecter $_vol (un fichier est peut-être encore ouvert).")"
    return 1
  fi
}

# Folders offered when no PATH is given
candidate_dirs() {
  if [ -d /Volumes ]; then
    for _cd in /Volumes/*; do
      if [ ! -d "$_cd" ] || [ -L "$_cd" ]; then continue; fi   # skip "Macintosh HD" (symlink to /)
      case ${_cd##*/} in com.apple.*) continue ;; esac
      if is_mac_disk "$_cd"; then continue; fi            # backup drives etc.: not a card
      printf '%s\n' "$_cd"
    done
  else
    # Linux desktops, then the usual ROM folders of console firmwares
    for _cd in /media/*/* /run/media/*/* /roms /roms2 /userdata/roms \
               /storage/roms /mnt/SDCARD /mnt/mmc /mnt/sdcard; do
      if [ -d "$_cd" ]; then printf '%s\n' "$_cd"; fi
    done
  fi
}

# Interactive choice of the card -> sets PICKED
pick_target() {
  _list=$(candidate_dirs)
  if [ -z "$_list" ]; then
    err "$(t "no card found. Plug in the card, or give its path: $PROG /path/to/card" "aucune carte trouvée. Branchez la carte, ou indiquez son chemin : $PROG /chemin/de/la/carte")"
    exit 2
  fi
  printf '%s\n' "$(t 'Which card do you want to clean?' 'Quelle carte voulez-vous nettoyer ?')" >&2
  printf '%s\n' "$_list" | awk '{ printf "  %d) %s\n", NR, $0 }' >&2
  _count=$(printf '%s\n' "$_list" | awk 'END { print NR }')
  printf '%s' "$(t 'Number (Enter to cancel): ' 'Numéro (Entrée pour annuler) : ')" >&2
  read -r _choice || _choice=''
  case $_choice in
    '') say "$(t 'Cancelled.' 'Annulé.')"; exit 0 ;;
    *[!0-9]*) die_usage "$(t "invalid choice: $_choice" "choix invalide : $_choice")" ;;
  esac
  if [ "$_choice" -lt 1 ] || [ "$_choice" -gt "$_count" ]; then
    die_usage "$(t "invalid choice: $_choice" "choix invalide : $_choice")"
  fi
  PICKED=$(printf '%s\n' "$_list" | sed -n "${_choice}p")
}

# clean_target PATH -> 0 if OK, 1 on error
clean_target() {
  _in=$1
  case $_in in -*) _in="./$_in" ;; esac

  if [ ! -e "$_in" ]; then
    err "$(t "not found: $1" "introuvable : $1")"; return 1
  fi
  if [ ! -d "$_in" ]; then
    err "$(t "not a folder: $1" "ce n'est pas un dossier : $1")"; return 1
  fi
  if ! _root=$(cd "$_in" 2>/dev/null && pwd -P); then
    err "$(t "cannot open: $1" "impossible d'ouvrir : $1")"; return 1
  fi
  if is_forbidden "$_root"; then
    err "$(t "refusing to clean $_root (system or home folder). Point to your SD card, e.g. /Volumes/EASYROMS." "refus de nettoyer $_root (dossier système ou personnel). Indiquez votre carte SD, par ex. /Volumes/EASYROMS.")"
    return 1
  fi
  for _jd in $JUNK_DIRS; do
    if [ "${_root##*/}" = "$_jd" ]; then
      err "$(t "$_root is itself a junk folder: delete it directly." "$_root est lui-même un dossier parasite : supprimez-le directement.")"
      return 1
    fi
  done

  if [ "$FORCE" -eq 0 ] && is_mac_disk "$_root"; then
    err "$(t "$_root is on a Mac disk ($(fs_type "$_root")), not on a console SD card: nothing was touched. There, folders like .DocumentRevisions-V100 hold real data. Add --force only if you are sure." "$_root est sur un disque Mac ($(fs_type "$_root")), pas sur une carte SD de console : rien n'a été touché. Là, des dossiers comme .DocumentRevisions-V100 contiennent de vraies données. Ajoutez --force seulement si vous êtes sûr.")"
    return 1
  fi

  say ""
  say "${C_BOLD}$_root${C_OFF}"

  # shellcheck disable=SC2046
  set -- $(junk_find "$_root" print 2>/dev/null | classify)
  _total=$5

  if [ "$_total" -eq 0 ]; then
    say "  ${C_GRN}$(t 'Already clean, nothing to delete.' 'Déjà propre, rien à supprimer.')${C_OFF}"
    if [ "$EJECT" -eq 1 ] && [ "$DRY_RUN" -eq 0 ]; then eject_volume "$_root"; return $?; fi
    return 0
  fi

  _kb=$(junk_find "$_root" size 2>/dev/null | awk '{ s += $1 } END { print s + 0 }')
  _size=$(human_size "$_kb")

  if [ "$1" -gt 0 ]; then say "$(printf '  %6d  %s' "$1" "$(t '._* files (AppleDouble)' 'fichiers ._* (AppleDouble)')")"; fi
  if [ "$2" -gt 0 ]; then say "$(printf '  %6d  %s' "$2" '.DS_Store')"; fi
  if [ "$3" -gt 0 ]; then say "$(printf '  %6d  %s' "$3" "$(t 'macOS system items (.Spotlight-V100, .Trashes...)' 'éléments système macOS (.Spotlight-V100, .Trashes…)')")"; fi
  if [ "$4" -gt 0 ]; then say "$(printf '  %6d  %s' "$4" "$(t 'Windows files' 'fichiers Windows')")"; fi
  say "  ${C_DIM}------${C_OFF}"
  say "${C_BOLD}  $(t 'Total:' 'Total :') $(n_items "$_total"), $_size${C_OFF}"

  if [ "$QUIET" -eq 0 ]; then
    if [ "$DRY_RUN" -eq 1 ]; then
      say "  ${C_DIM}$(t 'Would be deleted:' 'Seraient supprimés :')${C_OFF}"; list_items "$_root"
    elif [ "$VERBOSE" -eq 1 ]; then
      say "  ${C_DIM}$(t 'To be deleted:' 'À supprimer :')${C_OFF}"; list_items "$_root"
    fi
  fi

  if [ "$KEEP_TRASH" -eq 0 ]; then
    _trash=$(trash_count "$_root")
    if [ "$_trash" -gt 0 ] && [ "$QUIET" -eq 0 ]; then
      warn "  $(t "Warning: the card's Trash holds $_trash file(s) deleted in Finder; they will be erased for good (use -k to keep them)." "Attention : la corbeille de la carte contient $_trash fichier(s) supprimé(s) dans le Finder ; ils seront effacés définitivement (-k pour les garder).")"
    fi
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    say "  ${C_YEL}$(t 'Dry run: nothing was deleted.' "Simulation : rien n'a été supprimé.")${C_OFF}"
    return 0
  fi

  if [ "$ASSUME_YES" -eq 0 ]; then
    if [ ! -t 0 ]; then
      err "$(t 'no terminal to ask for confirmation: add -y to delete.' 'pas de terminal pour demander confirmation : ajoutez -y pour supprimer.')"
      return 1
    fi
    printf '%s' "  $(t "Delete $(n_items "$_total")? [y/N] " "Supprimer $(n_items "$_total") ? [o/N] ")"
    read -r _answer || _answer=''
    case $_answer in
      [yYoO]*) ;;
      *) say "  $(t 'Cancelled, nothing was deleted.' "Annulé, rien n'a été supprimé.")"; return 0 ;;
    esac
  fi

  junk_find "$_root" delete 2>/dev/null

  # Check what is left
  # shellcheck disable=SC2046
  set -- $(junk_find "$_root" print 2>/dev/null | classify)
  _left=$5
  _rc=0

  if [ "$_left" -eq 0 ]; then
    say "  ${C_GRN}$(t 'Done:' 'Terminé :') $(n_deleted "$_total") ($_size $(t 'freed' 'libérés')).${C_OFF}"
  else
    _done=$((_total - _left))
    say "  ${C_GRN}$(n_deleted "$_done").${C_OFF}"
    if [ "$1" -eq 0 ] && [ "$2" -eq 0 ] && [ "$4" -eq 0 ]; then
      # Only system folders left: macOS recreated or locked them while mounted
      warn "  $(t "$_left macOS system folder(s) came back or are in use: macOS recreates them while the card is mounted. Harmless for your console; use -e to eject right after cleaning." "$_left dossier(s) système macOS sont revenus ou sont en cours d'utilisation : macOS les recrée tant que la carte est branchée. Sans danger pour la console ; utilisez -e pour éjecter juste après le nettoyage.")"
    else
      warn "  $(t "Could not delete $(n_items "$_left"):" "Impossible de supprimer $(n_items "$_left") :")"
      list_items "$_root" >&2
      warn "  $(t 'Check that the card is not read-only, then try again (or with sudo).' "Vérifiez que la carte n'est pas en lecture seule, puis relancez (ou avec sudo).")"
      _rc=1
    fi
  fi

  if [ "$EJECT" -eq 1 ] && [ "$_rc" -eq 0 ]; then
    eject_volume "$_root" || _rc=1
  fi
  return "$_rc"
}

# --- Main --------------------------------------------------------------------
main() {
  # Parse options anywhere on the command line; paths are kept in order.
  _n=$#
  while [ "$_n" -gt 0 ]; do
    _arg=$1; shift; _n=$((_n - 1))
    case $_arg in
      -n|--dry-run) DRY_RUN=1 ;;
      -y|--yes)     ASSUME_YES=1 ;;
      -w|--windows) CLEAN_WINDOWS=1 ;;
      -e|--eject)   EJECT=1 ;;
      -v|--verbose) VERBOSE=1 ;;
      -q|--quiet)   QUIET=1 ;;
      -k|--keep-trash) KEEP_TRASH=1 ;;
      --force)      FORCE=1 ;;
      --lang=*)
        set_lang "${_arg#--lang=}" || die_usage "$(t "unknown language: ${_arg#--lang=} (use en or fr)" "langue inconnue : ${_arg#--lang=} (en ou fr)")" ;;
      --lang)
        if [ "$_n" -eq 0 ]; then die_usage "$(t '--lang needs a value: en or fr' '--lang attend une valeur : en ou fr')"; fi
        set_lang "$1" || die_usage "$(t "unknown language: $1 (use en or fr)" "langue inconnue : $1 (en ou fr)")"
        shift; _n=$((_n - 1)) ;;
      -h|--help)    SHOW_HELP=1 ;;
      -V|--version) printf 'dotcleaner %s\n' "$VERSION"; exit 0 ;;
      --)
        while [ "$_n" -gt 0 ]; do set -- "$@" "$1"; shift; _n=$((_n - 1)); done ;;
      --*) die_usage "$(t "unknown option: $_arg" "option inconnue : $_arg")" ;;
      -?*)
        if [ ${#_arg} -gt 2 ]; then
          # combined short options: -ny -> -n -y
          _rest=${_arg#-?}; _first=${_arg%"$_rest"}
          set -- "$_first" "-$_rest" "$@"; _n=$((_n + 2))
        else
          die_usage "$(t "unknown option: $_arg" "option inconnue : $_arg")"
        fi ;;
      *) set -- "$@" "$_arg" ;;
    esac
  done

  if [ "$SHOW_HELP" -eq 1 ]; then usage; exit 0; fi   # after --lang was read

  if [ "$KEEP_TRASH" -eq 1 ]; then
    JUNK_DIRS=$(printf ' %s ' "$JUNK_DIRS" | sed 's/ \.Trashes / /; s/^ *//; s/ *$//')
  fi

  trap 'printf "\n%s\n" "$(t "Interrupted." "Interrompu.")" >&2; exit 130' INT TERM

  say "${C_BOLD}dotcleaner $VERSION${C_OFF}"

  if [ $# -eq 0 ]; then
    if [ ! -t 0 ]; then die_usage "$(t 'no path given.' 'aucun chemin indiqué.')"; fi
    pick_target
    set -- "$PICKED"
  fi

  _status=0
  for _target in "$@"; do
    clean_target "$_target" || _status=1
  done
  exit "$_status"
}

main "$@"
