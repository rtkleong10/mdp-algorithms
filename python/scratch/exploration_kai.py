from enums import Cell, Direction, Movement
from utils import print_map
from map_descriptor import generate_map
from fastest_path import FastestPath

with open("../maps/sample_arena5.txt", "r") as f:
	strs = f.read().split("\n")

map_real = generate_map(*strs)

check_enter_goal = False



# debugging
# def printMap(map):
# 	for i in range(19, -1, -1):
# 		print(map[i])
#

# initialise map
map = [[0] * 15 for i in range(20)]

# initialise bot position [x,y]
# not neccessary from start zone
bot = [1, 1]

# state start zone
start = [1, 1]

# state goal zone
goal = [13, 18]

# initialise start zone, may not start from start
for x in range(bot[0] - 1, bot[0] + 2):
	for y in range(bot[1] - 1, bot[1] + 2):
		map[y][x] = Cell.FREE

# variable to check if enter goal zone
check_enter_goal = False

# initialise pre pos
prev_pos = []

print_map(map)


# obstacles = {(5, 4): 1, (5, 5): 1, (5, 6): 1, (5, 7): 1, (6, 4): 1, (7, 4): 1, (8, 4): 1, (9, 4): 1, (9, 5): 1, (9, 6): 1, (9, 7): 1, }
# obstacles={(4,4):1,(5,3):1,(6,2):1,(7,1):1,(6,15):1,(7,16):1,(8,17):1,(9,18):1}
# for simulation

# SimulatorRobot.sense()
def sense(bot, bot_dir):
	global obstacles, map
	front = 2  # how far it can sense
	left = 2  # same as above
	right = 2  # same as above
	for i in range(front):
		if bot_dir == Direction.EAST:
			x, y = bot[0] + 2 + i, bot[1]
		elif bot_dir == Direction.NORTH:
			x, y = bot[0], bot[1] + 2 + i
		elif bot_dir == Direction.SOUTH:
			x, y = bot[0], bot[1] - 2 - i
		elif bot_dir == Direction.WEST:
			x, y = bot[0] - 2 - i, bot[1]

		if x < 0 or x > 14 or y < 0 or y > 19:
			break
		if map_real[y][x] == Cell.OBSTACLE:
			map[y][x] = Cell.OBSTACLE
			break
		else:
			map[y][x] = Cell.FREE
	for i in range(front):
		if bot_dir == Direction.EAST:
			x, y = bot[0] + 2 + i, bot[1] - 1
		elif bot_dir == Direction.NORTH:
			x, y = bot[0] - 1, bot[1] + 2 + i
		elif bot_dir == Direction.SOUTH:
			x, y = bot[0] - 1, bot[1] - 2 - i
		elif bot_dir == Direction.WEST:
			x, y = bot[0] - 2 - i, bot[1] - 1
		if x < 0 or x > 14 or y < 0 or y > 19:
			break

		if map_real[y][x] == Cell.OBSTACLE:
			map[y][x] = Cell.OBSTACLE
			break
		else:
			map[y][x] = Cell.FREE
	for i in range(front):
		if bot_dir == Direction.EAST:
			x, y = bot[0] + 2 + i, bot[1] + 1
		elif bot_dir == Direction.NORTH:
			x, y = bot[0] + 1, bot[1] + 2 + i
		elif bot_dir == Direction.SOUTH:
			x, y = bot[0] + 1, bot[1] - 2 - i
		elif bot_dir == Direction.WEST:
			x, y = bot[0] - 2 - i, bot[1] + 1
		if x < 0 or x > 14 or y < 0 or y > 19:
			break
		if map_real[y][x] == Cell.OBSTACLE:
			map[y][x] = Cell.OBSTACLE
			break
		else:
			map[y][x] = Cell.FREE

	for i in range(left):
		if bot_dir == Direction.SOUTH:
			x, y = bot[0] + 2 + i, bot[1]
		elif bot_dir == Direction.EAST:
			x, y = bot[0], bot[1] + 2 + i
		elif bot_dir == Direction.WEST:
			x, y = bot[0], bot[1] - 2 - i
		elif bot_dir == Direction.NORTH:
			x, y = bot[0] - 2 - i, bot[1]
		if x < 0 or x > 14 or y < 0 or y > 19:
			break
		if map_real[y][x] == Cell.OBSTACLE:
			map[y][x] = Cell.OBSTACLE
			break
		else:
			map[y][x] = Cell.FREE

	for i in range(right):
		if bot_dir == Direction.NORTH:
			x, y = bot[0] + 2 + i, bot[1]
		elif bot_dir == Direction.WEST:
			x, y = bot[0], bot[1] + 2 + i
		elif bot_dir == Direction.EAST:
			x, y = bot[0], bot[1] - 2 - i
		elif bot_dir == Direction.SOUTH:
			x, y = bot[0] - 2 - i, bot[1]
		if x < 0 or x > 14 or y < 0 or y > 19:
			break
		if map_real[y][x] == Cell.OBSTACLE:
			map[y][x] = Cell.OBSTACLE
			break
		else:
			map[y][x] = Cell.FREE


