from enums import Cell, Direction, Movement
from utils import print_map, generate_unexplored_map
from map_descriptor import generate_map
from fastest_path import FastestPath
from constants import START_POS, GOAL_POS, NUM_ROWS, NUM_COLS
from robots import SimulatorBot
import time


class Exploration:
	def __init__(self, robot, on_move=None, coverage_limit=None, time_limit=None):
		"""
		Args:
			robot (robots.Robot): Robot object to explore the map.
		"""
		self.robot = robot
		self.entered_goal = False
		self.prev_pos = None
		self.explored_map = generate_unexplored_map()
		self.start_time = time.time()
		self.coverage_limit = coverage_limit
		self.time_limit = time_limit

		if on_move is None:
			self.on_move = lambda: None
		else:
			self.on_move = on_move

	@property
	def coverage(self):
		return 1 - (sum([row.count(Cell.UNEXPLORED) for row in self.explored_map]) / (NUM_ROWS * NUM_COLS))

	@property
	def time_elapsed(self):
		return time.time() - self.start_time

	@property
	def is_limit_exceeded(self):
		return (self.coverage_limit is not None and self.coverage_limit < self.coverage) or (self.time_limit is not None and self.time_limit < self.time_elapsed + (FastestPath.heuristic_function(self.robot.pos, START_POS) * 2) / self.robot.speed)

	# find cord wrt the bot based on where it's facing
	def find_right_pos(self):
		direction_vector = Direction.get_direction_vector((self.robot.direction + 1) % 4)
		current_pos = self.robot.pos
		return current_pos[0] + direction_vector[0], current_pos[1] + direction_vector[1]

	# check for surroundings
	def check_surroundings(self, movement):
		if self.robot.direction == Direction.EAST:
			if movement == Movement.RIGHT:
				return (0, -2), (-1, -2), (1, -2)
			elif movement == Movement.LEFT:
				return (0, 2), (-1, 2), (1, 2)
			elif movement == Movement.FORWARD:
				return (2, 0), (2, -1), (2, 1)
		elif self.robot.direction == Direction.NORTH:
			if movement == Movement.RIGHT:
				return (2, 0), (2, -1), (2, 1)
			elif movement == Movement.LEFT:
				return (-2, 0), (-2, 1), (-2, -1)
			elif movement == Movement.FORWARD:
				return (0, 2), (-1, 2), (1, 2)
		elif self.robot.direction == Direction.SOUTH:
			if movement == Movement.RIGHT:
				return (-2, 0), (-2, 1), (-2, -1)
			elif movement == Movement.LEFT:
				return (2, 0), (2, -1), (2, 1)
			elif movement == Movement.FORWARD:
				return (0, -2), (-1, -2), (1, -2)
		elif self.robot.direction == Direction.WEST:
			if movement == Movement.RIGHT:
				return (0, 2), (-1, 2), (1, 2)
			elif movement == Movement.LEFT:
				return (0, -2), (-1, -2), (1, -2)
			elif movement == Movement.FORWARD:
				return (-2, 0), (-2, 1), (-2, -1)

	# check if should turn right
	def check_right(self):
		current_pos = self.robot.pos
		obstacle = False

		for x, y in self.check_surroundings(Movement.RIGHT):
			# check wall
			if current_pos[1] + y < 0 or current_pos[1] + y > 19 or current_pos[0] + x < 0 or current_pos[0] + x > 14:
				return False
			# check if right is unexplored
			elif self.explored_map[current_pos[1] + y][current_pos[0] + x] == Cell.UNEXPLORED:
				return True
			# check for obstacles
			elif self.explored_map[current_pos[1] + y][current_pos[0] + x] == Cell.OBSTACLE:
				obstacle = True

		if obstacle:
			return False

		right_pos = self.find_right_pos()
		if right_pos == self.prev_pos:
			return False
		return True

	# check if should move forward
	def check_forward(self):
		current_pos = self.robot.pos

		for x, y in self.check_surroundings(Movement.FORWARD):
			# check wall
			if current_pos[1] + y < 0 or current_pos[1] + y > 19 or current_pos[0] + x < 0 or current_pos[0] + x > 14:
				return False
			# check for obstacles
			elif self.explored_map[current_pos[1] + y][current_pos[0] + x] == Cell.OBSTACLE:
				return False

		return True

	# check if should turn left
	def check_left(self):
		current_pos = self.robot.pos

		for x, y in self.check_surroundings(Movement.LEFT):
			# check wall
			if current_pos[1] + y < 0 or current_pos[1] + y > 19 or current_pos[0] + x < 0 or current_pos[0] + x > 14:
				return False
			# check for obstacles
			elif self.explored_map[current_pos[1] + y][current_pos[0] + x] == Cell.OBSTACLE:
				return False

		return True

	def find_unexplored(self):
		pos_to_check = {}

		for r in range(20):
			for c in range(15):
				if self.explored_map[r][c] == Cell.UNEXPLORED:
					for pos in self.possible_pos((c, r)):
						pos_to_check[pos] = (c, r)

		if len(pos_to_check) == 0:
			return False

		best_pos = min(pos_to_check.keys(), key=lambda pos: FastestPath.heuristic_function(self.robot.pos, pos))
		unexplored_pos = pos_to_check[best_pos]

		fp = FastestPath(self.explored_map, self.robot.direction, self.robot.pos, best_pos)
		movements = fp.movements

		for movement in movements:
			if self.is_limit_exceeded:
				return

			self.move(movement)

		if best_pos[0] - unexplored_pos[0] == 2:
			correct_direction = Direction.WEST
		elif best_pos[0] - unexplored_pos[0] == -2:
			correct_direction = Direction.EAST
		elif best_pos[1] - unexplored_pos[1] == 2:
			correct_direction = Direction.SOUTH
		elif best_pos[1] - unexplored_pos[1] == -2:
			correct_direction = Direction.NORTH
		else:
			raise ValueError

		num_rotate_right = (correct_direction - self.robot.direction) % 4

		if num_rotate_right == 2:
			self.move(Movement.RIGHT)
			self.move(Movement.RIGHT)

		elif num_rotate_right == 1:
			self.move(Movement.RIGHT)

		elif num_rotate_right == 3:
			self.move(Movement.LEFT)

		return True

	def is_pos_safe(self, x, y):
		if x < 1 or x > 13 or y < 1 or y > 18:
			return False

		for col in range(x - 1, x + 2):
			for row in range(y - 1, y + 2):
				if self.explored_map[row][col] == Cell.OBSTACLE or self.explored_map[row][col] == Cell.UNEXPLORED:
					return False

		return True

	def possible_pos(self, goal):
		d = set()
		x, y = goal
		arr = [(0, -2), (-1, -2), (1, -2), (0, 2), (-1, 2), (1, 2), (2, 0), (2, -1), (2, 1), (-2, 0), (-2, 1), (-2, -1)]
		for i in arr:
			pos = (x + i[0], y + i[1])
			if self.is_pos_safe(*pos):
				d.add(pos)

		return d

	def run_exploration(self):
		self.start_time = time.time()
		self.sense_and_repaint()

		while True:
			if self.is_limit_exceeded:
				break

			print_map(self.explored_map, [self.robot.pos])
			if self.entered_goal and self.robot.pos == START_POS:
				break

			if self.robot.pos == GOAL_POS:
				self.entered_goal = True

			if self.check_right():
				self.move(Movement.RIGHT)

			elif self.check_forward():
				self.move(Movement.FORWARD)

			elif self.check_left():
				self.move(Movement.LEFT)

			else:
				self.move(Movement.RIGHT)
				self.move(Movement.RIGHT)

		while True:
			if self.is_limit_exceeded:
				break

			can_find = self.find_unexplored()
			if not can_find:
				break

		# Go back to start
		fp = FastestPath(self.explored_map, self.robot.direction, self.robot.pos, START_POS)
		movements = fp.movements

		if movements is None:
			print("Can't go back to start?")

		for movement in movements:
			self.move(movement)

	def move(self, movement, sense=True):
		if movement == Movement.FORWARD or movement == Movement.BACKWARD:
			self.prev_pos = self.robot.pos

		self.robot.move(movement)

		if sense:
			self.sense_and_repaint()

		self.on_move()

	def sense_and_repaint(self):
		sensor_values = self.robot.sense()

		for i in range(len(sensor_values)):
			sensor_value = sensor_values[i]
			sensor = self.robot.sensors[i]
			direction_vector = Direction.get_direction_vector(sensor.get_current_direction(self.robot))
			current_sensor_pos = sensor.get_current_pos(self.robot)

			if sensor_value == -1:
				continue

			elif sensor_value is None:
				for j in range(*sensor.get_range()):
					pos_to_mark = (current_sensor_pos[0] + j * direction_vector[0], current_sensor_pos[1] + j * direction_vector[1])

					if 0 <= pos_to_mark[0] <= NUM_COLS - 1 and 0 <= pos_to_mark[1] <= NUM_ROWS - 1:
						self.explored_map[pos_to_mark[1]][pos_to_mark[0]] = Cell.FREE

			else:
				for j in range(sensor.get_range()[0], sensor_value + 1):
					pos_to_mark = (current_sensor_pos[0] + j * direction_vector[0], current_sensor_pos[1] + j * direction_vector[1])

					if 0 <= pos_to_mark[0] <= NUM_COLS - 1 and 0 <= pos_to_mark[1] <= NUM_ROWS - 1:
						self.explored_map[pos_to_mark[1]][pos_to_mark[0]] = Cell.FREE if j != sensor_value else Cell.OBSTACLE


def main():
	with open("maps/sample_arena5.txt", "r") as f:
		strs = f.read().split("\n")

	map_real = generate_map(*strs)
	bot = SimulatorBot(START_POS, Direction.EAST, lambda m: None)
	bot.map = map_real

	exp = Exploration(bot, lambda: None)
	exp.run_exploration()
	print_map(exp.explored_map)
	print_map(map_real)


if __name__ == '__main__':
	main()
