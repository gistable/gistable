#----------------------------------------------------------
# File photo.py - cubify a named image in project.
# @knowuh (Noah Paessel)  http://bit.ly/photoblend
# License: MIT ( http://opensource.org/licenses/MIT )
#----------------------------------------------------------

import bpy
from random import uniform


def make_material(color):
    alpha = 1.0
    red, green, blue, alpha = color
    color_name = '%(red)03d_%(green)03d_%(blue)03d' % {"red": red, "green": green, "blue": blue}
    color = bpy.data.materials.new(color_name)
    color.use_nodes = True
    Diffuse_BSDF = color.node_tree.nodes['Diffuse BSDF']
    Diffuse_BSDF.inputs[0].default_value = [red, green, blue, alpha]
    return color


def draw_pix(x, y, col):
    material = make_material(col)
    r, g, b, a = col
    size = 16 - ((r + g + b) * 4)
    z = size
    bpy.ops.mesh.primitive_cube_add(location=(x, y, z))
    bpy.ops.transform.resize(value=(0.9,0.9,size))
    new_obj = bpy.context.active_object
    new_obj.data.materials.append(material)


def cubify(image_name):
    myImage = bpy.data.images[image_name]
    width, height = myImage.size
    for y in range(0, height):
        for x in range(0, width):
            block_number = (y * width) + x
            color = []
            for color_index in range(0, 4):
                index = (block_number * 4) + color_index
                color.append(myImage.pixels[index])
            draw_pix(x * 2, y * 2, color)
        print ("y: %(y)04d / %(height)04d" % {"y": y, "height": height})

cubify('sprite.png')