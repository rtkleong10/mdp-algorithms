from rpi import RPi
from fastest_path import FastestPath
from exploration_class import Exploration
from threading import Thread
from constants import START_POS, GOAL_POS
from robots import RealBot
from enums import Direction
# from map_descriptor import generate_map
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

		while True:
			msg_type, msg = self.rpi.receive_msg_with_type()

			# Exploration
			if msg_type == RPi.EXPLORE_MSG:
				exp = Exploration(self.robot, self.on_update)
				self.explored_map = exp.explored_map
				exp.run_exploration()

			# Waypoint
			elif msg_type == RPi.WAYPOINT_MSG:
				# Sample message: (1, 1)
				m = re.match(r"\((\d+),\s*(\d+)\)", msg)

				if m is None:
					print("Unable to update waypoint")
					continue

				self.waypoint = (int(m.group(1)), int(m.group(2)))
				print("Waypoint:", self.waypoint)

				self.gui.waypoint = self.waypoint
				self.gui.map = self.explored_map
				self.update_gui()

			# Reposition
			elif msg_type == RPi.REPOSITION_MSG:
				# Sample message: (1, 1) N
				m = re.match(r"\((\d+),\s*(\d+)\)\s*([NSEW])", msg)

				if m is None:
					print("Unable to reposition")
					continue

				self.robot.pos = (int(m.group(1)), int(m.group(2)))
				self.robot.direction = Direction.convert_from_string(m.group(3))
				self.update_gui()

			# Fastest Path
			elif msg_type == RPi.FASTEST_PATH_MSG:
				self.robot.pos = START_POS
				fp = FastestPath(self.explored_map, self.robot.direction, START_POS, GOAL_POS, self.waypoint)
				for movement in fp.movements:
					self.robot.move(movement)

	def display_gui(self):
		self.gui.start()

	def update_gui(self):
		self.gui.map = self.explored_map
		self.gui.update_canvas()

	def on_move(self, movement):
		self.rpi.send_movement(movement, self.robot)
		self.update_gui()

	def on_update(self):
		self.rpi.send_map(self.explored_map)
		self.update_gui()


if __name__ == '__main__':
	rr = RealRun()
	Thread(target=rr.connect_to_rpi).start()
	rr.display_gui()
