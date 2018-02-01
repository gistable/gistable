import struct

def get_os_struct():
    """Get system os struct."""

    return str(struct.calcsize('P') * 8)