# To use this script, you must first change a few things.
# First, you'll want to change the filepath for the sound file.
# This is on line 76. Second, you might want to change the materials or the settings.
# To render this, you'll need to set the background color, enable Only Render on the display window, and render it with OpenGL (it's much faster and most optimal for 2D renders.)
# LICENSE = wtfpl
# VERSION = 0.3

import bpy

def makeMaterial(name, diffuse, alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.alpha = alpha
    mat.ambient = 1
    mat.use_shadeless = True
    return mat

def setMaterial(ob, mat):
    me = ob.data
    me.materials.append(mat)

# SETTINGS:
bars = 50
maxfreq = 20000 # 20000 is the highest the ear can hear
minfreq = 20 # 20 is the lowest the ear can hear
barheight = 6 # 1 = about 4 blender units
# </settings>

c = 1
l = 1
h = 1

base = ( maxfreq / minfreq ) ** ( 1 / ( bars - 1 ) )
    
#                    name   R  G  B   A
white = makeMaterial('EQ', (1, 1, 1), 1)
# The material settings can be adjusted manually after the script finishes running.

for i in range(0, bars):
    
    l = h
    
    #calculate the frequency
    h = minfreq * base ** ( c - 1 )

    # add a plane
    bpy.ops.mesh.primitive_plane_add(location = (c, 1, 0))
    # set the material
    setMaterial(bpy.context.object, white)
    # move the cursor location to the plane location
    bpy.context.scene.cursor_location = bpy.context.active_object.location
    # move the cursor 1 unit down
    bpy.context.scene.cursor_location.y -= 1
    # move the object origin to the cursor locationa
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    
    # scale the plane
    bpy.context.active_object.scale.x = 0.3
    bpy.context.active_object.scale.y = barheight
    bpy.context.active_object.scale.z = 1

    # apply the scale
    bpy.ops.object.transform_apply(scale=True)
    
    # insert a scale keyframe
    bpy.ops.anim.keyframe_insert_menu(type='Scaling')
    
    # lock X and Z for scaling
    bpy.context.active_object.animation_data.action.fcurves[0].lock = True
    bpy.context.active_object.animation_data.action.fcurves[2].lock = True
    
    # change this to a graph editor because baking sound only works with that
    bpy.context.area.type = 'GRAPH_EDITOR'
    
    # bake the sound into the plane
    bpy.ops.graph.sound_bake(filepath="/home/tyler/Music/Skream/Midnight Request Line_I/01 - Midnight Request Line.mp3", low=l, high=h, attack=0.001, release=0.2) #Replace this path with the path of your song
    
    # lock the y scaling just because
    bpy.context.active_object.animation_data.action.fcurves[1].lock = True
    
    # add 1 to the C value that is used to determine the frequency for the plane
    c += 1
    
#change it back to the text editor.
bpy.context.area.type = 'TEXT_EDITOR'