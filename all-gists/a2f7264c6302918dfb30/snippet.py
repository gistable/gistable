#!/usr/bin/env python
#
# Adds the ability to add / modify tasks using a "blocks:" attribute,
# the opposite of "depends:".
#
# This script acts as an on-modify, on-add and on-launch hook at the same time.
#
### SETUP
# Save this file as
#   ~/.task/hooks/on-modify.blocks_attr.py
# change to that directory:
#   $ cd ~/.task/hooks
# make the script executable:
#   $ chmod +x on-modify.blocks_attr.py
# then create symlinks to that file with the other hook names:
#   $ ln -s on-modify.blocks_attr.py on-add.blocks_attr.py
#   $ ln -s on-modify.blocks_attr.py on-launch.blocks_attr.py
#
# Now tell Taskwarrior about the "blocks" attribute:
#   $ task config uda.blocks.type string
#   $ task config uda.blocks.label Blocks
#
# And we're ready to go!
#
# bf@id:~$ t add a
# Created task 1.
#
# bf@id:~$ t add b
# Created task 2.
#
# bf@id:~$ t add c blocks:1
# Created task 3.
#
# bf@id:~$ t 2 mod blocks:1
# Modifying task 2 'b'.
# Modified 1 task.
#
# bf@id:~$ t
# [t next]
#
# ID Age Deps Description Urg 
#  2 18s      b              8
#  3 8s       c              8
#  1 29s 2 3  a             -5
#

import json
import os
import subprocess
import sys

# Adjust this if "task" is not regular Taskwarrior.
TASK = 'task'
# Adjust path if needed. It is a temporary file managed by the hook.
SHIMFILE = "%s/.task/hooks/blocks_shim.txt" % os.getenv('HOME')

def on_launch():
    try:
        with open(SHIMFILE, 'r') as f:
            shim = f.readlines()
    except IOError:
        sys.exit(0)
    while shim:
        line = shim.pop(0).rstrip()
        if not line:
            continue
        if subprocess.call(line.split()) != 0:
            # Error handling by escalating to the user :)
            print("%s ERROR: First line in %s is failing to run!" % (sys.argv[0], SHIMFILE))
            print("Feel free to delete the file, or edit its contents to resolve the problem.")
            shim = [line + '\n'] + shim
            break
    if shim:
        with open(SHIMFILE, 'w') as f:
            f.write(''.join(shim))
        sys.exit(1)
    else:
        os.remove(SHIMFILE)

def handle_blocks_attribute(new):
    if 'blocks' in new:
        with open(SHIMFILE, "a") as f:
            # This needs error handling. If a later hook aborts, the UUID is invalid.
            f.write("%s rc.hooks=off rc.confirmation=no rc.bulk=10000 rc.verbose=nothing %s mod dep:%s\n" % (TASK, new['blocks'], new['uuid']))
        del new['blocks']
    print(json.dumps(new))

old = sys.stdin.readline()
new = sys.stdin.readline()

if not old:
    on_launch()
elif not new:
    handle_blocks_attribute(json.loads(old))
else:
    handle_blocks_attribute(json.loads(new))
