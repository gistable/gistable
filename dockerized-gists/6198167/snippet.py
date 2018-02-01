#!/usr/bin/env python
# Call with python CleanBinaryStrings.py <binaryName>
# Will edit the binary in place
import struct
import sys
import mmap
import string
import binascii
import hashlib
import subprocess

### constants
# defined in /usr/include/mach-o/loader.h
LC_SEGMENT = 0x01
LC_SEGMENT_64 = 0x19
LC_SYMTAB = 0x02

# cpu type
CPU_TYPE_X86_64 = int(0x7|0x1000000)
CPU_TYPE_ARM = 12

# magic
MAGIC_MULTIPLE_ARCHITECTURES = 0xCAFEBABE
MAGIC_32_BIT = 0xFEEDFACE
MAGIC_64_BIT = 0xFEEDFACF

archs = {
    # (type, subtype)
    (CPU_TYPE_X86_64, 3) : 'x86_64', # any subtype
    (CPU_TYPE_ARM, 6): 'armv6',
    (CPU_TYPE_ARM, 9): 'armv7',
    (CPU_TYPE_ARM, 11): 'armv7s',
}

class vmap (object):
    def __init__ (self, pmap, offset=0):
        self.pmap = pmap
        self.offset = offset
    def __offsetindex (self, n):
        if isinstance (n, slice):
            return slice (self.offset+(n.start or 0), self.offset+(n.stop or 0), n.step)
        else:
            return self.offset + n
    def __getitem__ (self, n):
        return self.pmap[self.__offsetindex (n)]
    def __setitem__ (self, n, v):
        self.pmap[self.__offsetindex (n)] = v
    def __enter__ (self):
        return self
    def __exit__ (self, a, b, c):
        self.close ()
    def flush (self):
        self.pmap.flush ()
    def close (self):
        self.pmap.close ()
    def submap (self, offset=0):
        return vmap (self.pmap, self.offset + offset)
    def blocks (self, size, n):
        return (self.submap (i * size) for i in range (n))

    def read_le_uint8 (self, n):
        return struct.unpack ('<B', self[n])[0]
    def read_be_uint8 (self, n):
        return struct.unpack ('>B', self[n])[0]
    def read_le_uint16 (self, n):
        return struct.unpack ('<H', self[n:n+2])[0]
    def read_be_uint16 (self, n):
        return struct.unpack ('>H', self[n:n+2])[0]
    def read_le_uint32 (self, n):
        return struct.unpack ('<I', self[n:n+4])[0]
    def read_be_uint32 (self, n):
        return struct.unpack ('>I', self[n:n+4])[0]
    def read_le_uint64 (self, n):
        return struct.unpack ('<Q', self[n:n+8])[0]
    def read_be_uint64 (self, n):
        return struct.unpack ('>Q', self[n:n+8])[0]

    def write_le_uint32 (self, n, v):
        self[n:n+4] = struct.pack ('<I', v)
    def write_be_uint32 (self, n, v):
        self[n:n+4] = struct.pack ('>I', v)

    def read_string (self, n):
        s = ['x']
        while s[-1] != '\0':
            s.append (self[n])
            n += 1
        return ''.join (s[1:-1])
    def write_string (self, n, v):
        for k, c in enumerate (v):
            self[n+k] = c
        self[n+len(v)] = '\0'

symbols = []
sections = []
clsections = []
cleanmap = {}

def demangle (x):
    return subprocess.check_output (['c++filt', x])[:-1] # remove \n at end

def isvalidcxx (x):
    return ('::' not in x) and ('::' in demangle (x))

def process (vm):
    """
    Process one Mach-o file
    """

    magic = vm.read_le_uint32 (0)
    if magic not in (MAGIC_32_BIT, MAGIC_64_BIT):
        raise ValueError ("bad magic!")

    is64bit = magic == MAGIC_64_BIT

    process_command(LC_SYMTAB, process_command_symtab, vm, is64bit)
    if is64bit:
        process_command(LC_SEGMENT_64, process_command_segment, vm, is64bit)
    else:
        process_command(LC_SEGMENT, process_command_segment, vm, is64bit)

    ncleaned = 0
    validchars = set (string.ascii_letters + string.digits + '_')
    for clindex, _, _, claddr, cloffset, clsize in clsections:
        for n_index, (n_name, n_type, n_sect, n_desc, n_value) in enumerate (symbols):
            # n_type is an 8bit field that looks like this:
            # xxxx tttx
            #  The 'x' has data we don't care about
            #  t = N_TYPE:  Defines type of symbol.
            #               The type we care about is N_SECT (noting that this
            #               symbol is defined in the section number given in
            #               n_sect; mask 0x0e)
            if n_type & 0x0e != 0x0e: # if not N_SECT
                continue
            if n_sect != clindex:
                continue
            stroffset = n_value - claddr + cloffset
            strvalue = vm.read_string (stroffset)
            if not strvalue:
                continue
            if not validchars.issuperset (strvalue):
                continue
            if not isvalidcxx (strvalue):
                continue
            clean_string (stroffset, vm)
            ncleaned += 1

    cputype = vm.read_le_uint32 (4)
    cpusubtype = vm.read_le_uint32 (8)

    print 'Cleaned %d strings for architecture %s.' % (
        ncleaned,
        archs.get ((cputype, cpusubtype), "<cputype=%d cpusubtype=%d>" % (cputype, cpusubtype))
    )

