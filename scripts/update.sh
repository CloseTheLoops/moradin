#!/bin/bash
# Moradin framework update — chezmoi-style merge from upstream.
# Preserves user content (memory/*, projects/*) via merge strategy.
#
# Usage: ./scripts/update.sh
#
# License: MIT
set -e

UPSTREAM_REMOTE="${MORADIN_UPSTREAM_REMOTE:-upstream}"
UPSTREAM_URL="${MORADIN_UPSTREAM_URL:-https://github.com/closetheloops/moradin.git}"
UPSTREAM_BRANCH="${MORADIN_UPSTREAM_BRANCH:-main}"

echo "Moradin framework update"
echo "========================"
echo "Upstream remote: $UPSTREAM_REMOTE"
echo "Upstream URL:    $UPSTREAM_URL"
echo "Upstream branch: $UPSTREAM_BRANCH"
echo ""

if ! git remote | grep -q "^${UPSTREAM_REMOTE}$"; then
  echo "Adding remote ${UPSTREAM_REMOTE}..."
  git remote add "${UPSTREAM_REMOTE}" "${UPSTREAM_URL}"
fi

echo "Fetching upstream..."
git fetch "${UPSTREAM_REMOTE}"

echo ""
echo "Merging ${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH} (preserving user content via -X ours)..."
git merge "${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH}" -X ours --no-edit

echo ""
echo "Done. Review what changed:"
echo "  git log -p HEAD~..HEAD"
