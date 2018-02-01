"""BIL parser to load elevation info from sites like
http://earthexplorer.usgs.gov/

Mostly based of:
http://stevendkay.wordpress.com/2010/05/29/parsing-usgs-bil-digital-elevation-models-in-python/

Documentation for the format itself:
http://webhelp.esri.com/arcgisdesktop/9.2/index.cfm?TopicName=BIL,_BIP,_and_BSQ_raster_files

Documentation for the accompanying world files:
http://webhelp.esri.com/arcgisdesktop/9.2/index.cfm?TopicName=World_files_for_raster_datasets
"""


def parse_header(hdr):
    """
    Parse a BIL header .hdr file, like:

    BYTEORDER I
    LAYOUT BIL
    NROWS 1201
    NCOLS 1201
    ...
    """
    contents = open(hdr).read()
    lines = contents.strip().splitlines()
    header = {}
    for li in lines:
        key, _, value = li.partition(" ")
        header[key] = value

    return header


def parse_bil(path, width, height):
    # where you put the extracted BIL file
    fi = open(path, "rb")
    contents = fi.read()
    fi.close()

    # unpack binary data into a flat tuple z
    s = "<%dH" % (int(width*height),)
    z = struct.unpack(s, contents)

    heights = [[None for x in range(height)] for x in range(width)]

    for r in range(0,height):
        for c in range(0,width):
            elevation = z[(width*r)+c]

            if (elevation==65535 or elevation<0 or elevation>20000):
                # may not be needed depending on format, and the "magic number"
                # value used for 'void' or missing data
                elevation=0.0

            heights[r][c]=float(elevation)

    return heights


class BilParser(object):
    def __init__(self, headerpath):
        self.basepath = os.path.splitext(headerpath)[0]
        
        self.header = parse_header(self.basepath + ".hdr")
        self.heights = parse_bil(
            self.basepath + ".bil",
            width = int(self.header['NROWS']),
            height = int(self.header['NCOLS']))


bp = BilParser("n56w004.hdr")
print bp.header
