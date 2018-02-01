# for http://blender.stackexchange.com/questions/32787/example-of-creating-and-setting-a-cycles-material-node-with-the-python-api

import bpy

# get the material
mat = bpy.data.materials['Material']
# get the nodes
nodes = mat.node_tree.nodes

# clear all nodes to start clean
for node in nodes:
    nodes.remove(node)

# create emission node
node_ani = nodes.new(type='ShaderNodeBsdfAnisotropic')
node_ani.inputs[0].default_value = (0,1,0,1)  # green RGBA
node_ani.inputs[1].default_value = 5.0 # strength
node_ani.location = 0,0

# create output node
node_output = nodes.new(type='ShaderNodeOutputMaterial')   
node_output.location = 400,0

# link nodes
links = mat.node_tree.links
link = links.new(node_ani.outputs[0], node_output.inputs[0])