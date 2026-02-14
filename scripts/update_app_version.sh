#!/bin/bash
# This script updates the version in src/i18n/__init__.py based on the version specified in pyproject.toml
# Usage: ./scripts/update_app_version.sh

CUR_DIR="$(cd "$(dirname "$0")" >/dev/null 2>&1 && pwd)"
PJ_DIR="$(cd $CUR_DIR/.. && pwd)"

# Read version from pyproject.toml
version=$(grep '^version\s*=' $PJ_DIR/pyproject.toml | sed -E "s/version\s*=\s*['\"]([^'\"]+)['\"]/\\1/")

# Replace version in src/i18n/__init__.py
sed -i -E "s/(__version__\s*=\s*).*/\1\"$version\"/" $PJ_DIR/src/i18n/__init__.py
echo "Updated version to $version in src/i18n/__init__.py"
