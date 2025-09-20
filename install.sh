#!/usr/bin/env bash
set -euo pipefail

TARGET="/usr/local/bin/project"
SCRIPT_NAME="project"

# Prefer /opt/homebrew on Apple Silicon if writable
if [[ $(uname -m) == "arm64" && -d "/opt/homebrew/bin" && -w "/opt/homebrew/bin" ]]; then
  TARGET="/opt/homebrew/bin/project"
fi

if [[ ! -f "$SCRIPT_NAME" ]]; then
  echo "Run this from the directory containing the 'project' script." >&2
  exit 1
fi

chmod +x "$SCRIPT_NAME"
mkdir -p "$(dirname "$TARGET")"
cp "$SCRIPT_NAME" "$TARGET"

echo "Installed to $TARGET"
"$TARGET" help || true