#!/usr/bin/env bash
set -euo pipefail

# Install binary
BIN_SRC="project"
BIN_NAME="project"
TARGET="/usr/local/bin/$BIN_NAME"

# Prefer /opt/homebrew on Apple Silicon if writable
if [[ $(uname -m) == "arm64" && -d "/opt/homebrew/bin" && -w "/opt/homebrew/bin" ]]; then
  TARGET="/opt/homebrew/bin/$BIN_NAME"
fi

if [[ ! -f "$BIN_SRC" ]]; then
  echo "Run this from the directory containing the '$BIN_SRC' script." >&2
  exit 1
fi

chmod +x "$BIN_SRC"
mkdir -p "$(dirname "$TARGET")"
cp "$BIN_SRC" "$TARGET"

echo "Installed binary to $TARGET"

# Determine Homebrew prefix if available (helps find completion dirs)
BREW_PREFIX=""
if command -v brew >/dev/null 2>&1; then
  BREW_PREFIX="$(brew --prefix 2>/dev/null || true)"
fi

# Install shell completions
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ZSH_SRC="$SCRIPT_DIR/completion/project.zsh"
BASH_SRC="$SCRIPT_DIR/completion/project.bash"

SHELL_NAME="$(basename "${SHELL:-}")"

install_zsh_completion() {
  local dest
  # Priority order of common zsh site-function paths
  for dest in \
    "$BREW_PREFIX/share/zsh/site-functions" \
    "/usr/local/share/zsh/site-functions" \
    "/opt/homebrew/share/zsh/site-functions" \
    "$HOME/.zsh/completions"; do
    [[ -n "$dest" ]] || continue
    mkdir -p "$dest"
    if cp "$ZSH_SRC" "$dest/_project" 2>/dev/null; then
      echo "Installed zsh completion to $dest/_project"
      echo "If not active, ensure in ~/.zshrc: fpath=($dest $fpath); autoload -Uz compinit && compinit"
      return 0
    fi
  done
  echo "Could not install zsh completion automatically. Copy $ZSH_SRC to a directory in your fpath as _project." >&2
}

install_bash_completion() {
  local dest
  # Priority order of common bash-completion dirs
  for dest in \
    "$BREW_PREFIX/etc/bash_completion.d" \
    "/usr/local/etc/bash_completion.d" \
    "/opt/homebrew/etc/bash_completion.d" \
    "$HOME/.bash_completions"; do
    [[ -n "$dest" ]] || continue
    mkdir -p "$dest"
    if cp "$BASH_SRC" "$dest/project.bash" 2>/dev/null; then
      echo "Installed bash completion to $dest/project.bash"
      # If we installed to a user dir, try to source it automatically
      if [[ "$dest" == "$HOME/.bash_completions" ]]; then
        local rc
        for rc in "$HOME/.bashrc" "$HOME/.bash_profile"; do
          if [[ -f "$rc" ]] && ! grep -q "project.bash" "$rc" 2>/dev/null; then
            echo "source $dest/project.bash" >> "$rc"
            echo "Added 'source $dest/project.bash' to $rc"
          fi
        done
      fi
      return 0
    fi
  done
  echo "Could not install bash completion automatically. Source $BASH_SRC from your ~/.bashrc." >&2
}

# Only attempt completion install if sources exist
if [[ -f "$ZSH_SRC" || -f "$BASH_SRC" ]]; then
  case "$SHELL_NAME" in
    zsh)
      [[ -f "$ZSH_SRC" ]] && install_zsh_completion || echo "zsh completion source not found: $ZSH_SRC" ;;
    bash)
      [[ -f "$BASH_SRC" ]] && install_bash_completion || echo "bash completion source not found: $BASH_SRC" ;;
    *)
      # Unknown shell; try both, silently ignore failures
      [[ -f "$ZSH_SRC" ]] && install_zsh_completion || true
      [[ -f "$BASH_SRC" ]] && install_bash_completion || true
      ;;
  esac
else
  echo "Completion sources not found; skipping completion installation."
fi

# Show help at the end
"$TARGET" help || true