def process_command (tcmd, tproc, vm, is64bit):
    """
    Call tproc when cmd 'tcmd' is found (cmds are after header)
        32 bit:                     | 64 bit:
        struct mach_header {        |  struct mach_header_64 {
          uint32_t magic;           |  uint32_t magic;
          cpu_type_t cputype;       |  cpu_type_t cputype;
          cpu_subtype_t cpusubtype; |  cpu_subtype_t cpusubtype;
          uint32_t filetype;        |  uint32_t filetype;
          uint32_t ncmds;           |  uint32_t ncmds;
          uint32_t sizeofcmds;      |  uint32_t sizeofcmds;
          uint32_t flags;           |  uint32_t flags;
                                    |  uint32_t reserved;
        };                          | };
    """
    # number of load commands
    ncmds = vm.read_le_uint32 (16)

    # load commands are after header
    cvm = vm.submap(32) if is64bit else vm.submap(28)
    # struct load_command {
    #   uint32_t cmd;
    #   uint32_t cmdsize;
    # };
    for _ in range (ncmds):
        cmd = cvm.read_le_uint32 (0)
        cmdsize = cvm.read_le_uint32 (4)
        if cmd == tcmd:
            tproc(cvm, vm, is64bit)
            break
        cvm = cvm.submap (cmdsize)

def process_command_symtab (cvm, vm, is64bit):
    """
    Process a symtab command:
      struct symtab_command {
        uint_32 cmd;
        uint_32 cmdsize;
        uint_32 symoff;
        uint_32 nsyms;
        uint_32 stroff;
        uint_32 strsize;
      };

    A symtab command struct describes the size and location of the symbol table
    data structures.

    cvm points to the current command, vm to the beginning of the mach-o file.
    """

    symoff = cvm.read_le_uint32 (8)
    nsyms = cvm.read_le_uint32 (12)
    stroff = cvm.read_le_uint32 (16)
    strsize = cvm.read_le_uint32 (20)

    strvm = vm.submap (stroff)

    # 32 bit:                    | 64 bit:
    #   struct nlist {           | struct nlist_64 {
    #       union {              |     union {
    #          #ifndef __LP64__  |        uint32_t n_strx;
    #          char *n_name;     |     } n_un;
    #          #endif            |
    #          int32_t n_strx;   |
    #       } n_un;              |
    #       uint8_t n_type;      |     uint8_t n_type;
    #       uint8_t n_sect;      |     uint8_t n_sect;
    #       int16_t n_desc;      |     int16_t n_desc;
    #       uint32_t n_value;    |     uint64_t n_value;
    #   };                       | };

    nlist_size = 16 if is64bit else 12
    # process each entry (nlist) in the symbol table
    for symvm in vm.submap (symoff).blocks (nlist_size, nsyms):
        n_strx = symvm.read_le_uint32(0)
        n_type = symvm.read_le_uint8(4)
        n_sect = symvm.read_le_uint8(5)
        n_desc = symvm.read_le_uint16(6)
        if is64bit:
            n_value = symvm.read_le_uint64(8)
        else:
            n_value = symvm.read_le_uint32(8)

        n_name = strvm.read_string (n_strx)

        symbols.append ((n_name, n_type, n_sect, n_desc, n_value))

