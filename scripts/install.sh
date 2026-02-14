#!/bin/bash
# This script to install the package.
# Usage: ./scripts/install.sh
set -euo pipefail

CUR_DIR="$(cd "$(dirname "$0")" >/dev/null 2>&1 && pwd)"
PJ_DIR="$(cd "$CUR_DIR"/.. && pwd)"
DIST_DIR="$PJ_DIR/dist"

# Install the package:
cd "$PJ_DIR"
# Collect all wheel files
WHEELS=("$DIST_DIR"/*.whl)
if [ ! -e "${WHEELS[0]}" ]; then
    echo "Error: no .whl files found in $DIST_DIR"
    exit 1
fi

echo "Installing wheel files:"
for w in "${WHEELS[@]}"; do
    echo " - $(basename "$w")"
done

if ! uv pip install "${WHEELS[@]}" "$@"; then
    echo "Installation failed."
    exit 1
fi
echo "Installed wheel files successfully."
