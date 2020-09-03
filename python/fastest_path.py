import math
from constants import NUM_ROWS, NUM_COLS, START_POS, GOAL_POS
from enums import Cell, Direction, Movement
from utils import add_virtual_obstacles, print_map
from map_descriptor import generate_map


class FastestPath:
	def __init__(self, explored_map, direction, source, dest, waypoint=None):
		"""Inits FastestPath algorithm by adding virtual boundaries to the map

		Args:
			explored_map (list): 2D list of `constants.Cell` objects representing the map layout.
			direction (Direction): Starting direction at the source.
			source (tuple): Position of source.
			dest (tuple): Position of destination.
			waypoint (tuple): Position of waypoint (optional).
		"""
		self.map = add_virtual_obstacles(explored_map)

		self.direction = direction
		self.source = source
		self.dest = dest
		self.waypoint = waypoint
		self.path_found = False
		self._steps = None
		self._movements = None

		self.compute_fastest_path()

	@property
	def steps(self):
		return self._steps

	@property
	def movements(self):
		return self._movements

	def compute_fastest_path(self):
		"""Calculates the fastest path from the source to the destination, possibly with a waypoint.
		"""
		if self.waypoint:
			steps0 = self.a_star(self.source, self.waypoint)
			steps1 = self.a_star(self.waypoint, self.dest)

			if steps0 is None or steps1 is None:
				return None

			self.path_found = True
			self._steps = steps0 + steps1[1:]
			self._movements = FastestPath.compute_movements(self._steps, self.direction)

		else:
			steps = self.a_star(self.source, self.dest)

			if steps is None:
				return None

			self.path_found = True
			self._steps = steps
			self._movements = FastestPath.compute_movements(self._steps, self.direction)

	def a_star(self, source, dest):
		"""Performs A* search on the graph to find the optimal path from the source node to the destination node.

		Args:
			source (tuple): Position of source.
			dest (tuple): Position of destination.

		Returns:
			steps (list): List of positions to move directly between to execute the path.
		"""
		nodes = [source]
		g = [0]  # Cost
		h = [self.heuristic_function(source, dest)]
		pi = [None]  # Search tree in terms of parents
		p_queue = [0]

		while len(p_queue) > 0:
			# Remove top of priority queue
			min_f = g[p_queue[0]] + h[p_queue[0]]
			u = p_queue[0]

			for i in p_queue[1:]:
				f = g[i] + h[i]

				if f < min_f:
					min_f = f
					u = i

			# Check if destination reached
			if nodes[u] == dest:
				return self.compute_steps(pi, nodes, u)

			p_queue.remove(u)

			# Check neighbours
			for neighbour in self.get_neighbours(nodes[u]):
				if self.map[neighbour[1]][neighbour[0]] != Cell.FREE:
					continue

				# Path cost from source to neighbour via u
				new_cost = g[u] + 1

				# Rotation cost
				if not (pi[u] is None or (neighbour[0] == nodes[pi[u]][0]) or (neighbour[1] == nodes[pi[u]][1])):
					new_cost += 1

				try:
					# Existing node
					i = nodes.index(neighbour)

					# Skip if explored
					if i not in p_queue:
						continue

					# Update cost
					if new_cost < g[i]:
						g[i] = new_cost
						pi[i] = u

				except ValueError:
					# Add new node
					nodes.append(neighbour)
					g.append(new_cost)
					h.append(self.heuristic_function(neighbour, dest))
					pi.append(u)
					p_queue.append(len(nodes) - 1)

		return None

	def get_neighbours(self, pos):
		neighbours = []

		if pos[0] > 0:
			neighbours.append((pos[0] - 1, pos[1]))

		if pos[0] < NUM_COLS - 1:
			neighbours.append((pos[0] + 1, pos[1]))

		if pos[1] > 0:
			neighbours.append((pos[0], pos[1] - 1))

		if pos[1] < NUM_ROWS - 1:
			neighbours.append((pos[0], pos[1] + 1))

		return [neighbour for neighbour in neighbours if self.map[neighbour[1]][neighbour[0]] == Cell.FREE]

	@staticmethod
	def heuristic_function(p0, p1):
		"""Computes the manhattan distance between point 0 and point 1 as the heuristic function.

		Args:
			p0 (tuple): Point 0.
			p1 (tuple): Point 1.

		Returns:
			h (int): Manhattan distance between point 0 and point 1.
		"""
		return abs(p1[0] - p0[0]) + abs(p1[1] - p0[1])

	@staticmethod
	def compute_steps(pi, nodes, dest_node):
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

		while cur is not None:
			steps.append(nodes[cur])
			cur = pi[cur]

		steps.reverse()
		return steps

	@staticmethod
	def compute_movements(steps, direction):
		"""Converts the steps into movements where  robot starts from the first step position and in the provided direction.

		Args:
			steps (list): List of positions to move directly between to execute the path.
			direction (Direction): Starting direction at the source.

		Returns:
			movements (list): List of movements for the robot to make to execute the path.
		"""
		movements = []
		robot_direction = direction

		for i in range(1, len(steps)):
			# Determine move direction
			start_pos = steps[i - 1]
			end_pos = steps[i]

			c_diff = end_pos[0] - start_pos[0]
			r_diff = end_pos[1] - start_pos[1]

			if c_diff < 0:
				move_direction = Direction.WEST
			elif c_diff > 0:
				move_direction = Direction.EAST
			else:
				if r_diff < 0:
					move_direction = Direction.SOUTH
				elif r_diff > 0:
					move_direction = Direction.NORTH
				else:
					continue

			# Determine robot movements
			num_rotate_right = (move_direction - robot_direction) % 4

			if num_rotate_right == 2:
				movements.append(Movement.BACKWARD)
			else:
				if num_rotate_right == 1:
					movements.append(Movement.RIGHT)
				elif num_rotate_right == 3:
					movements.append(Movement.LEFT)

				movements.append(Movement.FORWARD)
				robot_direction = move_direction

		return movements


def main():
	with open("maps/map3.txt", "r") as f:
		strs = f.read().split("\n")

	map_test = generate_map(*strs)
	fp = FastestPath(map_test, Direction.EAST, START_POS, GOAL_POS)

	print_map(add_virtual_obstacles(map_test), fp.steps)

	if fp.path_found:
		for i, step in enumerate(fp.steps):
			print("{}.".format(i + 1), step)

		for i, movement in enumerate(fp.movements):
			print("{}.".format(i + 1), movement)


if __name__ == "__main__":
	main()
