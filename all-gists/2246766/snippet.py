"""From the seemingly undocumented IRIDAS .look format to .csp
"""


import re
import os
import sys
import struct
import binascii
import xml.etree.ElementTree as ET


class LookParsingError(Exception):
    pass


def warn(msg):
    sys.stderr.write("%s\n" % msg)


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


class LookParser(object):
    """Slightly hacky parser for IRIDAS's .look LUT
    """

    def __init__(self, source):
        """source is string containing .look file contents
        """
        tree = ET.fromstring(source)
        self.lut3d = self.parse_lut3d(tree)

    def parse_lut3d(self, tree):
        """Parses the LUT section of the .look, which contains a
        edge-size and binary 3D LUT.

        Data is packed series of (float, float, float), and probably
        something else (there is a suspicious 12 bytes left over..)
        """

        # Data to return
        lut3d = {}

        # Get 3D LUT edge size from
        #   <LUT>
        #     <size>"8"</size>

        lut = tree.find("LUT")
        cube_edge_size = int(lut.find("size").text.replace("\"", ""))

        lut3d['edgelen'] = cube_edge_size

        # Clean up LUT data - remove whitespace, quotes etc
        lutdata = lut.find("data").text
        lutdata = re.sub("[^A-Z0-9]+", "", lutdata)

        # Parse 3D LUT data
        data_binary = binascii.unhexlify(lutdata)

        # Little endian, 3 floats
        format = "<fff"

        samples = list(struct.unpack(format, chunk) for chunk in chunks(data_binary, struct.calcsize(format)))

        if len(samples) != cube_edge_size ** 3:
            raise LookParsingError("Cube size was not correct, was %s, expected %s (%s**3)" % (
                    len(samples),
                    cube_edge_size**3,
                    cube_edge_size))

        lut3d['samples'] = samples

        return lut3d


def csp_header_with_noop_prelut():
    lines = []
    lines.append("CSPLUTV100")
    lines.append("3D")
    lines.append("")
    for x in range(3):
        lines.append("2")
        lines.append("0.0 1.0")
        lines.append("0.0 1.0")
        lines.append("")

    return lines


def main(in_fname = None):
    if in_fname is None:
        in_fname = sys.argv[1]

    f = open(in_fname)
    contents = f.read()
    p = LookParser(contents)

    outcsp = csp_header_with_noop_prelut()
    outcsp.append("%s %s %s" % ((p.lut3d['edgelen'],)*3))

    for s in p.lut3d['samples']:
        outcsp.append("%.05f %.05f %.05f" % s)

    out_fname = os.path.splitext(in_fname)[0] + ".csp"
    df = open(out_fname, "w")
    df.write("\n".join(outcsp))
    df.close()


if __name__ == "__main__":
    main()
