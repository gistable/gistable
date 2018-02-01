from idaapi import *

# with code taken from
# - http://hexblog.com/idapro/vmware_modules.py
# - HexRays forum
# - https://gist.github.com/nmulasmajic/f90661489f858237bcd68fbde5516abd#file-find_nt_imagebase_x64-py

class LoadedModulesList(Choose2):

    def __init__(self, title, modlistEA=BADADDR, flags=0, width=None, height=None, embedded=False, modal=False):
      self.ptr = modlistEA if modlistEA != BADADDR else get_name_ea_simple("PsLoadedModuleList")
      if self.ptr == BADADDR:
        raise ValueError('Missing symbol: PsLoadedModuleList')
      self.n = 0
      self.lines = []
      self.modules = []
      self.icon = 82
      self.selcount = 0
      self.modal = modal
      self.is64 = get_inf_structure().is_64bit()
      self.fmt = "%016X" if self.is64 else "%08X"
      self.bits = 3 if self.is64 else 2
      self.get_value = Qword if self.is64 else Dword

      Choose2.__init__(
        self,
        title,
        [ ["BaseAddress", 16], ["BaseDllName", 16], ["FullDllName", 24], ["SizeOfImage", 16], ["EntryPoint", 16] ],
        flags = flags,
        width = width,
        height = height,
        embedded = embedded)

      self.walk_modulelist()

    def OnClose(self):
      self.modules = []
      self.lines = []

    def OnSelectLine(self, n):
      jumpto(self.modules[n][0])

    def OnGetLine(self, n):
      return self.lines[n]

    def OnGetSize(self):
      return len(self.lines)

    def add_module(self, BaseAddress, BaseDllName, FullDllName, SizeOfImage, EntryPoint):
      self.modules.append((BaseAddress, BaseDllName, FullDllName, SizeOfImage, EntryPoint))

    def update(self):
      self.n = 0
      self.lines = [self.make_item() for x in xrange(len(self.modules))]
      self.Refresh()
      return self.Show(self.modal) >= 0

    def make_item(self):
      r = [self.fmt % self.modules[self.n][0], # func name
         "%s" % self.modules[self.n][1], # xrefs
         "%s" % self.modules[self.n][2], # total no of loops in function
         self.fmt % self.modules[self.n][3],# total nodes in func
         self.fmt % self.modules[self.n][4]]# total nodes in func             
      self.n += 1
      return r

    #read a string from UNICODE_STRING structure
    def get_unistr(self, addr):
      len = Word(addr)      #USHORT Length;
      start = self.get_value(addr + (1<<self.bits)) #PWSTR  Buffer;
      if len>1000:
        raise ValueError(self.fmt + ": String too long (%d)"%(addr, len))
      res = u''
      while len>0:
        c = Word(start)
        if c==0: break
        res += unichr(c)
        start += 2
        len -= 1
      return res

    def walk_modulelist(self):
      # get the first module
      cur_mod = self.get_value(self.ptr)
      # loop until we come back to the beginning

      # TODO: proper parsing of the PsLoadedModuleList
      # structure should involve loading the 
      # _LDR_DATA_TABLE_ENTRY structure and getting
      # offsets from it by field names
      while cur_mod != self.ptr and cur_mod != BADADDR:
        BaseAddress  = self.get_value(cur_mod + (6<<self.bits))
        EntryPoint   = self.get_value(cur_mod + (7<<self.bits))
        SizeOfImage  = Dword(cur_mod + (8<<self.bits))
        FullDllName  = self.get_unistr(cur_mod + (9<<self.bits)).encode('utf-8')
        BaseDllName  = self.get_unistr(cur_mod + (0xB<<self.bits)).encode('utf-8')
        self.add_module(BaseAddress, BaseDllName, FullDllName, SizeOfImage, EntryPoint)
        #get next module (FLink)
        next_mod = self.get_value(cur_mod)
        #check that BLink points to the previous structure
        if self.get_value(next_mod + (1<<self.bits)) != cur_mod:
          print self.fmt + ": List error!" % cur_mod
          break
        cur_mod = next_mod
      self.update()



'''
  Module Name: 
    find_nt_imagebase_x64.py
  
  Abstract:
    Discovers the base address of ntoskrnl when IDA's GDB stub is 
    loaded by leveraging the IDT.
  
    NOTE: This is only compatible for 64-bit editions of Windows.
    
  Author:
    Nemanja (Nemi) Mulasmajic <nm@triplefault.io>
      http://triplefault.io
'''

