displayName = "PC -> PE"

replaceBlocks = {
    28: 0,
    29: 0,
    33: 0,
    34: 0,
    55: 0,
    69: 0,
    70: 0,
    72: 0,
    75: 0,
    76: 0,
    77: 0,
    90: 0,
    93: 0,
    94: 0,
    97: 0,
    113: 85,
    115: 0,
    116: 0,
    117: 0,
    118: 0,
    119: 0,
    122: 0,
    123: 89,
    124: 89,
    125: 157,
    126: 158,
    130: 54,
    131: 0,
    132: 0,
    137: 0,
    138: 0,
    143: 0,
    144: 0,
    145: 0,
    146: 0,
    147: 0,
    148: 0,
    149: 0,
    150: 0,
    151: 0,
    152: 0,
    153: 0,
    154: 0,
    160: 0,
    161: 18,
    162: 17,
    165: 0,
    166: 0,
    167: 0,
    168: 0,
    169: 0,
    175: 0,
}

def perform(level, box, options):
    for x in xrange(box.minx, box.maxx):
        for y in xrange(box.miny, box.maxy):
            for z in xrange(box.minz, box.maxz):
                blockid = level.blockAt(x, y, z)
                try:
                    newid = replaceBlocks[blockid]
                    level.setBlockAt(x, y, z, newid)
                    break
                except:
                    pass