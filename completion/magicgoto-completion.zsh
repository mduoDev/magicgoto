#compdef project

_project() {

  local -a subcmds
  case "$words[2]" in
    rename|remove)
      local -a projects
      projects=("${(@f)$(project list | sed -E 's/^ *([^ ]+) +.*/\1/')}")
      _values 'project names' $projects
      ;;
    *)
  esac

  if (( CURRENT == 2 )); then
    projects=("${(@f)$(project list | sed -E 's/^ *([^ ]+) +.*/\1/')}")
    _values 'project names' $projects
  fi
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

  case "$words[2]" in
    update|rename|remove)
      local -a keys
      keys=("${(@f)$(goto list | grep -E '^- [^:]+:' | sed 's/^- \([^:]*\):.*/\1/')}")
      _values 'shortcut keys' $keys
      ;;
    *)
      _files
      ;;
  esac
}
compdef _goto goto
