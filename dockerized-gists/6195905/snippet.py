class Node:
    def __init__(self,value=None,kids=[]):
        self.value = value
        self.kids = kids


def rdfs(n, previsit, postvisit):
    '''Recursive depth-first traversal'''
    previsit(n)
    for k in n.kids:
        rdfs(k, previsit, postvisit)
    postvisit(n)


def dfs(startnode, previsit, postvisit):
    '''Non-recursive depth-first traversal'''
    stack = [[startnode,True]]
    while len(stack) > 0:
        (n,down) = stack.pop()
        if down:
            previsit(n)
            stack.append([n,False])
            stack.extend([[k,True] for k in reversed(n.kids)])
        else:
            postvisit(n)


def demo():
    root = Node(1,[
        Node(10,[
            Node(100),
            Node(101),
            Node(102),
        ]),
        Node(20,[
            Node(200,[
                Node(2000),
                Node(2001),
                Node(2002),
            ]),
            Node(201),
        ]),
    ])

    global depth  # Don't see why previsit/postvisit don't pick up depth in a closure.
    depth=""
    def previsit(n):
        global depth
        print "%s%d \\" % (depth,n.value)
        depth += " "
        if len(depth) > 20:
            raise RuntimeError("Probable Stack Overflow")
    def postvisit(n):
        global depth
        depth = depth[1:]
        print "%s%d /" % (depth,n.value)
   

    print "\nrecursive:"
    rdfs(root, previsit, postvisit)
    print "\nnon-recursive:"
    dfs(root, previsit, postvisit)
