from rpi import RPi
from fastest_path import FastestPath
from threading import Thread
from constants import START_POS, GOAL_POS
from robots import RealBot
from enums import Direction
from scratch.exploration import Exploration
from map_descriptor import generate_map
import re


class RealRun:
	def __init__(self):
		with open("maps/map3.txt", "r") as f:
			strs = f.read().split("\n")

		self.explored_map = generate_map(*strs)

		self.robot = RealBot(START_POS, Direction.EAST, self.send_movement, self.receive_sensor)
		# self.explored_map = None
		self.waypoint = None
		self.rpi = RPi()

	def receive_sensor(self):
		while True:
			msg_type, msg = self.rpi.receive_msg_with_type()

			if msg_type == RPi.SENSOR_MSG:
				m = re.match(r"(\d+),\s+(\d+),\s+(\d+),\s+(\d+),\s+(\d+),\s+(\d+)", msg)

				if m is None:
					continue

				sensor_values = [int(m.group(i)) for i in range(1, 7)]
				print("Sensor value:", sensor_values)
				return sensor_values

	def send_movement(self, movement):
		self.rpi.send_movement(movement, self.robot)

	def send_map(self):
		self.rpi.send_map(self.explored_map)

	def communicate_with_rpi(self):
		self.rpi.open_connection()

		while True:
			msg_type, msg = self.rpi.receive_msg_with_type()

			# Exploration
			if msg_type == RPi.EXPLORE_MSG:
				exp = Exploration(self.robot, self.send_map)
				self.explored_map = exp.explored_map
				exp.run_exploration()

			# Waypoint
			elif msg_type == RPi.WAYPOINT_MSG:
				m = re.match(r"\((\d+),\s+(\d+)\)", msg)

				if m is None:
					print("Unable to update waypoint")
					continue

				self.waypoint = (int(m.group(1)), int(m.group(2)))
				print("Waypoint:", self.waypoint)

			# Reposition
			elif msg_type == RPi.REPOSITION_MSG:
				m = re.match(r"\((\d+),\s+(\d+)\)\s+([NSEW])", msg)

				if m is None:
					print("Unable to reposition")
					continue

				self.robot.pos = (int(m.group(1)), int(m.group(2)))
				self.robot.direction = Direction.convert_from_string(m.group(3))

			# Fastest Path
			elif msg_type == RPi.FASTEST_PATH_MSG:
				if self.explored_map is None:
					continue

				fp = FastestPath(self.explored_map, self.robot.direction, START_POS, GOAL_POS, self.waypoint)
				for movement in fp.movements:
					self.robot.move(movement)


if __name__ == '__main__':
	rr = RealRun()
	rpi_thread = Thread(target=rr.communicate_with_rpi)
	rpi_thread.start()
