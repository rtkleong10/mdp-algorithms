from enums import Cell, Direction, Movement
from utils import print_map, generate_unexplored_map
from map_descriptor import generate_map
from constants import START_POS, GOAL_POS, NUM_ROWS, NUM_COLS
from robots import SimulatorBot

MIN_STEPS_WITHOUT_CALIBRATION = 0

class HugFastestPath:
	def __init__(self, robot, on_calibrate=None, explored_map=None):
		"""
		Args:
			robot (robots.Robot): Robot object to explore the map.
			on_update_map (function): Function called whenever the map is updated.
			explored_map (list): 2D list of Cell objects representing the map.
		"""
		self.robot = robot
		self.prev_pos = None
		self.explored_map = explored_map if explored_map is not None else generate_unexplored_map()
		self.steps_without_calibration = 0
		self.obstacles = {}

		if on_calibrate is None:
			self.on_calibrate = lambda is_front: None
		else:
			self.on_calibrate = on_calibrate

	# find cord wrt the bot based on where it's facing
	def find_right_pos(self):
		direction_vector = Direction.get_direction_vector((self.robot.direction + 1) % 4)
		current_pos = self.robot.pos
		return current_pos[0] + direction_vector[0], current_pos[1] + direction_vector[1]

	# check for surroundings
	def check_surroundings(self, movement):
		check_direction = self.robot.direction

		if movement == Movement.RIGHT:
			check_direction = (check_direction + 1) % 4
		elif movement == Movement.LEFT:
			check_direction = (check_direction - 1) % 4
		elif movement == Movement.BACKWARD:
			check_direction = (check_direction + 2) % 4

		if check_direction == Direction.NORTH:
			return (0, 2), (-1, 2), (1, 2)
		elif check_direction == Direction.EAST:
			return (2, 0), (2, -1), (2, 1)
		elif check_direction == Direction.SOUTH:
			return (0, -2), (-1, -2), (1, -2)
		elif check_direction == Direction.WEST:
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

	def run_fastest_path(self):
		while True:
			if self.robot.pos == GOAL_POS:
				break

			if self.check_right():
				self.move(Movement.RIGHT)

			elif self.check_forward():
				self.move(Movement.FORWARD)

			elif self.check_left():
				self.move(Movement.LEFT)

			else:
				self.move(Movement.LEFT)
				self.move(Movement.LEFT)

	# TODO: Copy from today
	def calibrate(self):
		front_direction = self.robot.direction
		right_direction = (front_direction + 1) % 4
		front_direction_vector = Direction.get_direction_vector(front_direction)
		right_direction_vector = Direction.get_direction_vector(right_direction)

		# Check front
		can_calibrate_front = False
		for i in range(-1, 2):
			c = self.robot.pos[0] + 2 * front_direction_vector[0] + i * right_direction_vector[0]
			r = self.robot.pos[1] + 2 * front_direction_vector[1] + i * right_direction_vector[1]

			if c < 0 or c > NUM_COLS - 1 or r < 0 or r > NUM_ROWS - 1 or self.explored_map[r][c] == Cell.OBSTACLE:
				can_calibrate_front = True
				break

		if can_calibrate_front:
			self.on_calibrate(is_front=True)

		# Check right
		if self.steps_without_calibration > MIN_STEPS_WITHOUT_CALIBRATION:
			can_calibrate_right = True
			for i in [-1, 1]:
				c = self.robot.pos[0] + i * front_direction_vector[0] + 2 * right_direction_vector[0]
				r = self.robot.pos[1] + i * front_direction_vector[1] + 2 * right_direction_vector[1]

				if 0 <= c < NUM_COLS and 0 <= r < NUM_ROWS and self.explored_map[r][c] != Cell.OBSTACLE:
					can_calibrate_right = False

			if can_calibrate_right:
				self.on_calibrate(is_front=False)
				self.steps_without_calibration = 0

	def move(self, movement):
		if not isinstance(movement, Movement) or movement == Movement.FORWARD or movement == Movement.BACKWARD:
			self.prev_pos = self.robot.pos

		self.calibrate()
		self.steps_without_calibration += 1
		self.robot.move(movement)

def main():
	with open("maps/sample_arena5.txt", "r") as f:
		strs = f.read().split("\n")

	map_real = generate_map(*strs)
	bot = SimulatorBot(START_POS, Direction.EAST, lambda m: None)
	bot.map = map_real

	exp = HugFastestPath(bot, lambda: None)
	exp.run_fastest_path()
	print_map(exp.explored_map)
	print_map(map_real)


if __name__ == '__main__':
	main()
