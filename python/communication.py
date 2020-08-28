import socket

HOST = "192.168.4.4"
PORT = 8000

class SocketClient:
	def __init__(self):
		self.conn = None
		self.is_connected = False

	def open_connection(self):
		try:
			self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.conn.connect((HOST, PORT))
			self.is_connected = True

		except Exception as e:
			print("Unable to establish connection\nError:", e)

	def close_connection(self):
		try:
			self.conn.close()
			self.is_connected = False

		except Exception as e:
			print("Unable to close connection\nError:", e)

	def send(self, msg):
		try:
			self.conn.sendall(str.encode(msg))

		except Exception as e:
			print("Unable to send message\nError:", e)


	def receive(self, bufsize=1024):
		try:
			msg = self.conn.recv(bufsize)
			return msg.decode("utf-8")

		except Exception as e:
			print("Unable to receive message\nError:", e)

def main():
	sc = SocketClient()
	sc.open_connection()
	sc.send("Hello")
	msg = sc.receive()
	print(msg)

if __name__ == '__main__':
	main()
