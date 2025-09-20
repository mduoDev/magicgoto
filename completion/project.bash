# Bash completion for project-cli
# Source this file from ~/.bashrc or install via install.sh

_project_complete() {
  local cur prev
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD-1]}"

  _projects() { command project --_complete-project-names 2>/dev/null; }
  _keys() { command project --_complete-goto-keys 2>/dev/null; }

  # at position 1 (after command): suggest subcommands or project names
  if [[ $COMP_CWORD -eq 1 ]]; then
    local subcmds="add list rename remove goto active help"
    COMPREPLY=( $(compgen -W "$subcmds" -- "$cur") $(compgen -W "$(_projects)" -- "$cur") )
    return 0
  fi

  case "${COMP_WORDS[1]}" in
    add)
      return 0;;
    rename)
      if [[ $COMP_CWORD -eq 2 ]]; then
        COMPREPLY=( $(compgen -W "$(_projects)" -- "$cur") )
      fi
      return 0;;
    remove)
      COMPREPLY=( $(compgen -W "$(_projects)" -- "$cur") ); return 0;;
    goto)
      if [[ $COMP_CWORD -eq 2 ]]; then
        COMPREPLY=( $(compgen -W "add list rename remove" -- "$cur") $(compgen -W "$(_keys)" -- "$cur") )
        return 0
      fi
      case "${COMP_WORDS[2]}" in
        add)
          # key then value (path/url)
          if [[ $COMP_CWORD -eq 3 ]]; then
            return 0
          else
            COMPREPLY=( $(compgen -f -- "$cur") )
            return 0
          fi;;
        list)
          if [[ $COMP_CWORD -eq 3 ]]; then
            COMPREPLY=( $(compgen -W "url dir" -- "$cur") )
          fi
          return 0;;
        rename|remove)
          COMPREPLY=( $(compgen -W "$(_keys)" -- "$cur") ); return 0;;
        *)
          COMPREPLY=( $(compgen -W "$(_keys)" -- "$cur") ); return 0;;
      esac;;
    *)
      return 0;;
  esac
}

complete -F _project_complete project