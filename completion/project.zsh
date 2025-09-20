#compdef project
# Zsh completion for project-cli

__project_list_projects() {
  command project --_complete-project-names 2>/dev/null
}

__project_list_keys() {
  command project --_complete-goto-keys 2>/dev/null
}

_project() {
  local -a subcmds
  subcmds=(
    'add:Add a new project'
    'list:List projects'
    'rename:Rename a project'
    'remove:Remove a project'
    'goto:Work with shortcuts'
    'active:Show active project'
    'help:Show help'
  )

  if (( CURRENT == 2 )); then
    # Offer subcommands or direct project names (for selection)
    _describe -t commands 'project subcommand' subcmds
    compadd -- $(__project_list_projects)
    return
  fi

  case ${words[2]} in
    add)
      _message 'project name';;
    rename)
      if (( CURRENT == 3 )); then
        compadd -- $(__project_list_projects)
      else
        _message 'new project name'
      fi ;;
    remove)
      compadd -- $(__project_list_projects) ;;
    active)
      ;;
    help)
      ;;
    goto)
      if (( CURRENT == 3 )); then
        # allow subcommands or direct <key>
        compadd add list rename remove
        compadd -- $(__project_list_keys)
        return
      fi
      case ${words[3]} in
        add)
          if (( CURRENT == 4 )); then _message 'shortcut key'; else _message 'url or directory path'; fi ;;
        list)
          if (( CURRENT == 4 )); then compadd url dir; fi ;;
        rename)
          compadd -- $(__project_list_keys) ;;
        remove)
          compadd -- $(__project_list_keys) ;;
        *)
          # direct key mode (project goto <key>)
          compadd -- $(__project_list_keys) ;;
      esac ;;
    *) ;;
  esac
}

compdef _project project