from constants import NUM_COLS, NUM_ROWS, START_POS, GOAL_POS
from enums import Cell, Direction, Movement


class Exploration:
	def __init__(self, robot, on_move=None):
		self.robot = robot
		self.explored_map = [[Cell.UNEXPLORED for c in range(NUM_COLS)] for r in range(NUM_ROWS)]

		if on_move is None:
			self.on_move = lambda : None
		else:
			self.on_move = on_move

		for r in range(START_POS[1] - 1, START_POS[1] + 2):
			for c in range(START_POS[0] - 1, START_POS[0] + 2):
				self.explored_map[r][c] = Cell.FREE

		for r in range(GOAL_POS[1] - 1, GOAL_POS[1] + 2):
			for c in range(GOAL_POS[0] - 1, GOAL_POS[0] + 2):
				self.explored_map[r][c] = Cell.FREE

		self.touch_goal = False

	def run_exploration(self):
		self.sense_and_repaint()

		while not self.is_complete():
			self.next_move()

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

	def is_complete(self):
		return self.touch_goal and self.robot.pos == START_POS

	def next_move(self):
		if self.look_right():
			self.robot.move(Movement.RIGHT)
			self.sense_and_repaint()
			self.on_move()
			self.robot.move(Movement.FORWARD)
			self.sense_and_repaint()
			self.on_move()
		elif self.look_front():
			self.robot.move(Movement.FORWARD)
			self.sense_and_repaint()
			self.on_move()
		elif self.look_left():
			self.robot.move(Movement.LEFT)
			self.sense_and_repaint()
			self.on_move()
			self.robot.move(Movement.FORWARD)
			self.sense_and_repaint()
			self.on_move()
		elif self.look_back():
			self.robot.move(Movement.RIGHT)
			self.sense_and_repaint()
			self.on_move()
			self.robot.move(Movement.RIGHT)
			self.sense_and_repaint()
			self.on_move()
			self.robot.move(Movement.FORWARD)
			self.sense_and_repaint()
			self.on_move()

		if self.robot.pos == GOAL_POS:
			self.touch_goal = True

	def look_right(self):
		current_direction = self.robot.direction

		if current_direction == Direction.NORTH:
			return self.east_free()
		elif current_direction == Direction.EAST:
			return self.south_free()
		elif current_direction == Direction.SOUTH:
			return self.west_free()
		else:  # Direction.WEST
			return self.north_free()

	def look_front(self):
		current_direction = self.robot.direction

		if current_direction == Direction.NORTH:
			return self.north_free()
		elif current_direction == Direction.EAST:
			return self.east_free()
		elif current_direction == Direction.SOUTH:
			return self.south_free()
		else:  # Direction.WEST
			return self.west_free()

	def look_left(self):
		current_direction = self.robot.direction

		if current_direction == Direction.NORTH:
			return self.west_free()
		elif current_direction == Direction.EAST:
			return self.north_free()
		elif current_direction == Direction.SOUTH:
			return self.east_free()
		else:  # Direction.WEST
			return self.south_free()

	def look_back(self):
		current_direction = self.robot.direction

		if current_direction == Direction.NORTH:
			return self.south_free()
		elif current_direction == Direction.EAST:
			return self.west_free()
		elif current_direction == Direction.SOUTH:
			return self.north_free()
		else:  # Direction.WEST
			return self.east_free()

	def north_free(self):
		current_pos = self.robot.pos
		r = current_pos[1] + 2

		if r > NUM_ROWS - 1:
			return False

		for i in range(-1, 2):
			if self.explored_map[r][current_pos[0] + i] != Cell.FREE:
				return False

		return True

	def east_free(self):
		current_pos = self.robot.pos
		c = current_pos[0] + 2

		if c > NUM_COLS - 1:
			return False

		for i in range(-1, 2):
			if self.explored_map[current_pos[1] + i][c] != Cell.FREE:
				return False

		return True

	def south_free(self):
		current_pos = self.robot.pos
		r = current_pos[1] - 2

		if r < 0:
			return False

		for i in range(-1, 2):
			if self.explored_map[r][current_pos[0] + i] != Cell.FREE:
				return False

		return True

	def west_free(self):
		current_pos = self.robot.pos
		c = current_pos[0] - 2

		if c < 0:
			return False

		for i in range(-1, 2):
			if self.explored_map[current_pos[1] + i][c] != Cell.FREE:
				return False

		return True
