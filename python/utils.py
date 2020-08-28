from constants import NUM_ROWS, NUM_COLS, Cell
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

		print()