# The size of a page on x86/AMD64.
PAGE_SIZE = 4096

def splice(string, start_token, end_token):
  '''
    Given an input 'string', extracts the contents between the
    starting and ending tokens.
  '''
  start_pos = string.find(start_token)
  end_pos = string.rfind(end_token)
  
  # This means our tokens are invalid and don't exist in the string.
  if start_pos == -1 or end_pos == -1:
    return None
  
  start_pos += len(start_token)

  # Can't splice the string if this is true.
  if start_pos > end_pos:
    return None 
    
  # Splices the string.
  return string[start_pos:end_pos]

def read_idt_entry(address):
  '''
    Extracts the virtual address of the _KIDTENTRY64 at 'address'.
  '''
  
  # nt!_KIDTENTRY64
  '''
    +0x000 OffsetLow        : Uint2B
    +0x002 Selector         : Uint2B
    +0x004 IstIndex         : Pos 0, 3 Bits
    +0x004 Reserved0        : Pos 3, 5 Bits
    +0x004 Type             : Pos 8, 5 Bits
    +0x004 Dpl              : Pos 13, 2 Bits
    +0x004 Present          : Pos 15, 1 Bit
    +0x006 OffsetMiddle     : Uint2B
    +0x008 OffsetHigh       : Uint4B
    +0x00c Reserved1        : Uint4B
    +0x000 Alignment        : Uint8B
  '''
  
  # Relevant structure offsets.
  OFFSET_KIDTENTRY64_OFFSETLOW = 0x0
  OFFSET_KIDTENTRY64_OFFSETMIDDLE = 0x6
  OFFSET_KIDTENTRY64_OFFSETHIGH = 0x8

  # Read the data.
  OffsetLow = Word(address + OFFSET_KIDTENTRY64_OFFSETLOW)
  OffsetMiddle = Word(address + OFFSET_KIDTENTRY64_OFFSETMIDDLE)
  OffsetHigh = Dword(address + OFFSET_KIDTENTRY64_OFFSETHIGH)
  
  # Failed to read some part of the offset.
  if OffsetLow is None or OffsetMiddle is None or OffsetHigh is None:
    return None
  
  # Build the 64-bit address representing this structure.
  return ((OffsetHigh << 32) + (OffsetMiddle << 16) + OffsetLow)

def page_align(address):
  '''
    Aligns the 'address' on an architecture page boundary (0x1000).
  ''' 
  return (address & ~(PAGE_SIZE - 1))
  
def find_base_address(address, verbose = True):
  '''
    Walks memory backwards from the starting 'address' until a 
    valid PE header is located.
  '''

  # nt!_IMAGE_DOS_HEADER
  '''
    +0x000 e_magic          : Uint2B
    +0x002 e_cblp           : Uint2B
    +0x004 e_cp             : Uint2B
    +0x006 e_crlc           : Uint2B
    +0x008 e_cparhdr        : Uint2B
    +0x00a e_minalloc       : Uint2B
    +0x00c e_maxalloc       : Uint2B
    +0x00e e_ss             : Uint2B
    +0x010 e_sp             : Uint2B
    +0x012 e_csum           : Uint2B
    +0x014 e_ip             : Uint2B
    +0x016 e_cs             : Uint2B
    +0x018 e_lfarlc         : Uint2B
    +0x01a e_ovno           : Uint2B
    +0x01c e_res            : [4] Uint2B
    +0x024 e_oemid          : Uint2B
    +0x026 e_oeminfo        : Uint2B
    +0x028 e_res2           : [10] Uint2B
    +0x03c e_lfanew         : Int4B
  '''
  IMAGE_DOS_SIGNATURE = 0x5A4D # 'MZ'

  # Relevant structure offsets.
  OFFSET_IMAGE_DOS_HEADER_E_MAGIC = 0x0
  OFFSET_IMAGE_DOS_HEADER_E_LFANEW = 0x3c
    
  # nt!_IMAGE_NT_HEADERS
  '''
     +0x000 Signature        : Uint4B
     +0x004 FileHeader       : _IMAGE_FILE_HEADER
     +0x018 OptionalHeader   : _IMAGE_OPTIONAL_HEADER64
  '''
  IMAGE_NT_SIGNATURE = 0x00004550 # 'PE00'
  
  # Relevant structure offsets.
  OFFSET_IMAGE_NT_HEADERS_SIGNATURE = 0x0
  
  # Find the page aligned offset of the specified symbol's address by
  # stripping off the page RVA.
  DosHeader = page_align(address)
  
  if verbose:
    print "\nSearching for base address of symbol @ {} ({}).".format(hex(address), hex(DosHeader))
    print "=" * 100
  
  while DosHeader != 0:
    e_magic = Word(DosHeader + OFFSET_IMAGE_DOS_HEADER_E_MAGIC)
    
    # If we can't read the page, it's most likely invalid (not 
    # mapped in). In the kernel most PE images (like ntoskrnl) 
    # are more or less guaranteed to have their PE header in 
    # the NonPagedPool. We skip invalid pages here.
    if e_magic is not None:
      if verbose:
        print "{} --> {}".format(hex(DosHeader), hex(e_magic))
        
      # Do we have an 'MZ'?
      if e_magic == IMAGE_DOS_SIGNATURE:
        # Extract the e_lfanew.
        e_lfanew = Dword(DosHeader + OFFSET_IMAGE_DOS_HEADER_E_LFANEW)
        
        # Go to the (potential) IMAGE_NT_HEADERS at this location.
        NtHeaders = DosHeader + e_lfanew
      
        # The IMAGE_NT_HEADERS should be on the same 
        # page as the IMAGE_DOS_HEADER. If this is not true, 
        # something's weird and we shouldn't read from this address.
        if page_align(NtHeaders) == DosHeader:
          Signature = Dword(NtHeaders + OFFSET_IMAGE_NT_HEADERS_SIGNATURE)
        
          if verbose:
            print "\t{} --> {}".format(hex(NtHeaders), hex(Signature))
      
          # Do we have a 'PE00'?
          if Signature == IMAGE_NT_SIGNATURE:
            if verbose:
              print "\t{} Base address located @ {}.".format("^" * 50, hex(DosHeader))
            
            # At this point, it looks like we have both a valid 
            # DOS and NT header. This should be the right base 
            # address.
            return DosHeader    
    
    # Try another page.
    DosHeader -= PAGE_SIZE
  
  # If we get to here... someone left this script running way too long.
  return None


