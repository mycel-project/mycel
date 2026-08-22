#!/bin/bash
# Usage: ./scripts/bump_version.sh 1.2.3
#        ./scripts/bump_version.sh 1.3.0-beta

set -e
 
cd "$(dirname "$0")/.."
 
if [ -z "$1" ]; then
    echo "Usage: $0 <version>   (e.g. $0 1.2.3 or $0 1.3.0-beta)"
    exit 1
fi
 
VERSION="$1"
TAG="v${VERSION}"
 
# Refuse to run with a dirty working tree
if [ -n "$(git status --porcelain)" ]; then
    echo "Error: working tree is not clean. Commit or stash your changes first."
    exit 1
fi
 
# Refuse if the tag already exists
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "Error: tag $TAG already exists."
    exit 1
fi
 
echo "==> Bumping VERSION to ${VERSION}"
echo "${VERSION}" > VERSION
 
# If an "Unreleased" section exists, rename it to the new version.
# Otherwise, insert a fresh "## <version>" section at the top for the user
# to fill in.
if grep -qE "^## Unreleased" CHANGELOG.md; then
    sed -i "0,/^## Unreleased/s//## ${VERSION}/" CHANGELOG.md
    echo "==> Renamed '## Unreleased' to '## ${VERSION}' in CHANGELOG.md"
else
    echo "==> No '## Unreleased' section found — inserting a new '## ${VERSION}' section."
    TMP=$(mktemp)
    {
        echo "## ${VERSION}"
        echo "- "
        echo ""
        cat CHANGELOG.md
    } > "$TMP"
    mv "$TMP" CHANGELOG.md
fi
 
# Let the user freely review/edit CHANGELOG.md in their own editor
echo ""
echo "==> Review/edit CHANGELOG.md now (e.g. in Emacs), then come back here."
read -p "Press Enter once you're done editing... "
 
if ! grep -qE "^## (${TAG}|${VERSION})" CHANGELOG.md; then
    echo "Warning: no '## ${VERSION}' (or '## ${TAG}') section found in CHANGELOG.md."
    read -p "Continue anyway? (y/N) " CONFIRM
    if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
        echo "Aborted."
        git checkout -- VERSION CHANGELOG.md 2>/dev/null || true
        exit 1
    fi
fi
 
git add VERSION CHANGELOG.md
git commit -m "chore: release ${VERSION}"
 
echo "==> Tagging ${TAG}"
git tag "${TAG}"
 
echo ""
echo "==> Ready to push. This will trigger the release workflow."
read -p "Push commit and tag now? (y/N) " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Not pushed. Run manually when ready:"
    echo "  git push origin HEAD"
    echo "  git push origin ${TAG}"
    exit 0
fi
 
git push origin HEAD
git push origin "${TAG}"
 
echo "==> Done. Release ${TAG} pushed."
 
