from fontTools.pens.basePen import BasePen


class MyPen(BasePen):
    
    def _moveTo(self, pt):
        print "move to", pt
        
    def _lineTo(self, pt):
        print "line to", pt
        
    def _curveToOne(self, pt1, pt2, pt3):
        print "curve to", pt1, pt2, pt3

g = CurrentGlyph()

pen = MyPen(g.getParent())
g.draw(pen)
        