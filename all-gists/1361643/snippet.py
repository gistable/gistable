from __future__ import division # allows floating point division from integers
from FreeCAD import Base
import Part
import math

# Run this macro to create a generic project enclosure box
# You can change all the parameters by selecting the object in the tree view and tweaking values in the "Data" tab

# Possible additions/improvements
#   counterbore bridging .4mm
#   screwpost corner ribbing on/off
#   screwpost edgeNormal ribbing on/off
# lid:
#    make lid lip more like a border?
#    alternatively inset lid in body, have tabs to make it grabbable

# rewrite to accept any polygon (not just rectangles) for box shape, when viewed from top.
# tabbed enclosures?  (ex http://www.amazon.com/Electronics-Enclosure-Plastic-Project-Tabs/dp/B003EAHOYS )
# extra standoffs for boards?

#  sanity checks:
#     SideRadius < width / 2  and < length / 2
#     ScrewpostInset > ScrewpostOD / 2?

class BoxEnclosure:
    def __init__(self, obj,
            OuterWidth=100, OuterLength=150, OuterHeight=50, Thickness=3, 
            SideRadius=10, TopAndBottomRadius = 2,
            ScrewpostInset = 8, ScrewpostID = 4, ScrewpostOD = 10,
            BoreDiameter=0, BoreDepth=0,
            CountersinkAngle=90, CountersinkDiameter=8,
            LipHeight = 1, LidFlip=False):

        obj.addProperty("App::PropertyLength","OuterWidth","BoxBody","Outer width of box enclosure.\nIf inner width is set, this will automatically update accordingly.").OuterWidth = OuterWidth
        obj.addProperty("App::PropertyLength","OuterLength","BoxBody","Outer length of box enclosure.\nIf inner length is set, this will automatically update accordingly.").OuterLength = OuterLength
        obj.addProperty("App::PropertyLength","OuterHeight","BoxBody","Outer height of box enclosure.\nIf inner height is set, this will automatically update accordingly.").OuterHeight = OuterHeight
        obj.addProperty("App::PropertyLength","InnerWidth","BoxBody","Inner width of box enclosure.\nIf outer width is set, this will automatically update accordingly.").InnerWidth = OuterWidth - 2 * Thickness
        obj.addProperty("App::PropertyLength","InnerLength","BoxBody","Inner length of box enclosure.\nIf outer length is set, this will automatically update accordingly.").InnerLength = OuterLength - 2 * Thickness
        obj.addProperty("App::PropertyLength","InnerHeight","BoxBody","Inner height of box enclosure.\nIf outer height is set, this will automatically update accordingly.").InnerHeight = OuterHeight - 2 * Thickness
        obj.addProperty("App::PropertyLength","Thickness","BoxBody","Thickness of the box walls").Thickness = Thickness

        obj.addProperty("App::PropertyLength","SideRadius","Fillets","Radius for the curves around the sides of the box").SideRadius = SideRadius
        obj.addProperty("App::PropertyLength","TopAndBottomRadius","Fillets","Radius for the curves on the top and bottom edges of the box").TopAndBottomRadius = TopAndBottomRadius

        obj.addProperty("App::PropertyLength","ScrewpostInset","Screwposts","How far in from the edges the screwposts should be place").ScrewpostInset = ScrewpostInset
        obj.addProperty("App::PropertyLength","ScrewpostID","Screwposts","Inner Diameter of the screwpost holes, should be roughly screw diameter not including threads").ScrewpostID = ScrewpostID
        obj.addProperty("App::PropertyLength","ScrewpostOD","Screwposts","Outer Diameter of the screwposts.\nDetermines overall thickness of the posts.\nMust be larger than the ScrewpostID!").ScrewpostOD = ScrewpostOD

        obj.addProperty("App::PropertyLength","BoreDiameter","Counterbore","Diameter of the counterbore hole, if any").BoreDiameter = BoreDiameter
        obj.addProperty("App::PropertyLength","BoreDepth","Counterbore","Depth of the counterbore hole, if any").BoreDepth = BoreDepth

        obj.addProperty("App::PropertyLength","CountersinkDiameter","Countersink","Outer diameter of countersink.  Should roughly match the outer diameter of the screw head").CountersinkDiameter = CountersinkDiameter
        obj.addProperty("App::PropertyAngle","CountersinkAngle","Countersink","Countersink angle (complete angle between opposite sides, not from center to one side)").CountersinkAngle = CountersinkAngle

        obj.addProperty("App::PropertyBool","LidFlip","BoxLid","Whether to place the lid with the top facing down or not.\nDoes not affect the part shape at all").LidFlip = LidFlip
        obj.addProperty("App::PropertyLength","LipHeight","BoxLid","Height of lip on the underside of the lid.\nSits inside the box body for a snug fit.").LipHeight = LipHeight

        # used in error handling, to revert to last good value upon error
        self.oldValues = { 
            "OuterWidth": obj.OuterWidth,
            "OuterLength": obj.OuterLength,
            "OuterHeight": obj.OuterHeight,
            "InnerWidth": obj.InnerWidth,
            "InnerLength": obj.InnerLength,
            "InnerHeight": obj.InnerHeight,
            "Thickness": obj.Thickness,
            "SideRadius": obj.SideRadius,
            "TopAndBottomRadius": obj.TopAndBottomRadius,
            "ScrewpostInset": obj.ScrewpostInset,
            "ScrewpostID": obj.ScrewpostID,
            "ScrewpostOD": obj.ScrewpostOD,
            "BoreDiameter": obj.BoreDiameter,
            "BoreDepth": obj.BoreDepth,
            "CountersinkDiameter": obj.CountersinkDiameter,
            "CountersinkAngle": obj.CountersinkAngle,
            "LidFlip": obj.LidFlip,
            "LipHeight": obj.LipHeight,
        }
        
        obj.Proxy = self

    def onChanged(self, fp, prop):
        "Do something when a property has changed"
        print "%s changed" % prop
        if prop == "InnerWidth":
            self.updateProperty(fp, "OuterWidth", fp.InnerWidth + 2 * fp.Thickness)
        elif prop == "InnerLength":
            self.updateProperty(fp, "OuterLength", fp.InnerLength + 2 * fp.Thickness)
        elif prop == "InnerHeight":
            self.updateProperty(fp, "OuterHeight", fp.InnerHeight + 2 * fp.Thickness)
        elif prop == "OuterWidth":
            self.updateProperty(fp, "InnerWidth", fp.OuterWidth - 2 * fp.Thickness)
        elif prop == "OuterLength":
            self.updateProperty(fp, "InnerLength", fp.OuterLength - 2 * fp.Thickness)
        elif prop == "OuterHeight":
            self.updateProperty(fp, "InnerHeight", fp.OuterHeight - 2 * fp.Thickness)
        elif prop == "BoreDepth":
            if fp.BoreDepth >= fp.Thickness:
                fp.BoreDepth = self.oldValues[prop]
                raise ValueError("Bore Depth must be less than Thickness" % prop)
        elif prop == "ScrewpostID":
            if fp.ScrewpostID >= fp.ScrewpostOD:
                fp.ScrewpostID = self.oldValues[prop]
                raise ValueError("Screwpost ID must be less than Screwpost OD" % prop)
        elif prop == "ScrewpostOD":
            if fp.ScrewpostOD <= fp.ScrewpostID:
                fp.ScrewpostOD = self.oldValues[prop]
                raise ValueError("Screwpost OD must be greater than Screwpost ID" % prop)
        elif prop == "Thickness":
            if fp.Thickness <= 0:
                fp.Thickness = self.oldValues[prop]
                raise ValueError("%s must be > 0" % prop)
            elif fp.Thickness <= fp.BoreDepth:
                fp.Thickness = self.oldValues[prop]
                raise ValueError("Thickness must be greater than Bore Depth " % prop)
            self.updateProperty(fp, "OuterWidth", fp.InnerWidth + 2 * fp.Thickness)
            self.updateProperty(fp, "OuterLength", fp.InnerLength + 2 * fp.Thickness)
            self.updateProperty(fp, "OuterHeight", fp.InnerHeight + 2 * fp.Thickness)
                
        elif prop == "Shape":
            for k in self.oldValues.keys():
                self.oldValues[k] = getattr(fp, k)
        print self.oldValues

    def updateProperty(self, fp, prop, value):
        epsilon = 0.0001
        if abs(getattr(fp, prop) - value) > epsilon:
            setattr(fp, prop, value)

    def execute(self, fp):
        box = Part.makeBox(fp.OuterWidth, fp.OuterLength, fp.OuterHeight + fp.LipHeight)
        hollow = Part.makeBox(fp.InnerWidth, fp.InnerLength, fp.InnerHeight, Base.Vector(fp.Thickness, fp.Thickness, fp.Thickness))
        if fp.SideRadius > fp.TopAndBottomRadius:
            box = self.filletBox(box, fp.SideRadius)
            box = self.filletBox(box, fp.TopAndBottomRadius, filletZ=True)    
            hollow = self.filletBox(hollow, fp.SideRadius - fp.Thickness)
            hollow = self.filletBox(hollow, fp.TopAndBottomRadius - fp.Thickness, filletZ=True)    
        else:
            box = self.filletBox(box, fp.TopAndBottomRadius, filletZ=True)    
            box = self.filletBox(box, fp.SideRadius)
            hollow = self.filletBox(hollow, fp.TopAndBottomRadius - fp.Thickness, filletZ=True)    
            hollow = self.filletBox(hollow, fp.SideRadius - fp.Thickness)
        
        box = box.cut(hollow)

        points = (
            (fp.ScrewpostInset, fp.ScrewpostInset, fp.Thickness), 
            (fp.OuterWidth - fp.ScrewpostInset, fp.ScrewpostInset, fp.Thickness), 
            (fp.ScrewpostInset, fp.OuterLength - fp.ScrewpostInset, fp.Thickness), 
            (fp.OuterWidth - fp.ScrewpostInset, fp.OuterLength - fp.ScrewpostInset, fp.Thickness)
        )
        
        box = self.addStandoffs(box, fp.OuterHeight + fp.LipHeight - fp.Thickness, fp.ScrewpostID, fp.ScrewpostOD, points)    
        
        (body, lid) = self.cleaveZ(box, fp.OuterHeight - fp.Thickness)
        
        # create lip on lid
        lid.translate(Base.Vector(0, 0, -fp.LipHeight))
        lid = lid.cut(body)

        # drop lid down so that top is at thickness height
        lid.translate(Base.Vector(0, 0, fp.Thickness - fp.OuterHeight))

        # counterbore and/or countersink
        if fp.BoreDiameter > 0 and fp.BoreDepth > 0:
            lid = self.counterBore(lid, fp.BoreDiameter, fp.BoreDepth, points)
        if fp.CountersinkDiameter > 0 and fp.CountersinkAngle > 0:
            lid = self.counterSink(lid, fp.CountersinkDiameter, fp.CountersinkAngle, points, fp.BoreDepth)
    
        # compensate for lip height
        lid.translate(Base.Vector(0, 0, fp.LipHeight))

        # orient the lid upside down or not
        if fp.LidFlip:
            lid.rotate(Base.Vector(fp.OuterWidth/2, fp.OuterLength/2, (fp.Thickness + fp.LipHeight) / 2), Base.Vector(0,1,0), 180)

        # slide lid over to the side of box body
        lid.translate(Base.Vector(fp.OuterWidth + fp.Thickness, 0, 0))
    
        fp.Shape = body.fuse(lid)

    def counterBore(self, part, diameter, depth, points):
        for point in points:
            if type(point) is tuple or type(point) is list:
                point = Base.Vector(point[0], point[1], point[2])
            bore = Part.makeCylinder(diameter/2.0, depth, point)
            bore.translate(Base.Vector(0,0,-depth))
            part = part.cut(bore)
        return part

    def counterSink(self, part, diameter, angle, points, boreDepth=0):
        if boreDepth < 0:
            boreDepth = 0
        r = diameter / 2.0
        h = r / math.tan(math.radians(angle / 2.0))
        for point in points:
            if type(point) is tuple or type(point) is list:
                point = Base.Vector(point[0], point[1], point[2])
            sink = Part.makeCone(0,r, h, point)
            sink.translate(Base.Vector(0,0,-h-boreDepth))
            part = part.cut(sink)
        return part

    def addStandoffs(self, part, height, ID, OD, points):
        for point in points:
            if type(point) is tuple or type(point) is list:
                point = Base.Vector(point[0], point[1], point[2])
            post = Part.makeCylinder(OD/2.0, height, point)
            part = part.fuse(post)
            screwhole = Part.makeCylinder(ID/2.0, height, point)
            part = part.cut(screwhole)
        return part


    def cleaveZ(self, part, z):
        b = part.BoundBox
        topBox = Part.makeBox(b.XLength, b.YLength, b.ZMax - z, Base.Vector(b.XMin, b.YMin, z))
        bottomBox = Part.makeBox(b.XLength, b.YLength, z - b.ZMin, Base.Vector(b.XMin, b.YMin, b.ZMin))
        return part.cut(topBox), part.cut(bottomBox)
     
    # fillets only edges restricted to X and Y,  or just along Z 
    def filletBox(self, part, radius, filletZ=False):
        if (radius > 0):
            return part.makeFillet(radius, self.filterZEdges(part.Edges, filletZ))
        return part

    def filterZEdges(self, edges, invert=False):
        result = []
        for e in edges:
            if (e.Vertexes[0].Z == e.Vertexes[1].Z) == invert:
                result.append(e)
        return result



def makeBoxEnclosure():
    if FreeCAD.ActiveDocument is None:
        App.newDocument()
    a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","BoxEnclosure")
    BoxEnclosure(a)
    a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
    FreeCAD.ActiveDocument.recompute()
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
    return a

if __name__ == "__main__":
    makeBoxEnclosure()
