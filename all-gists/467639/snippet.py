from StringIO import StringIO

tree1 = ("Root", ("Child 1", ("Child 2", None)))
get_label1 = lambda x: x[0]
def get_children1(node):
    if node[1] is not None:
        yield node[1]

class Node(object):
    
    def __init__(self, name, parent=None):
        self.name = name
        self.children = []
        if parent:
            parent.children.append(self)
    
    def get_label(self):
        return self.name
    
    def get_children(self):
        return self.children

tree2 = Node('A')
_b = Node('B', tree2)
_c = Node('C', tree2)
_d = Node('D', _b)
_e = Node('E', _b)

def lead_in(out, level, horiz):
    for n in xrange(level):
        out.write('|')
        if n == level - 1 and horiz:
            out.write('-')
        else:
            out.write(' ')

def tree(root, get_label, get_children):
    def internal(out, node, level):
        lead_in(out, level, False)
        out.write('\n')
        lead_in(out, level, True)
        out.write(get_label(node))
        out.write('\n')
        for child in get_children(node):
            internal(out, child, level+1)
    outf = StringIO()
    internal(outf, root, 0)
    return outf.getvalue()

print tree(tree1, get_label1, get_children1)
print
print tree(tree2, Node.get_label, Node.get_children)