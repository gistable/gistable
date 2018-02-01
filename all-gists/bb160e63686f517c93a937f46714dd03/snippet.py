''' 
ROP Analyze
Written by St4rk

The code is a total mess and I don't know python (it's one of many reasons 
that I decided to use python here, to learn)
Feel free to modify and do whatever you want
'''

# imports
import struct
from capstone import *
from capstone.arm import *


# init capstone arm mode
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True

# rop (with address base)
rop = open('x_rop', 'rb')
# rop (without address base)
rop_w = open('xd',  'rb')

# modules
SceWebKit = open('SceWebKit.bin', 'rb')
SceLibKernel = open('SceLibKernel.bin', 'rb')
SceLibC = open('SceLibC.bin', 'rb')
SceLibHttp = open('SceLibHttp.bin', 'rb')
SceNet = open('SceNet.bin', 'rb')

# address base
stack_base = 0x50000000
SceWebKit_addr = 0x83a00780
SceLibKernel_addr = 0xe0004d40
SceLibC_addr = 0x83980a10
SceLibHttp_addr = 0xe0604c80
SceNet_addr = 0xe05236d0
# Need to dump yet, dummy value
SceAppMgr = 0x6000000

# total of gadget that it will dump
ROP_DUMP_SIZE = 0x3800

# reg list used to know what is the Library that it will jump
reg_list = {'r0': 0, 'r1': 0, 'r2': 0, 'r3': 0, 'r4': 0, 'r5': 0, \
            'r6': 0, 'r7': 0, 'r8': 0, 'r9': 0, 'r10': 0, 'r11': 0}


def rop_diss(code, addr): 
    POP_GADGET = True
    
    for i in md.disasm(code, addr):
        # function ptr
        if i.id in (ARM_INS_BL, ARM_INS_BLX):
            print "0x%X:\t%s\t%s" % (i.address, i.mnemonic, i.op_str)
            print "\t\taddr: 0x%X"  % (reg_list[i.reg_name(i.operands[0].value.reg)])
            break

        # POP gadget to fill registers values
        elif i.id in (ARM_INS_POP, ARM_INS_VPOP):
            print "0x%X:\t%s\t%s" %(i.address, i.mnemonic, i.op_str)
            # TODO implement gadget list: op.value.reg
            for n in i.operands:
                if (i.reg_name(n.value.reg) != "pc"):
                    reg_value = struct.unpack('I', rop.read(4))[0]
                    
                    # dump stack
                    if (reg_value <= 0x60000000 and reg_value >= 0x50000000):
                        stack_value = reg_value - stack_base
                        current_pos = rop.tell()
                        rop.seek(stack_value)
                        stack_value = struct.unpack('I', rop.read(4))[0]
                        rop.seek(current_pos)
                        print "\t\t%s : 0x%X - stack: 0x%X" % (i.reg_name(n.value.reg), \
                        reg_value, stack_value)
                    else:
                        print "\t\t%s : 0x%X" % (i.reg_name(n.value.reg), \
                        reg_value)

                    reg_list[i.reg_name(n.value.reg)] = reg_value


                    # just to increment the dummy x
                    rop_w.read(4)
            break
        else:
            print "0x%X:\t%s\t%s" % (i.address, i.mnemonic, i.op_str)

def main():

    
    for i in range(0, ROP_DUMP_SIZE):
        # verify what is the base
        gadget = struct.unpack('I', rop.read(4))[0]
        gadget_w = struct.unpack('I', rop_w.read(4))[0]

        print "x offset: 0x%X" % rop.tell()

        # check if is a shared module
        if (gadget > 0xE0000000):
            # check what is the shared module that we will use

            # SceLibKernel
            if (gadget - SceLibKernel_addr == gadget_w):
                print "SceLibKernel"
                offset = gadget_w - 1
                SceLibKernel.seek(offset)
                code = SceLibKernel.read(32)
                rop_diss(code, gadget)

            # SceLibHttp
            elif (gadget - SceLibHttp_addr == gadget_w):
                print "SceLibHttp"
                offset = gadget_w - 1
                SceLibHttp.seek(offset)
                code = SceLibHttp.read(32)
                rop_diss(code, gadget)

            # SceNet
            elif (gadget - SceNet_addr == gadget_w):
                print "SceNet"
                offset = gadget_w - 1
                SceNet.seek(offset)
                code = SceNet.read(32)
                rop_diss(code, gadget)

            # SceAppMgr
            elif (gadget - SceAppMgr == gadget_w):
                print "A gadget with SceAppMgr:" + hex(gadget)

        else:
            # check if it's SceWebKit or SceLibC
            if (gadget - SceWebKit_addr == gadget_w):
                print "SceWebKit"
                # find file offset
                offset = gadget_w - 1
                SceWebKit.seek(offset)
                code = SceWebKit.read(32)
                rop_diss(code, gadget)

            elif (gadget - SceLibC_addr == gadget_w):
                print "SceLibC"
                offset = gadget_w - 1
                SceLibC.seek(offset)
                code = SceLibC.read(32)
                rop_diss(code, gadget)

    # close all FD
    rop.close()
    rop_w.close()

    # modules
    SceWebKit.close()
    SceLibKernel.close()
    SceLibC.close()
    SceLibHttp.close()
    SceNet.close()



if __name__ == '__main__':
    main()