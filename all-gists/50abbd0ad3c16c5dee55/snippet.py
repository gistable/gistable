from idaapi import *
from idc import *
from idautils import *
import sys
#Jared DeMott, labs.bromium.com

def error(e):
  print "Fatal error: ", e
  sys.exit(-1)

HeapAlloc_addr = LocByName("__imp__HeapAlloc@12")
if HeapAlloc_addr == 0xffffffff:
  error("bad HeapAlloc_addr")
process_heap   = LocByName("_g_hProcessHeap")
if process_heap == 0xffffffff:
  error("bad process_heap")
GetProcessHeap = LocByName("__imp__GetProcessHeap@0")
if GetProcessHeap == 0xffffffff:
  error("bad GetProcessHeap")

patched=0
if patched:
  isolated_heap  = LocByName("_g_hIsolatedHeap")
  if isolated_heap == 0xffffffff:
    error("bad isolated_heap")
else:
  isolated_heap = 0x12345678 #hack, if data happens to be present will detect i_heap in unpatched

p_heap=0
i_heap=0
d_heap=0
v_heap=0
dynamic_size=0
heap_name = ""
DYSIZE = 0
debug = 0

def check_for_first_jmp_to_this_location(addr):
  ret_addr = 0
  for x_ref in XrefsTo(addr, 0):
    if x_ref.type == 19: #Code_Near_Jump
      ret_addr = x_ref.frm #only return the first
      break
  return ret_addr

def get_prior_addr(addr):
  _addr = check_for_first_jmp_to_this_location(addr)
  if _addr:
    inst=DecodePreviousInstruction(_addr)
    addr=inst.ea
  else:
    inst=DecodePreviousInstruction(addr)
    addr=inst.ea
  return addr

def find_wrapper_size(addr):
  loop = 0
  found_pop = 0
  size = 0
  if debug:
    print "start wrapper_size"
  while True:
    loop+=1
    if loop > 15:
      dynamic_size = 1
      break
    inst = GetMnem(addr)
    if debug:
      print loop, hex(addr), inst
    if inst == "pop":
      if GetOpnd(addr, 0) == "eax":
        found_pop = 1
    elif inst == "mov":
      if GetOpnd(addr, 0) == "eax":
        size = GetOpnd(addr, 1)
        break
    elif inst == "push":
      if found_pop:
        size = GetOpnd(addr, 0)
        break
    addr = get_prior_addr(addr)

  return size

def find_push(addr, ignore_first_push):
  loop = 0
  if debug:
    print "start find_push"
  while True:
    loop+=1
    inst = GetMnem(addr)
    if debug:
      print loop, hex(addr), inst
    if inst != "push":
      if loop < 22:
        addr = get_prior_addr(addr)
        continue
      else:
        print "Failed to find next PUSH, assuming ??? size"
        print "\tAddr: %x" %(addr)
        addr = 0 # is this ok for flags, needed for size
        break
    else:
      if ignore_first_push:
        ignore_first_push-=1
        addr = get_prior_addr(addr)
        continue
      break

  return addr

def find_heap(addr):
  global heap_name, debug
  lcopy_addr=addr
  loop=0
  op_num=1
  second_time=0
  pushes_seen=0
  done = 0
  if debug:
    print "start find_heap"
  while done==0:
    loop+=1
    if loop > 1: #first time just points to 'call heapalloc'
      Mnem = GetMnem(addr)
      op_val = GetOperandValue(addr, op_num)

      if debug:
        print loop, hex(addr), Mnem, hex(op_val)

      if Mnem == "push":
        pushes_seen+=1

      if op_val == process_heap:
        heap_name = "process_heap"
        done = 1
      elif op_val == isolated_heap:
        heap_name = "isolated_heap"
        done = 1

      if Mnem == "call":
        if op_val==GetProcessHeap:
          heap_name = "default_heap"
          done = 1
        else:
          for ref in XrefsFrom(addr, 0):
            if ref.to == GetProcessHeap:
              heap_name = "default_heap"
              done = 1

    if loop < 22:
      addr = get_prior_addr(addr)
    else:
      if second_time == 0:
        op_num=0
        loop=1 #cant be zero else reset addr
        second_time=1
        addr=lcopy_addr
      else:
        heap_name = "variable_heap"
        done = 1

  return heap_name, addr, pushes_seen

def dynamic_check(addr):
  global dynamic_size
  if GetOpType(addr, 0) > 4:
    dynamic_size = 0 #immediate data
  else:
    dynamic_size = 1 #reg or mem ref

  return dynamic_size

