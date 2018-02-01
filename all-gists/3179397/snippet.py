#
# This script is to be run as a tool in a Houdini shelf.
#

# Our "global" variables
sel = hou.selectedNodes()[0]

if sel.type().name() != "voronoifracture":
    hou.ui.displayMessage("Please select a Voronoi Fracture SOP.", ('Ok',), hou.severityType.Error, title="Wrong type...")
    import sys
    sys.exit(0)

selParent = sel.parent()
geo = sel.geometry()
obj = hou.node("/obj")

# Turn on group creation if not already toggled
if not sel.parm("newg").eval():
    sel.parm("newg").set(1)
# Use the entry in Piece Group Prefix to build a list of piece groups
prefix = sel.parm("groupprefix").eval()
groups = [g.name() for g in geo.primGroups() if prefix in g.name()]

# Setup a null to be the grab point for each of the chunk pieces
n = selParent.createNode("null","OUT_FRACT_PTS")
n.setInput(0,sel)
n.moveToGoodPosition()

# Build a subnet to store each of the object-level chunks, and hide it
subnet = obj.createNode("subnet","%s_fracture_objects" %(selParent.name()))
subnet.moveToGoodPosition()
subnet.setDisplayFlag(0)

# This list stores the new path extracted for each piece
pieces = []

# Iterate over each group
for grp in groups:
    # Create new geo object, with the name of the original piece
    nm = "%s_chunk" %(grp)
    g = subnet.createNode("geo", nm)
    
    # Destroy file1
    hou.node('%s/file1' %(g.path())).destroy()

    # Merge in only the piece we want
    om = g.createNode("object_merge","__merge_from_orig")
    om.parm("objpath1").set(n.path())
    om.parm("group1").set(grp)
    om.parm("xformtype").set(1) # Gives us world transforms
    
    # Create xform, translate piece back to origin
    tr = g.createNode("xform","__center_piece")
    tr.setInput(0,om)
    tr.parm("tx").setExpression("-$CEX")
    tr.parm("ty").setExpression("-$CEY")
    tr.parm("tz").setExpression("-$CEZ")
    tr.cook(force=True)

    # Without the display flag here, transforms are skewed
    nl = g.createNode("null","OUT_PIECE")
    nl.setInput(0,tr)
    nl.setDisplayFlag(1)
    nl.setRenderFlag(1)
    
    # Clean up the node layout
    g.layoutChildren()

    # Clean up the coordinate into a string
    coordinate = str( ( tr.parm("tx").eval()*-1,tr.parm("ty").eval()*-1,tr.parm("tz").eval()*-1) )
    coordinate = coordinate.replace(')','')
    coordinate = coordinate.replace('(','')
    coordinate = coordinate.replace(', ',',')

    # Add the tuple for this piece's path and centroid to the pieces list
    pieces.append( (g.path(),coordinate) )

# Clean up the geo nodes inside the subnet
subnet.layoutChildren()

# Create the geom object to store our point cloud
ptobj = obj.createNode("geo","%s_fracture_points" %(selParent.name()))
hou.node('%s/file1' %(ptobj.path())).destroy()
ptobj.moveToGoodPosition()

# Turn the list of attributes into strings for consumption by fracturepoints sop*
attrnames = [ str(c[0]) for c in pieces ]
attrnames = " ".join(attrnames)
pointcoords = [ str(c[1]) for c in pieces ]
pointcoords = " ".join(pointcoords)

# Create a fracturepoints sop and the point/instance settings
fp = ptobj.createNode("fracturepoints","__fracture_points")
fp.parm("pointlist").set(pointcoords)    
fp.parm("attrlist").set(attrnames)

# Add null for organization, set display/render flags here
nl = ptobj.createNode("null","OUT")
nl.setInput(0,fp)
nl.setDisplayFlag(1)
nl.setRenderFlag(1)

ptobj.layoutChildren()


# *The fracturepoints sop is a Python SOP that should be in the same otl as this tool.