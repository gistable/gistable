#!/usr/bin/python3

# Estimates time spent on a project from commit timestamps
#
# If two commits are less than INERTIA time apart, the time
# between them is considered spent, otherwise SINGLE_COMMIT
# time is taken.

import os

SINGLE_COMMIT=1800 # 30 min
INERTIA=7200 # 2 h

log = os.popen("git log --pretty='format:%ae;%at'")
lines = [line.strip().split(';') for line in log]

commits = dict()
last_commits = dict()
cum_time = dict()


for line in sorted(lines):
    name, time = line
    time = int(time)
    
    if name not in last_commits:
        last_commits[name] = None
        cum_time[name] = 0
        commits[name] = 0
    
    if last_commits[name] != None and time - last_commits[name] <= INERTIA:
        cum_time[name] += time - last_commits[name]
    else:
        cum_time[name] += SINGLE_COMMIT
    
    commits[name] += 1 
    last_commits[name] = time

for name, time in cum_time.items():
    print("{}\t{:.1f}\t{}\t{:.0f}".format(name, time/3600, commits[name], time/commits[name]/60))

