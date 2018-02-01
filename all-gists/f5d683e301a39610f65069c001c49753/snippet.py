# inspired by https://openmaya.quora.com/How-to-implement-Voronoi-with-Python-for-Maya

import numpy as np
import random
import math

class MBoundingBox:

    def __init__(self):
        self.xyz = None

    def add_all(self, vectors):
        self.xyz = np.array(vectors)

        x = self.xyz[:,0]
        y = self.xyz[:,1]
        z = self.xyz[:,2]

        self.width = max(x) - min(x)
        self.depth = max(y) - min(y)
        self.height = max(z) - min(z)
        self.center = (
            min(x) + (self.width / 2),
            min(y) + (self.depth / 2),
            min(z) + (self.height / 2)
        )


def cmds_polyCube(width, height, depth): return []
def cmds_move(vector): pass
def cmds_duplicate(something): return []
def cmds_parent(a, b): pass
def cmds_angleBetween(euler, v1, v2): return []
def cmds_polyCut(working_geom, deleteFaces, cutPlaneCenter, cutPlaneRotate): pass
def cmds_polyCloseBorder(working_geom): pass
def cmds_spaceLocator(): return 0,0,0  # some global locator

def voronoi_3d(vps):

    bb = MBoundingBox()
    bb.add_all(vps)

    startCube = cmds_polyCube(width=bb.width*1.2, height=bb.height*1.2, depth=bb.depth*1.2)
    cmds_move(bb.center)  #xyz

    for from_point in vps:
        working_geom = cmds_duplicate(startCube[0])
        for to_point in vps:
            if from_point != to_point:
                
                locator = cmds_spaceLocator()
                cmds_move(from_point)
                cmds_parent(locator, working_geom)
                
                center_point = [(e1 + e2) / 2 for (e1, e2) in zip(to_point, from_point)]
                n = [(e1 - e2) for (e1, e2) in zip(from_point, to_point)]
                
                es = cmds_angleBetween(euler=True, v1=[0, 0, 1], v2=n)

                cmds_polyCut(working_geom, deleteFaces=True, cutPlaneCenter=center_point, cutPlaneRotate=es)
                cmds_polyCloseBorder(working_geom)

    cmds_delete(startCube)

voronoi_3d()