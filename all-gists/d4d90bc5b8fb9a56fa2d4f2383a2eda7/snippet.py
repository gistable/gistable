#!/usr/bin/python

import sys
from keystone import *
from unicorn import *
from unicorn.arm_const import *
from capstone import *
from capstone.arm import *
from capstone.x86 import *

# architectures and modes for the assembler, disassembler, and emulator
ks_arch = KS_ARCH_ARM
ks_mode = KS_MODE_THUMB
cs_arch = CS_ARCH_ARM
cs_mode = CS_MODE_THUMB
emu_arch = UC_ARCH_ARM
emu_mode = UC_MODE_THUMB

# declare assembler, disassembler, and emulator objects
ks = Ks(ks_arch, ks_mode)
cs = Cs(cs_arch, cs_mode)
cs_arm = Cs(cs_arch, CS_MODE_ARM)
emu = Uc(emu_arch, emu_mode)

# the program
code = 'eors r0, r0;'
code += 'adds r0, #0x42;'
code += 'mov r1, #0x1111;'
code += 'movt r1, #0x1111;'
code += 'mov r2, #0x2222;'
code += 'movt r2, #0x2222;'
code += 'push {r0, r1, r2};'
code += 'pop {r3};'

# callback for tracing instructions
def hook_code(uc, address, size, user_data):
	#global cs
	#print 'address = 0x{:x}, size = {}'.format(address, size)
	code = uc.mem_read(address, size)
	code = ''.join(map(chr, code))
	asm = list(cs.disasm(code, size))
	if len(asm) == 0:
		print '>>> 0x{:x}\t{}\tdisasm failure'.format(address, code.encode('hex'))
	for ins in asm:
		print '>>> 0x{:x}\t{}\t{} {}'.format(address, code.encode('hex'), ins.mnemonic, ins.op_str) 

def hook_intr(uc, intno, user_data):
	print 'Interrupt 0x{:x}'.format(intno)

def dumpSimple(mu):
	sp = mu.reg_read(UC_ARM_REG_SP)
	pc = mu.reg_read(UC_ARM_REG_PC)
	lr = mu.reg_read(UC_ARM_REG_LR)
	r0 = mu.reg_read(UC_ARM_REG_R0)
	r1 = mu.reg_read(UC_ARM_REG_R1)
	r2 = mu.reg_read(UC_ARM_REG_R2)
	r3 = mu.reg_read(UC_ARM_REG_R3)
	print 'SP = 0x{:08x}'.format(sp) 
	print 'PC = 0x{:08x}'.format(pc) 
	print 'LR = 0x{:08x}'.format(lr) 
	print 'R0 = 0x{:08x}'.format(r0) 
	print 'R1 = 0x{:08x}'.format(r1) 
	print 'R2 = 0x{:08x}'.format(r2) 
	print 'R3 = 0x{:08x}'.format(r3) 

def dumpMem(mu, addr, size):
	x = mu.mem_read(addr, size)
	x = ''.join(map(chr, x))
	wrap = 16
	group = 4
	for i in xrange(0, len(x), wrap):
		k = i + wrap if i + wrap < len(x) else len(x)
		sys.stdout.write('0x{:x} | '.format(addr+i))
		for j in xrange(i, k):
			sys.stdout.write('{}'.format(x[j].encode('hex')))
			if j % group == group-1: sys.stdout.write(' ')
		sys.stdout.write('\n')

# assemble the program
thumb_code, count = ks.asm(code)
# convert list to str for emulator
thumb_code = ''.join(map(chr, thumb_code))

# emulator setup
emu.hook_add(UC_HOOK_CODE, hook_code)
emu.hook_add(UC_HOOK_INTR, hook_intr)
text_base = 0x1000
text_size = 0x1000
stack_base = 0xf000
stack_size = 0x1000
emu.mem_map(text_base, text_size)
emu.mem_write(text_base, thumb_code)
emu.mem_map(stack_base, stack_size)
emu.mem_write(stack_base, '\x00'*stack_size)
# initialize registers
emu.reg_write(UC_ARM_REG_SP, stack_base + 0xff0)
emu.reg_write(UC_ARM_REG_R0, 0x1234)
emu.reg_write(UC_ARM_REG_R1, 0x5678)
emu.reg_write(UC_ARM_REG_R2, 0xdead)
emu.reg_write(UC_ARM_REG_R3, 0xbeef)
emu.reg_write(UC_ARM_REG_R4, 0xcafe)
emu.reg_write(UC_ARM_REG_R5, 0xbabe)
emu.reg_write(UC_ARM_REG_R6, 0x1337)
emu.reg_write(UC_ARM_REG_R7, 0xfeed)
emu.reg_write(UC_ARM_REG_R8, 0xface)
emu.reg_write(UC_ARM_REG_R9, 0xbaad)
emu.reg_write(UC_ARM_REG_R10, 0xd00d)
emu.reg_write(UC_ARM_REG_R11, 0xcaa7)

print '--- Start context ---'
dumpSimple(emu)
dumpMem(emu, stack_base + 0xfd0, 0x20)
print '\nStarting emulator...'
emu.emu_start(text_base, text_base + len(thumb_code))
print '\n--- End context ---'
dumpSimple(emu)
print '\n--- Stack View ---'
dumpMem(emu, stack_base + 0xfd0, 0x20)

print '\n--- Dead listing ---'
asm = list(cs.disasm(thumb_code, len(thumb_code)))
for ins in asm:
	print '>>> {} {}'.format(ins.mnemonic, ins.op_str) 
	
