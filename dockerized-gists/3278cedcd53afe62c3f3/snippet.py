
import graphviz as gv

g1 = gv.Graph(format='svg')
g1.node('A')
g1.node('B')
g1.edge('A', 'B')

print(g1.source)

filename = g1.render(filename='img/g1')
print(filename)

g2 = gv.Digraph(format='svg')
g2.node('A')
g2.node('B')
g2.edge('A', 'B')
g2.render('img/g2')

import functools
graph = functools.partial(gv.Graph, format='svg')
digraph = functools.partial(gv.Digraph, format='svg')

g3 = graph()

nodes = ['A', 'B', ('C', {})]

edges = [
    ('A', 'B'),
    ('B', 'C'),
    (('A', 'C'), {}),
]


def add_nodes(graph, nodes):
    for n in nodes:
        if isinstance(n, tuple):
            graph.node(n[0], **n[1])
        else:
            graph.node(n)
    return graph


def add_edges(graph, edges):
    for e in edges:
        if isinstance(e[0], tuple):
            graph.edge(*e[0], **e[1])
        else:
            graph.edge(*e)
    return graph

add_edges(
    add_nodes(digraph(), ['A', 'B', 'C']),
    [('A', 'B'), ('A', 'C'), ('B', 'C')]
).render('img/g4')

add_edges(
    add_nodes(digraph(), [
        ('A', {'label': 'Node A'}),
        ('B', {'label': 'Node B'}),
        'C'
    ]),
    [
        (('A', 'B'), {'label': 'Edge 1'}),
        (('A', 'C'), {'label': 'Edge 2'}),
        ('B', 'C')
    ]
).render('img/g5')

g6 = add_edges(
    add_nodes(digraph(), [
        ('A', {'label': 'Node A'}),
        ('B', {'label': 'Node B'}),
        'C'
    ]),
    [
        (('A', 'B'), {'label': 'Edge 1'}),
        (('A', 'C'), {'label': 'Edge 2'}),
        ('B', 'C')
    ]
)

styles = {
    'graph': {
        'label': 'A Fancy Graph',
        'fontsize': '16',
        'fontcolor': 'white',
        'bgcolor': '#333333',
        'rankdir': 'BT',
    },
    'nodes': {
        'fontname': 'Helvetica',
        'shape': 'hexagon',
        'fontcolor': 'white',
        'color': 'white',
        'style': 'filled',
        'fillcolor': '#006699',
    },
    'edges': {
        'style': 'dashed',
        'color': 'white',
        'arrowhead': 'open',
        'fontname': 'Courier',
        'fontsize': '12',
        'fontcolor': 'white',
    }
}


def apply_styles(graph, styles):
    graph.graph_attr.update(
        ('graph' in styles and styles['graph']) or {}
    )
    graph.node_attr.update(
        ('nodes' in styles and styles['nodes']) or {}
    )
    graph.edge_attr.update(
        ('edges' in styles and styles['edges']) or {}
    )
    return graph

g6 = apply_styles(g6, styles)
g6.render('img/g6')

g7 = add_edges(
    add_nodes(digraph(), [
        ('A', {'label': 'Node A'}),
        ('B', {'label': 'Node B'}),
        'C'
    ]),
    [
        (('A', 'B'), {'label': 'Edge 1'}),
        (('A', 'C'), {'label': 'Edge 2'}),
        ('B', 'C')
    ]
)

g8 = apply_styles(
    add_edges(
        add_nodes(digraph(), [
            ('D', {'label': 'Node D'}),
            ('E', {'label': 'Node E'}),
            'F'
        ]),
        [
            (('D', 'E'), {'label': 'Edge 3'}),
            (('D', 'F'), {'label': 'Edge 4'}),
            ('E', 'F')
        ]
    ),
    {
        'nodes': {
            'shape': 'square',
            'style': 'filled',
            'fillcolor': '#cccccc',
        }
    }
)

g7.subgraph(g8)
g7.edge('B', 'E', color='red', weight='2')

g7.render('img/g7')