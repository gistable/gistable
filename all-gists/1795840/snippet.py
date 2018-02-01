import maya.OpenMaya as OpenMaya
from maya.OpenMayaFX import MFnParticleSystem
from maya.OpenMaya import MPoint, MPointOnMesh, MVector, MFloatPoint
import maya.cmds as cmds


import time
from operator import itemgetter


step = 100

def fillOptimized():

    sel = cmds.ls(sl=1)
    if not sel:
        print "no mesh selected !"
        return

    obj=sel[0]
    objList = OpenMaya.MSelectionList()
    objList.add(obj)
    path = OpenMaya.MDagPath()
    objList.getDagPath(0,path)
    path.extendToShape()

    closest = OpenMaya.MMeshIntersector()
    closest.create(path.node(),path.inclusiveMatrix())

    try:
        cmds.particleFill(rs=step,maxX=1,maxY=1,maxZ=1,minX=0,minY=0,minZ=0,pd=1.0,cp=True)
    except RuntimeError:
        pass
    
    part = cmds.ls(sl=1)[0]
    partShape = cmds.listRelatives(part,shapes=1)[0]

    nplist  = OpenMaya.MSelectionList()
    nplist.add(partShape)

    npobj   = OpenMaya.MObject()
    nplist.getDependNode(0,npobj)

    npnode  = OpenMaya.MFnDependencyNode(npobj)
    nplug   = npnode.findPlug("position")
    nhdl    = nplug.asMDataHandle()
    ndata   = OpenMaya.MFnVectorArrayData(nhdl.data())

    radii    = OpenMaya.MDoubleArray()
    points   = OpenMaya.MVectorArray() 
    points.copy(ndata.array())

    cmds.delete(part)

    mpom = MPointOnMesh()
    radii_index = {}

    for p in xrange(points.length()):
        vec = points[p]
        point = MPoint(vec)
        closest.getClosestPoint(point, mpom)
        closestPoint = mpom.getPoint()
        radius = point.distanceTo(MPoint(closestPoint))
        radii_index[p] = (vec, point, radius) 


    radii_sorted = sorted(radii_index.itervalues(), key=itemgetter(2), reverse=True)
    newPoints = OpenMaya.MVectorArray()
    newRadii  = OpenMaya.MDoubleArray()
    
    pointsRemain = lambda: len(radii_sorted)

    while pointsRemain():
        print "%s problem points still left..." % pointsRemain()

        vec, p, radius = radii_sorted.pop(0)

        newPoints.append(vec)
        newRadii.append(radius*1.2)

        for i in reversed(xrange(pointsRemain())):

            vec2, p2, otherRadius = radii_sorted[i]

            if p.distanceTo(p2) < (otherRadius + radius):
                del radii_sorted[i]


    #note: the default nParticle creation mode should be set to "points"
            
    part    = cmds.nParticle()[1]
    plist   = OpenMaya.MSelectionList()
    plist.add(part)
    
    newNPObj = OpenMaya.MObject()
    dagPath = OpenMaya.MDagPath()
    plist.getDependNode(0,newNPObj)
    plist.getDagPath(0, dagPath)
    name = dagPath.fullPathName()
    
    newNPNode   = OpenMaya.MFnDependencyNode(newNPObj)
    newPosPlug  = newNPNode.findPlug("position")
    newNPHdl    = newPosPlug.asMDataHandle()
    newposdata  = OpenMaya.MFnVectorArrayData(newNPHdl.data())
    newposdata.set(newPoints)
    newPosPlug.setMObject(newposdata.object())
    
    prt = newNPNode.findPlug("particleRenderType")
    prt.setInt(4)
    
    isg = newNPNode.findPlug("ignoreSolverGravity")
    isg.setInt(1)
    
    tattr   = OpenMaya.MFnTypedAttribute()
    rpp     = tattr.create("radiusPP","rpp",OpenMaya.MFnData.kDoubleArray)
    newNPNode.addAttribute(rpp)
    # rppPlug = newNPNode.findPlug("radiusPP")
    # rpphdl  = rppPlug.asMDataHandle()
    # rppdata = OpenMaya.MFnDoubleArrayData(rpphdl.data())
    # rppdata.set(newRadii)
    # rppPlug.setMObject(rppdata.object())

    fnParticleSys = MFnParticleSystem(newNPObj)
    fnParticleSys.setPerParticleAttribute("radiusPP", newRadii)

        
    print "finished."
   