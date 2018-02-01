class Node:
    left = right = None

def node_only(iterable_nodes):
    return filter(bool, iterable_nodes)

def iter_layer(layer):
    layer = node_only(layer)
    while layer:
        yield layer
        layer = node_only(node.left for node in layer) + node_only(node.right for node in layer)

def tree_width(root):
    return max(map(len, iter_layer([root])) or [0])