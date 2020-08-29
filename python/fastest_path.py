import math
from constants import NUM_ROWS, NUM_COLS, START_POS, GOAL_POS, Cell
from utils import add_virtual_obstacles, print_map
from map_descriptor import generate_map
import graphics

def euclidean_distance(p0, p1):
	"""Computes the Euclidean distance between point 0 and point 1.

	Args:
		p0 (tuple): Point 0.
		p1 (tuple): Point 1.

	Returns:
		euclidean_distance (float): Euclidean distance between point 0 and point 1.
	"""
	return math.sqrt((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2)

def manhattan_distance(p0, p1):
	"""Computes the manhattan distance between point 0 and point 1.

	Args:
		p0 (tuple): Point 0.
		p1 (tuple): Point 1.

	Returns:
		manhattan_distance (int): Manhattan distance between point 0 and point 1.
	"""
	return abs(p1[0] - p0[0]) + abs(p1[1] - p0[1])

class FastestPath:
	def __init__(self, map):
		"""Inits FastestPath algorithm by adding virtual boundaries to the map

		Args:
			map (list): 2D list of `constants.Cell` objects representing the map layout.
		"""
		self.map = add_virtual_obstacles(map)

	def compute_fastest_path(self, source, dest, waypoint = None):
		"""Calculates the fastest path from the source to the destination, possibly with a waypoint.

		Args:
			source (tuple): Position of source.
			dest (tuple): Position of destination.
			waypoint (tuple): Position of waypoint (optional).

		Returns:
			steps (list): List of positions to move directly between to execute the path
		"""
		pass

	def compute_steps(self, pi, nodes, dest_node):
		"""Computes the steps from the search tree generated.

		Args:
			pi (list): List where the ith value corresponds to the parent of the ith node. Represents the search tree.
			nodes (list): List of nodes.
			dest_node (int): Position of the destination.

		Returns:
			steps (list): List of positions to move directly between to execute the path.
		"""
		steps = []
		cur = dest_node

		while cur != None:
			steps.append(nodes[cur])
			cur = pi[cur]

		steps.reverse()
		return steps

class FastestPathEuclidean(FastestPath):
	def __init__(self, map):
		super().__init__(map)
		self.obstacle_vertices = self.find_obstacle_vertices()

	def compute_fastest_path(self, source, dest, waypoint=None):
		extra_nodes = [source, dest]
		if waypoint:
			extra_nodes.append(waypoint)

		nodes, edges, weights = self.create_visibility_graph(extra_nodes)
		source_node = nodes.index(source)
		dest_node = nodes.index(dest)

		if waypoint:
			waypoint_node = nodes.index(waypoint)

			pi0 = self.a_star(nodes, edges, weights, source_node, waypoint_node)
			pi1 = self.a_star(nodes, edges, weights, waypoint_node, dest_node)

			if pi0 == None or pi1 == None:
				return None

			steps0 = self.compute_steps(pi0, nodes, waypoint_node)
			steps1 = self.compute_steps(pi1, nodes, dest_node)

			combined_steps = steps0 + steps1[1:]
			return self.smooth_steps(combined_steps)

		else:
			pi = self.a_star(nodes, edges, weights, source_node, dest_node)

			if pi == None:
				return None

			steps = self.compute_steps(pi, nodes, dest_node)
			return self.smooth_steps(steps)

	def find_obstacle_vertices(self):
		"""Finds the vertices of the virtual obstacles.

		Returns:
			obstacle_vertices (list): List of vertices of virtual obstacles.
		"""
		obstacle_vertices = []

		for r in range(NUM_ROWS):
			for c in range(NUM_COLS):
				if self.map[r][c] == Cell.FREE:
					top = self.map[r + 1][c] if r < NUM_ROWS - 1 else None
					bottom = self.map[r - 1][c] if r > 0 else None
					left = self.map[r][c - 1] if c > 0 else None
					right = self.map[r][c + 1] if c < NUM_COLS - 1 else None
					top_left = self.map[r + 1][c - 1] if top != None and left != None else None
					top_right = self.map[r + 1][c + 1] if top != None and right != None else None
					bottom_left = self.map[r - 1][c - 1] if bottom != None and left != None else None
					bottom_right = self.map[r - 1][c + 1] if bottom != None and right != None else None

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

	def create_visibility_graph(self, extra_nodes=None):
		"""Creates a visibility graph from the map.

		Args:
			extra_nodes (list): List of positions of nodes to add (e.g. source, destination, waypoint).

		Returns:
			nodes (list): List of nodes, including obstacle vertices and `extra_nodes`.
			edges (list): List of edges that don't intersect with an obstacle.
			weights (list): List of weights of the edges (calculated using euclidean distance).
		"""
		# Nodes
		nodes = self.obstacle_vertices.copy()

		if extra_nodes != None:
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

				if not self.does_edge_intersect_with_obstacle(node0, node1):
					edges.append((i, j))
					weights.append(euclidean_distance(node0, node1))

		return nodes, edges, weights

	def does_edge_intersect_with_obstacle(self, p0, p1):
		"""Checks whether the edge formed from p0 to p1 intersects with any obstacle in the map.

		Args:
			p0 (tuple): Point 0.
			p1 (tuple): Point 1.

		Returns:
			does_intersect (bool): Whether or not the edge intersects with an obstacle.
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
				pos = self.map[i][x]
				if pos == Cell.OBSTACLE:
					return True
		# Horizontal line
		elif p1[1] == p0[1]:
			y = p0[1]
			for i in range(x0, x1 + 1):
				pos = self.map[y][i]
				if pos == Cell.OBSTACLE:
					return True

		# Not horizontal or vertical line
		else:
			m = (p1[1] - p0[1]) / (p1[0] - p0[0])
			c = p0[1] - (m * p0[0])
			denominator = math.sqrt(m ** 2 + 1)

			for i in range(y0, y1 + 1):
				for j in range(x0, x1 + 1):
					pos = self.map[i][j]
					perpendicular_distance = abs(m * j - i + c) / denominator

					# TODO: Tweak perpendicular distance from centre of obstacle to line (currently, it's sqrt(2))
					if pos == Cell.OBSTACLE and perpendicular_distance <= 1.414:
						return True

		return False

	def a_star(self, nodes, edges, weights, source_node, dest_node):
		"""Performs A* search on the graph to find the optimal path from the source node to the destination node.

		Args:
			nodes (list): List of nodes.
			edges (list): List of edges.
			weights (list): List of weights.
			source_node (int): Node index of source.
			dest_node (int): Node index of destination.

		Returns:
			pi (list): List where the ith value corresponds to the parent of the ith node. Represents the search tree.
		"""
		g = [None for i in nodes] # Actual cost
		pi = [None for i in nodes]
		S = [False for i in nodes]

		# Estimated cost from node to destination
		h = []
		for node in nodes:
			h.append(euclidean_distance(node, nodes[dest_node]))

		g[source_node] = 0

		while False in S:
			min_f = None
			u = None

			for i in range(len(nodes)):
				if not S[i] and g[i] != None:
					f = g[i] + h[i]

					if min_f == None or f < min_f:
						min_f = f
						u = i

			if u == None:
				break

			if u == dest_node:
				return pi

			S[u] = True

			for i, edge in enumerate(edges):
				if u in edge:
					v = edge[1] if u == edge[0] else edge[0]

					if not S[v] and (g[v] == None or g[v] > g[u] + weights[i]):
						g[v] = g[u] + weights[i]
						pi[v] = u

		return None

	def smooth_steps(self, steps):
		"""Smooths the steps by removing intermediate steps with the same direction to prevent stops.

		Args:
			steps (list): List of positions to move directly between to execute the path.

		Returns
			smooth_steps (list): List of positions after smoothing steps.
		"""
		if steps == None:
			return None

		smooth_steps = [steps[0]]

		for i in range(1, len(steps) - 1):
			prev_pos = steps[i - 1]
			cur_pos = steps[i]
			next_pos = steps[i + 1]

			theta0 = self.compute_angle(prev_pos, cur_pos)
			theta1 = self.compute_angle(cur_pos, next_pos)

			if theta0 != None and theta1 != None and abs(theta0 - theta1) > 0.01:
				smooth_steps.append(cur_pos)

		if len(steps) > 1:
			smooth_steps.append(steps[-1])

		return smooth_steps

	def compute_angle(self, p0, p1):
		"""Calculates the angle between the line formed from p0 to p1 and the x-axis in the counter-clockwise direction.

		Args:
			p0 (tuple): Point 0.
			p1 (tuple): Point 1.

		Returns:
			angle (float): Angle between the line and the x-axis in the counter-clockwise direction.
		"""
		if p1[0] - p0[0] == 0:
			if p1[1] - p0[1] > 0:
				return math.pi / 2
			elif p1[1] - p0[1] == 0:
				return None
			else:
				return -math.pi / 2

		return math.atan((p1[1] - p0[1]) / (p1[0] - p0[0]))

class FastestPathManhattan(FastestPath):
	def compute_fastest_path(self, source, dest, waypoint=None):
		if waypoint:
			pi0, nodes0 = self.a_star(source, waypoint)
			pi1, nodes1 = self.a_star(waypoint, dest)

			if pi0 == None or pi1 == None:
				return None

			waypoint_node = nodes0.index(waypoint)
			dest_node = nodes1.index(dest)

			steps0 = self.compute_steps(pi0, nodes0, waypoint_node)
			steps1 = self.compute_steps(pi1, nodes1, dest_node)
			combined_steps = steps0 + steps1[1:]

			return self.smooth_steps(combined_steps)

		else:
			pi, nodes = self.a_star(source, dest)

			if pi == None:
				return None

			dest_node = nodes.index(dest)
			steps = self.compute_steps(pi, nodes, dest_node)
			return self.smooth_steps(steps)

	def a_star(self, source, dest):
		"""Performs A* search on the graph to find the optimal path from the source node to the destination node.

		Args:
			source (tuple): Position of source.
			dest (tuple): Position of destination.

		Returns:
			pi (list): List where the ith value corresponds to the parent of the ith node. Represents the search tree. Return `None` if `dest` not found.
			nodes (list): List of nodes.
		"""
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

			if u == None:
				break

			if nodes[u] == dest:
				return pi, nodes

			p_queue.remove(u)
			explored[u] = True

			# Check neighbours
			node = nodes[u]
			neighbours = []

			if node[0] > 0:
				neighbours.append((node[0] - 1, node[1]))

			if node[0] < NUM_COLS - 1:
				neighbours.append((node[0] + 1, node[1]))

			if node[1] > 0:
				neighbours.append((node[0], node[1] - 1))

			if node[1] < NUM_ROWS - 1:
				neighbours.append((node[0], node[1] + 1))

			print(neighbours)

			for neighbour in neighbours:
				if self.map[neighbour[1]][neighbour[0]] != Cell.FREE:
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

		return None, nodes

	def smooth_steps(self, steps):
		"""Smooths the steps by removing intermediate steps with the same direction to prevent stops.

		Args:
			steps (list): List of positions to move directly between to execute the path.

		Returns
			smooth_steps (list): List of positions after smoothing steps.
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

def main():
	with open("maps/map3.txt", "r") as f:
		strs = f.read().split("\n")

	map = generate_map(*strs)
	steps = FastestPathManhattan(map).compute_fastest_path(START_POS, GOAL_POS)

	print_map(add_virtual_obstacles(map), steps)

	if steps == None:
		print("No path found")
	else:
		for i, step in enumerate(steps):
			print("{}.".format(i + 1), step)

	graphics.display_maze(map, add_virtual_obstacles(map), steps)

if __name__ == "__main__":
	main()
