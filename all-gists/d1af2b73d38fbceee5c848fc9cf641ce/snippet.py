import idaapi
import idautils
import idc
import struct

def do_rename(eaaddr, name):
    idc.MakeCode(eaaddr)
    idc.MakeFunction(eaaddr)
    idc.MakeNameEx(eaaddr, name, idc.SN_NOWARN)


if __name__ == "__main__":
    # name.stackTrace/addr.stackTrace are in rom:/debug/ for Fire Emblem If/Fates (all regions).
    with open('name.StackTrace', 'rb') as f:
        names = f.read()
    with open('addr.StackTrace', 'rb') as f:
        addrs = f.read()
    functions = []
    while len(addrs) > 0:
        addr, name_ofs = struct.unpack('<II', addrs[:8])
        addrs = addrs[8:]
        name = names[name_ofs:names.index('\x00', name_ofs)]
        if '(' in name:
            name = name[:name.index('(')]
        # TODO: extract input variable type information.
        do_rename(addr, name)