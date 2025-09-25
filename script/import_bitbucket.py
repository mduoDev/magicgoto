import re
import subprocess
import os
from pathlib import Path

def read_repo_env(env_path='.env'):
    repo_path = None
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('REPO='):
                repo_path = line.strip().split('=', 1)[1]
                repo_path = os.path.expanduser(repo_path)
                break
    return repo_path

repo = read_repo_env()

with open('urls.txt', 'r') as file:
    for line in file:
        url = line.strip()
        if not url: continue
        if url.endswith('/browse'):
            url = url[:-6]
        match = re.search(r'repos\/(.*?)\/', url)
        if match:
            project = match.group(1)
            # subprocess.run(f"project add {project}".split(" "))
            subprocess.run(f"project {project}".split(" "))
            subprocess.run(f"goto update repo {url}".split(" "))
