#compdef project

_project() {
  local -a subcmds
  subcmds=('add:Add a new project' 'list:List projects' 'rename:Rename a project' 'remove:Remove a project' 'active:Show active project')

  if (( CURRENT == 2 )); then
    _describe 'subcommand' subcmds
    return
  fi

  case "$words[2]" in
    add|rename|remove)
      local -a projects
      projects=("${(@f)$(project --_complete-project-names)}")
      _values 'project names' $projects
      ;;
    *)
      _files
      ;;
  esac
}

compdef _project project

#compdef goto

_goto() {
  local -a subcmds
  subcmds=('add:Add shortcut' 'update:Update shortcut' 'list:List shortcuts' 'rename:Rename shortcut' 'remove:Remove shortcut')

  if (( CURRENT == 2 )); then
    local -a keys
    keys=("${(@f)$(goto list | grep -E '^- [^:]+:' | sed 's/^- \([^:]*\):.*/\1/')}")
    _values 'shortcut keys' $keys
    return
  fi
}

compdef _goto goto
