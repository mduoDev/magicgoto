# project-cli

A lightweight macOS terminal tool to manage projects and their shortcuts (URLs & directories).

### Project Management
```bash
# Add and manage projects
project add project-a             # Create new project
project project-a                 # Switch to project-a as active
project list                      # List all projects with shortcut counts
project list frontend             # List projects that have 'frontend' shortcut
project active                    # Show currently active project
project rename old-name new-name  # Rename a project
project remove project-a          # Remove project (with confirmation)
project remove project-a -y       # Remove project without confirmation
```

### Shortcuts Management (goto)
```bash
# Add shortcuts to the active project
goto add url https://google.com           # Add URL shortcut
goto add frontend ~/project-a/frontend/   # Add directory shortcut

# List shortcuts
goto list                                 # Show all shortcuts (URLs first, then directories)

# Use shortcuts
goto url                                  # Open URL in browser
goto frontend                            # Print directory path (use with cd)

# Manage shortcuts
goto update frontend ~/new-path/          # Update existing shortcut
goto rename old-key new-key               # Rename shortcut key
goto remove frontend                      # Remove shortcut
```


### Enable Autocomplete (zsh)

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