#!/usr/bin/env python3
import subprocess
import json
import sys
import re

# Get optional filter key from command line argument
if len(sys.argv) < 2:
    exit(0)

list_type = sys.argv[1] or ' '

# Build command with optional filter parameter
cmd = f"goto list {list_type}".split(" ")

result = subprocess.run(cmd, capture_output=True, text=True)
lines = result.stdout.strip().split('\n')[1:]

items = []
for key in lines:
    matches = re.match(r'^- ([\w|-]+?): (.+)', key)

    if not matches: continue

    key, value = matches.group(1, 2)
    items.append({
        "title": key,
        "subtitle": value,
        "arg": key,
        "autocomplete": key,
    })

output = {"items": items}
print(json.dumps(output, indent=4, ensure_ascii=False))
