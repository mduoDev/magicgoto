#!/usr/bin/env bash
set -euo pipefail

BIN_NAME="project"
CONFIG_DIR="$HOME/.project-cli"
PURGE=false
YES=false

for arg in "$@"; do
  case "$arg" in
    --purge) PURGE=true ;;
    -y|--yes) YES=true ;;
    -h|--help)
      cat <<EOF
Usage: ./uninstall.sh [--purge] [-y]

Removes the project-cli binary from your PATH. Optional --purge also deletes stored data in $CONFIG_DIR.
  --purge    Also remove $CONFIG_DIR (all saved projects).
  -y         Assume Yes to all prompts.
  -h         Show this help.
EOF
      exit 0 ;;
  esac
done

TARGET=$(command -v "$BIN_NAME" || true)
if [[ -z "${TARGET}" ]]; then
  for c in "/opt/homebrew/bin/$BIN_NAME" "/usr/local/bin/$BIN_NAME"; do
    if [[ -x "$c" ]]; then TARGET="$c"; break; fi
  done
fi

if [[ -n "${TARGET}" ]]; then
  echo "Removing binary: $TARGET"
  if [[ -w "$TARGET" ]]; then
    rm -f "$TARGET"
  else
    echo "Not writable. Attempting with sudo..."
    sudo rm -f "$TARGET"
  fi
  echo "Removed $TARGET"
else
  echo "No '$BIN_NAME' binary found."
fi

if [[ "$PURGE" == true ]]; then
  if [[ -d "$CONFIG_DIR" ]]; then
    if [[ "$YES" == true ]]; then
      REPLY="y"
    else
      read -r -p "Delete all data in $CONFIG_DIR? This cannot be undone. [y/N] " REPLY || true
    fi
    if [[ "$REPLY" == "y" ]]; then
      rm -rf "$CONFIG_DIR"
      echo "Purged $CONFIG_DIR"
    else
      echo "Skipped purging $CONFIG_DIR"
    fi
  else
    echo "No data directory at $CONFIG_DIR"
  fi
fi

echo "project-cli has been uninstalled."