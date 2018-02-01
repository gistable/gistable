#http://stackoverflow.com/questions/7553726/blender-how-to-export-shape-keys-using-python
#and three js blender exporter
import bpy
import json

# monkeypatch the json encoder to truncate floats
# http://stackoverflow.com/questions/1447287/format-floats-with-standard-json-module
from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.15g')

path = "/Users/plkap74/Documents/robots.json"

#templates

TEMPLATE_VEC4 = '[ %g, %g, %g, %g ]'
TEMPLATE_VEC3 = '[ %g, %g, %g ]'
TEMPLATE_VEC2 = '[ %g, %g ]'
TEMPLATE_VERTEX = "%g,%g,%g"

TEMPLATE_MORPH_TARGET = """{"name" : "%s", "vertices" : %s}"""

TEMPLATE_SECTION = """
"%s" : %s\n\n
"""

TEMPLATE_MODEL_ASCII = """\
{
   
    "name"  : "%(name)s", 
    
	"vertices" : %(vertices)s,

	"morphTargets" : %(morphTargets)s,
    
    "faces" : %(faces)s,
    
    "normals" : [],

	"colors" : [],

	"uvs" : [],

	"bones" : [],

	"skinIndices" : [],

	"skinWeights" : [],

	"animation" : "",

}
"""

chunks = []
def veckey3(x,y,z):
    return round(x, 6), round(y, 6), round(z, 6)

def veckey3d(v):
    return veckey3(v.x, v.y, v.z)

def generate_vec3(vec):
    return TEMPLATE_VERTEX % (vec[0], vec[1], vec[2])

def generate_vertex(v):
    return generate_vec3( veckey3d(v) )
    
def verticesToString(verts):
    
    vs = []
    for i, v in verts :
        vs.append( v.co.x ) 
        vs.append( v.co.y )
        vs.append( v.co.z )
       
    return json.dumps(vs)

def facesToString(faces):
    faces_s ="["
    faces_a = []
    for f in faces :
        #faces_s += faceToString( f )
        faces_a.append( faceToString( f) )
    faces_s+="]"
    return json.dumps( faces_a )

def faceToString(f):
    verts = []
    # not sure why I can't just json serialize this
    for v in f.vertices:
        verts.append(v)
    return verts
for object in bpy.data.objects:
    if object.type == 'MESH' and object.data.shape_keys:
        
        object.data.update( calc_tessface=True )
        
        faces = facesToString( object.data.tessfaces )
        
        morphTargets = "[\n  "
        
        keyBlocks = object.data.shape_keys.key_blocks
        cKey = 0
        
        for block in keyBlocks:
            
            name = block.name
            vertices = "["
            cVert = 0
            for data in block.data:
                vertex = data.co
                
                if not cVert == 0:
                    vertices += ", "
                    
                vertices += generate_vertex(vertex) 
                
                cVert += 1

            vertices += "]"
            
            morphTarget = TEMPLATE_MORPH_TARGET % (name, vertices)
            
            if not cKey == 0 :
                morphTargets += ",\n"
                
            morphTargets += morphTarget
            
            cKey += 1
            
        morphTargets += "\n]"
        
        model_s = TEMPLATE_MODEL_ASCII % {
            "name" : object.name,
            "vertices" : verticesToString( object.data.vertices.items() ),
            "morphTargets" : morphTargets, 
            "faces" : faces
            }
        chunks.append( model_s )
            
         
file = open(path, "w", encoding="utf8")
file.write( chunks[0] )
file.close()