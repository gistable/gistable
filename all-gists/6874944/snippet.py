# Copyright (c) 2013, Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ============================================================================
#
# This script imports a Cinema 4D scenefile and disables all deformers,
# generators and expressions. This is useful if the scene was saved at a state
# it is unrecoverable because of an issue while scripting (eg. saved the scene
# before a Python tag was executed, but now that Python tag always runs in an
# infinite loop).
#
# Use this script to recover your scene!

import os
import c4d

options = {
    'turn_off_objects': True,
    'turn_off_displacement_channels': True,
}

def disable(op):
    info = op.GetInfo()
    if info & c4d.OBJECT_GENERATOR or info & c4d.OBJECT_DEFORMER:
        op.SetDeformMode(False)

    for tag in op.GetTags():
        info = tag.GetInfo()
        bc = tag.GetDataInstance()
        if info & c4d.TAG_EXPRESSION and bc.FindIndex(c4d.EXPRESSION_ENABLE) >= 0:
            tag[c4d.EXPRESSION_ENABLE] = False

    for child in op.GetChildren():
        disable(child)

def main():
    filename = c4d.storage.LoadDialog(c4d.FILESELECTTYPE_SCENES)
    if not filename or not os.path.isfile(filename):
        return

    flags = c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS | c4d.SCENEFILTER_DIALOGSALLOWED | \
            c4d.SCENEFILTER_PROGRESSALLOWED | c4d.SCENEFILTER_NONEWMARKERS | c4d.SCENEFILTER_SAVECACHES
    doc = c4d.documents.LoadDocument(filename, flags)
    if not doc:
        c4d.gui.MessageDialog("The document could not be loaded.")
        return

    # Disable all objects in the scene.
    if options['turn_off_objects']:
        for op in doc.GetObjects():
            disable(op)

    # Disable the displacement channel of each material.
    if options['turn_off_displacement_channels']:
        for mat in doc.GetMaterials():
            print mat.GetName()
            mat[c4d.MATERIAL_USE_DISPLACEMENT] = False

    c4d.documents.InsertBaseDocument(doc)
    c4d.documents.SetActiveDocument(doc)
    c4d.EventAdd()

main()

