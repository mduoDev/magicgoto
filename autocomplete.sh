#!/usr/bin/env bash
# Bash completion for project-cli

_project_cli_completions() {
  local cur prev cmds
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD-1]}"

  cmds="add list rename remove goto active help"

  case "$prev" in
    project)
      COMPREPLY=( $(compgen -W "$cmds" -- "$cur") )
      return 0
      ;;
    goto)
      COMPREPLY=( $(compgen -W "add list rename remove" -- "$cur") )
      # also complete keys from active project
      keys=$(project goto list 2>/dev/null | awk '{print $2}')
      COMPREPLY+=( $(compgen -W "$keys" -- "$cur") )
      return 0
      ;;
    list)
      if [[ ${COMP_WORDS[COMP_CWORD-2]} == "goto" ]]; then
        COMPREPLY=( $(compgen -W "url dir" -- "$cur") )
      fi
      return 0
      ;;
  esac
}

complete -F _project_cli_completions project