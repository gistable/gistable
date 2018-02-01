#!/usr/bin/env python

"""
Automatically create split windows in vim like so:
vimsp.py col1row1 col2row1 / col1row2 col2row2
"""

def neighborhood(iterable):
    iterator = iter(iterable)
    prev = None
    item = iterator.next()  # throws StopIteration if empty.
    for next in iterator:
        yield (prev,item,next)
        prev = item
        item = next
    yield (prev,item,None)

HSPLIT,VSPLIT = 'split','vsplit'
def hsplit(file): return HSPLIT+' '+file
def vsplit(file): return VSPLIT+' '+file

import sys
files = sys.argv[1:]

numlines = files.count('/')
if numlines == 1 and files[0] == '/':
    # make all hsplits into vsplits
    oldfiles = files[1:]
    files = []
    for file in oldfiles:
        files.append(file)
        files.append('/')
    files = files[:-1] # remove the last /
    numlines = len(oldfiles)

args = ['vim'] #,'-c','set splitright']

# split top-down first
# each split goes up and opens that file there
for prev, file, next in neighborhood(files):
    if next and next=='/': # last file of a line
        args.extend(['-c','split %s' % file])

# then split left-right for each
# we're starting out in the top split
for prev, file, next in neighborhood(files):
    if file=='/': # move down
        args.extend(['-c','wincmd j'])
    elif next and next!='/': # don't touch the last file
        args.extend(['-c','vsplit %s' % file])

# move to the top
for i in range(numlines):
    args.extend(['-c','wincmd k'])

# add last to the end of the args
if files[-1]!='/':
    args.append(files[-1])

# filter out repeat and useless moves, just for clarity
import re
arg_match = re.compile('wincmd ([jk])')
dir_map = {'j':'k','k':'j'}
removes = []
for i, arg in enumerate(args):
    if i in removes: continue

    count = 1
    pos = 1
    m = arg_match.match(arg)
    if m:
        dir = m.groups()[0]
        other = dir_map[dir]
        while count and len(args)>i+count*2: # we have at least 2 more args left
            nm = arg_match.match(args[i+pos*2])
            if not nm: break
            if nm.groups()[0]==other:
                if count == 1:
                    removes.extend([i-1,i,i+1,i+2]) # remove the -c and the next arg too
                    break
                else:
                    count -= 1 # this arg just undoes the latest arg
                    pos += 1
            else:
                count += 1
                pos += 1
                # remove the next two, change this one
                removes.extend([i+1,i+2])
                newarg = re.sub(r'\d*wincmd','%dwincmd' % count,arg)
                args[i] = newarg

newargs = []
for i, arg in enumerate(args):
    if i not in removes:
        newargs.append(arg)

args = newargs


import subprocess
print args
subprocess.call(args)
