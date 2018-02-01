#!/usr/bin/env python2.7
from __future__ import print_function
import commands
import os
import stat

from gitlab import Gitlab

def get_clone_commands(token, repo_root):
    con = Gitlab("http://gitlab.your.domain", token)
    con.auth()

    for project in con.Project(per_page=200):
        url = project.ssh_url_to_repo

        subdir = url.split(":")[1].split("/")[0]
        cmd = "bash -c '(mkdir -p {repo_root}/{subdir} && cd {repo_root}/{subdir} && git clone {url})'".format(**locals())
        yield cmd

def restructure_repos(repo_root):
    cmd = r"""
    #!/bin/sh
    cd {repo_root}/{subdir}
    git filter-branch --index-filter \
            'git ls-files -s | sed "s%\t\"*%&{prefix}/%" |
                    GIT_INDEX_FILE=$GIT_INDEX_FILE.new \
                            git update-index --index-info &&
             mv "$GIT_INDEX_FILE.new" "$GIT_INDEX_FILE"' HEAD
    """.strip()

    repo_root = os.path.abspath(repo_root)
    for entry in os.walk(repo_root):
        dir = entry[0]
        subdir = os.path.relpath(dir, repo_root)
        if len(subdir.split("/")) != 2:
            continue
        repo = subdir.replace(".git", "")

        yield cmd.format(repo_root=repo_root, prefix=repo, subdir=subdir)


def get_branches(dir):
    output = commands.getoutput("(cd {dir} && git branch -a)".format(dir=dir))
    branches = [b.strip().replace("* ", "") for b in output.strip().split("\n")]
    return branches

def integrate_repos(repo_root, monorepo):
    cmd = r"""
#!/bin/sh
cd {monorepo}
git remote add -f {alias} {dir}
git pull --no-edit {alias} {branch}
""".strip()

    repo_root = os.path.abspath(repo_root)
    for entry in os.walk(repo_root):
        dir = entry[0]
        subdir = os.path.relpath(dir, repo_root)
        if len(subdir.split("/")) != 2:
            continue
        repo = subdir.replace(".git", ""    )
        alias = repo.replace("/", "-")

        for branch in get_branches(dir):
            if branch != "master":
                continue
            if branch == "master":
                monobranch = "master"
            else:
                monobranch = "{alias}-{branch}".format(alias=alias, branch=branch)
            yield cmd.format(branch=branch, monobranch=monobranch, monorepo=monorepo, alias=alias, repo_root=repo_root, prefix=repo, subdir=subdir, dir=dir, repo=repo)

def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)

def execute_script(cmd):
    script_name = "/tmp/cmd"
    with open(script_name, "w") as f:
        f.write(cmd)
    make_executable(script_name)
    return os.system(script_name)


def main():
    WORKDIR = "/tmp/repo"
    os.system("rm -fr {}".format(WORKDIR))

    REPO_ROOT = os.path.join(WORKDIR, "repos")
    os.system("mkdir -p {}".format(REPO_ROOT))

    for cmd in get_clone_commands("YOUR_GITLAB_TOKEN", REPO_ROOT):
        rc = os.system(cmd)
        assert rc == 0

    for cmd in restructure_repos(REPO_ROOT):
        print(cmd)
        rc = execute_script(cmd)
        assert rc == 0

    MONOREPO = os.path.join(WORKDIR, "monorepo")
    os.system("rm -fr {}".format(MONOREPO))
    os.system("mkdir -p {}".format(MONOREPO))
    os.system("cd {monorepo} && git init".format(monorepo=MONOREPO))

    for cmd in integrate_repos(REPO_ROOT, MONOREPO):
        print(cmd)
        rc = execute_script(cmd)
        assert rc == 0

if __name__ == "__main__":
    main()
