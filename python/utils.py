from constants import NUM_ROWS, NUM_COLS, START_POS, GOAL_POS
from enums import Cell
import time

def timeit(method):
	def timed(*args, **kw):
		ts = time.time()
		result = method(*args, **kw)
		te = time.time()
		if 'log_time' in kw:
			name = kw.get('log_name', method.__name__.upper())
			kw['log_time'][name] = int((te - ts) * 1000)
		else:
			print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))

		return result
	return timed

def print_map(map, marked_points=None):
	if marked_points == None:
		marked_points = []

	for r, row in enumerate(reversed(map)):
		for c, cell in enumerate(row):
			if (c, NUM_ROWS - 1 - r) in marked_points:
				print("+", end="")
			else:
				if cell == Cell.UNEXPLORED:
					print("?", end="")

				elif cell == Cell.FREE:
					print("_", end="")

				elif cell == Cell.OBSTACLE:
					print("X", end="")
				# TODO: Remove
				else:
					print(cell, end="")

		print()

# TODO: Move to fastest path
def add_virtual_obstacles(map_real):
	"""Adds virtual obstacles to the map.

	Treats unexplored cells as well as the cells around walls, unexplored cell and obstacles as virtual obstacles.

	Args:
		map_real (list): 2D list of `constants.Cell` objects representing the map layout.

	Returns:
		map_virtual (list): 2D list of `constants.Cell` objects representing the map layout with virtual obstacles.
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


def generate_unexplored_map():
	unexplored_map = [[Cell.UNEXPLORED for c in range(NUM_COLS)] for r in range(NUM_ROWS)]

	for r in range(START_POS[1] - 1, START_POS[1] + 2):
		for c in range(START_POS[0] - 1, START_POS[0] + 2):
			unexplored_map[r][c] = Cell.FREE

	for r in range(GOAL_POS[1] - 1, GOAL_POS[1] + 2):
		for c in range(GOAL_POS[0] - 1, GOAL_POS[0] + 2):
			unexplored_map[r][c] = Cell.FREE

	return unexplored_map
