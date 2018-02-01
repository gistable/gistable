import soptoolutils

selection = None
if type(kwargs['pane']) is hou.SceneViewer:
    viewer = kwargs['pane']
    selection = viewer.selectGeometry(geometry_types=(hou.geometryType.Primitives, hou.geometryType.Edges,))


n = soptoolutils.genericTool(kwargs, '$HDA_NAME')

if selection is not None:
    selstring = ''
    for sel in selection.selectionStrings():
        selstring += sel
        selstring += ' '
    
    if len(selstring) != 0:
        geotype = selection.geometryType()
        if geotype == hou.geometryType.Edges:
            n.setParms({'group':selstring, 'grouptype':'edges'})
        if geotype == hou.geometryType.Primitives:
            n.setParms({'group':selstring, 'grouptype':'prims'})