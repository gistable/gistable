import bpy
from mathutils import Vector

listOfVectors = [((0,0,0,1)),((1,0,0,1)),((1,1,0,1)),((0,1,0,1))]

shapes = [  [((0,0,0,1)),((1,0,0,1)),((1,1,0,1)),((0,1,0,1))],
            [((0,0,0,1)),((2,0,0,1)),((1,1,0,1)),((0,1,0,1))],
            [((0,0,0,1)),((1,0,0,1)),((1,2,0,1)),((0,1,0,1))],
            [((0,0,0,1)),((1,0,0,1)),((1,1,0,1)),((-1,1,0,1))]
            ]


def print_divider():
    print()
    print("="*40)

            
# turn tuple list into vector list.
def vectorize_list(shapes):
    shapes_as_vectors = []
    for shape in shapes:
        shape_points = []
        for i in shape:
            shape_points.append(Vector(i))
        shapes_as_vectors.append(shape_points)    
    return shapes_as_vectors



# create a spline curve from a number of points
def MakePolyFace(objname, curvename, cList):
    curvedata = bpy.data.curves.new(name=curvename, type='CURVE')
    curvedata.dimensions = '2D'

    objectdata = bpy.data.objects.new(objname, curvedata)
    objectdata.location = (0,0,0) #object origin
    bpy.context.scene.objects.link(objectdata)

    polyline = curvedata.splines.new('POLY')
    polyline.points.add(len(cList)-1)

    for num in range(len(cList)):
        polyline.points[num].co = (cList[num])
        
    polyline.order_u = len(polyline.points)-1  
    polyline.use_endpoint_u = True
    polyline.use_cyclic_u = True 


MakePolyFace("NameOfMyCurveObject", "NameOfMyCurve", listOfVectors)

# select the shape
bpy.context.scene.objects.active = bpy.data.objects["NameOfMyCurveObject"]
polyface = bpy.context.active_object


print_divider()

# Milestone 2
# make several shape keys

shapes = vectorize_list(shapes)
for shape in shapes:
    #print(shape)
    iterator = 0
    for point in polyface.data.splines[0].points:
        print("is", point.co)
        print("should be", shape[iterator])
        # point.co = shape[iterator]
        iterator += 1
    
    print("----")
    # polyface.shape_key_add()        
    

# code snips
# bpy.ops.anim.change_frame(frame=current_frame)
# bpy.context.active_object.data.shape_keys
# me.shape_keys.key_blocks['Key 1'].keyframe_insert(
