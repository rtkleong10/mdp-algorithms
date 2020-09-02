import time

from constants import NUM_ROWS, NUM_COLS
from enums import Direction, Movement, Cell
# from communication import RPi

class Robot:
	def __init__(self, pos, direction):
		self.pos = pos
		self.direction = direction
		self.sensors = [
			Sensor(False, (0, 1), Direction.NORTH),
			Sensor(True, (1, 1), Direction.NORTH),
			Sensor(True, (1, 1), Direction.EAST),
			Sensor(True, (1, 0), Direction.EAST),
			Sensor(True, (1, -1), Direction.EAST),
			Sensor(True, (1, -1), Direction.SOUTH),
		]

	def move(self, movement):
		if movement == Movement.FORWARD:
			if self.direction == Direction.NORTH:
				self.pos = (self.pos[0], self.pos[1] + 1)
			elif self.direction == Direction.EAST:
				self.pos = (self.pos[0] + 1, self.pos[1])
			elif self.direction == Direction.SOUTH:
				self.pos = (self.pos[0], self.pos[1] - 1)
			elif self.direction == Direction.WEST:
				self.pos = (self.pos[0] - 1, self.pos[1])

		elif movement == Movement.BACKWARD:
			if self.direction == Direction.NORTH:
				self.pos = (self.pos[0], self.pos[1] - 1)
			elif self.direction == Direction.EAST:
				self.pos = (self.pos[0] - 1, self.pos[1])
			elif self.direction == Direction.SOUTH:
				self.pos = (self.pos[0], self.pos[1] + 1)
			elif self.direction == Direction.WEST:
				self.pos = (self.pos[0] + 1, self.pos[1])

		elif movement == Movement.RIGHT:
			self.direction = Direction((self.direction + 1) % 4)

		elif movement == Movement.LEFT:
			self.direction = Direction((self.direction - 1) % 4)

	def sense(self):
		pass

class RealBot(Robot):
	def move(self, movement):
		# Move virtual state
		super().move(movement)

		# Send message to move real robot
		# RPi.move_robot(movement)

	def sense(self):
		pass

class SimulatorBot(Robot):
	def __init__(self, pos, direction):
		super().__init__(pos, direction)
		self.map = []

	def move(self, movement):
		# Wait to simulate robot
		time.sleep(0.3)

		# Move virtual state
		super().move(movement)

	def sense(self):
		sensor_values = []

		for sensor in self.sensors:
			direction_vector = Direction.get_direction_vector(sensor.get_current_direction(self))
			sensor_pos = sensor.get_current_pos(self)
			sensor_range = sensor.get_range()

			for i in range(sensor_range[1]):
				pos_to_check = (sensor_pos[0] + i * direction_vector[0], sensor_pos[1] + i * direction_vector[1])
				if pos_to_check[0] < 0 or pos_to_check[0] >= NUM_COLS or pos_to_check[1] < 0 or pos_to_check[1] >= NUM_ROWS or self.map[pos_to_check[1]][pos_to_check[0]] == Cell.OBSTACLE:

					if i < sensor_range[0]:
						sensor_values.append(-1)
					else:
						sensor_values.append(i)
					break

			else:
				sensor_values.append(None)

		return sensor_values

class Sensor:
	# TODO: Add real ranges
	# Exclusive at upper
	SR_RANGE = (1, 5)
	LR_RANGE = (1, 8)

	def __init__(self, is_short_range, pos, direction):
		self.is_short_range = is_short_range
		self.pos = pos
		self.direction = direction

	def get_range(self):
		if self.is_short_range:
			return Sensor.SR_RANGE
		else:
			return Sensor.LR_RANGE

	def get_current_direction(self, robot):
		return Direction((robot.direction + self.direction - Direction.EAST) % 4)

	def get_current_pos(self, robot):
		if robot.direction == Direction.NORTH:
			return (robot.pos[0] - self.pos[1], robot.pos[1] + self.pos[0])
		elif robot.direction == Direction.EAST:
			return (robot.pos[0] + self.pos[0], robot.pos[1] + self.pos[1])
		elif robot.direction == Direction.SOUTH:
			return (robot.pos[0] + self.pos[1], robot.pos[1] - self.pos[0])
		else: # Direction.WEST
			return (robot.pos[0] - self.pos[0], robot.pos[1] - self.pos[1])
