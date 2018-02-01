"""This tool queries undefined symbols in a lib, then queries defined
symbols, and then diffs the two sets so we know what the actual
externals for the purpose of the lib are."""
import os
import re
import subprocess

libname = 'libbink2.a' # command line parsing? please.

def parse_def_sym(str):
    """Parses defined symbols from str."""
    curlib = None
    sym_regexp = re.compile('([0-9a-fA-F]+) (.) (\S+)')
    syms = {}
    for line in str.split('\n'):
        match = sym_regexp.match(line)
        if line[-1:] == ':':
            curlib = line[:-1]
        elif match:
            syms[match.group(3)] = curlib
    return syms

def parse_undef_sym(str):
    """Parses undefined symbols from str."""
    curlib = None
    syms = {}
    for line in str.split('\n'):
        if line[-1:] == ':':
            curlib = line[:-1]
        elif line != '':
            syms[line] = curlib
    return syms

undef_sym_output = subprocess.check_output(['nm', '-u', libname])
def_sym_output = subprocess.check_output(['nm', '-Ug', libname])

def_syms = parse_def_sym(def_sym_output)
undef_syms = parse_undef_sym(undef_sym_output)

# Figure out the symbols that are *really* undefined
undef_list = []
for usym, ufile in undef_syms.iteritems():
    if not usym in def_syms:
        undef_list.append('undef sym %s in %s' % (usym, ufile))

undef_list.sort()

print('\n'.join(undef_list))