#!/usr/bin/env python
#
# Simple utility to disassemble a raw bytecode file using Capstone.
#
# -jduck
#

import argparse
import capstone
import struct

def arm_mode(string):
    if string == "arm":
        return capstone.CS_MODE_ARM
    elif string == "thumb":
        return capstone.CS_MODE_THUMB
    msg = "%r is not a valid ARM execution mode" % string
    raise argparse.ArgumentTypeError(msg)
    return None

def hexbytes(insn):
    b = buffer(insn.bytes)
    if len(insn.bytes) == 4:
        return "0x%08x" % (struct.unpack_from('I', b))
    elif len(insn.bytes) == 2:
        return "0x%04x" % (struct.unpack_from('H', b))
    raise 'Unknown instruction lenght?!'

if __name__ == "__main__":
    p = argparse.ArgumentParser(description='ARM disassembler tool')
    #p.add_argument('-a', '--arch', default='x86', type=arch
    p.add_argument('-m', '--mode', default='arm', type=arm_mode, help='ARM execution mode')
    p.add_argument('-f', '--file', default=None, help='File to read opcodes from')
    args = p.parse_args()

    code = None
    with open(args.file, 'rb') as f:
        code = f.read()

    md = capstone.Cs(capstone.CS_ARCH_ARM, args.mode)
    for insn in md.disasm(code, 0x0):
        print "0x%08x: %-10s %s %s" % (insn.address, hexbytes(insn), insn.mnemonic, insn.op_str)
