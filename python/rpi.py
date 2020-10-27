import socket
from enums import Movement, Direction
from map_descriptor import generate_map_descriptor
import re
from collections import deque
from datetime import datetime
import time


class RPi:
	HOST = "192.168.4.4"
	PORT = 4444

	# Message Types
	HELLO_MSG = "HELLO"
	CALIBRATE_MSG = "C"
	CALIBRATE_FRONT_MSG = "f"
	CALIBRATE_RIGHT_MSG = "r"
	EXPLORE_MSG = "E"
	FASTEST_PATH_MSG = "F"
	WAYPOINT_MSG = "W"
	REPOSITION_MSG = "R"
	SENSE_MSG = "S"
	TAKE_PHOTO_MSG = "P"
	MOVEMENT_MSG = "M"
	MDF_MSG = "D"
	HIGH_SPEED_MSG = "H"
	LOW_SPEED_MSG = "T"
	QUIT_MSG = "Q"
	TYPE_DIVIDER = ":"

	def __init__(self, on_quit=None):
		self.conn = None
		self.is_connected = False
		self.on_quit = on_quit if on_quit is not None else lambda: None
		self.queue = deque([])

	def open_connection(self):
		try:
			self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.conn.connect((RPi.HOST, RPi.PORT))
			self.is_connected = True
			print("Successfully established connection...")

		except Exception as e:
			print("Unable to establish connection\nError:", e)

	def close_connection(self):
		try:
			self.conn.close()
			self.is_connected = False
			print("Successfully closed connection")

		except Exception as e:
			print("Unable to close connection\nError:", e)

	def send(self, msg):
		try:
			self.conn.sendall(str.encode(msg))
			print("Message sent:", msg)

		except Exception as e:
			print("Unable to send message\nError:", e)

	def receive(self, bufsize=2048):
		try:
			print("Receiving RPI message: " + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
			msg = self.conn.recv(bufsize).decode("utf-8")
			print("Message received:", msg)
			return msg

		except Exception as e:
			print("Unable to receive message\nError:", e)

	def send_msg_with_type(self, msg_type, msg=None):
		full_msg = msg_type

		if msg is not None:
			full_msg += RPi.TYPE_DIVIDER + msg

		self.send(full_msg)

	def receive_msg_with_type(self):
		if len(self.queue) < 1:
			time.sleep(0.01)
			return "", ""

		full_msg = self.queue.popleft()
		if full_msg is None:
			return "", ""
		full_msg = full_msg.strip()
		m = full_msg.split(RPi.TYPE_DIVIDER)

		if len(m) > 1:
			msg_type, msg = m[0], RPi.TYPE_DIVIDER.join(m[1:])
		else:
			msg_type, msg = full_msg, ""

		if msg_type == RPi.QUIT_MSG:
			self.on_quit()

		return msg_type, msg

	def ping(self):
		# Sample message: HELLO
		self.send(RPi.HELLO_MSG)

	def send_movement(self, movement, robot):
		print(movement)
		if movement == Movement.FORWARD:
			movement_str = "1"
		elif isinstance(movement, Movement):
			movement_str = Movement.convert_to_string(movement)
		else:
			movement_str = str(movement)

		# Sample message: M:R 1,2 E
		msg = "{} {},{} {}".format(
			movement_str,
			robot.pos[0],
			robot.pos[1],
			Direction.convert_to_string(robot.direction),
		)
		self.send_msg_with_type(RPi.MOVEMENT_MSG, msg)
		return self.receive_sensor_values(send_msg=False)

	def send_map(self, explored_map):
		# Sample message: D:FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,000000000400000001C800000000000700000000800000001F80000700000000020000000000
		self.send_msg_with_type(RPi.MDF_MSG, ",".join(generate_map_descriptor(explored_map)))

	def receive_sensor_values(self, send_msg=True):
		# Sample message: S
		if send_msg:
			self.send(RPi.SENSE_MSG)

		sent_time = time.time()

		while True:
			# Ask for sense message again if it's been too long
			if time.time() - sent_time > 3:
				self.send(RPi.SENSE_MSG)
				sent_time = time.time()

			# Sample message: S:1,1,1,1,1,1
			msg_type, msg = self.receive_msg_with_type()

			if msg_type == RPi.QUIT_MSG:
				return []

			if msg_type != RPi.SENSE_MSG:
				continue

			m = re.match(r"(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)", msg)

			if m is None:
				print("Unable to receive sensor input")
				return []
			else:
				sensor_values = []

				for i in range(1, 7):
					num = int(m.group(i))

					if num < 0:
						sensor_values.append(-1)
					elif num == 0:
						sensor_values.append(None)
					else:
						sensor_values.append(num)

				return sensor_values

	def take_photo(self, obstacles, robot=None):
		# Sample message: P:7,2,1
		if len(obstacles) != 0:
			msg = "Y {},{},{}".format(*(obstacles[0]))
		elif robot is not None:
			msg = "N {},{},{}".format(*robot.pos, int(robot.direction))
		else:
			return

		self.send_msg_with_type(RPi.TAKE_PHOTO_MSG, msg)

	def calibrate(self, is_front=True):
		# Sample message: f
		calibrate_msg = RPi.CALIBRATE_FRONT_MSG if is_front else RPi.CALIBRATE_RIGHT_MSG
		self.send(calibrate_msg)
		sent_time = time.time()

		while True:
			# Ask for calibrate message again if it's been too long
			if time.time() - sent_time > 3:
				self.send(calibrate_msg)
				sent_time = time.time()

			# Sample message: f
			msg_type, msg = self.receive_msg_with_type()

			if msg_type == RPi.QUIT_MSG:
				break

			if msg_type == calibrate_msg:
				print("Calibration successful")
				break

	def set_speed(self, is_high=True):
		# Sample message: H
		speed_msg = RPi.HIGH_SPEED_MSG if is_high else RPi.LOW_SPEED_MSG
		self.send(speed_msg)

	def receive_endlessly(self):
		while True:
			msg = self.receive()
			self.queue.append(msg)


def main():
	rpi = RPi()
	rpi.open_connection()
	rpi.send("Hello there")
	msg = rpi.receive()
	print(msg)
	rpi.close_connection()


if __name__ == '__main__':
	main()
