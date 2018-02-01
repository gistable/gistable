class MinMax(object):
    """
    Calculate various area metrics from a list of points,
    such as min, max, midpoint, radius and size.
    """
    def __init__(self):
        super(MinMax, self).__init__()
        FLOATMIN = sys.float_info[3]-1000 # workaround for underflow error
        FLOATMAX = sys.float_info[0]
        self.min = c4d.Vector(FLOATMAX, FLOATMAX, FLOATMAX)
        self.max = c4d.Vector(FLOATMIN, FLOATMIN, FLOATMIN)
    
    def __str__(self):
        return "%r\n  size = %s\n  mp = %s\n  min = %s\n  max = %s" % (
            self, self.getSize(), self.getMp(), self.min, self.max
        )
    
    def addPoint(self, p):
        if p.x < self.min.x: self.min.x = p.x
        if p.x > self.max.x: self.max.x = p.x
        if p.y < self.min.y: self.min.y = p.y
        if p.y > self.max.y: self.max.y = p.y
        if p.z < self.min.z: self.min.z = p.z
        if p.z > self.max.z: self.max.z = p.z
    
    def addPoints(self, lst):
        for p in lst:
            self.addPoint(p)
    
    def addSelectedPoints(self, op):
        """
        Add selected points from object 'op'.
        
        Returns number of points added, or
        False if there are no points or op
        doesn't exist.
        """
        if op is None: return False
        allpnts = op.GetAllPoints()
        if len(allpnts) == 0: return False
        pntsel = op.GetPointS()
        pntcnt = op.GetPointCount()
        n = 0
        if pntsel.HostAlive():
            for i, p in enumerate(allpnts):
                if pntsel.IsSelected(i):
                    self.addPoint(op.GetPoint(i))
                    n += 1
        else:
            return False
        return n
    
    def getMax(self):
        return self.max
    
    def getMin(self):
        return self.min
    
    def getMp(self):
        return (self.min + self.max) * 0.5
    
    def getRad(self):
        return (self.max - self.min) * 0.5
    
    def getSize(self):
        return self.max - self.min
    

