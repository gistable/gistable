import maya.cmds as cmds

#import edgeLord
#edgeLord.run()

def run():	
	#get selected edgeloop
	edgeLoop = cmds.ls(selection=True)
	#get verticles in the edge loop
	vertLoop = cmds.polyListComponentConversion(edgeLoop, fromEdge=True, toVertex=True)
	#sort individual verticles into a list
	vertLoop = cmds.ls(vertLoop, flatten=True)

	#open undo chunk so entire operation is a single action
	cmds.undoInfo(openChunk = True)

	#soften the mesh normals
	mesh = cmds.listRelatives(parent=1)
	cmds.polySoftEdge(mesh, angle=180)

	#run on each vertex on the edgeloop
	for vert in vertLoop:
		#unlock the normal of the vertex
		cmds.polyNormalPerVertex(vert, unFreezeNormal=True)
		#get the normals of the vertex on the loop
		vertNormals = list(cmds.polyNormalPerVertex(vert, query=True, xyz=True))
		#get only the first three vectors
		vertNormals = vertNormals[:3]

		# select the neighboring verticles using the declared function below
		vertNeighbors(vert, vertLoop)

		#set their normal angle to match the vertex on the loop
		cmds.polyNormalPerVertex(xyz=vertNormals)

	#reselect the edge loops
	cmds.select(edgeLoop)

	#close undo chunk, operation is done
	cmds.undoInfo(closeChunk = True)

# function to select a vertex's perpendicular neighbors 
def vertNeighbors(vert, vertLoop):
	#find the verticles connected to this vertex by edges
	connectedEdges = cmds.polyListComponentConversion(vert, toEdge=True)
	connectedVerts = cmds.polyListComponentConversion(connectedEdges, toVertex = True)

	#select the connected verticles, then deselect the verticles on the loop
	cmds.select(connectedVerts, replace = True)
	cmds.select(vertLoop, deselect = True)
	
