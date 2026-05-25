#!/usr/bin/env bash
# Extract the rsfs_mode/ subtree out of godmode into a standalone repo.
#
# Prereqs:
#   1. Empty repo tritathadore/rsfs_mode created on GitHub (Settings → New).
#   2. Local checkout of godmode on branch claude/tender-planck-pIbGk.
#
# Usage:
#   ./rsfs_mode/scripts/extract_rsfs_mode.sh \\
#       git@github.com:tritathadore/rsfs_mode.git
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "usage: $0 <new-repo-url>" >&2
  exit 2
fi
REMOTE_URL="$1"

BRANCH_NOW="$(git rev-parse --abbrev-ref HEAD)"
if [ "${BRANCH_NOW}" != "claude/tender-planck-pIbGk" ]; then
  echo "refusing to run from ${BRANCH_NOW}; check out claude/tender-planck-pIbGk first" >&2
  exit 2
fi

if [ ! -d rsfs_mode ]; then
  echo "rsfs_mode/ not found at repo root" >&2
  exit 2
fi

# Split rsfs_mode/ into its own history rooted at /, preserving commits.
git subtree split --prefix=rsfs_mode -b rsfs_mode-export

# Push the split branch as main of the new repo.
git push "${REMOTE_URL}" rsfs_mode-export:main

echo
echo "Pushed split history to ${REMOTE_URL} main."
echo "You can now delete the local rsfs_mode-export branch:"
echo "  git branch -D rsfs_mode-export"
