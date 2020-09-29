import socket
from enums import Movement, Direction
from map_descriptor import generate_map_descriptor
import re


class RPi:
	HOST = "192.168.4.4"
	# HOST = "127.0.0.1"
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
	TYPE_DIVIDER = ":"

	def __init__(self):
		self.conn = None
		self.is_connected = False

	def open_connection(self):
		try:
			self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			# self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
		msg = self.receive()
		m = re.match(rf"(.+){RPi.TYPE_DIVIDER}(.+)", msg)

		if m is not None:
			return m.group(1), m.group(2)
		else:
			return msg, ""

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

		while True:
			# Sample message: M
			msg_type, msg = self.receive_msg_with_type()

			if msg_type == RPi.MOVEMENT_MSG:
				break

	def send_map(self, explored_map):
		# Sample message: D:FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,000000000400000001C800000000000700000000800000001F80000700000000020000000000
		self.send_msg_with_type(RPi.MDF_MSG, ",".join(generate_map_descriptor(explored_map)))

	def ping(self):
		# Sample message: HELLO
		self.send(RPi.HELLO_MSG)

	def receive_sensor_values(self):
		# Sample message: S
		self.send(RPi.SENSE_MSG)

		while True:
			# Sample message: S:1,1,1,1,1,1
			msg_type, msg = self.receive_msg_with_type()

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

	def take_photo(self, obstacles):
		# Sample message: P
		msg = " ".join(["{},{}".format(*obstacle) for obstacle in obstacles])
		self.send_msg_with_type(RPi.TAKE_PHOTO_MSG, msg)

		while True:
			# Sample message: P
			msg_type, msg = self.receive_msg_with_type()

			if msg_type == RPi.TAKE_PHOTO_MSG:
				print("Photo successfully taken")
				break

	def calibrate(self, is_front=True):
		calibrate_msg = RPi.CALIBRATE_FRONT_MSG if is_front else RPi.CALIBRATE_RIGHT_MSG
		# Sample message: C
		self.send(calibrate_msg)

		while True:
			# Sample message: C
			msg_type, msg = self.receive_msg_with_type()

			if msg_type == calibrate_msg:
				print("Calibration successful")
				break


def main():
	rpi = RPi()
	rpi.open_connection()
	rpi.send("Hello there")
	msg = rpi.receive()
	print(msg)
	rpi.close_connection()


if __name__ == '__main__':
	main()
