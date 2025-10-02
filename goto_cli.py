#!/usr/bin/env python3
import argparse
import sys
import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".project-cli"
DATA_FILE = CONFIG_DIR / "projects.json"


def load_data():
    if not DATA_FILE.exists():
        return {}
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_data(d):
    tmp = DATA_FILE.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    tmp.replace(DATA_FILE)


def ensure_active(d):
    active = d.get("active-project")
    if not active or active not in d:
        print("No active project.", file=sys.stderr)
        sys.exit(2)
    return active


# --- Goto commands ---
def goto_add(args):
    d = load_data()
    active = ensure_active(d)
    key, val = args.key, args.value
    stored = val if val.startswith("http") else os.path.abspath(val)
    d[active][key] = stored
    save_data(d)
    print(f"[{active}] set '{key}' -> {stored}")


def goto_update(args):
    d = load_data()
    active = ensure_active(d)
    if args.key not in d[active]:
        print(f"No such shortcut: {args.key}", file=sys.stderr)
        sys.exit(1)
    new_val = args.value if args.value.startswith("http") else os.path.abspath(args.value)
    print(new_val)
    d[active][args.key] = new_val
    save_data(d)
    print(f"[{active}] updated '{args.key}' -> {new_val}")


def goto_list(args):
    d = load_data()
    active = ensure_active(d)
    entries = d.get(active, {})
    urls = {k: v for k, v in entries.items() if v.startswith("http")}
    dirs = {k: v for k, v in entries.items() if not v.startswith("http")}

    if urls:
        if args.filter is None or args.filter == "url":
            print("URLs:")
            for k, v in urls.items():
                print(f"- {k}: {v}")
            print()
    if dirs:
        if args.filter is None or args.filter == "dir":
            print("Directories:")
            for k, v in dirs.items():
                print(f"- {k}: {v}")


def goto_rename(args):
    d = load_data()
    active = ensure_active(d)
    d[active][args.new] = d[active].pop(args.old)
    save_data(d)
    print(f"[{active}] renamed '{args.old}' -> '{args.new}'")


def goto_remove(args):
    d = load_data()
    active = ensure_active(d)
    del d[active][args.key]
    save_data(d)
    print(f"[{active}] removed '{args.key}'")


def goto_key(args):
    d = load_data()
    active = ensure_active(d)
    entries = d.get(active, {})
    target = entries.get(args.key)
    if not target:
        print(f"No such shortcut: {args.key}", file=sys.stderr)
        sys.exit(1)
    if target.startswith("http"):
        os.system(f"open {target}")
    else:
        print(f"{target}")


def build_parser():
    p = argparse.ArgumentParser(prog="goto")
    sub = p.add_subparsers(dest="cmd")

    g_add = sub.add_parser("add", help="Add shortcut (e.g., url, frontend)")
    g_add.add_argument("key", help="Shortcut key name")
    g_add.add_argument("value", help="URL or directory path")
    g_add.set_defaults(func=goto_add)

    g_update = sub.add_parser("update", help="Update shortcut value")
    g_update.add_argument("key", help="Shortcut key to update")
    g_update.add_argument("value", help="New URL or directory path")
    g_update.set_defaults(func=goto_update)

    g_list = sub.add_parser("list", help="List shortcuts (URLs first)")
    g_list.add_argument("filter", nargs="?", choices=["url", "dir"],
                        help="List only URL shortcuts (url) or directory shortcuts (dir)")
    g_list.set_defaults(func=goto_list)

    g_ren = sub.add_parser("rename", help="Rename shortcut key")
    g_ren.add_argument("old", help="Old shortcut key")
    g_ren.add_argument("new", help="New shortcut key")
    g_ren.set_defaults(func=goto_rename)

    g_rm = sub.add_parser("remove", help="Remove shortcut")
    g_rm.add_argument("key", help="Shortcut key to remove")
    g_rm.set_defaults(func=goto_remove)

    return p


def main():
    parser = build_parser()
    known_cmds = {"add", "update", "list", "rename", "remove"}
    if len(sys.argv) > 1 and sys.argv[1] not in known_cmds:
        # Treat as key lookup: goto <key>
        class Args:
            pass

        args = Args()
        args.key = sys.argv[1]
        goto_key(args)
    else:
        args = parser.parse_args()
        if hasattr(args, "func"):
            args.func(args)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
