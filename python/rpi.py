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

	def receive_msg_with_type(self):
		msg = self.receive()
		m = re.match(rf"(.+){RPi.TYPE_DIVIDER}(.+)", msg)

		if m is not None:
			return m.group(1), m.group(2)
		else:
			return msg, ""

	def send_movement(self, movement, robot, explored_map=None):
		# Sample message: M:F 1,2 E
		msg = "{}{}{} {},{} {}".format(
			RPi.MOVEMENT_MSG,
			RPi.TYPE_DIVIDER,
			Movement.convert_to_string(movement),
			robot.pos[0],
			robot.pos[1],
			Direction.convert_to_string(robot.direction),
		)

		if explored_map is not None:
			msg += " " + ",".join(generate_map_descriptor(explored_map))

		self.send(msg)

	def send_map(self, map):
		# Sample message: D:FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,000000000400000001C800000000000700000000800000001F80000700000000020000000000
		msg = ",".join(generate_map_descriptor(map))
		self.send(msg)

	def ping(self):
		# Sample message: HELLO
		self.send(RPi.HELLO_MSG)

	def receive_sensor_values(self):
		# Sample message: S
		self.send(RPi.SENSE_MSG)

		# Sample message: S:1,1,1,1,1,1
		msg_type, msg = self.receive_msg_with_type()

		if msg_type != RPi.SENSE_MSG:
			return []

		m = re.match(r"(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)", msg)

		if m is None:
			print("Unable to receive sensor input")
			return []

		sensor_values = []

		for i in range(1, 7):
			num = int(m.group(i))
			sensor_values.append(None if num == 0 else num)

		return sensor_values

	def take_photo(self):
		# Sample message: P
		self.send(RPi.TAKE_PHOTO_MSG)

		# Sample message: P
		msg_type, msg = self.receive_msg_with_type()

		if msg_type != RPi.TAKE_PHOTO_MSG:
			print("Unable to take photo")
			return False
		else:
			print("Photo successfully taken")
			return True


def main():
	rpi = RPi()
	rpi.open_connection()
	rpi.send("Hello there")
	msg = rpi.receive()
	print(msg)
	rpi.close_connection()

if __name__ == '__main__':
	main()