def add_to_heap_count():
  global i_heap, p_heap, d_heap, v_heap, heap_name
  if heap_name == "isolated_heap":
    i_heap+=1
  elif heap_name == "process_heap":
    p_heap+=1
  elif heap_name == "default_heap":
    d_heap+=1
  elif heap_name == "variable_heap":
    v_heap+=1
  else:
    print "shouldn't get here ever"
    return -1
  return 1

def WrapperAlloc_output_data(f, name, key, d):
  global heap_name, debug

  if debug:
    print d[key][0], d[key][1], heap_name, d[key][2], d[key][3]

  f.write("%s\n" % d[key][0] )
  f.write("\t%s\n" % d[key][1] )
  f.write("\t%s(%s, %s, " % (name, heap_name, d[key][2]) )
  f.write("%s) from %x\n" % (d[key][3], key) )

def output_data(f, key, d):
  global heap_name, debug

  if debug:
    print d[key][0], d[key][1], heap_name, hex(d[key][2]), hex(d[key][3])
  f.write("%s\n" % d[key][0] )
  f.write("\t%s\n" % d[key][1] )
  f.write("\tHeapAlloc(%s, %s, " % (heap_name, GetOpnd(d[key][2], 0) ) )
  if size_addr:
    f.write("%s) from %x\n" % (GetOpnd(d[key][3], 0), key) )
  else:
    f.write("???) from %x\n" % key )

def handle_WrapperAlloc(f, flags, heap, name, funcs):
  print "handling %s" % name
  dynamic_size = 0
  for x in XrefsTo(LocByName(name), 0):
    ptr = x.frm
    try:
      x = funcs[ptr]
    except:
      funcs[ptr] = []

      func_name = GetFunctionName(ptr)
      d_func_name = Demangle(func_name, GetLongPrm(INF_SHORT_DN))

      heap_name = heap
      size = find_wrapper_size(ptr)

      funcs[ptr].append(func_name)
      funcs[ptr].append(d_func_name)
      funcs[ptr].append(flags)
      funcs[ptr].append(size)

      if dynamic_size == 0:
        if DYSIZE == 0:
          WrapperAlloc_output_data(f, name, ptr, funcs)
          add_to_heap_count()
      if dynamic_size == 1:
        if DYSIZE == 1:
          WrapperAlloc_output_data(f, name, ptr, funcs)
          add_to_heap_count()

print "Beginning"
if DYSIZE:
  f = open("C:\\Users\\AppSec\\Desktop\\uaf\\dynamic_MSHTML_Allocations.txt", "w")
else:
  f = open("C:\\Users\\AppSec\\Desktop\\uaf\\all_MSHTML_Allocations.txt", "w")
funcs = {}
for xref in XrefsTo(HeapAlloc_addr, 0):
  dynamic_size=0
  ptr = xref.frm
  try:
    x = funcs[ptr]
  except:
    funcs[ptr] = []

    func_name = GetFunctionName(ptr)
    d_func_name = Demangle(func_name, GetLongPrm(INF_SHORT_DN))
    #try:
    # if "CCustomCursor::BeginDownload" in d_func_name:
    #   debug = 1
    #except:
    # pass

    Mnem = GetMnem(ptr)
    if Mnem != "call":
      continue
    #print hex(ptr)
    heap_name, heap_addr, pushes_seen = find_heap(ptr)

    ignore_first_push=1

    flags_addr= find_push(ptr, ignore_first_push)
    size_addr = find_push(flags_addr, 1) #always ignore the one we just found
    dynamic_check(size_addr)

    funcs[ptr].append(func_name)
    funcs[ptr].append(d_func_name)
    funcs[ptr].append(flags_addr)
    funcs[ptr].append(size_addr)

    if DYSIZE==1:
      if dynamic_size==1:
        output_data(f, ptr, funcs)
        add_to_heap_count()
    else:
      output_data(f, ptr, funcs)
      add_to_heap_count()

    if "?ProcessHeapAllocClear@@YGPAXK@Z" == func_name:
      handle_WrapperAlloc(f, 8, "process_heap", func_name, funcs)

    if "?ProcessHeapAlloc@@YGPAXK@Z" == func_name:
      handle_WrapperAlloc(f, 0, "process_heap", func_name, funcs)

    if "__MemIsolatedAllocClear@4" == func_name:
      handle_WrapperAlloc(f, 8, "isolated_heap", func_name, funcs)

    if "__MemIsolatedAlloc@4" == func_name:
      handle_WrapperAlloc(f, 0, "isolated_heap", func_name, funcs)

    debug = 0

f.write("\n\nTotal allocations to the default/process heap=%d\n" % (p_heap+d_heap+v_heap) )
f.write("Total allocations to separate isolated heap=%d\n" % i_heap)
f.close()
print "Done."

