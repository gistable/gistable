#So far, my Python scripts for Blender are segmented into
#a "create the objects" script,
#and a "describe their motion over time" script.
#The "motion.py" script must be run and have the "register"
#checkbox clicked on it in the Blender "Text Editor" window,
#so that it will add the driver every time the file loads.
#To use the creation script, you must already have a group named
#"Dot" defined with some renderable mesh in it so that the
#"creation.py" script can create instances of that group.
#My "Dot" group has a 5 level subdivided Icosphere in it.

#This animation is designed to loop perfectly in 1 second worth
#of frames, based on your Frame Rate in your render settings.

#You should also probably have the checkbox turned on for:
#    "User Preferences -> File -> Auto Run Python Scripts"

#Steps to reproduce:
# * Open Blender. In your render settings, pick an a Frame Rate, and set your "End Frame" to that same number.
# * Make a mesh object. Group it. Name the group "Dot". Move it to another layer which is not visible.
# * Get/Make/Show a "Text Editor" window type.
# * Make a new script. Name it "motion.py". Put the below contents into there.
# ***** Click the "register" checkbox in the header of that window. Click the "Run Script" button.
# * Make a new script. Name it "creation.py". Put the apropriate contents into there.
# ***** Click the "Run Script" button.
# * In the 3D view, press alt-a and it animates or something. I hope.

################################START OF motion.py################################
import bpy
import math

pi = math.pi
tau = pi * 2

def get_time():
    return (bpy.context.scene.frame_current / bpy.context.scene.render.fps)

def move_dots(name, n, radius, i):
    item = bpy.data.objects[name]
    frac = 1 / n
    offset = pi * 0.5
    r_frac = tau * frac
    time = get_time()
    time_offset = frac * i
    angle = r_frac * i + offset
    item.location[0] = math.cos(angle + time * r_frac) * radius
    item.location[1] = math.sin(angle + time * r_frac) * radius
    return 0 #math.sin(angle)

bpy.app.driver_namespace['move_dots'] = move_dots
################################END OF motion.py################################

################################START OF creation.py################################
import bpy
import math

pi = math.pi
tau = pi * 2

def create_ring(n, radius):
    frac = 1 / n
    r_frac = tau * frac
    scale = 0.05
    offset = pi * 0.5
    item_num = 0
    
    for i in range(0, n):
        x = math.cos(r_frac * i + offset) * radius
        y = math.sin(r_frac * i + offset) * radius
        bpy.ops.object.group_instance_add(
            group='Dot',   
            location=(x, y, 0),
        )
        item = bpy.context.active_object
        item.name = 'item_' + str(radius) + '_' + str(n) + '_' + str(i)
        item.scale = [scale, scale, scale]
        driver = item.driver_add('location', 2).driver
        driver.expression = (
            'move_dots('
            + '"' + item.name + '"'
            + ', ' + str(n)
            + ', ' + str(radius)
            + ', ' + str(i)
            + ')'
        )

for i in range(2, 28):
    create_ring(i, (i - 1) * 0.1)

################################END OF creation.py################################
