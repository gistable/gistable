#!/usr/bin/python

import sys
import argparse

def main():
    for line in sys.stdin:
        line = line.strip()
        output = breduct(line)
        print output

def breduct(line,start=0):
    rets = []
    i=len(line)
    while True:
        occ = line.find("\\",start)
        #### Cannot find lambda anymore
        if occ == -1:
            break

        #### Finding lambda boundary to the corresponding function
        dot = line.find(".",occ)
        if dot == -1:
            print >> sys.stderr, "Cannot find matching function with previous lambda"
            sys.exit(1)

        #### Var is the lambda "\x1\x2\x3"
        lmbd = line[occ:dot].split("\\")

        #### Scanning all the function body 
        function = line.find("(",dot+1)     # character after (
        i = function+1                         # counter in first chracter in (
        depth = 1                           # we are now in one level of (
        while i < len(line) and depth != 0:
            if line[i] == '(':
                depth += 1
            elif line[i] == ')':
                depth -= 1
            i += 1

        if depth != 0:
            print >> sys.stderr, "Unbalance parentheses: ", line
            sys.exit(1)


        #### Go Depth to the child first!
        inner = breduct(line[dot+1:i])

        if i != len(line):
            var_next = i+1
            var_next_bound = line.find(")",i+1)
            i = var_next_bound + 1
            var = line[var_next:var_next_bound].split(",")
            
            #### Reduction phase
            for ii, lmbd_x in enumerate(lmbd):
                now = 0
                temp = ""
                if ii != 0:
                    find, target = lmbd_x, var[-ii] # beta reduction, the first lambda with the outmost variable
                    while True:
                        next_find = inner.find(find,now)
                        if next_find == -1:
                            break
                        temp += inner[now:next_find]
                        temp += target
                        now = next_find + len(find)
                    temp += inner[now:]
                    inner = temp
            start = var_next_bound + 2
            rets.append(inner)
        else:
            # Case of lambda without variable
            start = len(line)
            rets += [inner]
    return line[0:line.find("\\")] +','.join(rets) + line[i:] if rets != [] else line

if __name__ == '__main__':
    main()
