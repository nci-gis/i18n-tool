#!/bin/bash
# This script builds the package and creates a distributable wheel file.
# Usage: ./scripts/build.sh

CUR_DIR="$(cd "$(dirname "$0")" >/dev/null 2>&1 && pwd)"
PJ_DIR="$(cd "$CUR_DIR"/.. && pwd)"
DIST_DIR="$PJ_DIR/dist"

# Clean previous builds
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"
echo "Cleaned previous builds."

# Build the package:
cd "$PJ_DIR" || exit 1
# python -m build --wheel --outdir $DIST_DIR

if ! hatch build -c "$DIST_DIR"; then
    echo "Build failed."
    exit 1
fi
echo "Build succeeded. Wheel file created in $DIST_DIR."
