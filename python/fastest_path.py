import math
from constants import NUM_ROWS, NUM_COLS, START_POS, GOAL_POS, Cell
from utils import print_map, timeit
from map_descriptor import generate_map
import graphics

@timeit
def fastest_path(map, source, dest, waypoint=None):
	"""
	Calculates the fastest path from the source to the destination, possibly with a waypoint.

	Adds virtual boundaries to the map, computes the visibility graph and performs A* search to find the fastest path. The fastest path consists of a list of positions to move directly between to reach the execute the fastest path.

	:param map: 2D list of Cell objects
	:param source: Position of source
	:param dest: Position of destination
	:param waypoint: Position of waypoint (if applicable)
	:return: steps
	"""
	map_virtual = add_virtual_boundaries(map)

	extra_nodes = [source, dest]
	if waypoint:
		extra_nodes.append(waypoint)

	nodes, edges, weights = create_visibility_graph(map_virtual, extra_nodes)
	source_node = nodes.index(source)
	dest_node = nodes.index(dest)

	if waypoint:
		waypoint_node = nodes.index(waypoint)

		steps0 = compute_steps(nodes, edges, weights, source_node, waypoint_node)
		steps1 = compute_steps(nodes, edges, weights, waypoint_node, dest_node)

		if steps0 == None or steps1 == None:
			return None

		combined_steps = steps0 + steps1[1:]
		return smoothen_steps(combined_steps)

	else:
		steps = compute_steps(nodes, edges, weights, source_node, dest_node)
		return smoothen_steps(steps)

def add_virtual_boundaries(map_real):
	"""
	Adds virtual boundaries to the map from the arena exploration.

	Treats unexplored cells as well as the virtual boundaries around walls, unexplored cell and obstacles as obstacles

	:param map_real: 2D list of Cell objects
	:return: map_virtual
	"""
	map_virtual = []

	# Create base virtual map from real map (treat unexplored as obstacles)
	for r in range(0, NUM_ROWS):
		row_virtual = []

		for c in range(0, NUM_COLS):
			cell = map_real[r][c]
			row_virtual.append(Cell.FREE if cell == Cell.FREE else Cell.OBSTACLE)

		map_virtual.append(row_virtual)

	# Add virtual boundaries to walls
	for c in range(NUM_COLS):
		map_virtual[0][c] = Cell.OBSTACLE
		map_virtual[NUM_ROWS - 1][c] = Cell.OBSTACLE

	for r in range(NUM_ROWS):
		map_virtual[r][0] = Cell.OBSTACLE
		map_virtual[r][NUM_COLS - 1] = Cell.OBSTACLE

	# Add virtual boundaries to obstacles
	for r in range(0, NUM_ROWS):
		for c in range(0, NUM_COLS):
			if map_real[r][c] != Cell.FREE:
				for y in range(max(r - 1, 0), min(r + 2, NUM_ROWS)):
					for x in range(max(c - 1, 0), min(c + 2, NUM_COLS)):
						map_virtual[y][x] = Cell.OBSTACLE

	return map_virtual

def create_visibility_graph(map, extra_nodes=[]):
	"""
	Creates a visibility graph from the map.

	Uses the find_obstacle_vertices function to find the nodes of the visibility graph. Adds the extra nodes to the nodes list (e.g. source, destination, waypoint). Computes the edges that don't intersect with obstacles. Calculate the weights of the nodes using euclidean_distance.

	:param map: 2D list of Cell objects
	:return: visibility graph
	"""
	# Nodes
	nodes = find_obstacle_vertices(map)

	for node in extra_nodes:
		if node not in nodes:
			nodes.append(node)

	# Edges & Weights
	edges = []
	weights = []

	for i in range(len(nodes)):
		node0 = nodes[i]

		for j in range(i + 1, len(nodes)):
			node1 = nodes[j]

			if not does_edge_intersect_with_obstacle(map, node0, node1):
				edges.append((i, j))
				weights.append(euclidean_distance(node0, node1))

	return nodes, edges, weights

def compute_steps(nodes, edges, weights, source_node, dest_node):
	"""
	Performs A* search on the graph to find the fastest path from the source node to the destination node.

	:param nodes: list of nodes
	:param edges: list of edges
	:param weights: list of weights
	:param source_node: node index of source
	:param dest_node: node index of destination
	:return: steps
	"""
	pi = a_star(nodes, edges, weights, source_node, dest_node)

	steps = []
	cur = dest_node

	while cur != None:
		steps.append(nodes[cur])
		cur = pi[cur]

	steps.reverse()

	# No path found
	if len(steps) == 1 and source_node != dest_node:
		return None

	return steps

# TODO: Penalise rotation
def a_star(nodes, edges, weights, source_node, dest_node):
	"""
	Performs A* search on the graph to find the optimal path from the source node to the destination node.

	Returns the search tree from the search algorithm in the form a list, where the ith's node's parent node is pi[i].

	:param nodes: list of nodes
	:param edges: list of edges
	:param weights: list of weights
	:param source_node: node index of source
	:param dest_node: node index of destination
	:return: pi (models search tree)
	"""
	d = [None for i in nodes] # Actual cost
	pi = [None for i in nodes]
	S = [False for i in nodes]

	# Estimated cost from node to destination
	h = []
	for node in nodes:
		h.append(euclidean_distance(node, nodes[dest_node]))

	d[source_node] = 0

	while False in S:
		f = []

		min_f = None
		u = None

		for i in range(len(nodes)):
			if not S[i] and d[i] != None:
				f = d[i] + h[i]

				if min_f == None or f < min_f:
					min_f = f
					u = i

		if u == None or u == dest_node:
			break

		S[u] = True

		for i, edge in enumerate(edges):
			if u in edge:
				v = edge[1] if u == edge[0] else edge[0]

				if not S[v] and (d[v] == None or d[v] > d[u] + weights[i]):
					d[v] = d[u] + weights[i]
					pi[v] = u

	return pi

