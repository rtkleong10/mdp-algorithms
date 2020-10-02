from threading import Thread
from rpi import RPi


class DummyClient(RPi):
	def receive_endlessly(self):
		while True:
			if self.is_connected:
				self.receive()


def main():
	print("Turning on server...")
	c = DummyClient()
	c.open_connection()
	receive_thread = Thread(target=c.receive_endlessly, daemon=True)
	receive_thread.start()

	while True:
		msg = input("Message: ")
		c.send(msg)

	c.close_connection()


if __name__ == '__main__':
	main()
