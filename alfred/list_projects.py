#!/usr/bin/env python3
import subprocess
import json
import sys

# Get optional filter key from command line argument
filter_key = sys.argv[1] if len(sys.argv) > 1 else None

# Build command with optional filter parameter
cmd = ['project', 'list']
if filter_key:
    cmd.append(filter_key)

result = subprocess.run(cmd, capture_output=True, text=True)
lines = result.stdout.strip().split('\n')

items = []
for key in lines:
    key = key.strip().split(" ").pop(0).strip()
    items.append({
        "title": key,
        # "subtitle": key,
        "arg": key,
        "autocomplete": key,
    })

output = {"items": items}
print(json.dumps(output, indent=4))
