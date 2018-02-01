# Pure python reimplementation of .cpio.xz content extraction from pbzx file payload originally here:
# http://www.tonymacx86.com/general-help/135458-pbzx-stream-parser.html
#
# Cleaned up C version (as the basis for my code) here, thanks to Pepijn Bruienne / @bruienne
# https://gist.github.com/bruienne/029494bbcfb358098b41

# Example usage:
# parse_pbzx('PayloadJava', 'PayloadJava.cpio.xz')

# Updated for speeeeeeeeeeeeed

import struct

def parse_pbzx(pbzx_path, xar_out_path):
    with open(pbzx_path, 'rb') as f:
        with open(xar_out_path, 'wb') as g:
            real_magic = '\xfd7zXZ\x00'
            magic = f.read(4)
            if magic != 'pbzx':
                raise Exception("Error: Not a pbzx file")
            # Read 8 bytes for initial flags
            tmp = f.read(8)
            # Interpret the flags as a 64-bit big-endian unsigned int
            flags = struct.unpack('>Q', tmp)[0]
            xar_f = open(xar_out_path, 'wb')
            while (flags & (1 << 24)):
                # Read in more flags
                tmp1 = f.read(8)
                if len(tmp1) < 8:
                    # We're at the end!
                    break
                flags = struct.unpack('>Q', tmp1)[0]
                # Read in length
                tmp2 = f.read(8)
                f_length = struct.unpack('>Q', tmp2)[0]
                xzmagic = f.read(6)
                if xzmagic != real_magic:
                    raise Exception("Error: Header is not xar file header")
                f.seek(-6, 1)
                g.write(f.read(f_length))
