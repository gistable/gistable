import pymel.core as pm
import maya.cmds as cmds


cmds.hyperShade(o="lambert1")

cmds.ConvertSelectionToVertices()

#shrink selected region to avoid border verticies
cmds.ShrinkPolygonSelectionRegion()


#list selected verticies, sl for selected, fl for ungrouped
print pm.ls(sl=True,fl=True,l=True)
