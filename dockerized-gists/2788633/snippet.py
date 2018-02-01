# coding: utf-8
import os
import pydot

# sample
"""
import tree

class Dummy:
    def __init__(self, i):
        self.i = i
    def __nodeid__(self):
        return str(self.i) + str(id(self))
    def __nodetext__(self):
        return str(self.i)
    def __nodeattr__(self):
        return {
            'id': id(self),
            'sqr': self.i**2,
        }
    def __nodeext__(self, node):
        import random
        if random.random() <= .5:
            node.set_color('red')
        if random.random() <= .5:
            node.set_style('filled')
            node.set_fillcolor('gray')
    def __iter__(self):
        if self.i < 3:
            for j in range(self.i, 3):
                yield Dummy(self.i + 1)

root = Dummy(0)

tree.write(root, 'out.png')
"""

# define
# - __nodetext__()
# - __nodeid__() (optional)
# - __nodeattr__() (optional)
# - __nodeext__() (optional)
# overload
# - __iter__()

def walk(root, graph):
    node = pydot.Node(getnodeid(root), label=root.__nodetext__())
    if hasattr(root, '__nodeattr__'):
        node.set_shape('record')
        d = root.__nodeattr__()
        
        lbl = '{%s|{{%s}|{%s}}}' % (
            root.__nodetext__()
            , '|'.join(k for k in d)
            , '|'.join(unicode(d[k]) for k in d)
            )
        node.set_label(lbl)
    if hasattr(root, '__nodeext__'):
        root.__nodeext__(node)
    graph.add_node(node)
    for child in root:
        edge = pydot.Edge(getnodeid(root), getnodeid(child))
        graph.add_edge(edge)
        walk(child, graph)

def getnodeid(node):
    if hasattr(node, '__nodeid__'):
        return node.__nodeid__()
    else:
        return node.__nodetext__()

#def show(root, title='', command=None):
#    import Image # require PIL library
#    g = build(root, path, title)
#    img = Image.open(path)
#    if command is None:
#        img.show()
#    else:
#        img.show(command = command)
    
def write(root, path, title='title'):
    graph = pydot.Dot(title, graph_type='digraph')
    walk(root, graph)

    ext = os.path.splitext(path)[1]
    format = 'raw' if ext[1:] == '' else ext[1:]
    graph.write(path, prog='dot', format=format)