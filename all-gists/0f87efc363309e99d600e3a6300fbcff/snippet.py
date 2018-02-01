#!/usr/bin/env python

from gimpfu import *
import time
import json

gettext.install("gimp20-python", gimp.locale_directory, unicode=True)

def add_layers(img, layer, classes):

    gimp.context_push()
    img.undo_group_start()

    if img.base_type is RGB:
        type = RGBA_IMAGE
    else:
        type = GRAYA_IMAGE

    cl_list = json.loads(classes)

    for c in cl_list:
        layer = gimp.Layer(img, c,
                        layer.width, layer.height, type, 100, NORMAL_MODE)
        layer.fill(TRANSPARENT_FILL)
        img.insert_layer(layer)

    img.undo_group_end()
    gimp.context_pop()

register(
    "python-fu-addlayer",
    N_("Add layers stack"),
    "Add layers",
    "Eugene Mikhantiev",
    "Eugene Mikhantiev",
    "2017",
    N_("_Add layers"),
    "RGB*, GRAY*",
    [
        (PF_IMAGE, "image",       "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
        (PF_STRING, "classes",       _("_Json list"), '["1","2","3","4","5","6","7","8","9"]'),
    ],
    [],
    add_layers,
    menu="<Image>/Filters/Tools",
    domain=("gimp20-python", gimp.locale_directory)
    )

main()