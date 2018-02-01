#!/usr/bin/env python

import struct
import sys

class Instruction:
    def __init__(self, name, *args):
        self.name = name
        self.operands = args

    def decode(self, b):
        return self.name + ' ' + ', '.join([o.decode(b) for o in self.operands])

class Operand(object):
    struct = struct.Struct('>i')
    def __init__(self, start, length):
        self.start = start
        self.length = length

    def decode(self, b):
        i, = Operand.struct.unpack(b'\0' + b)
        i >>= self.start
        i &= (1 << self.length) - 1
        return hex(i)

class Base(Operand):
    def __init__(self):
        super(Base, self).__init__(0, 24)

class Float(Operand):
    struct = struct.Struct('>f')
    def __init__(self):
        super(Float, self).__init__(0, 24)

    def decode(self, b):
        f, = Float.struct.unpack(b + b'\0')
        return str(f)

optable = {
    0x00: Instruction('NOP'),
    0x01: Instruction('VADDR', Base()),
    0x02: Instruction('VADDR', Base()),
    0x04: Instruction('PRIM', Operand(0, 16), Operand(16, 3)),
    0x05: Instruction('BEZIER', Operand(0, 8), Operand(8, 8)),
    0x06: Instruction('SPLINE', Operand(0, 8), Operand(8, 8), Operand(16, 2), Operand(18, 2)),
    0x07: Instruction('BBOX', Operand(0, 16)),
    0x08: Instruction('JUMP', Base()),
    0x09: Instruction('BJUMP', Base()),
    0x0A: Instruction('CALL', Base()),
    0x0B: Instruction('RET'),
    0x0C: Instruction('END'),
    0x0E: Instruction('SIGNAL', Operand(0, 16), Operand(16, 8)),
    0x0F: Instruction('FINISH', Operand(0, 16)),
    0x10: Instruction('BASE', Operand(16, 4)),
    0x12: Instruction('VTYPE', Operand(0, 2), Operand(2, 3), Operand(5, 2), Operand(7, 2), Operand(9, 2), Operand(11, 2), Operand(14, 3), Operand(18, 3), Operand(23, 1)),
    0x13: Instruction('13', Base()),
    0x14: Instruction('14', Base()),
    0x15: Instruction('REGION1', Operand(0, 10), Operand(10, 10)),
    0x16: Instruction('REGION2', Operand(0, 10), Operand(10, 10)),
    0x17: Instruction('LTE', Operand(0, 1)),
    0x18: Instruction('LTE0', Operand(0, 1)),
    0x19: Instruction('LTE1', Operand(0, 1)),
    0x1A: Instruction('LTE2', Operand(0, 1)),
    0x1B: Instruction('LTE3', Operand(0, 1)),
    0x1C: Instruction('CPE', Operand(0, 1)),
    0x1D: Instruction('BME', Operand(0, 1)),
    0x1E: Instruction('TME', Operand(0, 1)),
    0x1F: Instruction('FGE', Operand(0, 1)),
    0x20: Instruction('DTE', Operand(0, 1)),
    0x21: Instruction('ABE', Operand(0, 1)),
    0x22: Instruction('ATE', Operand(0, 1)),
    0x23: Instruction('ZTE', Operand(0, 1)),
    0x24: Instruction('STE', Operand(0, 1)),
    0x25: Instruction('AAE', Operand(0, 1)),
    0x26: Instruction('PCE', Operand(0, 1)),
    0x27: Instruction('CTE', Operand(0, 1)),
    0x28: Instruction('LOE', Operand(0, 1)),
    0x2A: Instruction('BOFS', Operand(0, 24)),
    0x2B: Instruction('BONE', Float()),
    0x2C: Instruction('MW0', Float()),
    0x2D: Instruction('MW1', Float()),
    0x2E: Instruction('MW2', Float()),
    0x2F: Instruction('MW3', Float()),
    0x30: Instruction('MW4', Float()),
    0x31: Instruction('MW5', Float()),
    0x32: Instruction('MW6', Float()),
    0x33: Instruction('MW7', Float()),
    0x36: Instruction('PSUB', Operand(0, 8), Operand(8, 8)),
    0x37: Instruction('PPRIM', Operand(0, 2)),
    0x38: Instruction('PFACE', Operand(0, 1)),
    0x3A: Instruction('WMS'),
    0x3B: Instruction('WORLD', Float()),
    0x3C: Instruction('VMS'),
    0x3D: Instruction('VIEW', Float()),
    0x3E: Instruction('PMS'),
    0x3F: Instruction('PROJ', Float()),
    0x40: Instruction('TMS'),
    0x41: Instruction('TMATRIX', Float()),
    0x42: Instruction('XSCALE', Float()),
    0x43: Instruction('YSCALE', Float()),
    0x44: Instruction('ZSCALE', Float()),
    0x45: Instruction('XPOS', Float()),
    0x46: Instruction('YPOS', Float()),
    0x47: Instruction('ZPOS', Float()),
    0x48: Instruction('USCALE', Float()),
    0x49: Instruction('VSCALE', Float()),
    0x4A: Instruction('OFFSETU', Float()),
    0x4B: Instruction('OFFSETV', Float()),
    0x4C: Instruction('OFFSETX', Operand(0, 24)),
    0x4D: Instruction('OFFSETY', Operand(0, 24)),
    0x50: Instruction('SHADE', Operand(0, 1)),
    0x51: Instruction('RNORM', Operand(0, 1)),
    0x53: Instruction('CMAT', Operand(0, 3)),
    0x54: Instruction('EMC', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x55: Instruction('AMC', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x56: Instruction('DMC', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x57: Instruction('SMC', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x58: Instruction('AMA', Operand(0, 8)),
    0x5B: Instruction('SPOW', Float()),
    0x5C: Instruction('ALC', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x5D: Instruction('ALA', Operand(0, 8)),
    0x5E: Instruction('LMODE', Operand(0, 1)),
    0x5F: Instruction('LT0', Operand(0, 2), Operand(8, 2)),
    0x60: Instruction('LT1', Operand(0, 2), Operand(8, 2)),
    0x61: Instruction('LT2', Operand(0, 2), Operand(8, 2)),
    0x62: Instruction('LT3', Operand(0, 2), Operand(8, 2)),
    0x63: Instruction('LXP0', Float()),
    0x64: Instruction('LYP0', Float()),
    0x65: Instruction('LZP0', Float()),
    0x66: Instruction('LXP1', Float()),
    0x67: Instruction('LYP1', Float()),
    0x68: Instruction('LZP1', Float()),
    0x69: Instruction('LXP2', Float()),
    0x6A: Instruction('LYP2', Float()),
    0x6B: Instruction('LZP2', Float()),
    0x6C: Instruction('LXP3', Float()),
    0x6D: Instruction('LYP3', Float()),
    0x6E: Instruction('LZP3', Float()),
    0x6F: Instruction('LXD0', Float()),
    0x70: Instruction('LYD0', Float()),
    0x71: Instruction('LZD0', Float()),
    0x72: Instruction('LXD1', Float()),
    0x73: Instruction('LYD1', Float()),
    0x74: Instruction('LZD1', Float()),
    0x75: Instruction('LXD2', Float()),
    0x76: Instruction('LYD2', Float()),
    0x77: Instruction('LZD2', Float()),
    0x78: Instruction('LXD3', Float()),
    0x79: Instruction('LYD3', Float()),
    0x7A: Instruction('LZD3', Float()),
    0x7B: Instruction('LCA0', Float()),
    0x7C: Instruction('LLA0', Float()),
    0x7D: Instruction('LQA0', Float()),
    0x7B: Instruction('LCA1', Float()),
    0x7F: Instruction('LLA1', Float()),
    0x80: Instruction('LQA1', Float()),
    0x81: Instruction('LCA2', Float()),
    0x82: Instruction('LLA2', Float()),
    0x83: Instruction('LQA2', Float()),
    0x84: Instruction('LCA3', Float()),
    0x85: Instruction('LLA3', Float()),
    0x86: Instruction('LQA3', Float()),
    0x87: Instruction('87', Operand(0, 24)),
    0x88: Instruction('88', Operand(0, 24)),
    0x89: Instruction('89', Operand(0, 24)),
    0x8A: Instruction('8A', Operand(0, 24)),
    0x8B: Instruction('8B', Operand(0, 24)),
    0x8C: Instruction('8C', Operand(0, 24)),
    0x8D: Instruction('8D', Operand(0, 24)),
    0x8E: Instruction('8E', Operand(0, 24)),
    0x8F: Instruction('ALC0', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x90: Instruction('DLC0', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x91: Instruction('SLC0', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x92: Instruction('ALC1', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x93: Instruction('DLC1', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x94: Instruction('SLC1', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x95: Instruction('ALC2', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x96: Instruction('DLC2', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x97: Instruction('SLC2', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x98: Instruction('ALC3', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x99: Instruction('DLC3', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x9A: Instruction('SLC3', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0x9B: Instruction('FFACE', Operand(0, 1)),
    0x9C: Instruction('FBP', Operand(0, 24)),
    0x9D: Instruction('FBW', Operand(0, 16), Operand(16, 8)),
    0x9E: Instruction('ZBP', Operand(0, 24)),
    0x9F: Instruction('ZBW', Operand(0, 16), Operand(16, 8)),
    0xA0: Instruction('TBP0', Operand(0, 24)),
    0xA1: Instruction('TBP1', Operand(0, 24)),
    0xA2: Instruction('TBP2', Operand(0, 24)),
    0xA3: Instruction('TBP3', Operand(0, 24)),
    0xA4: Instruction('TBP4', Operand(0, 24)),
    0xA5: Instruction('TBP5', Operand(0, 24)),
    0xA6: Instruction('TBP6', Operand(0, 24)),
    0xA7: Instruction('TBP7', Operand(0, 24)),
    0xA8: Instruction('TBW0', Operand(0, 16), Operand(16, 4)),
    0xA9: Instruction('TBW1', Operand(0, 16), Operand(16, 4)),
    0xAA: Instruction('TBW2', Operand(0, 16), Operand(16, 4)),
    0xAB: Instruction('TBW3', Operand(0, 16), Operand(16, 4)),
    0xAC: Instruction('TBW4', Operand(0, 16), Operand(16, 4)),
    0xAD: Instruction('TBW5', Operand(0, 16), Operand(16, 4)),
    0xAE: Instruction('TBW6', Operand(0, 16), Operand(16, 4)),
    0xAF: Instruction('TBW7', Operand(0, 16), Operand(16, 4)),
    0xB0: Instruction('CBP', Operand(0, 24)),
    0xB1: Instruction('CBPH', Operand(16, 4)),
    0xB2: Instruction('TRXSBP', Operand(0, 24)),
    0xB3: Instruction('TRXSBW', Operand(0, 16), Operand(16, 8)),
    0xB4: Instruction('TRXDBP', Operand(0, 24)),
    0xB5: Instruction('TRXDBW', Operand(0, 16), Operand(16, 8)),
    0xB8: Instruction('TSIZE0', Operand(0, 8), Operand(8, 16)),
    0xB9: Instruction('TSIZE1', Operand(0, 8), Operand(8, 16)),
    0xBA: Instruction('TSIZE2', Operand(0, 8), Operand(8, 16)),
    0xBB: Instruction('TSIZE3', Operand(0, 8), Operand(8, 16)),
    0xBC: Instruction('TSIZE4', Operand(0, 8), Operand(8, 16)),
    0xBD: Instruction('TSIZE5', Operand(0, 8), Operand(8, 16)),
    0xBE: Instruction('TSIZE6', Operand(0, 8), Operand(8, 16)),
    0xBF: Instruction('TSIZE7', Operand(0, 8), Operand(8, 16)),
    0xC0: Instruction('TMAP', Operand(0, 2), Operand(8, 2)),
    0xC1: Instruction('C1', Operand(0, 2), Operand(8, 2)),
    0xC2: Instruction('TMODE', Operand(0, 1), Operand(8, 8), Operand(16, 4)),
    0xC3: Instruction('TPSM', Operand(0, 24)),
    0xC4: Instruction('CLOAD', Operand(0, 24)),
    0xC5: Instruction('CMODE', Operand(0, 2), Operand(2, 6), Operand(8, 8), Operand(16, 8)),
    0xC6: Instruction('TFLT', Operand(0, 3), Operand(8, 3)),
    0xC7: Instruction('TWRAP', Operand(0, 1), Operand(8, 1)),
    0xC8: Instruction('TBIAS', Operand(0, 16), Operand(16, 8)),
    0xC9: Instruction('TFUNC', Operand(0, 3), Operand(8, 1), Operand(16, 1)),
    0xCA: Instruction('TEC', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0xCB: Instruction('TFLUSH'),
    0xCC: Instruction('TSYNC'),
    0xCD: Instruction('FFAR'),
    0xCE: Instruction('TDIST', Float()),
    0xCF: Instruction('FCOL', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0xD0: Instruction('TSLOPE', Float()),
    0xD2: Instruction('PSM', Operand(0, 2)),
    0xD3: Instruction('CLEAR', Operand(0, 1), Operand(8, 3)),
    0xD4: Instruction('SCISSOR1', Operand(0, 10), Operand(10, 10)),
    0xD5: Instruction('SCISSOR2', Operand(0, 10), Operand(10, 10)),
    0xD6: Instruction('NEARZ', Operand(0, 16)),
    0xD7: Instruction('FARZ', Operand(0, 16)),
    0xD8: Instruction('CTST', Operand(0, 2)),
    0xD9: Instruction('CREF', Operand(0, 24)),
    0xDA: Instruction('CMSK', Operand(0, 24)),
    0xDB: Instruction('ATST', Operand(0, 3), Operand(8, 8), Operand(16, 8)),
    0xDC: Instruction('STST', Operand(0, 3), Operand(8, 8), Operand(16, 8)),
    0xDD: Instruction('SOP', Operand(0, 3), Operand(8, 4), Operand(16, 3)),
    0xDE: Instruction('ZTST', Operand(0, 3)),
    0xDF: Instruction('ALPHA', Operand(0, 3), Operand(4, 4), Operand(8, 4)),
    0xE0: Instruction('SFIX', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0xE1: Instruction('DFIX', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0xE2: Instruction('DTH0', Operand(0, 4), Operand(4, 4), Operand(8, 4), Operand(12, 4)),
    0xE3: Instruction('DTH1', Operand(0, 4), Operand(4, 4), Operand(8, 4), Operand(12, 4)),
    0xE4: Instruction('DTH2', Operand(0, 4), Operand(4, 4), Operand(8, 4), Operand(12, 4)),
    0xE5: Instruction('DTH3', Operand(0, 4), Operand(4, 4), Operand(8, 4), Operand(12, 4)),
    0xE6: Instruction('LOP', Operand(0, 4)),
    0xE7: Instruction('ZMSK', Operand(0, 16)),
    0xE8: Instruction('PMSKC', Operand(0, 8), Operand(8, 8), Operand(16, 8)),
    0xE9: Instruction('PMSKA', Operand(0, 8)),
    0xEA: Instruction('TRXKICK', Operand(0, 1)),
    0xEB: Instruction('TRXSPOS', Operand(0, 10), Operand(10, 10)),
    0xEC: Instruction('TRXDPOS', Operand(0, 10), Operand(10, 10)),
    0xEE: Instruction('TRXSIZE', Operand(0, 10), Operand(10, 10)),
}

undefOp = Instruction('UNDEF')

def disasm(instruction):
    opcode = instruction[0]
    if isinstance(opcode, str):
        opcode = ord(opcode)
    op = optable.get(opcode, undefOp)
    return op.decode(instruction[1:4])

if __name__ == '__main__':
    if sys.version_info >= (3,1):
        sys.stdin = sys.stdin.detach()
    f = open(sys.argv[1], 'rb')
    while True:
        cache = f.read(32)
        if len(cache) < 4:
            break
        while len(cache) >= 4:
            print(disasm(cache[3::-1])) # Reverse the endianness
            cache = cache[4:]
