from ctypes import *

def convert_bytes_to_structure(st, byte):
    # sizoef(st) == sizeof(byte)
    memmove(addressof(st), byte, sizeof(st))


def convert_struct_to_bytes(st):
    buffer = create_string_buffer(sizeof(st))
    memmove(buffer, addressof(st), sizeof(st))
    return buffer.raw


def conver_int_to_bytes(number, size):
    return (number).to_bytes(size, 'big')