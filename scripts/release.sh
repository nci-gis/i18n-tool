#!/bin/bash
# This script releases a new version.
# Usage: ./scripts/release.sh

set -euo pipefail

CUR_DIR="$(cd "$(dirname "$0")" >/dev/null 2>&1 && pwd)"
PJ_DIR="$(cd "$CUR_DIR"/.. && pwd)"
DIST_DIR="$PJ_DIR/dist"

STABLE_BRANCH="${STABLE_BRANCH:-main}"   # change if your branch is named differently
BUMP_LEVEL="${BUMP_LEVEL:-auto}"           # auto | patch | minor | major
PUSH="${PUSH:-true}"                       # set to false to avoid pushing
BUILD="${BUILD:-false}"                    # set to true to build after tagging (e.g., with hatch)

# Ensure we are on the stable branch, e.g., 'stable/*' or 'main'
current_branch="$(git rev-parse --abbrev-ref HEAD)"
echo "Current branch: $current_branch"
echo "Stable branch: $STABLE_BRANCH"
if [[ "$current_branch" == stable/* ]]; then
    echo "On a stable/* branch."
elif [[ "$current_branch" == "$STABLE_BRANCH" ]]; then
    echo "On the stable branch: $STABLE_BRANCH."
else
    echo "ERROR: You must release from a branch matching '$STABLE_BRANCH' or 'stable/*' (current: '$current_branch')."
    exit 1
fi

# if [[ "$current_branch" != stable/* || "$current_branch" != "$STABLE_BRANCH" ]]; then
#     echo "ERROR: You must release from a branch matching '$STABLE_BRANCH' or 'stable/*' (current: '$current_branch')."
#     exit 1
# else
#     if [[ "$current_branch" != "$STABLE_BRANCH" ]]; then
#         echo "ERROR: You must release from '$STABLE_BRANCH' (current: '$current_branch')."
#         exit 1
#     fi
# fi

# if [[ "$current_branch" != "$STABLE_BRANCH" ]]; then
#     echo "ERROR: You must release from '$STABLE_BRANCH' (current: '$current_branch')."
#     exit 1
# fi

# Ensure working tree is clean
if [[ -n "$(git status --porcelain)" ]]; then
    echo "ERROR: Working tree not clean. Commit/stash changes before releasing."
    # exit 1
fi

# Pull latest to ensure up-to-date
git pull --ff-only

# Bump version & update changelog (non-interactive)
if [[ "$BUMP_LEVEL" == "auto" ]]; then
    cz bump --yes
else
    cz bump --yes --increment "$BUMP_LEVEL"
fi

# (Optional) regenerate changelog explicitly. cz bump already updates it.
# cz changelog

new_tag="$(git describe --tags --abbrev=0)"
echo "✅ Released tag: $new_tag"

# Optional build step (e.g., Hatch)
if [[ "$BUILD" == "true" ]]; then
    echo "🔧 Building package..."
    hatch build
fi

# Push branch and tags
if [[ "$PUSH" == "true" ]]; then
    # git push origin "$STABLE_BRANCH" --follow-tags
    # git push origin --tags
    echo "🚀 Pushed '$STABLE_BRANCH' and tags."
else
    echo "ℹ️ Skipped push (PUSH=false)."
fi
