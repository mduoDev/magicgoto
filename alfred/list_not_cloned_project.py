#!/usr/bin/env python3
import subprocess
import json
import sys


def get_non_existing_clones():
    cmd = ["project", "list", "!dir"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    non_cloned_project = set(result.stdout.strip().split('\n'))

    cmd = ["project", "list", "repo"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    projects_with_repo = set(result.stdout.strip().split('\n'))

    return non_cloned_project.intersection(projects_with_repo)


def main():
    try:
        ready_to_clone = get_non_existing_clones()
        items = []
        for key in ready_to_clone:
            key = key.strip().split(" ").pop(0).strip()
            items.append({
                "title": key,
                "arg": key,
                "autocomplete": key,
            })

        output = {"items": items}
        print(json.dumps(output, indent=4))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
