import datetime
import os
import subprocess

repo = "PaulShannon/TestRepo"
author = "PythonCronScript <>"
message = "Auto Updating"

def run(commands):
    for c in commands:
        r = subprocess.call(c)
        print r, c
        if r != 0:
            exit()

directory = os.path.dirname(os.path.realpath(__file__))
repo_url = 'git@github.com:{}.git'.format(repo)
repo_path = os.path.join(directory, repo.split('/')[1])
filename = os.path.join(repo_path, 'README.md')

if os.path.isdir(repo_path):
    os.chdir(repo_path)
    run(["git pull -Xtheirs",])
else:
    run(["git clone {} {}".format(repo_url, repo_path),])
    os.chdir(repo_path)

with open(filename, 'a') as f:
    f.write('\n- Updating @ ({})'.format(datetime.datetime.now().strftime('%c')))

run([
    "git add {}".format(filename),
    "git commit --author=\"{}\" -m \"{}\"".format(author, message),
    "git push origin main",
    ])