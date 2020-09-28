from rpi import RPi
from fastest_path import FastestPath
from exploration_class import Exploration
from threading import Thread
from constants import START_POS, GOAL_POS, NUM_ROWS, NUM_COLS
from robots import RealBot
from enums import Direction, Cell, Movement
from map_descriptor import generate_map_descriptor
from gui import GUI
from utils import generate_unexplored_map
import re


class RealRun:
	def __init__(self):
		self.rpi = RPi()
		self.robot = RealBot(
			pos=START_POS,
			direction=Direction.EAST,
			on_move=self.on_move,
			get_sensor_values=self.rpi.receive_sensor_values,
		)
		self.explored_map = generate_unexplored_map()
		self.gui = GUI(self.explored_map, self.robot)
		self.waypoint = None

		# with open("maps/map3.txt", "r") as f:
		# 	strs = f.read().split("\n")
		#
		# self.explored_map = generate_map(*strs)

	def connect_to_rpi(self):
		self.rpi.open_connection()
		self.rpi.ping()

		while True:
			msg_type, msg = self.rpi.receive_msg_with_type()

			# Exploration
			if msg_type == RPi.EXPLORE_MSG:
				if self.robot.pos == START_POS:
					self.calibrate()

				exp = Exploration(self.robot, self.on_update, explored_map=self.explored_map, time_limit=360)
				exp.run_exploration()

				mdf = generate_map_descriptor(self.explored_map)
				print("MDF:", ",".join(mdf))
				# TODO: Standardise
				self.rpi.send("Exploration complete!")

			# Waypoint
			elif msg_type == RPi.WAYPOINT_MSG:
				# Sample message: W:1,1
				m = re.match(r"\(?(\d+),\s*(\d+\)?)", msg)

				if m is None:
					print("Unable to update waypoint")
					continue

				self.waypoint = (int(m.group(1)), int(m.group(2)))
				print("Waypoint:", self.waypoint)

				self.gui.waypoint = self.waypoint
				self.update_gui()

			# Reposition
			elif msg_type == RPi.REPOSITION_MSG:
				# Sample message: M:1,1 N
				m = re.match(r"\(?(\d+),\s*(\d+)\)?\s*([NSEW])", msg)

				if m is None:
					print("Unable to reposition")
					continue

				c = int(m.group(1))
				r = int(m.group(2))
				self.robot.pos = (c, r)
				self.robot.direction = Direction.convert_from_string(m.group(3))

				for i in range(max(0, r - 1), min(NUM_ROWS, r + 2)):
					for j in range(max(0, c - 1), min(NUM_COLS, c + 2)):
						self.explored_map[i][j] = Cell.FREE

				self.update_gui()

			# Fastest Path
			elif msg_type == RPi.FASTEST_PATH_MSG:
				# TODO: Calibrate for fastest path
				self.robot.pos = START_POS
				fp = FastestPath(self.explored_map, self.robot.direction, START_POS, GOAL_POS, self.waypoint)
				for movement in fp.movements:
					self.robot.move(movement)

				# TODO: Standardise
				self.rpi.send("Fastest path complete!")

	def display_gui(self):
		self.gui.start()

	def update_gui(self):
		self.gui.update_canvas()

	def on_move(self, movement):
		self.rpi.send_movement(movement, self.robot)
		self.update_gui()

	def on_update(self):
		self.rpi.send_map(self.explored_map)
		self.update_gui()

	def calibrate(self):
		if self.robot.direction == Direction.NORTH:
			# Calibrate with west wall
			self.robot.move(Movement.LEFT)
			self.rpi.calibrate()

			# Calibrate with south wall
			self.robot.move(Movement.LEFT)
			self.rpi.calibrate()

			# Turn back
			self.robot.move(Movement.RIGHT)
			self.robot.move(Movement.RIGHT)

		elif self.robot.direction == Direction.EAST:
			# Calibrate with south wall
			self.robot.move(Movement.RIGHT)
			self.rpi.calibrate()

			# Calibrate with west wall
			self.robot.move(Movement.RIGHT)
			self.rpi.calibrate()

			# Turn back
			self.robot.move(Movement.LEFT)
			self.robot.move(Movement.LEFT)

		elif self.robot.direction == Direction.SOUTH:
			# Calibrate with south wall
			self.rpi.calibrate()

			# Calibrate with west wall
			self.robot.move(Movement.RIGHT)
			self.rpi.calibrate()
			
			# Turn back
			self.robot.move(Movement.LEFT)

		elif self.robot.direction == Direction.WEST:
			# Calibrate with west wall
			self.rpi.calibrate()

			# Calibrate with south wall
			self.robot.move(Movement.LEFT)
			self.rpi.calibrate()

			# Turn back
			self.robot.move(Movement.RIGHT)


if __name__ == '__main__':
	rr = RealRun()
	Thread(target=rr.connect_to_rpi).start()
	rr.display_gui()
