import ctypes, zlib
import xml.etree.ElementTree as ET

class SimpleObj(object):
    pass

class XarHeader(ctypes.BigEndianStructure):
    _pack_   = 1
    _fields_ = [('magic',                   ctypes.c_char*4),
                ('size',                    ctypes.c_uint16),
                ('version',                 ctypes.c_uint16),
                ('toc_length_compressed',   ctypes.c_uint64),
                ('toc_length_uncompressed', ctypes.c_uint64),
                ('chksum_alg',              ctypes.c_uint32),
                ]

def request_bytes(url, start=0, length=1):
    f = open(url)
    data = f.read()
    f.seek(start)
    data = f.read(length)
    f.close()
    return data

def retrieve_TOC_offset(url):
    header_raw = request_bytes(url, length=28)
    header = XarHeader.from_buffer_copy(header_raw)
    return (header.size, header.toc_length_compressed)

def retrieve_TOC(url):
    TOC_start, TOC_length = retrieve_TOC_offset(url)
    compressed_TOC = request_bytes(url, start=TOC_start, length=TOC_length)
    decompressor = zlib.decompressobj()
    TOC = SimpleObj()
    TOC.heap_start = TOC_start + TOC_length
    TOC.contents = decompressor.decompress(compressed_TOC)
    return TOC

# The heap begins immediately following the compressed toc. Offset values listed in the toc
# are offsets from the beginning of the heap. The length values in the toc refer to the
# actual number of bytes stored in the heap (compressed or not) whereas the size value
# refers to the extracted size of the item (after decompressing if necessary).

def object_bytes(url, objectname):
    header_len,toc_len = retrieve_TOC_offset(url)
    toc = retrieve_TOC(url)
    toc_root   = ET.fromstring(toc.contents)
    root_files = toc_root.find('toc').findall('file')
    for x in root_files:
        if x.find('name').text == objectname:
            data = x.find('data')
            f_offset = int(data.find('offset').text)
            f_length = int(data.find('length').text)
            true_offset = header_len + toc_len + f_offset
            return request_bytes(url, start=true_offset, length=f_length)
