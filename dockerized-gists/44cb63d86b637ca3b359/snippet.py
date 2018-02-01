# encode a 32x32x16 brick coordinate as a 128x128 coordinate, with
# the z value sorted in morton order

def part2to4(x):
    x = x & 3 # not strictly necessary if value is clean
    return (x ^ (x << 1)) & 5

def compact4to2(x):
    x = x & 5
    return (x ^ (x >> 1)) & 3

def xy2z(x,y):
    return (part2to4(y)<<1) | part2to4(x)

def z2xy(z):
    return compact4to2(z), compact4to2(z>>1)

def xyz2xy(x,y,z):
    u,v = z2xy(z)
    return (x<<2)|u, (y<<2)|v

def xy2xyz(x,y):
    z = xy2z(x,y)
    return x>>2, y>>2, z
