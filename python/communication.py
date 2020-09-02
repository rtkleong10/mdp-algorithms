import socket
from enums import Movement, Direction
from map_descriptor import generate_map_descriptor

class RPi:
	HOST = "192.168.4.4"
	PORT = 5143

	# Message Types
	EXPLORE_MSG = "EXPLORE"
	FASTEST_PATH_MSG = "FASTEST_PATH"
	SENSOR_MSG = "SENSOR"
	MOVEMENT_MSG = "MOVEMENT"
	TYPE_DIVIDER = ": "

	def __init__(self):
		self.conn = None
		self.is_connected = False

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
			msg = self.conn.recv(bufsize).decode("utf-8")
			print("Message received:", msg)
			return msg

		except Exception as e:
			print("Unable to receive message\nError:", e)

	def send_movement(self, movement, pos, direction, map=None):
		msg = "{}{}{} {}".format(
			RPi.MOVEMENT_MSG,
			RPi.TYPE_DIVIDER,
			Movement.convert_to_string(movement),
			pos,
			Direction.convert_to_string(direction),
		)

		if map is not None:
			msg += " " + ",".join(generate_map_descriptor(map))

		self.send(msg)

	def send_map(self, map):
		msg = ",".join(generate_map_descriptor(map))
		self.send(msg)

	def receive_msg_with_type(self):
		msg = self.receive()
		return msg.split(RPi.TYPE_DIVIDER)


def main():
	rpi = RPi()
	rpi.open_connection()
	rpi.send_movement(Movement.FORWARD, (2, 1), Direction.EAST)
	msg_type, msg = rpi.receive_msg_with_type()
	print(msg_type, msg)
	rpi.close_connection()


if __name__ == '__main__':
	main()
