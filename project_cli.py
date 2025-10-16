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
DEBUG = False

KNOWN_SUBCMDS = {"add", "list", "rename", "remove", "active"}


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


def cmd_list(args):
    d = load_data()
    active = d.get("active-project")
    projects = d.keys()

    # If a key is specified, filter projects that contain that key
    if hasattr(args, 'key') and args.key:
        inverted = args.key.startswith("!")

        if inverted: args.key = args.key[1:]
        filtered_projects = set([p for p in projects if args.key in d.get(p, {})])

        if not filtered_projects:
            print(f"No projects found with key '{args.key}'.")
            return

        if inverted:
            filtered_projects = set(projects).difference(filtered_projects)

        # For key-filtered results, just show the project names
        for k in sorted(filtered_projects):
            print(k)
        print(len(filtered_projects))
        return

    if not projects:
        print("No projects yet. Add one with `project add <name>`.")
        return

    for k in sorted(projects):
        star = "*" if k == active and DEBUG else " "
        count = len(d.get(k, {}))
        print(f"{star} {k} ({count} shortcut{'s' if count != 1 else ''})")

    print(len(projects))

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
    p_list.add_argument("key", nargs="?", help="Filter projects by key (optional)")
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

    # active
    p_act = sub.add_parser("active", help="Show active project")

    def show_active(_):
        d = load_data()
        print(d.get("active-project") or "<none>")

    p_act.set_defaults(func=show_active)

    return p


def select_project(name: str):
    d = load_data()
    if name not in d:
        print(f"No such project: {name}", file=sys.stderr)
        sys.exit(1)
    d["active-project"] = name
    save_data(d)
    if DEBUG: print(f"Selected active project: {name}")


def main():
    # Hidden completion switches
    if "--_complete-project-names" in sys.argv:
        _print_project_names()
        return

    # Special case: if first arg isn't a known subcommand, treat as project selection
    if len(sys.argv) >= 2 and sys.argv[1] not in KNOWN_SUBCMDS and not sys.argv[1].startswith("-"):
        select_project(sys.argv[1])
        return

    parser = build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        return
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)


if __name__ == "__main__":
    main()
