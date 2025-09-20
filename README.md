# project-cli

A lightweight macOS terminal tool to manage projects and their shortcuts (URLs & directories).

## Features
- Add, list, rename, and remove projects.
- Select one project as the active project.
- Within a project, add/remove/list shortcuts to URLs and directories.
- `project goto <key>`: opens URLs in the browser or prints directory path for easy `cd $(...)`.
- **Shell autocompletion** for zsh and bash.

### Usage
```bash
project add project-a
project project-a
project goto add url https://google.com
project goto add frontend ~/project-a/frontend/
project goto list          # URLs first, then directories
project goto list url      # only URLs
project goto list dir      # only directories
project goto url           # opens browser
cd $(project goto frontend) # change directory
project list
```


### Enable Autocomplete (zsh)

Add the file to your path and enable:
```bash
# from repo root
mkdir -p ~/.zsh/completions
cp completion/project.zsh ~/.zsh/completions/_project
# in ~/.zshrc
fpath=(~/.zsh/completions $fpath)
autoload -Uz compinit && compinit
# reload shell or: source ~/.zshrc
```

### Uninstall
```bash
chmod +x uninstall.sh
./uninstall.sh            # remove binary only
./uninstall.sh --purge    # also delete ~/.project-cli (all saved projects)
```





### Data storage
```bash
~/.project-cli/projects.json
```


### Example JSON
```json
{
  "active-project": "project-a",
  "project-a": {
    "url": "https://google.com",
    "frontend": "~/project-a/frontend/"
  },
  "project-b": {
    "url": "https://google.com",
    "backend": "~/project-b/backend/"
  }
}
```