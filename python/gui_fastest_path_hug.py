from hug_fastest_path import HugFastestPath
from gui import SimulatorGUI


class HugSimulatorGUI(SimulatorGUI):
    def fastest_path(self):
        self.is_running = True
        self.reset()
        self.robot.map = self.map
        self.fp = HugFastestPath(self.robot, explored_map=self.map)
        self.fp.run_fastest_path()
        self.is_running = False


if __name__ == '__main__':
    gui = HugSimulatorGUI()
    gui.start()
