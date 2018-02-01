import sys

def something_reaches_goal(paths, goal_node):
  cheapest_path = sys.maxint
	for path in paths:
		if path["cost"] <= cheapest_path:
			cheapest_path = path["cost"]
	for path in paths:
		if goal_node in path["path"] and cheapest_path == path["cost"]:
			return True
	return False

def get_lowest_cost_path(paths):
	lowest_cost_path = paths[0]
	for path in paths:
		if lowest_cost_path["cost"] > path["cost"]:
			lowest_cost_path = path
	return lowest_cost_path

def get_nodes_and_costs(graph, path):
	last_node = path["path"][-1]
	if not last_node in graph:
		return []
	next_nodes = graph[last_node]
	next_paths = []
	for node in next_nodes:
		if node == last_node:
			continue
		new_path = []
		new_path.extend(path["path"])
		new_path.append(node)
		next_paths.append({"path": new_path, "cost": path["cost"] + next_nodes[node]})
	return next_paths

def get_path_that_reaches_goal(paths, goal_node):
	cheapest_path = sys.maxint
	for path in paths:
		if path["cost"] <= cheapest_path:
			cheapest_path = path["cost"]
	for path in paths:
		if goal_node in path["path"] and cheapest_path == path["cost"]:
			return path
	raise "BAM! Nothing matches!! WTF??"

def find_shortest_path(graph, start_node, goal_node):
	paths = [{'path': [start_node], 'cost': 0}]
	while not something_reaches_goal(paths, goal_node):
		path = get_lowest_cost_path(paths)
		new_paths = get_nodes_and_costs(graph, path)
		paths.extend(new_paths)
		paths.remove(path)
	return get_path_that_reaches_goal(paths, goal_node)