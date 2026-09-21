#!/usr/bin/env bash
# One-liner offline reconstruction from orphan branch, with PATH aliases.
# Usage: bash scripts/restore.sh [branch] [output-path]
#   branch defaults to sandbox/developer-linux-64 — the branch .pixi-sandbox.toml
#     publishes (branch_prefix "sandbox" + bundle "developer" + platform "linux-64").
#     Confirm with: pixi-sandbox plan --config .pixi-sandbox.toml
#   output-path defaults to .
# After restore, sources .pixi/sandbox-env.sh and adds dev env to PATH.
# Copied verbatim from Archont561/pixi-sandbox (scripts/restore.sh).

set -euo pipefail

BRANCH="${1:-sandbox/developer-linux-64}"
OUTPUT="${2:-.}"
TMPDIR="${TMPDIR:-/tmp}"
WORKTREE="$TMPDIR/sb-$$"

echo "→ fetching $BRANCH"
git fetch origin "$BRANCH:refs/remotes/origin/$BRANCH" --depth 1 || git fetch origin "$BRANCH"

echo "→ worktree $WORKTREE"
rm -rf "$WORKTREE"
git worktree add "$WORKTREE" "origin/$BRANCH" --force

# Prefer the self-contained root bootstrap produced by `pack --self-bin`; retain the
# nested path for branches generated before the root convenience copy existed.
BIN=""
for candidate in \
  "$WORKTREE/pixi-sandbox" \
  "$WORKTREE/pixi-sandbox.exe" \
  "$WORKTREE/.pixi-sandbox/tools/linux-64/pixi-sandbox" \
  "$WORKTREE/.pixi-sandbox/tools/linux-64/pixi-sandbox.exe" \
  "$WORKTREE/.pixi-sandbox/tools/win-64/pixi-sandbox.exe"; do
  if [ -x "$candidate" ] || [ -f "$candidate" ]; then
    BIN="$candidate"
    break
  fi
done

if [ -z "$BIN" ]; then
  echo "::error::No pixi-sandbox binary found in $WORKTREE"
  exit 1
fi

echo "→ doctor $BIN"
"$BIN" doctor --branch-location "$WORKTREE" --verify || true

echo "→ restore to $OUTPUT"
# `pixi-sandbox restore --output-path` requires the directory to exist; the documented
# usage is `restore.sh [branch] [output-path]`, and a fresh path is the normal case.
mkdir -p "$OUTPUT"
if [ -f "$WORKTREE/restore.sh" ]; then
  # New branches keep the restore policy next to the root binary.
  bash "$WORKTREE/restore.sh" "$OUTPUT"
else
  # Legacy branches may only have the nested self-binary and no launcher.
  if "$BIN" restore --branch-location "$WORKTREE" --output-path "$OUTPUT" --force 2>&1; then
    :
  else
    "$BIN" restore --branch-location "$WORKTREE" --path-to-main-repo-code "$OUTPUT" --force
  fi
fi

echo "→ cleanup worktree"
git worktree remove "$WORKTREE" --force || rm -rf "$WORKTREE"

# Wire PATH aliases like setup-pixi
if [ -f "$OUTPUT/.pixi/sandbox-env.sh" ]; then
  echo "→ sourcing $OUTPUT/.pixi/sandbox-env.sh"
  # shellcheck disable=SC1090
  source "$OUTPUT/.pixi/sandbox-env.sh"
  # `$OUTPUT`, not `$PWD`: restoring anywhere except the repository root is the whole
  # point of the second argument, and pointing PATH back at `$PWD` silently undoes it.
  export PATH="$OUTPUT/.pixi/envs/dev/bin:$PATH"
  echo "PATH now includes:"
  echo "  $OUTPUT/.pixi/tools/linux-64"
  echo "  $OUTPUT/.pixi/envs/dev/bin"
  echo "  pixi() function → bundled pixi"
  echo "Try: pixi --version; cargo --version; cargo check --offline"
else
  echo "restore complete but no sandbox-env.sh found"
fi