modlist = get_name_ea_simple("PsLoadedModuleList")
if modlist == BADADDR:
  # Ask for the idtr register from the VMware GDB stub.
  monitor_result = SendDbgCommand("r idtr")

  # The string is returned in the following format:
  #   idtr base=0xfffff800707c9070 limit=0xfff

  try:
    # Try to extract just the numerical base.
    idt_base = int(splice(monitor_result, "base=", " limit"), 16)
  except:
    print "ERROR: Failed to retrieve IDT base from VMware's GDB stub."
    exit(-1)
    
  print "IDT base @ {}.".format(hex(idt_base))

  idt_entry = read_idt_entry(idt_base)
  if idt_entry is None:
    print "ERROR: Failed to extract and parse KIDTENTRY64."
    exit(-2)
    
  print "_KIDTENTRY64[0] (nt!KiDivideErrorFault) @ {}.".format(hex(idt_entry))

  # We have a symbol in the address space of nt!* (unless someone 
  # detoured the IDT entry...). At this point, we walk kernel 
  # memory backwards from the start of this symbol until we
  # get to a valid PE header. This should be the base address of 
  # ntoskrnl.
  ntoskrnl_base = find_base_address(idt_entry)
  if ntoskrnl_base is not None:
    print "\nThe base address of nt (ntoskrnl) is @ {}.".format(hex(ntoskrnl_base))

    pdb_file = ask_file(0, "ntoskrnl.exe", "Path to copy of guest machine's ntoskrnl.exe")
    if pdb_file is None:
      print "\nERROR: Canceled."
      exit(-4)

    # Those come from pdb/common.h
    PDB_CC_USER_WITH_DATA=3
    PDB_DLLBASE_NODE_IDX=0
    PDB_DLLNAME_NODE_IDX=0

    pdb_node = idaapi.netnode()
    pdb_node.create("$ pdb")
    pdb_node.altset(PDB_DLLBASE_NODE_IDX, ntoskrnl_base)
    pdb_node.supset(PDB_DLLNAME_NODE_IDX, pdb_file)
    idaapi.load_and_run_plugin("pdb", PDB_CC_USER_WITH_DATA)
    rc = pdb_node.altval(PDB_DLLBASE_NODE_IDX)
    if not rc:
      print "\nERROR: Could not load PDB file."
      exit(-5)

  else:
    print "\nERROR: Could not find the base address of ntoskrnl after searching all resident memory. Something clearly went wrong. Additionally, you waited a very long time. Sorry!"
    exit(-3)

LoadedModulesList("Loaded Modules", modal=False)
