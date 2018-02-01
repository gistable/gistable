#!/usr/bin/python
## gitsh (pronounced like "glitch"), an interactive wrapper for git.
##
## gitsh parses the output of "git status" and numbers the files for
## you, for easy operations on multiple files.
##
## $ gitsh status
##  1) M foo/bar.py
##  2) M foo/baz.py
##  3) A blah.sh
##   ...
## 30) ? yadda.py
##
## gitsh> checkout 2-10 add 25,26,29 rm 7
##
## Commands are in the pattern CMD RANGE [CMD RANGE [CMD RANGE ...]]
## where CMD is a git file command like add, checkout, rm, etc.
## RANGE can be a single file number, a comma-separated list of
## file numbers, or a dashed interval. "2-5" means "2,3,4,5"
##
## Arguments to commands are not yet supported. So "blame -L2,4"
## will not do what you think.
##
## It also does not do well if you switch branches.
##
##  BSD licence.  carlos@bueno.org   12 Aug 2009

import sys, subprocess, re, cmd, string

class opener(cmd.Cmd):
    prompt = 'gitsh> '
    files = []

    def setBranch(self, b):
        self.prompt = 'gitsh (%s)> ' % b
        return self

    # "4-6"         -> (4,5,6)
    # "10"          -> (10,)
    # "34,56,90"    -> (34, 56, 90)
    # "2,4,7-10,13" -> (2, 4, 7, 8, 9, 10, 13)
    def parseRange(self, token):
       cur = ''
       tokens = []
       for c in token:
          if c in string.digits:
             cur += c
          else:
             tokens.append(int(cur))
             cur = ''
             if c == '-':
                tokens.append(c)
       tokens.append(int(cur))
       ret = []
       inrange = False
       lo = 0
       for t in tokens:
          if t != '-':
             if inrange:
                ret += range(lo+1, t+1)
                inrange = False
             else:
                ret.append(t)
             lo = t
          else:
             inrange = True
       return tuple(set(ret))

    def do_EOF(self, line):
        print "Mein leben!\n\n"
        sys.exit(0)

    def do_status(self, line):
        cmd = ['git', 'status', '--short', '--branch']
        process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE)
        results = process.communicate()[0].split('\n')
        self.setBranch(results[0][3:])
        self.files = [None]
        rem = re.compile(r'^(..)\s+(.+)$')
        for i, r in enumerate(results[1:]):
            m = rem.match(r)
            if m:
                status, fname = m.groups()
                self.files.append(fname)
                print "% 3d)  % 2s  %s\x1b[0m" % (i+1, status, fname.strip())


    ## This is supposed to be a command pre-parser, but we do all the
    ## heavy lifting here. The return '' means no command.
    def precmd(self, line):
        if line.strip() == 'status':
            return 'status'
        tokens = re.split(r'\s+', line.strip())
        commands = zip(*(iter(tokens),) * 2) # Python, you so crazy...
        for cmd, range_token in commands:
            flist = [self.files[i] for i in self.parseRange(range_token)]
            print '    ## '+' '.join(['git', cmd] + flist)
            proc = subprocess.Popen(['git', cmd] + flist)
        print ''
        return ''

try:
    print ''
    o = opener()
    o.do_status('status')
    o.cmdloop()
except:
    # raise
    print "Mein leiben!"
