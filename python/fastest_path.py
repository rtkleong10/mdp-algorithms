import math

NUM_COLS = 15
NUM_ROWS = 20

map_real = [
	[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	[1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
	[0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1],
	[1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1],
	[0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

map_virtual = [
	[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1],
	[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
	[1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
	[1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1],
	[1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1],
	[1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
	[1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
	[1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1],
	[1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1],
	[1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1],
	[1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1],
	[1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1],
	[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

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

@timeit
def add_virtual_boundaries_slow(map_real):
	map_virtual = [[1 for i in range(NUM_COLS)]]

	for i in range(1, NUM_ROWS - 1):
		row_virtual = [1]

		for j in range(1, NUM_COLS - 1):
			pos_virtual = 0

			for y in range(i - 1, i + 2):
				for x in range(j - 1, j + 2):
					if map_real[y][x] == 1:
						pos_virtual = 1
						break

				if pos_virtual == 1:
					break

			row_virtual.append(pos_virtual)

		row_virtual.append(1)
		map_virtual.append(row_virtual)

	map_virtual.append([1 for i in range(NUM_COLS)])
	return map_virtual

# Faster for few obstacles
def add_virtual_boundaries(map_real):
	map_virtual = [[1 for i in range(NUM_COLS)]]
	map_virtual.extend([[0 if i != 0 and i != NUM_COLS - 1 else 1 for i in range(NUM_COLS)] for j in range(NUM_ROWS - 2)])
	map_virtual.append([1 for i in range(NUM_COLS)])

	for i in range(0, NUM_ROWS):
		for j in range(0, NUM_COLS):
			if map_real[i][j] == 1:
				for y in range(max(i - 1, 0), min(i + 2, NUM_ROWS)):
					for x in range(max(j - 1, 0), min(j + 2, NUM_COLS)):
						map_virtual[y][x] = 1

	return map_virtual

START_POS = (1, 1)
END_POS = (13, 18)

def find_obstacle_vertices(map_virtual):
	obstacle_vertices = []

	for i in range(NUM_ROWS):
		for j in range(NUM_COLS):
			if map_virtual[i][j] != 1:
				top = map_virtual[i + 1][j] if i < NUM_ROWS - 1 else None
				bottom = map_virtual[i - 1][j] if i > 0 else None
				left = map_virtual[i][j - 1] if j > 0 else None
				right = map_virtual[i][j + 1] if j < NUM_COLS - 1 else None
				top_left = map_virtual[i + 1][j - 1] if top != None and left != None else None
				top_right = map_virtual[i + 1][j + 1] if top != None and right != None else None
				bottom_left = map_virtual[i - 1][j - 1] if bottom != None and left != None else None
				bottom_right = map_virtual[i - 1][j + 1] if bottom != None and right != None else None

				# ? ? ?
				# 1   ?
				# ? 1 ?
				if (right == 1 or left == 1) and (bottom == 1 or top == 1):
					obstacle_vertices.append((j, i))
					continue

				# ? ? ?
				# 0   ?
				# 1 0 ?
				if (bottom_right == 1 and right == 0 and bottom == 0) or \
						(bottom_left == 1 and left == 0 and bottom == 0) or \
						(top_right == 1 and right == 0 and top == 0) or \
						(top_left == 1 and left == 0 and top == 0):
					obstacle_vertices.append((j, i))

	return obstacle_vertices

def create_visibility_graph(map_virtual):
	"""
	:param map: Virtual map
	:return: Visibility graph
	"""
	# Nodes
	nodes = find_obstacle_vertices(map_virtual)

	if START_POS not in nodes or END_POS not in nodes:
		raise ValueError("Start position or end position not found in the vertices")

	# Edges & Weights
	edges = []
	weights = []

	for i in range(len(nodes)):
		node0 = nodes[i]

		for j in range(i + 1, len(nodes)):
			node1 = nodes[j]

			if not check_intersect_with_obstacles(node0, node1, map_virtual):
				edges.append((i, j))
				weights.append(euclidean_distance(node0, node1))

	return nodes, edges, weights

def euclidean_distance(p0, p1):
	return math.sqrt((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2)

def check_intersect_with_obstacles(p0, p1, map_virtual):
	# Bounding box
	x0 = min(p0[0], p1[0])
	x1 = max(p0[0], p1[0])
	y0 = min(p0[1], p1[1])
	y1 = max(p0[1], p1[1])

	# Vertical line
	if p1[0] == p0[0]:
		x = p0[0]
		for i in range(y0, y1 + 1):
			pos = map_virtual[i][x]
			if pos == 1:
				return True
	# Horizontal line
	elif p1[1] == p0[1]:
		y = p0[1]
		for i in range(x0, x1 + 1):
			pos = map_virtual[y][i]
			if pos == 1:
				return True

	# Not horizontal or vertical line
	else:
		m = (p1[1] - p0[1]) / (p1[0] - p0[0])
		c = p0[1] - (m * p0[0])

		for i in range(y0, y1 + 1):
			for j in range(x0, x1 + 1):
				pos = map_virtual[i][j]
				perpedicular_distance = abs(m * j - i + c) / math.sqrt(m ** 2 + 1)

				# TODO: Tweak perpendicular distance from centre of obstacle to line (current sqrt(2))
				if pos == 1 and perpedicular_distance <= 1.414:
					return True

	return False

def line_segments_intersect(p0, p1, p2, p3):
	# Check if bounding boxes intersect
	x0 = min(p0[0], p1[0])
	x1 = max(p0[0], p1[0])
	x2 = min(p2[0], p3[0])
	x3 = max(p2[0], p3[0])

	y0 = min(p0[1], p1[1])
	y1 = max(p0[1], p1[1])
	y2 = min(p2[1], p3[1])
	y3 = max(p2[1], p3[1])

	if not(x1 >= x2 and x3 >= x0 and y1 >= y2 and y3 >= y0):
		return False

	# Check if the segments straddle each other
	result0 = ((p2[0] - p0[0]) * (p1[1] - p0[1])) - ((p2[1] - p0[1]) * (p1[0] - p0[0]))
	result1 = ((p3[0] - p0[0]) * (p1[1] - p0[1])) - ((p3[1] - p0[1]) * (p1[0] - p0[0]))

	if (result0 < 0 and result1 > 0) or (result0 > 0 and result1 < 0):
		return True
	else:
		return False

# TODO: Penalise rotation
def dijkstra(nodes, edges, weights, source, dest):
	d = [None for i in nodes]
	pi = [None for i in nodes]
	S = [False for i in nodes]

	d[source] = 0

	while False in S:
		min_d = None
		u = None

		for i in range(len(S)):
			if not S[i] and d[i] != None and (min_d == None or d[i] < min_d):
				min_d = d[i]
				u = i

		if u == None or u == dest:
			break

		S[u] = True

		for i, edge in enumerate(edges):
			if u in edge:
				v = edge[1] if u == edge[0] else edge[0]

				if not S[v] and (d[v] == None or d[v] > d[u] + weights[i]):
					d[v] = d[u] + weights[i]
					pi[v] = u

	return d, pi

def a_star(nodes, edges, weights, source, dest):
	d = [None for i in nodes] # Actual cost
	pi = [None for i in nodes]
	S = [False for i in nodes]

	# Estimated cost from node to destination
	h = []
	for node in nodes:
		h.append(euclidean_distance(node, nodes[dest]))

	d[source] = 0

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

		if u == None or u == dest:
			break

		S[u] = True

		for i, edge in enumerate(edges):
			if u in edge:
				v = edge[1] if u == edge[0] else edge[0]

				if not S[v] and (d[v] == None or d[v] > d[u] + weights[i]):
					d[v] = d[u] + weights[i]
					pi[v] = u

	return d, pi