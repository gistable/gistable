import bpy
myCurve = bpy.data.curves[0] # here your curve
spline= myCurve.splines[0] # maybe you need a loop if more than 1 spline

scale = 200

curvepath_template = """
var curves = new THREE.CurvePath();
%s

var geometry = curves.createSpacedPointsGeometry(100);
var material = new THREE.LineBasicMaterial({
    color: 0xff0000
});

// Create the final Object3d to add to the scene
var curveObject = new THREE.Line(geometry, material);""" 

curve_template = """\ncurves.add(new THREE.CubicBezierCurve3(%s\n));""" 
vector3_template = """\n    new THREE.Vector3( %f, %f, %f ),"""

def makecurve(*vectors):
    vector3_string = ''
    for vector in vectors:
        vector3_string = vector3_string + vector3_template % (
            vector[0]*scale,
            vector[1]*scale,
            vector[2]*scale)
    return vector3_string

curves = []
for x in range(len(spline.bezier_points)):
    curves.append(curve_template % makecurve(spline.bezier_points[x].co
        ,spline.bezier_points[x].handle_right
        ,spline.bezier_points[x+1].handle_left
        ,spline.bezier_points[x+1].co)[:-1])

output = curvepath_template % ''.join(curves)
print(output)