def smoothen_steps(steps):
	"""
	Smoothen the steps by removing intermediate steps with the same angle to prevent stops.

	:param steps: List of (c, r) tuples
	:return: smooth_steps
	"""
	if steps == None:
		return None

	smooth_steps = [steps[0]]

	for i in range(1, len(steps) - 1):
		prev_pos = steps[i - 1]
		cur_pos = steps[i]
		next_pos = steps[i + 1]

		theta0 = compute_angle(prev_pos, cur_pos)
		theta1 = compute_angle(cur_pos, next_pos)

		# TODO: Tweak angle threshold (in radians)
		if theta0 != None and theta1 != None and abs(theta0 - theta1) > 0.01:
			smooth_steps.append(cur_pos)

	if len(steps) > 1:
		smooth_steps.append(steps[-1])

	return smooth_steps

def find_obstacle_vertices(map):
	"""
	Finds the corners of the map and returns them as tuples (c, r).

	:param map: 2D list of Cell objects
	:return: obstacle_vertices
	"""
	obstacle_vertices = []

	for r in range(NUM_ROWS):
		for c in range(NUM_COLS):
			if map[r][c] == Cell.FREE:
				top = map[r + 1][c] if r < NUM_ROWS - 1 else None
				bottom = map[r - 1][c] if r > 0 else None
				left = map[r][c - 1] if c > 0 else None
				right = map[r][c + 1] if c < NUM_COLS - 1 else None
				top_left = map[r + 1][c - 1] if top != None and left != None else None
				top_right = map[r + 1][c + 1] if top != None and right != None else None
				bottom_left = map[r - 1][c - 1] if bottom != None and left != None else None
				bottom_right = map[r - 1][c + 1] if bottom != None and right != None else None

				# ? ? ?
				# X _ ?
				# ? X ?
				if (right == Cell.OBSTACLE or left == Cell.OBSTACLE) and (bottom == Cell.OBSTACLE or top == Cell.OBSTACLE):
					obstacle_vertices.append((c, r))
					continue

				# ? ? ?
				# _ _ ?
				# X _ ?
				elif (bottom_right == Cell.OBSTACLE and right == Cell.FREE and bottom == Cell.FREE) or \
						(bottom_left == Cell.OBSTACLE and left == Cell.FREE and bottom == Cell.FREE) or \
						(top_right == Cell.OBSTACLE and right == Cell.FREE and top == Cell.FREE) or \
						(top_left == Cell.OBSTACLE and left == Cell.FREE and top == Cell.FREE):
					obstacle_vertices.append((c, r))

	return obstacle_vertices

def does_edge_intersect_with_obstacle(map, p0, p1):
	"""
	Checks whether the edge intersects with any obstacle in the map.

	:param map: 2D list of Cell objects
	:param p0: point 0
	:param p1: point 1
	:return: whether or not the edge intersects with an obstacle
	"""
	# Bounding box
	x0 = min(p0[0], p1[0])
	x1 = max(p0[0], p1[0])
	y0 = min(p0[1], p1[1])
	y1 = max(p0[1], p1[1])

	# Vertical line
	if p1[0] == p0[0]:
		x = p0[0]
		for i in range(y0, y1 + 1):
			pos = map[i][x]
			if pos == Cell.OBSTACLE:
				return True
	# Horizontal line
	elif p1[1] == p0[1]:
		y = p0[1]
		for i in range(x0, x1 + 1):
			pos = map[y][i]
			if pos == Cell.OBSTACLE:
				return True

	# Not horizontal or vertical line
	else:
		m = (p1[1] - p0[1]) / (p1[0] - p0[0])
		c = p0[1] - (m * p0[0])
		denominator = math.sqrt(m ** 2 + 1)

		for i in range(y0, y1 + 1):
			for j in range(x0, x1 + 1):
				pos = map[i][j]
				perpendicular_distance = abs(m * j - i + c) / denominator

				# TODO: Tweak perpendicular distance from centre of obstacle to line (currently, it's sqrt(2))
				if pos == Cell.OBSTACLE and perpendicular_distance <= 1.414:
					return True

	return False

def compute_angle(p0, p1):
	"""
	Calculates the angle between the line formed from p0 to p1 and the x-axis in the counter-clockwise direction.

	:param p0: point 0
	:param p1: point 1
	:return: angle
	"""
	if p1[0] - p0[0] == 0:
		if p1[1] - p0[1] > 0:
			return math.pi / 2
		elif p1[1] - p0[1] == 0:
			return None
		else:
			return -math.pi / 2

	return math.atan((p1[1] - p0[1]) / (p1[0] - p0[0]))

def euclidean_distance(p0, p1):
	"""
	Computes the euclidean distance between point 0 and point 1.

	:param p0: point 0
	:param p1: point 1
	:return: euclidean distance
	"""
	return math.sqrt((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2)

def main():
	with open("maps/map2.txt", "r") as f:
		strs = f.read().split("\n")

	map = generate_map(*strs)
	steps = fastest_path(map, START_POS, GOAL_POS)

	print_map(add_virtual_boundaries(map), steps)

	if steps == None:
		print("No path found")
	else:
		for i, step in enumerate(steps):
			print("{}.".format(i + 1), step)

	graphics.display_maze(map, add_virtual_boundaries(map), steps)

if __name__ == "__main__":
	main()
