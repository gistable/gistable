# @rosensteinn #c4dpytask Remove all empty texture tags on the Scene?
# Share it if you have a solution!

import c4d

def iter_hierarchy(op):
    # Iterate over each tag of the current object.
    for tag in op.GetTags():
        
        # Check if the tag is a texture tag, and if it is, if it has
        # _no_ material in its link field.
        if tag.CheckType(c4d.Ttexture) and not tag[c4d.TEXTURETAG_MATERIAL]:
            
            # Ok, there is not material in the texture tag, we can remove
            # if from the object. We need to tell the document that we
            # are about to remove the tag to make the complete script
            # undo-able.
            doc.AddUndo(c4d.UNDOTYPE_DELETE, tag)
            tag.Remove()

    # Iterate over each child of the current object and repeate
    # this process.
    for child in op.GetChildren():
        iter_hierarchy(child)

def main():
    # Initiate the process of checking for unused texture tags for
    # all objects in the top-hierarchy level.
    for op in doc.GetObjects():
        iter_hierarchy(op)
        
    # Update the Cinema 4D UI.
    c4d.EventAdd()

main()