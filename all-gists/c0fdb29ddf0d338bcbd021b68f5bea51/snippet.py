import bpy
#in armature you have mirror names
#this do the similar but for other objects (outside armatures)

def mirrorname(o):
    if o.name[-5:-4] == "L":
        o.name = o.name[:-5] + "R"
    elif o.name[-5:-4] == "R":
        o.name = o.name[:-5] + "L"
 
for o in bpy.context.selected_objects:
    if o.name[-4:-3] == '.':
        if o.name[-5:-4] == "L" or o.name[-5:-4] == "R":
            mirrorname(o)
