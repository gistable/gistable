import idaapi
import uuid

def read_guid(ea=None):
    if ea is None:
        ea = idaapi.get_screen_ea()
    # Pay attention to the endian!
    return '{{{}}}'.format(uuid.UUID(bytes_le=idaapi.get_many_bytes(ea, 16)))
Octotree is enabled on this page. Click this button or press cmd shift s (or ctrl shift s) to show it.
