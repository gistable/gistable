"""

Physics simulation with PyODE followed by a (basic) rendering with Vapory
See the result here: http://i.imgur.com/TdhxwGz.gifv

Zulko 2014
This script is placed in the Public Domain (Licence Creative Commons 0)

"""

# =============== FIRST PART : SIMULATION WITH PyODE

import ode

lx, ly, lz, density = 1.0, 1.0, 1.0, 1.0
world = ode.World()
world.setGravity( (0,-9.81,0) )

world.setCFM(1E-6)
space = ode.Space()
contactgroup = ode.JointGroup()
geoms = []


def near_callback(args, geom1, geom2):
    """Callback function for the collide() method below.
    This function checks if the given geoms do collide and
    creates contact joints if they do.
    """
    contacts = ode.collide(geom1, geom2)
    world,contactgroup = args
    for c in contacts:
        c.setBounce(0.01)
        c.setMu(60000)
        j = ode.ContactJoint(world, contactgroup, c)
        j.attach(geom1.getBody(), geom2.getBody())


def new_cube(xyz):
    """ Creates a new PyODE cude at position (x,y,z) """
    body = ode.Body(world)
    M = ode.Mass()
    M.setBox(density, lx, ly, lz)
    body.setMass(M)
    body.shape = "box"
    body.boxsize = (lx, ly, lz)
    body.setPosition(xyz)
    geom = ode.GeomBox(space, lengths=body.boxsize)
    geom.setBody(body)
    geoms.append(geom) # avoids that geom gets trashed
    return body

# The objects of the scene:

floor = ode.GeomPlane(space, (0,1,0), 0)
cubes = [new_cube(xyz) for xyz in
         [(0.5,3,0.5),(0.5,4,0),(0,5,0),(-0.5,6,0),
          (-0.5,7,-0.5),(0,8,0.5)]]

# Start the simulation !

t = 0.0
dt = 0.005
duration = 4.0
trajectories = []
while t<duration:
    trajectories.append([(c.getPosition(), c.getRotation())
                         for c in cubes])
    space.collide((world,contactgroup), near_callback)
    world.step(dt)
    contactgroup.empty()
    t+=dt


# =============== SECOND PART : RENDERING WITH VAPORY

from moviepy.editor import VideoClip, ipython_display
from vapory import *

light = LightSource( [10,10,10], 'color', [3,3,3],
                     'parallel', 'point_at', [0, 0, 0])

ground = Plane([0,1,0],0, Texture('Rosewood'))

def vapory_box(xyz, R):
    """ Draws a box with at the given position and rotation"""
    return Box([-lx/2, -ly/2, -lz/2], [lx/2, ly/2, lz/2],
                Texture('T_Ruby_Glass'), Interior('ior',4),
                'matrix', R+xyz)

def make_frame(t):
    """ Returns the image of the scene rendered at time t """
    boxes = [vapory_box(position, rotation)
             for (position, rotation) in trajectories[int(t/dt)]]
    scene = Scene( Camera("location", [0,3,-4], "look_at", [0,0,0]),
                   [light, ground, Background("White")] + boxes,
                   included=["colors.inc", "textures.inc", "glass.inc"])
    return scene.render(height=300, width=400, antialiasing=0.0001)

clip = VideoClip(make_frame, duration=duration)
clip.write_videofile("pyODE.avi", codec='png', fps=20)  # lossless format