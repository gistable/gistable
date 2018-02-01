import pymel.core as pm
import re

def parseVtxIdx(idxList):
    """convert vertex index list from strings to indexes.
    idxList : [u'vtx[1]', u'vtx[3]', u'vtx[6]', u'vtx[8]', u'vtx[12:13]']
    return : [1,3,6,8,12,13]
    """

    parseIdxList = []

    for idxName in idxList:
        match = re.search(r'\[.+\]', idxName)
        if match:
            content = match.group()[1:-1]
            if ':' in content:
                tokens = content.split(':')
                startTok = int(tokens[0])
                endTok = int(tokens[1])

                for rangeIdx in range(startTok, endTok + 1):
                    parseIdxList.append(rangeIdx)

            else:
                parseIdxList.append(int(content))

    return parseIdxList


def recoverMesh(bsNode, weightIdx):
    """recover the blendshape target from blendshape target attribute.
    usually blendshape targets are deleted after editing to save disk space and
    save / load / calculation time.
    but if you need to re-edit them later, there's no option in current maya tool
    to do so.
    """
    bsNode = pm.PyNode(bsNode)

    bsNode.envelope.set(0)

    aliasName = pm.aliasAttr(bsNode.weight[weightIdx], query=True)

    finalMeshes = pm.listFuture(bsNode,type="mesh")
    
    finalParent = None
    newParent = None

    # it is a group blendshapes
    if len(finalMeshes) > 1:
        finalParent = finalMeshes[0].getParent()

    if finalParent:
        newParent = pm.createNode('transform')
        pm.rename(newParent, aliasName)
        pm.delete(pm.parentConstraint(finalParent, newParent, mo=0))

    for finalIdx, finalMesh in enumerate(finalMeshes):
        newMesh = pm.duplicate(finalMesh)[0]
        newMeshShape = newMesh.getShape()

        vtxDeltaList = bsNode.inputTarget[finalIdx].inputTargetGroup[weightIdx].inputTargetItem[6000].inputPointsTarget.get()
        vtxIdxList = bsNode.inputTarget[finalIdx].inputTargetGroup[weightIdx].inputTargetItem[6000].inputComponentsTarget.get()

        # get bs shape
        if vtxIdxList:
            # need to convert [u'vtx[8]', u'vtx[11:13]] to [8,11,12,13]
            singleIdxList = parseVtxIdx(vtxIdxList)

            for vtxIdx,moveAmount in zip(singleIdxList,vtxDeltaList):
                pm.move('%s.vtx[%d]'%(newMesh.name(),vtxIdx),moveAmount,r=1)

        newMeshShape.worldMesh[0] >> bsNode.inputTarget[finalIdx].inputTargetGroup[weightIdx].inputTargetItem[6000].inputGeomTarget

        if newParent:
            pm.parent(newMesh,newParent)
            pm.rename(newMesh,finalMesh.name())

        else:
            pm.rename(newMesh,aliasName)
            if newMesh.getParent():
                pm.parent(newMesh,world=1)

    bsNode.envelope.set(1)

    if newParent:
        return newParent
    elif newMesh:
        return newMesh

recoverMesh("blendShape1",0)