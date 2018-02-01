import bpy
import sys
from mathutils import Vector
import numpy as np

class ConwayGOL_2D:
    def __init__(self, N):
        """
        2D Conway Game of Life
        :param N: grid side size (resulting grid will be a NxN matrix)
        """
        self.N = N
        self.grid = np.random.choice(2, (N,N))
    
    def update(self):
        """
        Update status of the grid
        """
        tmpGrid = self.grid.copy()
        for i in range(self.N):
            for j in range(self.N):
                neighbours = self.grid[max(0, i-1):min(i+2,self.N),max(0, j-1):min(j+2,self.N)].sum()
                neighbours -= self.grid[i, j]
                if self.grid[i, j] == 1:
                    if neighbours > 3 or neighbours < 2:
                        tmpGrid[i, j] = 0
                elif neighbours == 3:
                    tmpGrid[i, j] = 1
        self.grid = tmpGrid

#######################################
#           GENERATORS                #
#######################################
# generate and add an object with given properties to the scene

def suzanne_generator(size, x, y, z):
    bpy.ops.mesh.primitive_monkey_add(
                        radius = size,
                        location = (x*2, y*2, z))

def cube_generator(cube_side, x, y, z):
    bpy.ops.mesh.primitive_cube_add(
                        radius = cube_side,
                        location = (x*2, y*2, z))

def icosphere_generator(size, subdivisions, x, y, z):
    bpy.ops.mesh.primitive_ico_sphere_add(
                        subdivisions = subdivisions,
                        size = size,
                        location = (x*2, y*2, z))


#######################################
#             UPDATERS                #
#######################################
# define behavior for a Blender object based on gol grid value

# Hides object (both view and render)
def object_updater_hide(obj, grid_val, keyframe=True):
    obj.hide = not grid_val
    obj.hide_render = obj.hide
    if keyframe:
        obj.keyframe_insert("hide")
        obj.keyframe_insert("hide_render")

# shrink object when grid values is zero
def object_updater_scale(obj, grid_val, scale_factor=0.8, keyframe=True):
    origin_scale = Vector((1.0, 1.0, 1.0))
    # grid value 1, object should end up with original size
    if grid_val:
        # skip all (keyframing too) if already ok, otherwise set original size
        if obj.scale == origin_scale:
            return
        else:
            obj.scale = origin_scale
    # grid value 0, object should end up scaled
    else:
        # skip all (keyframing too) if already ok, otherwise set scaled size
        if obj.scale == origin_scale*scale_factor:
            return
        else:
            obj.scale = origin_scale*scale_factor
    if keyframe:
        obj.keyframe_insert("scale")

#######################################
#            UTIL METHODS             #
#######################################

# create grid of objects on current scene
# The object generator is responsible for the creation of a single object instance
def create_grid(gol, obj_generator):
    obj_grid = []
    for i in range(gol.N):
        row = []
        for j in range(gol.N):
            obj_generator(i, j, 0)
            row.append(bpy.context.scene.objects.active)
        obj_grid.append(row)
    return obj_grid

# update grid of Blender objects to reflect gol status, then update gol.
def update_grid(obj_grid, gol, obj_updater):
    for i in range(gol.N):
        for j in range(gol.N):
            obj_updater(obj_grid[i][j], gol.grid[i, j])
    gol.update()

# handler called at every frame change
def frame_handler(scene, grid, gol, obj_updater, num_frames_change):
    frame = scene.frame_current
    n = frame % num_frames_change
    if n == 0:
        update_grid(grid, gol, obj_updater)

# delete all objects of current scene (un-hide all hidden ones first)
def delete_all():
    for obj in bpy.data.objects:
        obj.hide = False
        # select/delete only meshes
        obj.select = obj.type == 'MESH'
    bpy.ops.object.delete(use_global=True)

def main(_):
    num_frames_change = 2
    grid_side = 5
    obj_size = 0.7
    subdivisions = 10
    scale_factor=0.2

    #obj_generator = lambda x,y,z:icosphere_generator(obj_size, subdivisions, x, y, z)
    obj_generator = lambda x,y,z:cube_generator(obj_size, x, y, z)
    #obj_updater = object_updater_hide
    obj_updater = lambda obj,grid:object_updater_scale(obj,grid, scale_factor=scale_factor)

    delete_all()
    gol = ConwayGOL_2D(grid_side)
    obj_grid = create_grid(gol, obj_generator)

    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(lambda x : frame_handler(x, obj_grid, gol,
                                                                   obj_updater,
                                                                   num_frames_change))

if __name__ == "__main__":
    main(sys.argv[1:])