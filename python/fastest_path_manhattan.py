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

	if waypoint:
		steps0 = compute_steps(map_virtual, source, waypoint)
		steps1 = compute_steps(map_virtual, waypoint, dest)

		if steps0 == None or steps1 == None:
			return None

		return smoothen_steps(steps0 + steps1[1:])

	else:
		return smoothen_steps(compute_steps(map_virtual, source, dest))

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

		if not (prev_pos[0] == next_pos[0] or prev_pos[1] == next_pos[1]):
			smooth_steps.append(cur_pos)

	if len(steps) > 1:
		smooth_steps.append(steps[-1])

	return smooth_steps

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

def compute_steps(map, source, dest):
	"""
	Performs A* search on the graph to find the fastest path from the source node to the destination node.

	:param nodes: list of nodes
	:param edges: list of edges
	:param weights: list of weights
	:param source_node: node index of source
	:param dest_node: node index of destination
	:return: steps
	"""
	nodes, pi = a_star(map, source, dest)
	source_node = nodes.index(source)
	dest_node = nodes.index(dest)

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
def a_star(map, source, dest):
	"""
	Performs A* search on the graph to find the optimal path from the source node to the destination node.

	Returns the search tree from the search algorithm in the form a list, where the ith's node's parent node is pi[i].

	:param map:
	:param source_node: node index of source
	:param dest_node: node index of destination
	:return: pi (models search tree)
	"""
	# TODO: Check why it's exploring all of the map
	# nodes = [(c, r) for r in range(len(map)) for c in range(len(row)) if map[r][c] == Cell.FREE]
	nodes = [source]
	g = [0] # Cost
	h = [manhattan_distance(source, dest)]
	pi = [None] # Search tree in terms of parents
	explored = [False]
	p_queue = [0]

	while len(p_queue) > 0:
		# Remove top of priority queue
		min_f = g[p_queue[0]] + h[p_queue[0]]
		u = p_queue[0]

		# print(nodes)
		for i in p_queue[1:]:
			f = g[i] + h[i]

			if f < min_f:
				min_f = f
				u = i

		if u == None or u == dest:
			break

		p_queue.remove(u)
		explored[u] = True

		# Check neighbours
		node = nodes[u]

		for neighbour in [(node[0] - 1, node[1]), (node[0] + 1, node[1]), (node[0], node[1] - 1), (node[0], node[1] + 1)]:
			if neighbour[0] < 0 or neighbour[0] >= NUM_COLS or neighbour[1] < 0 or neighbour[1] >= NUM_ROWS or map[neighbour[1]][neighbour[0]] != Cell.FREE:
				continue

			i = None

			try:
				# Existing node
				i = nodes.index(neighbour)
			except ValueError:
				# Add new node
				nodes.append(neighbour)
				i = len(nodes) - 1
				g.append(None)
				h.append(manhattan_distance(neighbour, dest))
				pi.append(None)
				explored.append(False)

			if explored[i]:
				continue

			# Add to priority queue
			if i not in p_queue:
				p_queue.append(i)

			edge_cost = 1

			# Rotation cost
			if not (pi[u] == None or (neighbour[0] == nodes[pi[u]][0]) or (neighbour[1] == nodes[pi[u]][1])):
				edge_cost += 1

			if g[i] == None or g[u] + edge_cost < g[i]:
				g[i] = g[u] + edge_cost
				pi[i] = u

	print_map(map, nodes)

	return nodes, pi

def manhattan_distance(p0, p1):
	"""
	Computes the manhattan distance between point 0 and point 1.

	:param p0: point 0
	:param p1: point 1
	:return: manhattan distance
	"""
	return abs(p1[0] - p0[0]) + abs(p1[1] - p0[1])

def main():
	with open("maps/map1.txt", "r") as f:
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
