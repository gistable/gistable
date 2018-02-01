import idautils
import struct 

def get_type1_xref(ea):
  for ref_ea in DataRefsTo(ea):
    # print GetDisasm(ref_ea)
    if Byte(ref_ea) == 0x78 and Byte(ref_ea + 1) == 0x44:
      return ref_ea
  return None

def get_type1_call(ea):
  next_addr = NextHead(ea)
  for i in xrange(0, 10):
    if GetMnem(next_addr) == "BL":
      return next_addr
    next_addr = NextHead(next_addr)
  return None

def get_decode_func_memcpy(ea):
  next_addr = ea
  for i in xrange(0, 0x20):
    if GetMnem(next_addr) == "BLX":
      func_address = GetOperandValue(next_addr, 0)
      if GetFunctionName(func_address) == "memcpy":
        return next_addr
    next_addr = NextHead(next_addr)

  return None

def read_key(ea):
  key = []
  for i in xrange(0, 8):
    key.append(chr(Byte(ea + i)))

  return key

def main():
  s = idautils.Strings(False)
  s.setup(strtypes=Strings.STR_UNICODE | Strings.STR_C)

  hex_str_addr_list = []

  for i, v in enumerate(s):
    if v is None:
      print("Failed to retrieve string index %d" % i)
    else:
      if (v.length + 1) % 2 != 0:
        continue
      # print("%x: len=%d type=%d index=%d-> '%s'" % (v.ea, v.length, v.type, i, str(v)))
      str_value = str(v)
      try:
        str_value = str_value.decode("hex")
        hex_str_addr_list.append(v.ea)
      except Exception, e:
        pass

  for ss_addr in hex_str_addr_list:
    xref = get_type1_xref(ss_addr)
    if xref is None:
      continue

    # print GetDisasm(xref)
    # next func.
    next_call = get_type1_call(xref)
    if next_call is None:
      continue

    # print hex(xref), GetDisasm(xref)
    # print hex(next_call), GetDisasm(next_call)
    # print "-----------------"
    
    decode_func_start = GetOperandValue(next_call, 0)
    decode_func_end = get_decode_func_memcpy(decode_func_start)

    if decode_func_end is None:
      print hex(decode_func_start), GetDisasm(decode_func_start)
      continue

    r1_refs = []
    walker = decode_func_end
    while walker > decode_func_start:
      # print hex(walker), GetDisasm(walker)
      if GetOpnd(walker, 0) == "R1":
        r1_refs.append(walker)
        if GetMnem(walker) == "LDR":
          break
      walker = PrevHead(walker)

    r1_refs.reverse()
    if len(r1_refs) == 0:
      # print "error " + hex(decode_func_start)
      continue

    # print hex(decode_func_start)
    t_offset = 0
    pc_offset = 0
    t_index = 0

    if len(r1_refs) == 2:
      t_offset = Dword(GetOperandValue(r1_refs[0], 1))
      pc_offset = r1_refs[1] + 4
    elif len(r1_refs) == 3:
      t_offset = Dword(GetOperandValue(r1_refs[0], 1))
      pc_offset = r1_refs[1] + 4
      t_index = GetOperandValue(r1_refs[2], 1)

    key_table = t_offset + pc_offset + t_index
    # print hex(decode_func_start), hex(key_table)

    key = read_key(key_table)
    hex_data = list(GetString(ss_addr).decode("hex"))
    for i in xrange(0, len(hex_data)):
      hex_data[i] = chr(ord(hex_data[i]) ^ ord(key[i%8]))
    print hex(ss_addr), "".join(hex_data)

    for i in xrange(0, len(GetString(ss_addr))):
      PatchByte(ss_addr + i, 0x00)

    for i in xrange(0, len(hex_data)):
      PatchByte(ss_addr + i, ord(hex_data[i]))

if __name__ == "__main__":
  main()
  print "done."