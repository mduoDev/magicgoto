#!/usr/bin/env python3

import sys
import webbrowser
from urllib.parse import urlparse


def extract_workspace_and_repo(bitbucket_url):
    # Handles URLs like: https://domain/projects/<workspace>/repos/<repo>/browse
    path = urlparse(bitbucket_url).path.strip('/')
    parts = path.split('/')
    try:
        workspace_idx = parts.index('projects') + 1
        repo_idx = parts.index('repos') + 1
        workspace = parts[workspace_idx]
        repo = parts[repo_idx]
    except (ValueError, IndexError):
        raise ValueError("Bitbucket URL must be in the format: https://domain/projects/<workspace>/repos/<repo>/browse")
    return workspace, repo


def main():
    if len(sys.argv) != 3:
        print("Usage: get_jenkins_url.py <bitbucket_url> <jenkins_domain>")
        sys.exit(1)

    bitbucket_url = sys.argv[1]
    jenkins_domain = sys.argv[2].rstrip('/')

    workspace, repo = extract_workspace_and_repo(bitbucket_url)
    jenkins_job_url = f"{jenkins_domain}/job/{workspace}/job/{repo}/view/default/builds"

    print(jenkins_job_url)



if __name__ == "__main__":
    main()
