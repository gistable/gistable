# coding: utf-8

# Copyright (c) 2013 Mountainstorm
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import bpy
import bmesh
import os

# easy_install Pillow
#

scene = bpy.context.scene
outputPath = os.path.dirname(bpy.data.filepath)
outputFilename = os.path.splitext(bpy.path.basename(bpy.data.filepath))[0]

# render background layer
scene.render.image_settings.color_mode = 'RGBA'
scene.render.filepath = '%s-bg' % os.path.join(outputPath, outputFilename)
#bpy.ops.render.render(write_still=True)

# render layers - start by making background transparent not sky
origAlphaMode = scene.render.alpha_mode
scene.render.alpha_mode = 'TRANSPARENT'

emptyMaterial = bpy.data.materials.new('.empty.material.material')
emptyMaterial.use_sky = True

# for each layer
layer = 1
layerGroup = 'layer.%u' % layer
emptyMaterialObjects = []
skyMaterials = {}
replacedMaterials = []

for obj in scene.objects:
    if obj.type == 'CAMERA':
        pass # leave all cameras
    elif obj.type == 'LAMP':
        pass # leave the lights
    elif obj.type == 'MESH':
        # only care about renderable objects
        if obj.hide_render == True:
            continue
        
        # give any empty material objects the mepty (invisible) material
        if obj.active_material == None:
            emptyMaterialObjects.append(obj)
            obj.active_material = emptyMaterial
            # Note: if this object was supposed to render it wont!
            continue
        
        # check if the object is in this layers group
        print(obj.name)
        visibleOnLayer = False
        for group in obj.users_group:
            if group.name == layerGroup:
                visibleOnLayer = True
                break
            
        # if it's supposed to be visible - we copy the material; so if it's shared we wont affect anything else
        mat = obj.active_material
        if visibleOnLayer:
            print('  match')
            newMat = mat.copy()
            replacedMaterials.append((obj, mat))
            obj.active_material = newMat
                        
        # we've goint to set the material used by this object to 'sky'; thus rendering transparent
        if mat.name not in skyMaterials:
            skyMaterials[mat.name] = (mat, mat.use_sky, mat.use_transparency)
            mat.use_sky = True
            mat.use_transparency = False # TODO: we might not want to actually do this?
    else:
        print('Unhandled object type: ' + obj.type)

# render scene
scene.render.filepath = '%s-%u' % (os.path.join(outputPath, outputFilename), layer)
#bpy.ops.render.render(animation=True, write_still=True)
bpy.ops.render.render(write_still=True)

# tidy up
for obj, mat in replacedMaterials:
    obj.active_material = mat
    
for mat, sky, transparency in skyMaterials.values():
    mat.use_sky = sky
    mat.use_transparency = transparency

for obj in emptyMaterialObjects:
    obj.active_material = None
del emptyMaterial

scene.render.alpha_mode = origAlphaMode