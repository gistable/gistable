#!/usr/bin/env python
import sys
import subprocess
import re
import os.path

def main():
    if len(sys.argv) < 2:
        print('Missing argument')
        sys.exit(-1)

    exe = sys.argv[1]
    
    if not os.path.isfile(exe):
        print('Not a file, sir.')
        exit(-2)

    o = subprocess.check_output(['objdump', '-M', 'intel', '-d', exe])
    r = subprocess.check_output(['readelf', '-a', exe])
    s = subprocess.check_output(['strings', '-t', 'x', exe])

    # match addresses in strings output
    regex = re.compile('^[ ]+(?P<addr>[0-9a-f]+) (.*)$')

    strings = {}
    for line in str(s).split('\n'):
        match = regex.search(line)
        if not match:
            continue

        (addr, string) = match.groups()
        strings[int(addr, 16)+0x8048000] = string
    
    # match output from readelf
    regex = re.compile('^[ ]+(?P<num>[0-9]+): (?P<addr>[0-9a-f]+)[ ]+(?P<size>[0-9]+)[ ]+OBJECT[ ]+(?P<bind>GLOBAL|WEAK|LOCAL)[ ]+(?P<vis>DEFAULT|HIDDEN)[ ]+(?P<ndx>[0-9]+|ABS|UND)[ ]+(?P<name>.+)$')
    variables = {}
    for line in str(r).split('\n'):
        match = regex.search(line)
        if not match:
            continue

        g = match.groupdict()

        variables[int(match.group('addr'), 16)] = match.groupdict()

    # Match addresses and strings
    def stringrepl(matchobj):
        # if matchobj is None:
        #     return None
        saddr = matchobj.groups()[1]
        addr = int(saddr, 16)
        if addr in strings:
            return '%s ;; "%s"' % (matchobj.groups()[0], strings[addr])

        return matchobj.groups()[0]

    # Match addresses and variables
    def varrepl(matchobj):
        # if matchobj is None:
        #     return None
        saddr = matchobj.groups()[1]
        addr = int(saddr, 16)
        if addr in variables:
            var = variables[addr]
            return '%s ;; var %s (%s, size %i)' % (matchobj.group('match'), var['name'], var['bind'].lower(), int(var['size']))

        return matchobj.groups()[0]

    replaced = re.sub(r'(.*?(0x[0-9a-f]{7,}).*)', stringrepl, str(o))
    replaced = re.sub(r'(?P<match>.*?(0x[0-9a-f]{7,}).*)', varrepl, replaced)

    print(replaced)

if __name__ == '__main__':
    main()
