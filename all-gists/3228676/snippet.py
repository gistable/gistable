def make_node(p, name=1):
    if p == 0:
        return [name]
    return [name, make_node(p - 1, 10 * name + 0),
                  make_node(p - 1, 10 * name + 1)]


def depth_first(p):
    print(p[0])
    if len(p) == 3:
        depth_first(p[1])
        depth_first(p[2])


def breadth_first(tree):
    yield tree
    for node in breadth_first(tree):
        if len(node) == 1:
            return
        for child in [node[1], node[2]]:
            yield child


tree = make_node(2)
print("depth first")
depth_first(tree)
print("breadth first")
print([x[0] for x in breadth_first(tree)])