# find cord wrt the bot based on where it's facing
def findRightPos(bot_dir):
	if bot_dir == Direction.EAST:
		return [0, -1]
	elif bot_dir == Direction.NORTH:
		return [1, 0]
	elif bot_dir == Direction.SOUTH:
		return [-1, 0]
	elif bot_dir == Direction.WEST:
		return [0, 1]


# check for surroundings
def checkSurroundings(bot_dir, _dir):
	if bot_dir == Direction.EAST:
		if _dir == Movement.RIGHT:
			return [0, -2], [-1, -2], [1, -2]
		elif _dir == Movement.LEFT:
			return [0, 2], [-1, 2], [1, 2]
		elif _dir == Movement.FORWARD:
			return [2, 0], [2, -1], [2, 1]
	elif bot_dir == Direction.NORTH:
		if _dir == Movement.RIGHT:
			return [2, 0], [2, -1], [2, 1]
		elif _dir == Movement.LEFT:
			return [-2, 0], [-2, 1], [-2, -1]
		elif _dir == Movement.FORWARD:
			return [0, 2], [-1, 2], [1, 2]
	elif bot_dir == Direction.SOUTH:
		if _dir == Movement.RIGHT:
			return [-2, 0], [-2, 1], [-2, -1]
		elif _dir == Movement.LEFT:
			return [2, 0], [2, -1], [2, 1]
		elif _dir == Movement.FORWARD:
			return [0, -2], [-1, -2], [1, -2]
	elif bot_dir == Direction.WEST:
		if _dir == Movement.RIGHT:
			return [0, 2], [-1, 2], [1, 2]
		elif _dir == Movement.LEFT:
			return [0, -2], [-1, -2], [1, -2]
		elif _dir == Movement.FORWARD:
			return [-2, 0], [-2, 1], [-2, -1]


# check if should turn right
def checkRight(bot, bot_dir, prev_pos):
	global map
	obstacle = False
	for x, y in checkSurroundings(bot_dir, Movement.RIGHT):
		if bot[1] + y < 0 or bot[1] + y > 19 or bot[0] + x < 0 or bot[0] + x > 14:  # check wall
			return False
		elif map[bot[1] + y][bot[0] + x] == Cell.UNEXPLORED:  # check if right is unexplored
			return True
		elif map[bot[1] + y][bot[0] + x] == Cell.OBSTACLE:  # check for obstacles
			obstacle = True
	if obstacle:
		return False
	add_x, add_y = findRightPos(bot_dir)
	rightpos = [bot[0] + add_x, bot[1] + add_y]
	if rightpos == prev_pos:
		return False
	return True


# check if should move forward
def checkForward(bot, bot_dir):
	global map
	for x, y in checkSurroundings(bot_dir, Movement.FORWARD):
		if bot[1] + y < 0 or bot[1] + y > 19 or bot[0] + x < 0 or bot[0] + x > 14:  # check wall
			return False
		elif map[bot[1] + y][bot[0] + x] == Cell.OBSTACLE:  # check for obstacles
			return False
	return True


# check if should turn left
def checkLeft(bot, bot_dir):
	global map
	for x, y in checkSurroundings(bot_dir, Movement.LEFT):
		if bot[1] + y < 0 or bot[1] + y > 19 or bot[0] + x < 0 or bot[0] + x > 14:  # check wall
			return False
		elif map[bot[1] + y][bot[0] + x] == Cell.OBSTACLE:  # check for obstacles
			return False
	return True


