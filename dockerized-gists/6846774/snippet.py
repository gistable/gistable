from collections import defaultdict, deque


def find_number_universe(keylog):
    numbers = set()
    for attempt in keylog:
        for num in attempt:
            numbers.add(num)
    return numbers


def connections(attempt):
    l = len(attempt)
    for i in range(l - 1):
        for j in range(i + 1, l):
            yield attempt[i], attempt[j]


def make_number_graph(keylog):
    graph = defaultdict(set)
    for attempt in keylog:
        for a, b in connections(attempt):
            graph[a].add(b)
    return graph


def find_smallest_code(start, graph, number_universe):
    queue = deque([(start, [start])])
    while queue:
        curr, path = queue.popleft()
        neighbours = graph.get(curr, [])
        for neighbour in neighbours:
            new_path = path + [neighbour]
            if not number_universe - set(new_path):
                return len(new_path), new_path
            queue.append((neighbour, new_path))


def solve(keylog):
    number_universe = find_number_universe(keylog)
    graph = make_number_graph(keylog)
    candidates = []
    for vertex in graph:
        code = find_smallest_code(vertex, graph, number_universe)
        if code: candidates.append(code)
    return sorted(candidates[0])


if __name__ == '__main__':
    with open('keylog') as log:
        _, solution = solve(map(str.strip, log.readlines()))
        print 'Solution:', ''.join(solution)
