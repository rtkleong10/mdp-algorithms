import tkinter as tk
from gui import GUI
from threading import Thread

from constants import NUM_ROWS, NUM_COLS, START_POS, GOAL_POS
from enums import Cell, Direction
from robots import SimulatorBot
from map_descriptor import generate_map, generate_map_descriptor
import time
from utils import generate_unexplored_map
import re


class ReplayGUI(GUI):
    def __init__(self):
        super(ReplayGUI, self).__init__(generate_unexplored_map(), SimulatorBot(START_POS, Direction.EAST, on_move=lambda movement=None: None))
        with open("logs/test12.txt", "r") as f:
            self.logs = f.read().split("\n")
        self.log_i = 0
        self.is_running = False

    def play(self):
        self.is_running = True

        while self.is_running:
            self.update_from_log()
            self.log_i += 1
            time.sleep(0.1)

    def pause(self):
        self.is_running = False

    def stop(self):
        self.is_running = False
        self.current_log_var.set("")
        self.log_i = 0
        self.map = generate_unexplored_map()
        self.robot = SimulatorBot(START_POS, Direction.EAST, on_move=lambda movement=None: None)
        self.update_canvas()

    def forward(self):
        self.update_from_log()
        self.log_i += 1
        self.update_from_log()

    def backward(self):
        self.update_from_log()
        self.log_i -= 1
        self.update_from_log()

    def update_from_log(self):
        if self.log_i >= len(self.logs):
            self.is_running = False
            return

        current_log = self.logs[self.log_i]
        self.current_log_var.set(current_log)
        current_log = current_log.split(" at ")[0]
        m = re.match(r"(?:Received PC message:|Message sent:|PRINT MESSAGE) (.+)", current_log)

        if m is None:
            return

        full_msg = m.group(1)
        msg_parts = full_msg.split(":")

        if len(msg_parts) != 2:
            return

        msg_type, msg = msg_parts

        if msg_type == "D":
            m = re.match(r"([^,\s]+),([^,\s]+)", msg)

            if m is None:
                return

            self.map = generate_map(m.group(1), m.group(2))
            self.update_canvas()

        elif msg_type == "M":
            m = re.match(r"[\dLRB]\s+(\d+),(\d)\s+([NSEW])", msg)

            if m is None:
                return

            self.robot.pos = (int(m.group(1)), int(m.group(2)))
            self.robot.direction = Direction.convert_from_string(m.group(3))
            self.update_robot()

    def start(self):
        self.root = tk.Tk()
        self.root.title("MDP")

        self.display_side_panel()
        self.display_canvas()

        self.root.mainloop()

    def display_side_panel(self):
        side_panel = tk.Frame(self.root)
        side_panel.pack(side=tk.LEFT, padx=20, pady=20)

        # Error Frame
        tk.Label(side_panel, text="Current Log:").pack()
        self.current_log_var = tk.StringVar()
        self.current_log_var.set("")
        tk.Label(side_panel, textvariable=self.current_log_var, width=50).pack()

        tk.Button(side_panel, text="Play", command=lambda: Thread(target=self.play, daemon=True).start()).pack()
        tk.Button(side_panel, text="Pause", command=self.pause).pack()
        tk.Button(side_panel, text="Stop", command=self.stop).pack()
        tk.Button(side_panel, text="Forward", command=self.forward).pack()
        tk.Button(side_panel, text="Backward", command=self.backward).pack()

if __name__ == '__main__':
    gui = ReplayGUI()
    gui.start()
