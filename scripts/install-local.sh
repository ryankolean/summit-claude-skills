#!/usr/bin/env bash
# Install Summit skills from this repo into ~/.claude/skills as plain copies.
# Copies, not symlinks: a symlink follows whatever branch this checkout is on,
# so a parallel session switching branches would change the installed skill.
#
# Usage:
#   bash scripts/install-local.sh web-motion site-security summit-website
#   bash scripts/install-local.sh --all
# Re-run after every pull that touches skills/.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
dest="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

if [ $# -eq 0 ]; then
  echo "usage: $0 <skill>... | --all" >&2
  exit 1
fi

branch="$(git -C "$repo" rev-parse --abbrev-ref HEAD)"
commit="$(git -C "$repo" rev-parse --short HEAD)"
if [ "$branch" != main ]; then
  echo "warning: $repo is on '$branch', not main; installing that branch's version" >&2
fi

if [ "$1" = --all ]; then
  set -- $(cd "$repo/skills" && ls -d */ | tr -d /)
fi

mkdir -p "$dest"
for name in "$@"; do
  src="$repo/skills/$name"
  if [ ! -f "$src/SKILL.md" ]; then
    echo "skip $name: no skills/$name/SKILL.md" >&2
    continue
  fi
  rm -rf "${dest:?}/$name"
  cp -R "$src" "$dest/$name"
  echo "installed $name ($branch@$commit) -> $dest/$name"
done
