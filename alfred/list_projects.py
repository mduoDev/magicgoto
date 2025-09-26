import subprocess
import json

result = subprocess.run(['project', 'list'], capture_output=True, text=True)
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