def process_command_segment (cvm, vm, is64bit):
    """
    Process a segment command:
        32 bit:                    | 64 bit:
        struct segment_command {   | struct segment_command_64 {
            uint32_t cmd;          |     uint32_t cmd;
            uint32_t cmdsize;      |     uint32_t cmdsize;
            char segname[16];      |     char segname[16];
            uint32_t vmaddr;       |     uint64_t vmaddr;
            uint32_t vmsize;       |     uint64_t vmsize;
            uint32_t fileoff;      |     uint64_t fileoff;
            uint32_t filesize;     |     uint64_t filesize;
            vm_prot_t maxprot;     |     vm_prot_t maxprot;
            vm_prot_t initprot;    |     vm_prot_t initprot;
            uint32_t nsects;       |     uint32_t nsects;
            uint32_t flags;        |     uint32_t flags;
        };                         | };

    A symtab command struct describes the size and location of the symbol table
    data structures.

    cvm points to the current command, vm to the beginning of the mach-o file.

    (vm_prot_t is an int, which means it's 8 bytes on 64bit)
    """

    if is64bit:
        nsects = cvm.read_le_uint32(64)
        segment_command_bytes = 72
        section_bytes = 80
    else:
        nsects = cvm.read_le_uint32(48)
        segment_command_bytes = 56
        section_bytes = 68

    # get file offset, loop over each section
    for svm in cvm.submap(segment_command_bytes).blocks(section_bytes, nsects):
        # 32 bit:                | 64 bit:
        # struct section {       | struct section_64 {
        #   char sectname[16];   |     char sectname[16];
        #   char segname[16];    |     char segname[16];
        #   uint32_t addr;       |     uint64_t addr;
        #   uint32_t size;       |     uint64_t size;
        #   uint32_t offset;     |     uint32_t offset;
        #   uint32_t align;      |     uint32_t align;
        #   uint32_t reloff;     |     uint32_t reloff;
        #   uint32_t nreloc;     |     uint32_t nreloc;
        #   uint32_t flags;      |     uint32_t flags;
        #   uint32_t reserved1;  |     uint32_t reserved1;
        #   uint32_t reserved2;  |     uint32_t reserved2;
        # };                     | };

        sectname = svm.read_string(0)
        segname = svm.read_string(16)
        if is64bit:
            addr = svm.read_le_uint64(32)
            size = svm.read_le_uint64(40)
            offset = svm.read_le_uint32(48)
        else:
            addr = svm.read_le_uint32(32)
            size = svm.read_le_uint32(36)
            offset = svm.read_le_uint32(40)

        section = (len (sections) + 1, segname, sectname, addr, offset, size)
        sections.append (section)

        if segname == '__TEXT' and sectname == '__const_coal':
            clsections.append (section)
        if segname == '__TEXT' and sectname == '__const':
            clsections.append (section)

def hash_string (st, length):

    sub = binascii.b2a_base64 (hashlib.sha512 (st).digest ())[:-3]
    sub = sub.replace ('+', '').replace ('/', '')
    while len (sub) < length:
        sub += sub
    return sub[:length]

def clean_string (index, vm):

    strvalue = vm.read_string (index)
    strlength = len (strvalue)

    if strlength < 10:
        print '%s: too short' % strvalue
        return

    base = hash_string (strvalue, 6)
    cksum = hash_string (base, 4)
    cleaned = cksum[:2] + base + cksum[2:]

    if strvalue in cleanmap:
        if cleanmap[strvalue] != cleaned:
            raise Exception ('hash collision!')
    else:
        cleanmap[strvalue] = cleaned

    remaining = len (strvalue) - 10
    vm.write_string (index, cleaned)
    vm.submap (index + 10)[:remaining] = '\0' * remaining

def main (args):
    if len (args) != 1:
        print >>sys.stderr, 'Usage: %s <binary>' % sys.argv[0]
        sys.exit (1)
    with open (args[0], 'r+') as handle, vmap (mmap.mmap (handle.fileno (), 0)) as vm:
        bmagic = vm.read_be_uint32 (0)
        lmagic = vm.read_le_uint32 (0)
        # https://developer.apple.com/library/mac/#documentation/DeveloperTools/Conceptual/MachORuntime/Reference/reference.html
        if bmagic == MAGIC_MULTIPLE_ARCHITECTURES: # fat header, multiple architectures
            # struct fat_header {
            #   uint32_t magic;
            #   uint32_t nfat_arch;
            # };
            nfat_arch = vm.read_be_uint32 (4)
            # loop over each architecture
            for avm in vm.submap (8).blocks(20, nfat_arch):
                # blocks of 20 bits:
                # struct fat_arch {
                #   cpu_type_t cputype;
                #   cpu_subtype_t cpusubtype;
                #   uint32_t offset;
                #   uint32_t size;
                #   uint32_t align;
                # };
                offset = avm.read_be_uint32 (8)
                process (vm.submap (offset))
        elif lmagic == MAGIC_32_BIT:
            # only have one architecture, 32 bit
            process (vm)
        elif lmagic == MAGIC_64_BIT:
            # only have one architecture, 64 bit
            process(vm)
        else:
            raise ValueError ("unknown file type!")

if __name__ == '__main__':
    main (sys.argv[1:])