import os
import glob

# Get lv2 syscall group
def getLv2SyscallGroup(id):
    if   1 <= id <=  31:
        return "sys_process"
    if  40 <= id <=  58:
        return "sys_ppu_thread"
    if  67 <= id <=  69 or id ==  77:
        return "sys_trace"
    if  70 <= id <=  76 or id == 141 or id == 142:
        return "sys_timer"
    if id in [80,81,84,88,89]:
        return "sys_interrupt"
    if id in [82,83,85,87,118] or 128 <= id <= 140:
        return "sys_event"
    if  90 <= id <= 94 or id == 114:
        return "sys_semaphore"
    if  95 <= id <= 99:
        return "sys_lwmutex"
    if 100 <= id <= 104:
        return "sys_mutex"
    if 105 <= id <= 110:
        return "sys_cond"
    if 111 <= id <= 112:
        return "sys_lwcond"
    if 120 <= id <= 127 or id == 148:
        return "sys_rwlock"
    if 143 <= id <= 147:
        return "sys_time"
    if 150 <= id <= 260:
        return "sys_spu/sys_raw_spu"
    if 300 <= id <= 352:
        return "sys_vm/sys_memory/sys_mmapper"
    if 367 <= id <= 370:
        return "sys_uart"
    if 372 <= id <= 376 or 410 <= id <= 412:
        return "sys_game"
    if 378 <= id <= 396:
        return "sys_sm/sys_ctrl"
    if 402 <= id <= 403:
        return "sys_tty"
    if 450 <= id <= 457:
        return "sys_overlay"
    if 460 <= id <= 499:
        return "#sys_prx"
    if 500 <= id <= 514:
        return "#sys_hid"
    if 516 <= id <= 525:
        return "sys_config"
    if 530 <= id <= 559:
        return "sys_usbd"
    if 560 <= id <= 569:
        return "sys_gl819"
    if 570 <= id <= 577:
        return "sys_pad"
    if 578 <= id <= 599:
        return "sys_bluetooth"
    if 600 <= id <= 623 or 837 <= id <= 838:
        return "sys_storage"
    if 624 <= id <= 627:
        return "sys_io"
    if 630 <= id <= 631:
        return "sys_gpio"
    if 650 <= id <= 659:
        return "sys_rsxaudio"
    if 666 <= id <= 679:
        return "sys_rsx"
    if 700 <= id <= 726:
        return "sys_net"
    if 801 <= id <= 834:
        return "lv2Fs"
    if 865 <= id <= 879:
        return "sys_ss/sys_get"
    return "unknown"


# String to unsigned 32-bit integer
def get32(s):
    return sum(map(lambda i: ord(s[3-i])<<(i*8), range(4)))

# File offset to unsigned 32-bit integer
def read32(f, addr):
    f.seek(addr)
    return get32(f.read(4))

# File offset to string
def readstr(f, addr):
    s = ""
    f.seek(addr)
    c = f.read(1)
    while c != '\x00':
        s += c
        c = f.read(1)
    return s


# Main
if __name__ == "__main__":
    for fname in glob.glob("external/*.sprx.elf"):
        print "\n*****************************************************\n"
        print "FILE:", "/dev_flash/sys/external/"+os.path.basename(fname)
        print "SIZE:", os.path.getsize(fname)
        prx = open(fname, 'rb')
        loadSectionAddr = read32(prx, 84)
        moduleInfoAddr = read32(prx, 100)

        # Module Info
        print "MODULE (@ 0x%x):" % (moduleInfoAddr),
        name = readstr(prx, moduleInfoAddr+4)
        expStart = read32(prx, moduleInfoAddr+36) + loadSectionAddr
        expEnd   = read32(prx, moduleInfoAddr+40) + loadSectionAddr
        impStart = read32(prx, moduleInfoAddr+44) + loadSectionAddr
        impEnd   = read32(prx, moduleInfoAddr+48) + loadSectionAddr
        print name

        # Exports
        print "EXPORTS (@ 0x%x - 0x%x):" % (expStart, expEnd)
        for expEntryAddr in range(expStart, expEnd, 28)[1:]:
            libNameAddr = read32(prx, expEntryAddr+16) + loadSectionAddr
            print " - " + readstr(prx, libNameAddr)
            
        # Imports
        print "IMPORTS (@ 0x%x - 0x%x):" % (impStart, impEnd)
        for impEntryAddr in range(impStart, impEnd, 44):
            libNameAddr = read32(prx, impEntryAddr+16) + loadSectionAddr
            print " - " + readstr(prx, libNameAddr)

        # lv2 SysCalls:
        syscalls = set()
        print "LV2SYCALLS (@ 0x%x - 0x%x):" % (loadSectionAddr, moduleInfoAddr)
        for instrAddr in xrange(loadSectionAddr, moduleInfoAddr, 4):
            if read32(prx, instrAddr) & ~(1023) == 0x39600000:
                sc = read32(prx, instrAddr) & 1023
                nextAddrs = range(instrAddr + 4*1, instrAddr + 4*10, 4)
                if 0x44000002 in map(lambda x: read32(prx, x), nextAddrs):
                    syscalls |= {getLv2SyscallGroup(sc)}
        for scgroup in syscalls:
            print " - " + scgroup