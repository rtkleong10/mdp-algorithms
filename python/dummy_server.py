import socket
from threading import Thread

class RPi:
	HOST = "192.168.0.104"
	PORT = 5143

	# Message Types
	EXPLORE_MSG = "EXPLORE"
	FASTEST_PATH_MSG = "FASTEST_PATH"
	WAYPOINT_MSG = "WAYPOINT"
	REPOSITION_MSG = "REPOSITION"
	SENSOR_MSG = "SENSOR"
	MOVEMENT_MSG = "MOVEMENT"
	TYPE_DIVIDER = ": "

	def __init__(self):
		self.server = None
		self.conn = None
		self.is_connected = False

	def open_connection(self):
		try:
			self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.server.bind((RPi.HOST, RPi.PORT))
			self.server.listen(1)
			self.conn, addr = self.server.accept()
			self.is_connected = True
			print("Successfully established connection...")

		except Exception as e:
			print("Unable to establish connection\nError:", e)

	def close_connection(self):
		try:
			self.server.close()
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

	def receive_endlessly(self):
		while True:
			if self.is_connected:
				self.receive()


def main():
	rpi = RPi()
	rpi.open_connection()
	receive_thread = Thread(target=rpi.receive_endlessly, daemon=True)
	receive_thread.start()

	while True:
		msg = input("Message: ")

		if msg in ["q", "Q"]:
			break

		rpi.send(msg)

	rpi.close_connection()


if __name__ == '__main__':
	main()
