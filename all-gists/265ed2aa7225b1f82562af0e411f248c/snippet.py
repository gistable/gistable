def getGUID(ea):
    import uuid
    import struct
    guid = [idaapi.get_byte(addr) for addr in range(ea,ea+16)]
    guid_str = "".join( map(lambda b: struct.pack("B",b),guid) )
    return uuid.UUID(bytes=guid_str)

#or just simple
# credits to @maciekkotowicz
def getGUID(ea):
    return uuid.UUID(bytes=idc.GetManyBytes(ea,16))

"""
Python>guid = getGUID(0x00000001C0002020)
Python>print guid
900448e4-b685-dd11-ad8b-0800200c9a66
"""