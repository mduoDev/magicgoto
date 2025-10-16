import sys
import subprocess
import os


def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: python git_clone_project.py <project-name>")
        sys.exit(1)

    project = sys.argv[1]

    # Check if dir is not empty
    dir_val = run_cmd(f"project {project} && goto haskey dir")
    if dir_val:
        raise Exception("Error: dir is not empty for this project.")

    # Check if repo is empty
    repo_val = run_cmd(f"project {project} && goto haskey repo")

    if not repo_val:
        raise Exception("Error: repo is empty for this project.")

    # Clone the repo
    os.chdir(os.path.expanduser("~/repo"))
    repo_url = (run_cmd(f"project {project} && goto haskey repo") \
                .replace('.no/projects/', '.no/scm/') \
                .replace('/repos/', '/'))

    if repo_url.endswith("/"): repo_url = repo_url[:-1]
    repo_url = repo_url + ".git"

    subprocess.check_call(f"git clone {repo_url}", shell=True)

    #  Add dir
    os.chdir(os.path.join(os.getcwd(), project))
    run_cmd("goto add dir .")


if __name__ == "__main__":
    main()
