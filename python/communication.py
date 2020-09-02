import socket


class SocketClient:
	HOST = "192.168.4.4"
	PORT = 5143

	def __init__(self):
		self.conn = None
		self.is_connected = False

	def open_connection(self):
		try:
			self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.conn.connect((SocketClient.HOST, SocketClient.PORT))
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

# class RPi:
# 	def move_robot(self, movement):
# 		print("Moving robot...")

def main():
	sc = SocketClient()
	sc.open_connection()
	sc.send("Hello")
	msg = sc.receive()
	print(msg)


if __name__ == '__main__':
	main()
