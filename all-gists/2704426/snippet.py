#!/usr/bin/env python3

import sys
import array
import math
import random
import os.path
import win32com.client

def get_catia():
    catapp = win32com.client.Dispatch("CATIA.Application")
    return catapp

def mkcube(cat, fname):
    part1 = cat.Documents.Add("Part").Part
    ad = cat.ActiveDocument
    part1 = ad.Part
    bod = part1.MainBody
    bod.Name="cube"

    cubeWidth = 10

    skts = bod.Sketches
    xyPlane = part1.CreateReferenceFromGeometry(part1.OriginElements.PlaneXY)
    shapeFact = part1.Shapefactory

    ms = skts.Add(xyPlane)
    ms.Name="Cube Outline"

    fact = ms.OpenEdition()
    fact.CreateLine(-cubeWidth, -cubeWidth,  cubeWidth, -cubeWidth)
    fact.CreateLine(cubeWidth, -cubeWidth,  cubeWidth, cubeWidth)
    fact.CreateLine(cubeWidth, cubeWidth,  -cubeWidth, cubeWidth)
    fact.CreateLine(-cubeWidth, cubeWidth,  -cubeWidth, -cubeWidth)
    ms.CloseEdition()
    mpad = shapeFact.AddNewPad(ms, cubeWidth)
    mpad.Name = "Python Pad"
    mpad.SecondLimit.Dimension.Value = cubeWidth

    sel = ad.Selection
    sel.Add(mpad)

    vp = sel.VisProperties
    vp.SetRealColor(random.randint(0,255),random.randint(0,255),random.randint(0,255), 0)
    part1.Update()
    
    hbs = part1.HybridBodies
    hBod = hbs.Add()
    hsf = part1.HybridShapeFactory

    sel.Search("Topology.Face,sel")
    faceCnt = sel.Count

    print("Found",faceCnt,"faces")
    hsd = hsf.AddNewDirectionByCoord(0,0,1)
    faces=[]
    for i in range(1, faceCnt+1):
        faces.append(sel.Item2(i))

    for fac in faces:
        sel.Clear()
        sel.Add(fac.Value)

        vp = sel.VisProperties
        vp.SetRealColor(random.randint(63,191), random.randint(63, 191), random.randint(63, 191), 0)

    sel.Clear()
    part1.Update()
    ad.SaveAs(fname)
    ad.Close()

def x(t):
    return 40.0*math.cos(t)

def y(t):
    return 40.0*math.sin(t)

def z(t):
    return 20*t

def mkhelix(cat, cube_name, fname):
    prod1 = cat.Documents.Add("Product").Product
    ad = cat.ActiveDocument
    prod1 = ad.Product
    prod_list = prod1.Products
    cn_list = [cube_name]
    num_cubes = 200
    
    min_t = -math.pi*10
    max_t = math.pi*10
    t = min_t
    dt = (max_t-min_t)/(num_cubes-1)

    for i in range(num_cubes):
        curName = 'Part1.{}'.format(i+1)
        prod_list.AddComponentsFromFiles(cn_list, "All")
        itm = prod_list.Item(curName)
        mvr = itm.Move
        mvr = mvr.MovableObject
        trans = [1.0,0.0,0.0,
                 0.0,1.0,0.0,
                 0.0,0.0,1.0,
                 x(t), y(t), z(t)]
        mvr.Apply(trans)
        trans = [math.cos(t),-math.sin(t),0.0,
                 math.sin(t),math.cos(t),0.0,
                 0.0,0.0,1.0,
                 0.0,0.0,0.0]
        mvr.Apply(trans)
        t += dt
                 
    ad.SaveAs(fname)
    ad.Close()
    
def main(args):
    cat = get_catia()
    cube_fname = os.path.abspath(args[0])
    helix_fname = os.path.abspath(args[1])
    try:
        os.unlink(cube_fname)
    except:
        pass
    try:
        os.unlink(helix_fname)
    except:
        pass
    mkcube(cat, cube_fname)
    mkhelix(cat, cube_fname, helix_fname)


if __name__=='__main__':
    main(sys.argv[1:])