# turn right
def turnRight(bot_dir):
	if bot_dir == Direction.EAST:
		return Direction.SOUTH

	elif bot_dir == Direction.NORTH:
		return Direction.EAST

	elif bot_dir == Direction.SOUTH:
		return Direction.WEST

	elif bot_dir == Direction.WEST:
		return Direction.NORTH


# move forward
def moveForward(bot, bot_dir):
	global map, prev_pos
	prev_pos = bot
	if bot_dir == Direction.EAST:
		bot = [bot[0] + 1, bot[1]]
	elif bot_dir == Direction.NORTH:
		bot = [bot[0], bot[1] + 1]
	elif bot_dir == Direction.SOUTH:
		bot = [bot[0], bot[1] - 1]
	elif bot_dir == Direction.WEST:
		bot = [bot[0] - 1, bot[1]]
	return bot


# turn left
def turnLeft(bot_dir):
	if bot_dir == Direction.EAST:
		return Direction.NORTH

	elif bot_dir == Direction.NORTH:
		return Direction.WEST

	elif bot_dir == Direction.SOUTH:
		return Direction.EAST

	elif bot_dir == Direction.WEST:
		return Direction.SOUTH


def findUnexplored(bot, bot_dir):
	global map
	for row in range(20):
		for col in range(15):
			if map[row][col] == Cell.UNEXPLORED:
				pos_to_check = list(possiblePos([col, row]).keys())

				if len(pos_to_check) == 0:
					continue

				best_pos = pos_to_check[0]
				best_pos_h = FastestPath.heuristic_function(bot, best_pos)

				for pos in pos_to_check[1:]:
					h = FastestPath.heuristic_function(bot, pos)

					if h < best_pos_h:
						best_pos = pos
						best_pos_h = h

				fp = FastestPath(map, bot_dir, bot, best_pos)
				movements = fp.movements

				if movements == None:
					print(best_pos, [col, row])
					continue
				print(best_pos, [col, row], movements)
				for movement in movements:
					print_map(map, [tuple(bot)])
					print(movement)
					if movement == Movement.RIGHT:
						print('turn right')
						bot_dir = turnRight(bot_dir)
						# sense and update map
						sense(bot, bot_dir)
					elif movement == Movement.FORWARD:
						print('move forward')
						bot = moveForward(bot, bot_dir)
						# sense and update map
						sense(bot, bot_dir)
					elif movement == Movement.LEFT:
						print('turn left')
						bot_dir = turnLeft(bot_dir)
						# sense and update map
						sense(bot, bot_dir)
					else:
						print('turn back')
						bot_dir = turnLeft(bot_dir)
						# sense update map
						sense(bot, bot_dir)
						bot_dir = turnLeft(bot_dir)
						# sense update map
						sense(bot, bot_dir)

						print('move forward')
						bot = moveForward(bot, bot_dir)
						# sense and update map
						sense(bot, bot_dir)

						print('turn back')
						bot_dir = turnLeft(bot_dir)
						# sense update map
						sense(bot, bot_dir)
						bot_dir = turnLeft(bot_dir)
						# sense update map
						sense(bot, bot_dir)

				if best_pos[0] - col == 2:
					correct_direction = Direction.WEST
				elif best_pos[0] - col == -2:
					correct_direction = Direction.EAST
				if best_pos[1] - row == 2:
					correct_direction = Direction.SOUTH
				elif best_pos[1] - row == -2:
					correct_direction = Direction.NORTH

				num_rotate_right = (correct_direction - bot_dir) % 4

				if num_rotate_right == 2:
					print('turn back')
					bot_dir = turnLeft(bot_dir)
					# sense update map
					sense(bot, bot_dir)
					bot_dir = turnLeft(bot_dir)
					# sense update map
					sense(bot, bot_dir)
				elif num_rotate_right == 1:
					print('turn right')
					bot_dir = turnRight(bot_dir)
					# sense and update map
					sense(bot, bot_dir)
				elif num_rotate_right == 3:
					print('turn left')
					bot_dir = turnLeft(bot_dir)
					# sense and update map
					sense(bot, bot_dir)

				return bot, True

	return bot, False

def isPosSafe(x, y):
	global map
	if x < 1 or x > 13 or y < 1 or y > 18:
		return False
	for col in range(x - 1, x + 2):
		for row in range(y - 1, y + 2):
			if map[row][col] == Cell.OBSTACLE or map[row][col] == Cell.UNEXPLORED:
				return False
	return True


