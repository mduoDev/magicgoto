import subprocess
import json

result = subprocess.run(['project', 'list'], capture_output=True, text=True)
lines = result.stdout.strip().split('\n')

items = []
for key in lines:
    if key == 'active-project':
        continue
    key = key.strip().split(" ").pop(0)
    items.append({
        "title": key,
        # "subtitle": key,
        "arg": key,
        "autocomplete": key,
    })

output = {"items": items}
print(json.dumps(output, indent=4))
