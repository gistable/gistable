# Blender Python script to triangulate obj coming from Google Blocks
# result http://vatelier.net/MyDemo/TestingTriangulation/
# via https://blender.stackexchange.com/questions/34537/how-to-batch-convert-between-file-formats
import bpy # Python interface for Blender, use Shift+F4 to start the interactive console.
# alternatively for headless server side batch conversion use blender -b -P triangulate_obj.py
import os

def convert_in_dir(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.obj') :
                print(f)
                mesh_file = os.path.join(path, f)
                obj_file = os.path.splitext(mesh_file)[0] + "_triangulated.obj"
                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.object.delete()
                bpy.ops.import_scene.obj(filepath=mesh_file)
                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.export_scene.obj(filepath=obj_file, use_triangles=True)
                # export to glTF, for AFrame us gltf-model-next from aframe-extras
                # cf http://vatelier.net/MyDemo/TestingTriangulation/gltf.html
                if "gltf" in dir(bpy.ops.export_scene):
                    gltf_file = os.path.splitext(mesh_file)[0] + ".gltf"
                    bpy.ops.export_scene.gltf(filepath=gltf_file)
    return;
            
path = 'C:/Users/UCB/Downloads/testing_triangulation/'
# assuming a lot of subdirectories to with one or more obj file to fix
for root, dirs, files in os.walk(path):
    # convert_in_dir(path)
    for d in dirs:
        cd = os.path.join(path, d)
        convert_in_dir(cd)
