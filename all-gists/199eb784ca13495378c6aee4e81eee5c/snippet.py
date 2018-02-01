#!/usr/bin/env python3
# W.J. van der Laan 2016
# Compute, at each instruction, the value of the stack pointer
# relative to the return address.
import sys
import json
import re

instructions = json.load(sys.stdin, strict=False)
debug = True

inst_by_addr = {}
for i,inst in enumerate(instructions):
    inst_by_addr[inst['addr']] = i

# - Propagate esp information over function, start at 0
# - Sort instructions in basic blocks
# - Compute esp at begin and end of each basic block
#   at (conditional) jumps -> esp at target must match esp at source

ptr = 0
heads = [(ptr,0)]

while heads:
    (ptr,esp) = heads.pop()
    if debug:
        di = instructions[ptr]
        print('%08x %08x %4i %s' % ((di['addr'],esp,inst.get('stackptr', 0),di['opcode'])), file=sys.stderr)
    while True: # advance forward
        inst = instructions[ptr]
        if debug:
            print('  %08x %08x %4i %s' % ((inst['addr'],esp,inst.get('stackptr', 0),inst['opcode'])), file=sys.stderr)
        if 'esp' in inst:
            if inst['esp'] != esp:
                print('Mismatch at 0x%08x! 0x%08x versus 0x%08x' % (inst['addr'], inst['esp'], esp), file=sys.stderr)
                exit(1)
            else:
                break # stop linear progress here, we have a match
        inst['esp'] = esp
        delta = 0
        if inst.get('stack', None) in {'inc','reset'}: # only inc and reset affect stack pointer
            delta = inst.get('stackptr')
        esp = esp + delta
        # watch for ends of basic blocks
        if inst['type'] == 'ret':
            if inst['esp'] != 0:
                print('WARNING: esp is not 0 at return point %08x' % (inst['addr']), file=sys.stderr)
            break # full stop
        elif inst['type'] in {'jmp','cjmp'}: # jumps
            if inst['type'] == 'cjmp': # conditional jumps can continue to next inst too
                heads.append((ptr+1,esp))
            heads.append((inst_by_addr[inst['jump']],esp))
            break # stop linear progress here
        else:
            ptr += 1

espexp = re.compile('\[esp(?: *([+\-]) *([x0-9a-fA-F]+))?\]')
maxofs = 0
for inst in instructions:
    if 'esp' in inst:
        # - Generate comments for all instuctions that either
        #   do an indirect load from esp+XXXX or compute relative
        #   addresses.
        #   [esp + XXX] [esp - XXX] and compute to ra-relative
        m = espexp.search(inst['opcode'])
        if m: # we could better than match the text, but meh
            if m.group(1) is None:
                ofs = 0
            else:
                ofs = int(m.group(2).strip(), 0)
                if m.group(1) == '-':
                    ofs = -ofs

            ofs = -inst['esp'] + ofs
            if ofs < 0: # relative to return address
                comment = '[ra - 0x%x]' % (-ofs)
            else:
                comment = '[ra + 0x%x]' % (ofs)
                if (ofs&3)==0:
                    comment += ' arg%i' % (ofs//4)
            #print('0x%08x 0x%08x %s # %s' % (inst['addr'], inst['esp'], inst['opcode'], comment))
            maxofs = max(ofs,maxofs)
            print('CCu %s @ 0x%08x' % (comment, inst['addr']))
        #print(inst)

lastaddr = None
for inst in instructions:
    if 'esp' in inst:
        lastaddr = inst['addr']

print('Max offset 0x%x (=%d args)' % (maxofs, maxofs//4), file=sys.stderr)
print('Last visited address is 0x%08x' % (lastaddr), file=sys.stderr)

