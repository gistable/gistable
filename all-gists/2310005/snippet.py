import os
import struct
import pylibemu

emu = pylibemu.Emulator()

# shellcode uses this address for the winexec call as cmdline
# modify it to see different emu_profile_output
emu.memory_write_dword(0x41414243, 0x41414141)
# this is used as exitprocess exitcode
emu.memory_write_dword(0x41414143, 0x00000021)

#b = open('/opt/pylibemu/urldownloadsc/test.s','rb').read()
b = 'eb6b566a3059648b018b400c8b701cad8b40085ec3608b6c24248b453c8b54057801ea8b4a188b5a2001ebe334498b348b01ee31ff31c0fcac84c07407c1cf0d01c7ebf43b7c242875e18b5a2401eb668b0c4b8b5a1c01eb8b048b01e88944241c61c35fe899ffffff89c3eb05e8f1ffffff6898fe8a0e53e898ffffff41516843424141ffd0687ed8e27353e884ffffff31d28b8a4341414151ffd0'.decode('hex')

MEM_OFFSET = 0x401000
# make the ret work by putting our address here
emu.memory_write_dword(MEM_OFFSET, MEM_OFFSET + 4)

# manually copy shellcode to mem
for i in range(0, len(b), 4):
	emu.memory_write_dword(MEM_OFFSET + 4 + i, struct.unpack('I',b[i:i+4].ljust(4, '\x00'))[0])

# c3 is ret, 90 is nop
emu.prepare('\xc3\x90\x90\x90', 0)

# set stack to MEM_OFFSET
emu.cpu_reg32_set(pylibemu.EMU_REGS.esp, MEM_OFFSET)

emu.test()

print 'EMU PROFILE OUTPUT:'
print emu.emu_profile_output

# output should look like:
#EMU PROFILE OUTPUT:
#UINT WINAPI WinExec (
#     LPCSTR = 0x01c5cdb0 => 
#           = "AAAA";
#     UINT uCmdShow = 49;
#) =  32;
#void ExitProcess (
#     UINT uExitCode = 2088763392;
#) =  0;