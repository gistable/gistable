import hou
sel_nodes = hou.selectedNodes()

if len(sel_nodes) == 0:
    hou.ui.displayMessage('Please select a node')
    
    
for node in sel_nodes:
    pos = node.position()
    name = node.name()
    parent = node.parent()
    null = parent.createNode('null', 'OUT_' + str(name))
    null.setNextInput(node)
    null.setPosition(pos)
    null.move([0, -1])
    color = hou.Color((1,0,0))
    null.setColor(color)
    
    null.setDisplayFlag(True)
    