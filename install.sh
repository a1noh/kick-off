#!/usr/bin/env bash
# Install the kickoff kit's skills into ~/.claude/skills, so /kickoff works in any folder on this computer.
#   ./install.sh              copy the skills (re-run after `git pull` to update)
#   ./install.sh --link       symlink instead: edits in this repo are live (for working on the kit)
#   ./install.sh --uninstall  remove them
# Phone / claude.ai/code: no install needed. Make a repo from this template; its .claude/skills/ come with the clone.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO/.claude/skills"
DEST="$HOME/.claude/skills"
BACKUP="$HOME/.claude/skills-backup"   # outside skills/, so old copies are never loaded as duplicate skills
SKILLS=(kickoff discovery build rehearse demo)
MODE="${1:---copy}"

case "$MODE" in --copy | --link | --uninstall) ;; *) echo "usage: ./install.sh [--link | --uninstall]" >&2; exit 2 ;; esac
mkdir -p "$DEST"
for s in "${SKILLS[@]}"; do
  target="$DEST/$s"
  if [ "$MODE" = "--uninstall" ]; then
    rm -rf "$target" && echo "removed  $target"
    continue
  fi
  [ -d "$SRC/$s" ] || { echo "missing $SRC/$s" >&2; exit 1; }
  if [ -e "$target" ] && [ ! -L "$target" ]; then  # a real folder from an older install: keep a backup
    mkdir -p "$BACKUP" && mv "$target" "$BACKUP/$s.$(date +%Y%m%d%H%M%S)"
  fi
  rm -f "$target"
  if [ "$MODE" = "--link" ]; then
    ln -s "$SRC/$s" "$target" && echo "linked   $target -> $SRC/$s"
  else
    cp -R "$SRC/$s" "$target" && echo "copied   $target"
  fi
done
# Working on the kit repo itself? Use its secrets guard for commits.
[ "$MODE" != "--uninstall" ] && git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1 && git -C "$REPO" config core.hooksPath .githooks
[ "$MODE" = "--uninstall" ] && echo "Done." || echo "Done. In any empty folder: claude → /kickoff   (to learn first: /kickoff, then /demo)"
