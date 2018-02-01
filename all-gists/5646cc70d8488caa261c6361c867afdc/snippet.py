import threading as th
from copy import deepcopy


class Node:
    def __init__(self, parent=None, state=[]):
        self.parent = parent
        self.generator_lock = th.Lock()
        self.generator = self._child_gen()
        self.state = state

    def _child_gen(self):
        for i in range(1, 4):
            state = deepcopy(self.state) + [i]
            yield Node(self, state)

    def next_child(self):
        with self.generator_lock:
            return next(self.generator, None)

    def is_leaf(self):
        return len(self.state) >= 10

    def __repr__(self):
        return '<Node state="{}">'.format(self.state)


class Worker:
    def __init__(self, id, searcher):
        self.searcher = searcher  # type: Searcher
        self.id = id

    def __call__(self):
        print("start worker: {}".format(self.id))
        while not self.searcher.is_end():
            self._run()
        print("end worker: {}".format(self.id))

    def _run(self):
        node = self.searcher.get_last_node()

        if node is None:
            return

        if node.is_leaf():
            self.searcher.remove_node(node)
            self.searcher.add_result(node)
            return

        bounds = self.searcher.get_bounds()
        if not self.satisfy_bounds(node, bounds):
            self.searcher.remove_node(node)
            return

        child = node.next_child()
        if child is None:
            self.searcher.remove_node(node)
        else:
            self.searcher.add_node(child)

    def satisfy_bounds(self, node, bound):
        return True


class Searcher:
    def __init__(self):
        self.root_node = Node()
        self.nodes = [self.root_node]  # TODO: priority queue
        self.nodes_lock = th.Lock()

        self._is_end = False
        self.workers = [
            Worker(i, self) for i in range(8)
            ]

        self.results = set()
        self.results_lock = th.Lock()

        self.bounds = [None, None]
        self.bounds_lock = th.Lock()
        self.threads = []

    def run(self):
        self.threads = [
            th.Thread(target=w, name="thread:{}".format(idx))
            for idx, w in enumerate(self.workers)
            ]
        for t in self.threads:
            t.start()
        for t in self.threads:
            t.join()

    def get_last_node(self):
        with self.nodes_lock:
            if self.nodes:
                return self.nodes[-1]
            else:
                self._is_end = True
                return None

    def add_node(self, node):
        with self.nodes_lock:
            self.nodes.append(node)

    def remove_node(self, node):
        with self.nodes_lock:
            if node in self.nodes:
                self.nodes.remove(node)

    def is_end(self):
        return self._is_end

    def check_end(self):
        with self.nodes_lock:
            self._is_end = len(self.nodes) == 0

    def add_result(self, node):
        with self.results_lock:
            self.results.add(node)

    def get_bounds(self):
        with self.bounds_lock:
            return deepcopy(self.bounds)


def main():
    s = Searcher()
    s.run()
    print(len(s.results))
    assert len(s.results) == 3 ** 10


if __name__ == '__main__':
    main()
