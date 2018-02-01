class Plane(object):
    """Represents a plane defined by position and normal vector"""
    def __init__(self, pos, n):
        super(Plane, self).__init__()
        self.pos = pos
        self.n = n.GetNormalized()
        if DEBUG: print "self.pos = %r, self.n = %r" % (pos, n)
    
    def setN(self, newn):
        self.n = newn.GetNormalized()
    
    def setPos(self, newpos):
        self.pos = newpos
    
    def sideAsString(self, d):
        if d < 0:
            res = "back"
        elif d == 0:
            res = "onplane"
        else:
            res = "front"
        return res
    
    def pointResidence(self, p):
        """
        Define the resident direction of a point with respect
        to the plane.
        
        The point can be either in front of the plane (+1), on the
        plane (0) or on the back of the plane (-1).
        """
        d = self.pointDistance(p)
        eps = 0.000001
        if d <= eps:
            d = -1
        elif abs(d) < eps:
            d = 0
        else:
            d = 1
        if DEBUG: "point residence = %r" % d
        return d
    
    def pointDistance(self, p, getsigned=True):
        """
        Calculate distance from a point p to the plane.
        
        getsigned    bool   set to True if you want a signed distance.
                            This can be useful to determine if the point
                            is located in the half space from the backside
                            of the plane or in the half space on the front.
        """
        if p is None:
            raise ValueError("Point p can't be None")
        if not isinstance(p, c4d.Vector):
            raise TypeError("Expected Vector, got %s" % type(p))
        if DEBUG: print "pos = %r, n = %r, p = %r" % (self.pos, self.n, p)
        if not getsigned:
            projp = self.lineIntersection(p)
            if projp is None:
                raise ValueError("dist can't be None when projected along plane normal!")
            dist = (p - projp).GetLength()
        else:
            pos = self.pos
            n = self.n
            d = -n * pos
            nx2 = n.x * n.x
            ny2 = n.y * n.y
            nz2 = n.z * n.z
            dist = (n.x * p.x + n.y * p.y + n.z * p.z + d)
            if DEBUG:
                s = ""
                if getsigned is True:
                    s = " (signed)"
                print "dist = %r%s" % (dist, s)
        return dist
    
    def lineIntersection(self, p, d=None):
        """
        Calculate intersection point with a line starting at position p
        and pointing in the direction d. May return None if an intersection
        isn't possible (parallel directions).
        
        d        vector    direction of the line. If None, the normal of the
                           plane will be used instead.
        """
        if p is None:
            raise ValueError("Point p can't be None")
        if not isinstance(p, c4d.Vector):
            raise TypeError("Expected Vector, got %s" % type(p))
        if not isinstance(d, (type(None), c4d.Vector)):
            raise TypeError("Expected Vector or None, got %s" % type(p))
        pos = self.pos
        n = self.n
        if d is None:
            d = n
        else:
            d.Normalize()
        ddn = d.Dot(n)
        if abs(ddn) < 0.000001:
            return None
        mu = (pos - p).Dot(n)/ddn
        pisect = p + mu * d
        return pisect
    
