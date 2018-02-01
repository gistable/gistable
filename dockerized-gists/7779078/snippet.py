import math
import sys

DELTA = 1.5e-8
_INFINITY = 1e+308

class Vec:
    __slots__ = ( 'x', 'y', 'z' )
    def __init__(self,x = 0.0, y = 0.0, z = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self):
        return "(%f,%f,%f)" % (self.x, self.y, self.z)

def add(a,b):
    return Vec(a.x+b.x, a.y+b.y, a.z+b.z)

def sub(a,b):
    return Vec(a.x-b.x, a.y-b.y, a.z-b.z)

def scale(s, a):
    return Vec(s * a.x, s * a.y, s * a.z)

def dot(a, b):
    return a.x*b.x + a.y*b.y + a.z*b.z

def unitize(a):
    return scale( 1.0 / ( math.sqrt( dot( a, a) ) ), a)

class Ray:
    __slots__ = ( 'orig', 'dir' )
    def __init__(self, orig, dir ):
        self.orig = orig 
        self.dir = dir

class Hit:
    __slots__ = ( 'lamb', 'normal' )
    def __init__(self, lamb, normal ):
        self.lamb = float(lamb)
        self.normal = normal

## all objects need to expose 
## .intersect( hit, ray )

class BaseObject:
    def intersect(self, hit, ray):
        return Hit(1.0,Vec())

class Sphere(BaseObject):
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def __str__(self):
        return "%s,%f" % ( str(self.center), self.radius)

    def ray_sphere(self, ray):
        v = sub( self.center, ray.orig)
        b = dot( v, ray.dir)
        disc = b*b - dot( v,v) + self.radius*self.radius
        if disc < 0.0:
            return _INFINITY
        d = math.sqrt(disc)
        t2 = b + d
        if t2  < 0.0:
            return _INFINITY
        t1 = b - d
        if t1 > 0.0:
            return t1
        else:
            return t2

    def intersect(self, hit, ray):
        l = self.ray_sphere( ray)
        if l >= hit.lamb:
            return hit
        n = add( ray.orig, sub( scale( l, ray.dir), self.center))
        return Hit( l, unitize( n))


class Group(BaseObject):
    __slots__ = ( 'bound', 'objs' )
    def __init__(self, sphere):
        self.bound = sphere
        self.objs = []

    def __str__(self):
        s = "bound: %s\n" % (self.bound)
        for t in self.objs:
            s += "\t" + str(t) + "\n"
        return s

    def intersect(self, hit, ray):
        l = self.bound.ray_sphere( ray)
        if l >= hit.lamb:
            return hit
        for s in self.objs:
            hit = s.intersect( hit, ray)
        return hit

def ray_trace( light, ray, scene):
    _ = Hit( _INFINITY, Vec( 0,0,0))
    hit = scene.intersect( _, ray)
    if hit.lamb == _INFINITY:
        return 0.0
    o = add( ray.orig, add( scale( hit.lamb, ray.dir), scale( DELTA, hit.normal) ) )
    g = dot( hit.normal, light)
    if g >= 0.0:
        return 0.0
    sray = Ray( o, scale( -1, light))
    si = scene.intersect( Hit( _INFINITY, Vec( 0,0,0)), sray)
    if si.lamb == _INFINITY:
        return -g
    else:
        return 0.0

def create( level, c, r):
    sphere = Sphere( c, r)
    if level == 1:
        return sphere
    group = Group( Sphere( c, 3*r))
    group.objs.append(sphere)
    rn = 3*r/math.sqrt(12)
    for dz in range(-1,2,2):
        for dx in range(-1,2,2):
            c2 = Vec(c.x+dx*rn, c.y+rn, c.z+dz*rn)
            group.objs.append( create( level-1, c2, r/2.0))

    return group
            



def run( dimension, level):
    n = dimension
    scene = create( level, Vec(0, -1, 0), 1)
    out = open("image.pgm","w")
    out.write( "P5\n" + str(n) + " " + str(n) + "\n255\n")
    for y in range( n-1, -1, -1):
        for x in range( 0, n, 1):
            d = Vec( x - (n/2.0), y - (n/2.0), n)
            ray = Ray( Vec( 0, 0, -4), unitize( d))
            g = ray_trace( unitize( Vec( -1, -3, 2)), ray, scene)
            out.write( chr( int(0.5 + (255.0 * g))))
    out.close()


if __name__ == "__main__":
    if "--run" in sys.argv:
        run( int(sys.argv[3]), int(sys.argv[2]))

