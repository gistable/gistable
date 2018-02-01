import unittest


class Graph(dict):
    def __init__(self, vertex_list, edge_list):
        for v in vertex_list:
            self[v] = set()
        for e in edge_list:
            self.add_edge(e)

    def add_edge(self, edge):
        self[edge[0]].add(edge[1])
        self[edge[1]].add(edge[0])

    def add_vertex(self, vertex):
        self[vertex] = set()

    def delete_edge(self, edge):
        self[edge[0]].remove(edge[1])
        self[edge[1]].remove(edge[0])
        
    def delete_vertex(self, vertex):
        temp_neighbour_set = self[vertex].copy()
        for neighbour_vertex in temp_neighbour_set:
            self.delete_edge((neighbour_vertex, vertex))
        del self[vertex]


class ListGraphTest(unittest.TestCase):

    def test_graph_simple_with_2_vertexes(self):
        g = Graph(['A', 'B'], [('A', 'B')])
        self.assertSetEqual(g['A'], set('B'))
        self.assertSetEqual(g['B'], set('A'))

    def test_graph_full_with_3_vertexes(self):
        edges = [
            ('A', 'B'), ('A', 'C'), ('B', 'C')
        ]
        g = Graph(['A', 'B', 'C'], edges)
        self.assertSetEqual(g['A'], set(['B', 'C']))
        self.assertSetEqual(g['B'], set(['A', 'C']))
        self.assertSetEqual(g['C'], set(['A', 'B']))

    def test_graph_add_vertex_to_existing_graph(self):
        g = Graph(['A', 'B'], [('A', 'B')])
        g.add_vertex('C')
        self.assertSetEqual(g['C'], set())

    def test_graph_add_edge_to_existing_graph(self):
        edges = [
            ('A', 'B'), ('A', 'C')
        ]
        g = Graph(['A', 'B', 'C'], edges)
        g.add_edge(('B', 'C'))

        self.assertSetEqual(g['B'], set(['A', 'C']))
        self.assertSetEqual(g['C'], set(['A', 'B']))

    def test_delete_edge(self):
        edges = [
            ('A', 'B'), ('A', 'C'), ('B', 'C')
        ]
        g = Graph(['A', 'B', 'C'], edges)
        g.delete_edge(('B', 'C'))

        self.assertSetEqual(g['B'], set(['A']))
        self.assertSetEqual(g['C'], set(['A']))

    def test_delete_vertex(self):
        edges = [
            ('A', 'B'), ('A', 'C'), ('B', 'C')
        ]
        g = Graph(['A', 'B', 'C'], edges)
        g.delete_vertex('B')

        self.assertSetEqual(g['A'], set(['C']))
        self.assertSetEqual(g['C'], set(['A']))
