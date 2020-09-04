import tkinter as tk
from tkinter.font import Font
from constants import NUM_ROWS, NUM_COLS, START_POS, GOAL_POS
from enums import Cell, Direction
from robots import SimulatorBot
from map_descriptor import generate_map, generate_map_descriptor
from fastest_path import FastestPath
from exploration_class import Exploration
import threading


# TODO: Add timer & coverage % display
class GUI:
    # Size
    CELL_SIZE = 40

    # Colours
    BLACK = "#2E3134"
    LIGHT_GREY = "#D4DFE7"
    DARK_GREY = "#737880"
    WHITE = "#FFFFFF"
    RED = "#CB7373"
    BLUE = "#589DCE"
    YELLOW = "#DABF56"

    # TAGS
    MAP_TAG = "map"
    ROBOT_TAG = "robot"

    # MAP OPTIONS
    MAP_OPTIONS = {
        "Sample Arena 1": "maps/sample_arena1.txt",
        "Sample Arena 2": "maps/sample_arena2.txt",
        "Sample Arena 3": "maps/sample_arena3.txt",
        "Sample Arena 4": "maps/sample_arena4.txt",
        "Sample Arena 5": "maps/sample_arena5.txt",
        "Custom": None,
    }

    # SPEED
    MIN_SPEED = 1
    MAX_SPEED = 10

    def __init__(self):
        with open("maps/sample_arena1.txt", "r") as f:
            strs = f.read().split("\n")

        self.selected_map = generate_map(*strs)
        self.map = self.selected_map.copy()
        self.canvas = None
        self.selected_map_str = None
        self.mdf_input = None
        self.root = None
        self.has_waypoint = None
        self.waypoint_x = None
        self.waypoint_y = None
        self.waypoint = None
        self.robot = SimulatorBot(START_POS, Direction.EAST)
        self.current_thread = None
        self.error_frame = None
        self.robot_speed = None

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
        self.error_frame = tk.Frame(side_panel)
        self.error_frame.pack(fill=tk.X, pady=10)

        # Algorithms Frame
        algorithms_frame = tk.Frame(side_panel)
        algorithms_frame.pack(fill=tk.X, pady=10)

        self.create_heading(algorithms_frame, "Algorithms").pack()
        self.create_button(algorithms_frame, "Exploration", lambda: self.execute_thread(self.exploration)) \
            .pack(fill=tk.X, pady=5)
        self.create_button(algorithms_frame, "Fastest Path", lambda: self.execute_thread(self.fastest_path)) \
            .pack(fill=tk.X, pady=5)
        self.create_button(algorithms_frame, "Reset", lambda: self.execute_thread(self.reset)) \
            .pack(fill=tk.X, pady=5)

        # Map Select Frame
        map_select_frame = tk.Frame(side_panel)
        map_select_frame.pack(fill=tk.X, pady=10)

        self.create_heading(map_select_frame, "Select Map").pack()

        map_option_strs = list(GUI.MAP_OPTIONS.keys())
        self.selected_map_str = tk.StringVar()
        self.selected_map_str.set(map_option_strs[0])
        tk.OptionMenu(map_select_frame, self.selected_map_str, *map_option_strs).pack()

        self.create_heading(map_select_frame, "If custom, please specify second MDF string", is_small=True).pack()
        self.mdf_input = tk.Entry(map_select_frame)
        self.mdf_input.pack(fill=tk.X)

        self.create_button(map_select_frame, "Load Map", lambda: self.execute_thread(self.load_map), True)\
            .pack(fill=tk.X)

        # Waypoint Frame
        waypoint_frame = tk.Frame(side_panel)
        waypoint_frame.pack(fill=tk.X, pady=10)

        self.create_heading(waypoint_frame, "Waypoint").pack()

        self.has_waypoint = tk.IntVar()
        tk.Checkbutton(waypoint_frame, text="Use waypoint", variable=self.has_waypoint).pack()

        tk.Label(waypoint_frame, text="X").pack(side=tk.LEFT)
        self.waypoint_x = tk.Entry(waypoint_frame)
        self.waypoint_x.pack(fill=tk.X, side=tk.LEFT)

        tk.Label(waypoint_frame, text="Y").pack(side=tk.LEFT)
        self.waypoint_y = tk.Entry(waypoint_frame)
        self.waypoint_y.pack(fill=tk.X, side=tk.LEFT)

        # Speed Setting
        speed_frame = tk.Frame(side_panel)
        speed_frame.pack(fill=tk.X, pady=10)

        self.create_heading(speed_frame, "Robot Speed (Moves Per Second)").pack(fill=tk.X)

        self.robot_speed = tk.IntVar()
        self.robot_speed.set(5)
        tk.Spinbox(speed_frame, from_=GUI.MIN_SPEED, to=GUI.MAX_SPEED, textvariable=self.robot_speed).pack(fill=tk.X)
        self.create_button(speed_frame, "Update Speed", self.update_speed, True).pack(fill=tk.X)

    def update_speed(self):
        self.robot.speed = self.robot_speed.get()

    def display_error_msg(self, text):
        label = tk.Label(self.error_frame, text=text, fg=GUI.RED)
        label.pack()
        label.after(3000, lambda: label.destroy())

    @staticmethod
    def create_heading(master, text, is_small=False):
        return tk.Label(
            master,
            text=text,
            font=Font(family="Helvetica", size=18 if is_small else 20, weight="normal" if is_small else "bold"),
        )

    @staticmethod
    def create_button(master, text, command, is_small=False):
        return tk.Button(
            master,
            text=text,
            font=Font(family="Helvetica", size=16 if is_small else 18),
            command=command,
            pady=5 if is_small else 10,
        )

    def display_canvas(self):
        self.canvas = tk.Canvas(self.root, height=NUM_ROWS * GUI.CELL_SIZE, width=NUM_COLS * GUI.CELL_SIZE, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=20, pady=20)
        self.display_map()
        self.display_robot()

    def display_map(self):
        self.canvas.delete(GUI.MAP_TAG)

        for r in range(NUM_ROWS):
            for c in range(NUM_COLS):
                cell = self.map[r][c]
                x = c * GUI.CELL_SIZE
                y = (NUM_ROWS - 1 - r) * GUI.CELL_SIZE

                if c in range(START_POS[0] - 1, START_POS[0] + 2) and r in range(START_POS[1] - 1, START_POS[1] + 2):
                    color = GUI.BLUE
                elif c in range(GOAL_POS[0] - 1, GOAL_POS[0] + 2) and r in range(GOAL_POS[1] - 1, GOAL_POS[1] + 2):
                    color = GUI.RED
                elif (c, r) == self.waypoint:
                    color = GUI.YELLOW
                elif cell == Cell.UNEXPLORED:
                    color = GUI.DARK_GREY
                elif cell == Cell.FREE:
                    color = GUI.LIGHT_GREY
                else:  # Obstacle
                    color = GUI.BLACK

                self.canvas.create_rectangle(
                    x,
                    y,
                    x + GUI.CELL_SIZE,
                    y + GUI.CELL_SIZE,
                    width=6,
                    outline=GUI.WHITE,
                    fill=color,
                    tag=GUI.MAP_TAG,
                )

    def display_robot(self):
        self.canvas.delete(GUI.ROBOT_TAG)

        x = (self.robot.pos[0] - 0.5) * GUI.CELL_SIZE
        y = (NUM_ROWS - 1.5 - self.robot.pos[1]) * GUI.CELL_SIZE
        self.canvas.create_oval(
            x,
            y,
            x + 2 * GUI.CELL_SIZE,
            y + 2 * GUI.CELL_SIZE,
            width=0,
            fill=GUI.BLACK,
            tag=GUI.ROBOT_TAG,
        )

        if self.robot.direction == Direction.NORTH:
            self.canvas.create_rectangle(
                x + GUI.CELL_SIZE - 4,
                y + 10,
                x + GUI.CELL_SIZE + 4,
                y + 26,
                width=0, fill=GUI.WHITE, tag=GUI.ROBOT_TAG
            )

        elif self.robot.direction == Direction.EAST:
            self.canvas.create_rectangle(
                x + 2 * GUI.CELL_SIZE - 26,
                y + GUI.CELL_SIZE - 4,
                x + 2 * GUI.CELL_SIZE - 10,
                y + GUI.CELL_SIZE + 4,
                width=0, fill=GUI.WHITE, tag=GUI.ROBOT_TAG
            )

        elif self.robot.direction == Direction.SOUTH:
            self.canvas.create_rectangle(
                x + GUI.CELL_SIZE - 4,
                y + 2 * GUI.CELL_SIZE - 26,
                x + GUI.CELL_SIZE + 4,
                y + 2 * GUI.CELL_SIZE - 10,
                width=0, fill=GUI.WHITE, tag=GUI.ROBOT_TAG
            )

        elif self.robot.direction == Direction.WEST:
            self.canvas.create_rectangle(
                x + 10,
                y + GUI.CELL_SIZE - 4,
                x + 26,
                y + GUI.CELL_SIZE + 4,
                width=0, fill=GUI.WHITE, tag=GUI.ROBOT_TAG
            )

    def get_waypoint(self):
        if self.has_waypoint.get() != 1:
            return None

        try:
            x = int(self.waypoint_x.get())
            y = int(self.waypoint_y.get())

            if x < 0 or x >= NUM_COLS or y < 0 or y >= NUM_ROWS or self.map[y][x] != Cell.FREE:
                self.display_error_msg("Invalid Waypoint")
                return None

            return x, y

        except ValueError:
            self.display_error_msg("Invalid Waypoint")

        return None

    def update_map(self):
        self.display_map()
        self.display_robot()

    def exploration(self):
        self.reset()
        self.robot.map = self.map
        exp = Exploration(self.robot, self.update_map)
        self.map = exp.explored_map
        self.update_map()
        exp.run_exploration()
        print(generate_map_descriptor(exp.explored_map))

    def fastest_path(self):
        self.reset(False)

        waypoint = self.get_waypoint()

        if waypoint is not None:
            self.waypoint = waypoint
            self.display_map()
            self.display_robot()

        fp = FastestPath(self.map, Direction.EAST, START_POS, GOAL_POS, waypoint)

        if fp.path_found:
            for movement in fp.movements:
                self.robot.move(movement)
                self.display_robot()

        else:
            self.display_error_msg("No path found")

    def reset(self, reset_map=True):
        self.waypoint = None

        if reset_map:
            self.map = self.selected_map.copy()
            self.display_map()

        self.robot = SimulatorBot(START_POS, Direction.EAST)
        self.update_speed()
        self.display_robot()

    def load_map(self):
        selected_map = GUI.MAP_OPTIONS[self.selected_map_str.get()]

        if selected_map is not None:
            with open(selected_map, "r") as f:
                strs = f.read().split("\n")

            self.selected_map = generate_map(*strs)
            self.reset()

        else:
            try:
                self.selected_map = generate_map("F" * 75, self.mdf_input.get())
                self.reset()

            except (IndexError, ValueError):
                self.display_error_msg("Invalid Map Descriptor")

    def execute_thread(self, method):
        if self.current_thread is not None and self.current_thread.is_alive():
            return

        self.current_thread = threading.Thread(target=method, daemon=True)
        self.current_thread.start()


if __name__ == '__main__':
    gui = GUI()
    gui.start()
