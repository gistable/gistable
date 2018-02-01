#!/usr/bin/env python
#
# A GIMP plugin to save each layer in an image as a separate file

from gimpfu import *
import os

def export_layers(img, drw, path, name):
    img = img.duplicate()
    
    for layer in img.layers:
        layer.visible = False
    
    for idx, layer in enumerate(img.layers):
        layer.visible = True
        
        filename = name % [ idx, layer.name ]
        fullpath = os.path.join(path, filename)
        
        layer_img = img.duplicate()
        layer_img.flatten()
        
        pdb.gimp_file_save(layer_img, drw, fullpath, filename)
        img.remove_layer(layer)

register(
    "python-fu-export-layers",
    "Export Layers",
    "Exports each layer as a separate file",
    "Andrew Short",
    "",
    "",
    "E_xport Layers...",
    "*",
    [
        (PF_IMAGE, "img", "Input image", None),
        (PF_DRAWABLE, "drw", "Input drawable", None),
        (PF_DIRNAME, "path", "Output directory", os.getcwd()),
        (PF_STRING, "name", "Output name", "layer_%d.jpg")
    ],
    [],
    export_layers,
    menu="<Image>/File/"
    )

main()