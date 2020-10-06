from map_descriptor import generate_map, generate_map_descriptor
from exploration import Exploration
from right_short_image_rec_exploration import ImageRecShort
from gui import SimulatorGUI


class ShortSimulatorGUI(SimulatorGUI):
    def exploration(self):
        self.is_running = True
        self.reset()
        self.robot.map = self.map
        with_image_rec = self.with_image_rec.get() == 1

        # Select exploration class
        exploration_class = ImageRecShort if with_image_rec else Exploration

        self.exp = exploration_class(
            self.robot,
            self.update_canvas,
            coverage_limit=self.coverage_limit_input.get() / 100,
            time_limit=self.time_limit_input.get()
        )

        self.map = self.exp.explored_map
        self.update_canvas()
        self.exp.run_exploration()
        mdf = generate_map_descriptor(self.exp.explored_map)
        print("MDF:", ",".join(mdf))

        if with_image_rec:
            print(self.exp.obstacles)

        self.is_running = False


if __name__ == '__main__':
    gui = ShortSimulatorGUI()
    gui.start()