def possiblePos(goal):
	d = {}
	x, y = goal
	arr = [[0, -2], [-1, -2], [1, -2], [0, 2], [-1, 2], [1, 2], [2, 0], [2, -1], [2, 1], [-2, 0], [-2, 1], [-2, -1]]
	for i in arr:
		X, Y = x + i[0], y + i[1]
		if isPosSafe(X, Y):
			d[(X, Y)] = 1
	return d


def fastestPath(bot, goal):
	import heapq
	global map
	x, y = bot
	cost = abs(goal[0] - x) + abs(goal[1] - y)
	heap = [[cost, 0, [[x, y]]]]
	visited = {}
	possiblePos = {}
	possiblePos = possiblePos(goal)
	while heap:
		cost, move, path = heapq.heappop(heap)
		x, y = path[len(path) - 1]
		if possiblePos.get(x, y) != None:
			return path
		if len(path) > 1:
			px, py = path[len(path) - 2]
		else:
			px, py = x, y
		visited[(x, y)] = 1
		if x > 1:
			if visited.get((x - 1, y)) == None and map[y][x - 1] != Cell.OBSTACLE and map[y][x - 1] != Cell.UNEXPLORED:
				new_path = path + [[x - 1, y]]
				turnCost = abs(x - 1 - px) % 2 + abs(y - py) % 2
				new_cost = abs(goal[0] - (x - 1)) + abs(goal[1] - y) + move + 1 + turnCost
				heapq.heappush(heap, [new_cost, move + 1, new_path])
		if x < 13:
			if visited.get((x + 1, y)) == None and map[y][x + 1] != Cell.OBSTACLE and map[y][x + 1] != Cell.UNEXPLORED:
				new_path = path + [[x + 1, y]]
				turnCost = abs(x - 1 - px) % 2 + abs(y - py) % 2
				new_cost = abs(goal[0] - (x + 1)) + abs(goal[1] - y) + move + 1 + turnCost
				heapq.heappush(heap, [new_cost, move + 1, new_path])
		if y > 1:
			if visited.get((x, y - 1)) == None and map[y - 1][x] != Cell.OBSTACLE and map[y - 1][x] != Cell.UNEXPLORED:
				new_path = path + [[x, y - 1]]
				turnCost = abs(x - 1 - px) % 2 + abs(y - py) % 2
				new_cost = abs(goal[0] - x) + abs(goal[1] - (y - 1)) + move + 1 + turnCost
				heapq.heappush(heap, [new_cost, move + 1, new_path])
		if y < 18:
			if visited.get((x, y + 1)) == None and map[y + 1][x] != Cell.OBSTACLE and map[y + 1][x] != Cell.UNEXPLORED:
				new_path = path + [[x, y + 1]]
				turnCost = abs(x - 1 - px) % 2 + abs(y - py) % 2
				new_cost = abs(goal[0] - x) + abs(goal[1] - (y + 1)) + move + 1 + turnCost
				heapq.heappush(heap, [new_cost, move + 1, new_path])


# bot dir to east
bot_dir = Direction.EAST

# start
# sense
sense(bot, bot_dir)

# map[bot[1]][bot[0]] = 3  # track bot path
while True:
	print_map(map, [tuple(bot)])
	if check_enter_goal and bot == start:
		break

	if bot == goal:
		check_enter_goal = True
	if checkRight(bot, bot_dir, prev_pos):
		print('turn right')
		bot_dir = turnRight(bot_dir)
		# sense and update map
		sense(bot, bot_dir)
	elif checkForward(bot, bot_dir):
		print('move forward')
		bot = moveForward(bot, bot_dir)
		# sense and update map
		sense(bot, bot_dir)
		# map[bot[1]][bot[0]] = 3  # track bot path
	elif checkLeft(bot, bot_dir):
		print('turn left')
		bot_dir = turnLeft(bot_dir)
		# sense and update map
		sense(bot, bot_dir)
	else:
		print('turn back')
		bot_dir = turnLeft(bot_dir)
		# sense update map
		sense(bot, bot_dir)
		bot_dir = turnLeft(bot_dir)
		# sense update map
		sense(bot, bot_dir)

while True:
	print_map(map, [tuple(bot)])
	bot, can_find = findUnexplored(bot, bot_dir)
	if not can_find:
		break

print_map(map_real, [tuple(bot)])

if __name__ == '__main__':
	pass