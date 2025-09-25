#!/usr/bin/env bash
set -euo pipefail

# Set target directory
TARGET_DIR="/usr/local/bin"
if [[ $(uname -m) == "arm64" && -d "/opt/homebrew/bin" && -w "/opt/homebrew/bin" ]]; then
  TARGET_DIR="/opt/homebrew/bin"
fi

declare -A SCRIPTS=(["goto"]="goto_cli.py" ["project"]="project_cli.py" )

for NAME in "${!SCRIPTS[@]}"; do
  SCRIPT="${SCRIPTS[$NAME]}"
  TARGET="$TARGET_DIR/$NAME"

  if [[ ! -f "$SCRIPT" ]]; then
    echo "Run this from the directory containing '$SCRIPT'." >&2
    exit 1
  fi

  chmod +x "$SCRIPT"
  mkdir -p "$(dirname "$TARGET")"
  cp "$SCRIPT" "$TARGET"
  echo "Installed $SCRIPT to $TARGET"
done