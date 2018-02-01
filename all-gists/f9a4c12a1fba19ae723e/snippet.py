# Skip to the end to see what this can do.
#
# http://s.sudre.free.fr/Stuff/Ivanhoe/FLAT.html
# Flat packages are xar files with a particular structure
# We're looking for the PackageInfo file within the xar file

import urllib2, ctypes, zlib
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
    req = urllib2.Request(url)
    req.headers['Range'] = 'bytes=%s-%s' % (start, start+length-1)
    f = urllib2.urlopen(req)
    data = f.read()
    f.close()
    return data

def retrieve_TOC_offset(url):
    # https://github.com/mackyle/xar/wiki/xarformat
    # Header is a minimum 28 byte structure
    # Beyond that (up to 64 bytes total) is a checksum we're ignoring
    # Grab 28 bytes from beginning
    header_raw = request_bytes(url, length=28)
    # Parse it as a xar header
    header = XarHeader.from_buffer_copy(header_raw)
    # Use the header length field to calculate TOC offset
    # Use the header toc_length_compressed field for TOC length
    return (header.size, header.toc_length_compressed)

def retrieve_TOC(url):
    # https://github.com/mackyle/xar/wiki/xarformat
    # TOC is a zlib compressed XML(-ish) structure
    # Location within the xar is within the header
    TOC_start, TOC_length = retrieve_TOC_offset(url)
    compressed_TOC = request_bytes(url, start=TOC_start, length=TOC_length)
    # Decompress raw zlib compressed stream
    decompressor = zlib.decompressobj()
    # Return TOC XML
    # You should really check out the raw XML - lots of fun stuff in it!
    TOC = SimpleObj()
    TOC.heap_start = TOC_start + TOC_length
    TOC.contents = decompressor.decompress(compressed_TOC)
    return TOC

def retrieve_PackageInfo_offsets(url):
    # https://github.com/mackyle/xar/wiki/xarformat#the-table-of-contents
    toc = retrieve_TOC(url)
    toc_root   = ET.fromstring(toc.contents)
    root_files = toc_root.find('toc').findall('file')
    root_names = [x.find('name').text for x in root_files]
    info_files = []
    if 'PackageInfo' in root_names:
        # Single package
        for x in root_files:
            if x.find('name').text == 'PackageInfo':
                # Name of the .pkg is None, there's only the file itself
                info_files.append([None, x])
    else:
        # Multiple packages, need to find PackageInfo for each
        for i,file_name in enumerate(root_names):
            if file_name.lower().endswith('.pkg'):
                sub_pkg = root_files[i]
                sub_files = sub_pkg.findall('file')
                for x in sub_files:
                    if x.find('name').text == 'PackageInfo':
                        # Remember name of the sub-pkg
                        info_files.append([file_name, x])
    # Now process the info_files
    # Data: package name: encoding, offset, length
    PackageInfo = SimpleObj()
    PackageInfo.TOC = toc
    PackageInfo.offsets = dict()
    for pkg_name, i_file in info_files:
        encoding = i_file.find('data').find('encoding').attrib['style']
        offset   = int(i_file.find('data').find('offset').text)
        length   = int(i_file.find('data').find('length').text)
        PackageInfo.offsets[pkg_name] = (encoding, offset, length)
    return PackageInfo

def retrieve_PackageInfo(url, pkg_name=None):
    # All of the PackageInfo offsets are retrieved
    PackageInfo = retrieve_PackageInfo_offsets(url)
    # pkg_name=None is the default, for when there's one package
    # Otherwise, set pkg_name to:
    #  * single string:   one sub-package to pull information about
    #  * list of strings: multiple sub-packages to pull
    if type(pkg_name) != type([]):
        packages = [pkg_name]
    else:
        packages = pkg_name
    results = []
    for a_pkg in packages:
        encoding, offset, length = PackageInfo.offsets[a_pkg]
        # Offset is stored from the beginning of the XAR heap
        offset += PackageInfo.TOC.heap_start
        if encoding not in ['application/x-gzip', 'application/zlib']:
            raise Exception('Only gzip/zlib decompression support so far (add more!)')
        compressed_PackageInfo = request_bytes(url, start=offset, length=length)
        decompressor = zlib.decompressobj()
        results.append(decompressor.decompress(compressed_PackageInfo))
    if type(pkg_name) != type([]):
        return results[0]
    return results

# SAMPLE_URL = 'http://cran.r-project.org/bin/macosx/R-3.1.0-mavericks.pkg'
#
# >>> retrieve_PackageInfo_offsets(SAMPLE_URL).offsets.keys()
# ['r.pkg', 'tcltk8.pkg', 'r-1.pkg']
# 
# ( v-- 5875 *bytes* of data + headers for 4 HTTP requests - for a 68 MB file)
#
# >>> for x in retrieve_PackageInfo(SAMPLE_URL, ['r.pkg', 'r-1.pkg']):
# ...     print '\n\n' + x
#
#
# <pkg-info format-version="2" identifier="org.r-project.R.mavericks.fw.pkg" version="30165387" install-location="/Library/Frameworks" auth="root">
#     <payload installKBytes="89740" numberOfFiles="3149"/>
#     <scripts>
#         <postinstall file="./postinstall"/>
#     </scripts>
#     <bundle id="org.r-project.R-framework" CFBundleIdentifier="org.r-project.R-framework" path="./R.framework" CFBundleVersion="3.1.0">
#         <bundle id="org.r-project.R-framework" CFBundleIdentifier="org.r-project.R-framework" path="./Versions/3.1" CFBundleVersion="3.1.0">
#             <bundle id="com.apple.xcode.dsym.org.r-project.R-framework" CFBundleIdentifier="com.apple.xcode.dsym.org.r-project.R-framework" path="./Resources/lib/libR.dylib.dSYM" CFBundleVersion="3.1.0"/>
#             <bundle id="com.apple.xcode.dsym.org.r-project.R-framework" CFBundleIdentifier="com.apple.xcode.dsym.org.r-project.R-framework" path="./Resources/lib/libRblas.dylib.dSYM" CFBundleVersion="3.1.0"/>
#             <bundle id="com.apple.xcode.dsym.org.r-project.R-framework" CFBundleIdentifier="com.apple.xcode.dsym.org.r-project.R-framework" path="./Resources/lib/libRlapack.dylib.dSYM" CFBundleVersion="3.1.0"/>
#         </bundle>
#     </bundle>
#     <bundle-version>
#         <bundle id="org.r-project.R-framework"/>
#         <bundle id="org.r-project.R-framework"/>
#         <bundle id="com.apple.xcode.dsym.org.r-project.R-framework"/>
#         <bundle id="com.apple.xcode.dsym.org.r-project.R-framework"/>
#         <bundle id="com.apple.xcode.dsym.org.r-project.R-framework"/>
#     </bundle-version>
# </pkg-info>
#
#
#
# <pkg-info format-version="2" identifier="org.r-project.R.mavericks.GUI.pkg" version="1.64" install-location="/Applications" auth="root">
#     <payload installKBytes="3888" numberOfFiles="137"/>
#     <bundle id="org.R-project.R" CFBundleIdentifier="org.R-project.R" path="./R.app" CFBundleVersion="6734"/>
#     <bundle-version>
#         <bundle id="org.R-project.R"/>
#     </bundle-version>
# </pkg-info>
