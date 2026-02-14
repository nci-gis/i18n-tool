#!/bin/bash
# This script init the project environment.
# Usage: ./scripts/init.sh

CUR_DIR="$(cd "$(dirname "$0")" >/dev/null 2>&1 && pwd)"
PJ_DIR="$(cd "$CUR_DIR"/.. && pwd)"
# DIST_DIR="$PJ_DIR/dist"

# check if "uv" is installed
if ! command -v uv >/dev/null 2>&1; then
    echo "'uv' could not be found. Please install 'uv' to proceed."
    echo "@See: https://docs.astral.sh/uv/getting-started/installation"
    exit 1
fi

# check if "uv venv" is ready
if [ ! -d "$PJ_DIR/.venv" ]; then
    echo "'uv venv' is not set up. Setting up now..."
    if ! uv venv; then
        echo "Failed to create 'uv venv'. Please check the errors above."
        exit 1
    fi
    echo "'uv venv' created successfully."
else
    echo "'uv venv' is already set up."
fi

## Activate the virtual environment
# if Posix-compliant shell
if [ -f "$PJ_DIR/.venv/bin/activate" ]; then
    # shellcheck source=/dev/null
    source "$PJ_DIR/.venv/bin/activate"
# if Windows cmd (e.g., Git Bash)
elif [ -f "$PJ_DIR/.venv/Scripts/activate" ]; then
    # shellcheck source=/dev/null
    source "$PJ_DIR/.venv/Scripts/activate"
else
    echo "Could not find the virtual environment activation script."
    exit 1
fi

## Install dependencies using uv
echo "Installing dependencies using 'uv'..."
cd "$PJ_DIR" || exit 1
if ! uv pip install -r requirements.txt; then
    echo "Failed to install dependencies. Please check the errors above."
    exit 1
fi
echo "Dependencies installed successfully."
echo "Project environment initialized successfully."
