from fontTools.pens.basePen import BasePen
 
def pointOnCurve(p1, c1, c2, p2, value):
    dx = p1[0]
    cx = (c1[0] - dx) * 3.0
    bx = (c2[0] - c1[0]) * 3.0 - cx
    ax = p2[0] - dx - cx - bx
 
    dy = p1[1]
    cy = (c1[1] - dy) * 3.0
    by = (c2[1] - c1[1]) * 3.0 - cy
    ay = p2[1] - dy - cy - by
 
    mx = ax*(value)**3 + bx*(value)**2 + cx*(value) + dx
    my = ay*(value)**3 + by*(value)**2 + cy*(value) + dy
 
    return (mx, my)
 
class AreaPen(BasePen):
    
    def __init__(self):
        BasePen.__init__(self, None)    
        self.points = []
        self.prevPoint = None
        self.precision = 10
        self._area = 0
    
    def addPoint(self, pt):
        if self.points and pt == self.points[-1]:
            return
        self.points.append(pt)
    
    def _moveTo(self, pt):
        self.addPoint(pt)
        self.prevPoint = pt
    
    def _lineTo(self, pt):
        self.addPoint(pt)
        self.prevPoint = pt
    
    def _curveToOne(self, pt1, pt2, pt3):
        self.addPoint(pt1)
        for v in range(1, self.precision):
            t = v / float(self.precision)
            p = pointOnCurve(self.prevPoint, pt1, pt2, pt3, t)
            self.addPoint(p)
        self.addPoint(pt3)
        self.prevPoint = pt3
    
    def closePath(self):
        self.calculateArea()
    
    def endPath(self):
        self.calculateArea()
    
    def calculateArea(self):
        n = len(self.points)
        area = 0
        for i in range(n):
            j = (i + 1) % n
            area += self.points[i][0] * self.points[j][1]
            area -= self.points[j][0] * self.points[i][1]
        self._area += area * .5
        self.points = []
    
    def getArea(self):
        return abs(self._area)
 
def AreaForGlyph(glyph):
    # copy the glyph
    glyph = glyph.copy()
    # area get distorted when there are overlaps
    glyph.removeOverlap()
    # create the pan
    pen = AreaPen()
    # draw into the pen
    glyph.draw(pen)
    # return the area
    return pen.getArea()
 
print AreaForGlyph(CurrentGlyph())