#!/usr/bin/python
# strace an existing process tree. `strace -f` only follows newly spawned
# processes which is not always what you want.
import os
import sys
import subprocess

# /proc/[pid]/task/*  == directory of threads including self
# /proc/[pid]/task/[pid]/children == child processes

def get_process_tree(root_pid, include_threads=True):
    found = []
    queue = [root_pid]
    while queue:
        pid = queue.pop()
        found.append(pid)
        with open('/proc/%s/task/%s/children' % (pid, pid), 'r') as f:
            children = f.read().split()
            queue.extend(children)
        if include_threads:
            threads = os.listdir('/proc/%s/task' % pid)
            threads.remove(pid)
            # Threads don't have children in /proc so don't explore further
            found.extend(threads)

    return found


def strace(pids):
    args = ['strace']
    for pid in pids:
        args.extend(['-p', pid])
    args.extend(sys.argv[2:])
    print args
    subprocess.call(args)


def main():
    if len(sys.argv) < 2:
        print("Usage: stracetree <pid> <strace flags>")
        sys.exit(1)
    pids = get_process_tree(sys.argv[1], include_threads=True)
    strace(pids)


if __name__ == '__main__':
    main()
