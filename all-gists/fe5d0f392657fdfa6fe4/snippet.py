#!/usr/bin/env python
#
# PoC: Manage a git repository in ~/.task that gets updated on changes.
#      Only pending.data and completed.data are included by default.
#      You can use "git add" to add whatever files you want to track in your
#      task folder.
#
# Inspired by https://gist.github.com/Unode/9366218
#
# Works with any Taskwarrior version that supports hooks.
# Needs Taskwarrior 2.4.3 in order to show fancy commit messages.
#
# NOTE: Little to no error handling. This is a PoC, remember?

import os
import subprocess
import sys

TASK_DIR = os.path.dirname(__file__) + os.sep + os.pardir

c = {}
if len(sys.argv) > 1:
  c = {k:v for k, v in (s.split(":", 1) for s in sys.argv[1:])}

if 'args' not in c:
  c['args'] = "Taskwarrior version too old, no info available."

os.chdir(TASK_DIR)

if not os.path.isdir(TASK_DIR + os.sep + ".git"):
  subprocess.call("git init".split())
  with open(".gitignore", "w") as f:
    f.write("*\n")
  subprocess.call("git add -f .gitignore pending.data completed.data".split())
  subprocess.call(["git", "commit", "-mInitial log"])

if subprocess.call("git diff --exit-code --quiet".split()) != 0:
  subprocess.call("git commit -a".split() + ["-m" + c['args']])
