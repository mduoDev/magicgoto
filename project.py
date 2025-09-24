#!/usr/bin/env python3
import argparse
import json
import os
import sys
import subprocess
from pathlib import Path

APP_NAME = "project-cli"
CONFIG_DIR = Path.home() / ".project-cli"
DATA_FILE = CONFIG_DIR / "projects.json"

KNOWN_SUBCMDS = {"add", "list", "rename", "remove", "goto", "active", "help"}


# ---------------- Utilities ---------------- #

def expand_path(p: str) -> str:
    return os.path.expanduser(os.path.expandvars(p))


def load_data() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        return {}
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {DATA_FILE} is not valid JSON.")
        sys.exit(1)


def save_data(d: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    tmp = DATA_FILE.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    tmp.replace(DATA_FILE)


def ensure_active(d: dict) -> str:
    active = d.get("active-project")
    if not active:
        print("No active project. Select one: `project <name>` or create with `project add <name>`. ", file=sys.stderr)
        sys.exit(2)
    if active not in d:
        print(f"Active project '{active}' missing. Fix by selecting another: `project <name>`.", file=sys.stderr)
        sys.exit(2)
    return active


def mac_open(target: str) -> int:
    # Use macOS `open` to launch URLs or paths
    try:
        return subprocess.call(["open", target])
    except FileNotFoundError:
        print("Error: macOS `open` command not found.", file=sys.stderr)
        return 1


# -------- Hidden completion helpers (used by shell completions) -------- #

def _print_project_names():
    d = load_data()
    for k in d.keys():
        if k != "active-project":
            print(k)


def _print_goto_keys():
    d = load_data()
    active = d.get("active-project")
    if not active or active not in d:
        return
    for k in d.get(active, {}).keys():
        print(k)


# ---------------- Commands ---------------- #

def cmd_add(args):
    d = load_data()
    name = args.name
    if name in d:
        if args.force:
            pass
        else:
            print(f"Project '{name}' already exists. Use --force to overwrite.", file=sys.stderr)
            sys.exit(1)
    d.setdefault("active-project", d.get("active-project") or name)
    d[name] = d.get(name, {})
    save_data(d)
    select_project(name)
    print(f"Added project '{name}'. Active = {name}")


def cmd_list(_args):
    d = load_data()
    active = d.get("active-project")
    projects = [k for k in d.keys() if k != "active-project"]
    if not projects:
        print("No projects yet. Add one with `project add <name>`.")
        return
    for k in sorted(projects):
        star = "*" if k == active else " "
        count = len(d.get(k, {}))
        print(f"{star} {k} ({count} shortcut{'s' if count != 1 else ''})")


def cmd_rename(args):
    d = load_data()
    old, new = args.old, args.new
    if old not in d:
        print(f"No such project: {old}", file=sys.stderr)
        sys.exit(1)
    if new in d and not args.force:
        print(f"Project '{new}' already exists. Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)
    d[new] = d.pop(old)
    if d.get("active-project") == old:
        d["active-project"] = new
    save_data(d)
    print(f"Renamed '{old}' -> '{new}'")


def cmd_remove(args):
    d = load_data()
    name = args.name
    if name not in d:
        print(f"No such project: {name}", file=sys.stderr)
        sys.exit(1)
    if not args.yes:
        resp = input(f"Delete project '{name}'? This cannot be undone. [y/N] ").strip().lower()
        if resp != "y":
            print("Aborted.")
            return
    del d[name]
    if d.get("active-project") == name:
        d["active-project"] = next((k for k in d.keys() if k != "active-project"), None)
    save_data(d)
    print(f"Removed '{name}'. Active = {d.get('active-project')}")


# ----- goto subcommands ----- #

def goto_add(args):
    d = load_data()
    active = ensure_active(d)
    key = args.key
    val = args.value
    # expand only for directories; keep URLs as-is
    if val.startswith("http://") or val.startswith("https://"):
        stored = val
    else:
        stored = os.path.expanduser(val)
    d[active][key] = stored
    save_data(d)
    print(f"[{active}] set '{key}' -> {stored}")


def goto_list(args):
    d = load_data()
    active = ensure_active(d)
    entries = d.get(active, {})
    if not entries:
        print(f"[{active}] No shortcuts yet. Add with `project goto add <key> <url|path>`.")
        return

    urls = {k: v for k, v in entries.items() if v.startswith("http://") or v.startswith("https://")}
    dirs = {k: v for k, v in entries.items() if not (v.startswith("http://") or v.startswith("https://"))}

    # Optional filters: url | dir
    if getattr(args, "filter", None) == "url":
        if urls:
            for k, v in urls.items():
                print(f"- {k}: {v}")
        return
    if getattr(args, "filter", None) == "dir":
        if dirs:
            for k, v in dirs.items():
                print(f"- {k}: {v}")
        return

    # Default: show URLs first, then directories
    if urls:
        print("URLs:")
        for k, v in urls.items():
            print(f"- {k}: {v}")
    if dirs:
        print("Directories:")
        for k, v in dirs.items():
            print(f"- {k}: {v}")


def goto_rename(args):
    d = load_data()
    active = ensure_active(d)
    if args.old not in d[active]:
        print(f"No such shortcut: {args.old}", file=sys.stderr)
        sys.exit(1)
    d[active][args.new] = d[active].pop(args.old)
    save_data(d)
    print(f"[{active}] renamed '{args.old}' -> '{args.new}'")


def goto_remove(args):
    d = load_data()
    active = ensure_active(d)
    if args.key not in d[active]:
        print(f"No such shortcut: {args.key}", file=sys.stderr)
        sys.exit(1)
    del d[active][args.key]
    save_data(d)
    print(f"[{active}] removed '{args.key}'")


def goto_key(args):
    d = load_data()
    active = ensure_active(d)
    entries = d.get(active, {})

    if args.key not in entries:
        print(f"No such shortcut: {args.key}", file=sys.stderr)
        sys.exit(1)

    target = entries[args.key]
    if target.startswith("http://") or target.startswith("https://"):
        print(f"Opening {args.key}: {target}")
        rc = mac_open(target)
        if rc != 0:
            print(f"Failed to open: {target}", file=sys.stderr)
    else:
        new_dir = expand_path(target)
        if os.path.isdir(new_dir):
            # Print command so user can `cd $(project goto <key>)`
            print(new_dir)
        else:
            print(f"Directory not found: {new_dir}", file=sys.stderr)
            sys.exit(1)


# ---------------- Argparse ---------------- #

def build_parser():
    p = argparse.ArgumentParser(prog="project", add_help=False)
    sub = p.add_subparsers(dest="cmd")

    # add
    p_add = sub.add_parser("add", help="Add a new project")
    p_add.add_argument("name")
    p_add.add_argument("--force", action="store_true", help="Overwrite if exists")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = sub.add_parser("list", help="List projects")
    p_list.set_defaults(func=cmd_list)

    # rename
    p_ren = sub.add_parser("rename", help="Rename a project")
    p_ren.add_argument("old")
    p_ren.add_argument("new")
    p_ren.add_argument("--force", action="store_true")
    p_ren.set_defaults(func=cmd_rename)

    # remove
    p_rm = sub.add_parser("remove", help="Remove a project")
    p_rm.add_argument("name")
    p_rm.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    p_rm.set_defaults(func=cmd_remove)

    # goto group
    p_goto = sub.add_parser("goto", help="Manage shortcuts for the active project")
    p_goto.add_argument("key")
    p_goto.set_defaults(func=goto_key)

    s = p_goto.add_subparsers(dest="gcmd")

    g_add = s.add_parser("add", help="Add a shortcut: key + url|path")
    g_add.add_argument("key")
    g_add.add_argument("value")
    g_add.set_defaults(func=goto_add)

    g_list = s.add_parser("list", help="List shortcuts")
    g_list.add_argument("filter", nargs="?", choices=["url", "dir"], help="Filter: url or dir")
    g_list.set_defaults(func=goto_list)

    g_ren = s.add_parser("rename", help="Rename a shortcut key")
    g_ren.add_argument("old")
    g_ren.add_argument("new")
    g_ren.set_defaults(func=goto_rename)

    g_rm = s.add_parser("remove", help="Remove a shortcut")
    g_rm.add_argument("key")
    g_rm.set_defaults(func=goto_remove)

    # active
    p_act = sub.add_parser("active", help="Show active project")

    def show_active(_):
        d = load_data()
        print(d.get("active-project") or "<none>")

    p_act.set_defaults(func=show_active)

    # help
    p_help = sub.add_parser("help", help="Show help")

    def show_help(_):
        print(USAGE)

    p_help.set_defaults(func=show_help)

    return p


USAGE = f"""
project — {APP_NAME}

Basic usage:
  project add <name>                 Add a new project
  project list                        List projects (\"*\" marks active)
  project rename <old> <new>         Rename a project
  project remove <name>              Remove a project
  project <name>                     Select active project
  project active                     Show active project

Shortcuts (for active project):
  project goto add <key> <url|path>  Add shortcut (e.g., url, frontend)
  project goto list                  List shortcuts (URLs first)
  project goto list url              List only URL shortcuts
  project goto list dir              List only directory shortcuts
  project goto rename <old> <new>    Rename shortcut key
  project goto remove <key>          Remove shortcut
  project goto <key>                 Open URL in browser or echo directory path

Examples:
  project add project-a
  project project-a
  project goto add url https://google.com
  project goto add frontend ~/project-a/frontend/
  project goto list url
  project goto list dir
  project goto url
  cd $(project goto frontend)
  project list

Data file: {DATA_FILE}
"""


def select_project(name: str):
    d = load_data()
    if name not in d:
        print(f"No such project: {name}", file=sys.stderr)
        sys.exit(1)
    d["active-project"] = name
    save_data(d)
    print(f"Selected active project: {name}")


def main():
    # Hidden completion switches
    if "--_complete-project-names" in sys.argv:
        _print_project_names()
        return
    if "--_complete-goto-keys" in sys.argv:
        _print_goto_keys()
        return

    # Special case: if first arg isn't a known subcommand, treat as project selection
    if len(sys.argv) >= 2 and sys.argv[1] not in KNOWN_SUBCMDS and not sys.argv[1].startswith("-"):
        select_project(sys.argv[1])
        return

    parser = build_parser()
    if len(sys.argv) == 1:
        print(USAGE)
        return
    args = parser.parse_args()

    # Allow direct `project goto <key>` without extra subcommand
    if args.cmd == "goto" and args.gcmd is None and len(sys.argv) >= 3:
        class FakeArgs: pass

        fake = FakeArgs()
        fake.key = sys.argv[2]
        goto_key(fake)
        return

    if hasattr(args, "func"):
        args.func(args)
    else:
        print(USAGE)


if __name__ == "__main__":
    main()
