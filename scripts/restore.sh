#!/usr/bin/env bash
# One-liner offline reconstruction of the pixi-skills toolchain from a published
# sandbox branch, with PATH aliases wired the way prefix-dev/setup-pixi does it.
#
# Layout copied from Archont561/pixi-sandbox@7a2dcb1 (scripts/restore.sh), with
# two deliberate changes:
#
#   * the default branch is this repository's `developer` bundle, and the PATH
#     alias points at the `default` pixi environment rather than `dev`;
#   * the scratch worktree lives on the *project* filesystem
#     (.pixi/.worktrees), not in /tmp. Upstream's own invariant #3 is that a
#     small tmpfs fails mid-restore because pixi-unpack stages into TMPDIR; its
#     script predates applying that rule to the worktree itself.
#
# Usage: bash scripts/restore.sh [branch] [output-path]
#   branch      defaults to sandbox/developer-linux-64
#   output-path defaults to .
#
# Inert until a sandbox branch has been published by
# .github/workflows/publish-sandbox.yml. Once pixi.toml exists, alias this as a
# task so the entry point stays `pixi run sandbox-restore`.

set -euo pipefail

BRANCH="${1:-sandbox/developer-linux-64}"
OUTPUT="${2:-.}"
WORKTREE_ROOT="${SANDBOX_WORKTREE_DIR:-.pixi/.worktrees}"
WORKTREE="$WORKTREE_ROOT/sb-$$"

cleanup() {
  git worktree remove "$WORKTREE" --force >/dev/null 2>&1 || rm -rf "$WORKTREE"
}
trap cleanup EXIT

echo "→ fetching $BRANCH"
git fetch origin "$BRANCH:refs/remotes/origin/$BRANCH" --depth 1 || git fetch origin "$BRANCH"

echo "→ worktree $WORKTREE"
rm -rf "$WORKTREE"
mkdir -p "$WORKTREE_ROOT"
git worktree add "$WORKTREE" "origin/$BRANCH" --force

# Prefer the self-contained root bootstrap produced by `pack --self-bin`; retain
# the nested paths for branches generated before the root convenience copy.
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

# Verify before write. Never fatal here: the restore below re-verifies and is
# the authority, while this run gives the operator the full failure list early.
echo "→ doctor $BIN"
"$BIN" doctor --branch-location "$WORKTREE" --verify || true

echo "→ restore to $OUTPUT"
if [ -f "$WORKTREE/restore.sh" ]; then
  # Current branches keep the restore policy next to the root binary.
  bash "$WORKTREE/restore.sh" "$OUTPUT"
elif "$BIN" restore --branch-location "$WORKTREE" --output-path "$OUTPUT" --force 2>&1; then
  :
else
  # Branches published before `--output-path` was renamed.
  "$BIN" restore --branch-location "$WORKTREE" --path-to-main-repo-code "$OUTPUT" --force
fi

# Wire PATH aliases like setup-pixi.
if [ -f "$OUTPUT/.pixi/sandbox-env.sh" ]; then
  echo "→ sourcing $OUTPUT/.pixi/sandbox-env.sh"
  # shellcheck disable=SC1090,SC1091
  source "$OUTPUT/.pixi/sandbox-env.sh"
  export PATH="$PWD/.pixi/envs/default/bin:$PATH"
  echo "PATH now includes:"
  echo "  $PWD/.pixi/tools/linux-64"
  echo "  $PWD/.pixi/envs/default/bin"
  echo "  pixi() function → bundled pixi"
  echo "Try: pixi --version; cargo --version; cargo check --offline"
else
  echo "restore complete but no sandbox-env.sh found"
fi
