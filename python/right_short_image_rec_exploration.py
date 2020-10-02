from exploration import Exploration
from enums import Cell, Direction, Movement
from map_descriptor import generate_map
from fastest_path import FastestPath
from constants import START_POS, GOAL_POS, NUM_ROWS, NUM_COLS
from robots import SimulatorBot
import time

class ImageRecShort(Exploration):
    def __init__(self, robot, on_update_map=None, on_calibrate=None, explored_map=None, coverage_limit=None, time_limit=None, on_take_photo=None):
        super().__init__(robot, on_update_map=on_update_map, on_calibrate=on_calibrate, explored_map=explored_map, coverage_limit=coverage_limit, time_limit=time_limit)

        self.obstacles ={} # {(pos):{0:0,1:0,2:0,3:0}} 0,1,2,3 represents each side

        if on_take_photo is None:
            self.on_take_photo = lambda obstacles: None
        else:
            self.on_take_photo = on_take_photo

    # check if any of the obstacle side is blocked by another obstacle
    def removeObstacleSide(self,pos): #pos must be tuple
        for i in range(1,4):
            if self.obstacles.get((pos[0]+i,pos[1]))!=None:
                if self.obstacles[pos].get(1)!=None:
                    self.obstacles[pos].pop(1)
                if self.obstacles[(pos[0]+i,pos[1])].get(3)!=None:
                    self.obstacles[(pos[0]+i,pos[1])].pop(3)
            if pos[0]+i >14 and self.obstacles[pos].get(1)!=None:
                self.obstacles[pos].pop(1)
            if self.obstacles.get((pos[0]-i,pos[1]))!=None:
                if self.obstacles[pos].get(3)!=None:
                    self.obstacles[pos].pop(3)
                if self.obstacles[(pos[0]-i,pos[1])].get(1)!=None:
                    self.obstacles[(pos[0]-i,pos[1])].pop(1)
            if pos[0]-i <0 and self.obstacles[pos].get(3)!=None:
                self.obstacles[pos].pop(3)
            if self.obstacles.get((pos[0],pos[1]+i))!=None:
                if self.obstacles[pos].get(0)!=None:
                    self.obstacles[pos].pop(0)
                if self.obstacles[(pos[0],pos[1]+i)].get(2)!=None:
                    self.obstacles[(pos[0],pos[1]+i)].pop(2)
            if pos[1]+ i >19 and self.obstacles[pos].get(0)!=None:
                self.obstacles[pos].pop(0)
            if self.obstacles.get((pos[0],pos[1]-i))!=None:
                if self.obstacles[pos].get(2)!=None:
                    self.obstacles[pos].pop(2)
                if self.obstacles[(pos[0],pos[1]-i)].get(0)!=None:
                    self.obstacles[(pos[0],pos[1]-i)].pop(0)
            if pos[1]-i<0 and self.obstacles[pos].get(2)!=None:
                self.obstacles[pos].pop(2)

    def checkObstacleSide(self,pos,direction): #check for obstacles around the bot
        obstacles = []
        if direction==0:
            if self.obstacles.get((pos[0],pos[1]+2))!=None:
                if self.obstacles[(pos[0],pos[1]+2)].get(2)!=None:
                    self.obstacles[(pos[0],pos[1]+2)].pop(2)
                    obstacles.append((pos[0],pos[1]+2))
        elif direction ==1:
            if self.obstacles.get((pos[0]+2,pos[1]))!=None:
                if self.obstacles[(pos[0]+2,pos[1])].get(3)!=None:
                    self.obstacles[(pos[0]+2,pos[1])].pop(3)
                    obstacles.append((pos[0]+2,pos[1]))
        elif direction ==2:
            if self.obstacles.get((pos[0],pos[1]-2))!=None:
                if self.obstacles[(pos[0],pos[1]-2)].get(0)!=None:
                    self.obstacles[(pos[0],pos[1]-2)].pop(0)
                    obstacles.append((pos[0],pos[1]-2))
        elif direction ==3:
            if self.obstacles.get((pos[0]-2,pos[1]))!=None:
                if self.obstacles[(pos[0]-2,pos[1])].get(1)!=None:
                    self.obstacles[(pos[0]-2,pos[1])].pop(1)
                    obstacles.append((pos[0]-2,pos[1]))
        return obstacles

    def snapObstacleSide(self):
        print('here')
        direction = self.robot.direction
        pos = self.robot.pos
        #if right side got obstacles with sides never see before, take photo
        right = (direction+1)%4
        obstacles = self.checkObstacleSide(pos,right)
        if len(obstacles) != 0:
            self.on_take_photo(obstacles)
            print('right take photo')

    def sense_and_repaint(self, sensor_values=None):
        if sensor_values is None:
            sensor_values = self.robot.sense()

        for i in range(len(sensor_values)):
            sensor_value = sensor_values[i]
            sensor = self.robot.sensors[i]
            direction_vector = Direction.get_direction_vector(sensor.get_current_direction(self.robot))
            current_sensor_pos = sensor.get_current_pos(self.robot)

            if sensor_value == -1:
                continue

            elif sensor_value is None:
                for j in range(*sensor.get_range()):
                    pos_to_mark = (current_sensor_pos[0] + j * direction_vector[0], current_sensor_pos[1] + j * direction_vector[1])

                    if 0 <= pos_to_mark[0] <= NUM_COLS - 1 and 0 <= pos_to_mark[1] <= NUM_ROWS - 1:
                        self.explored_map[pos_to_mark[1]][pos_to_mark[0]] = Cell.FREE

            else:
                for j in range(sensor.get_range()[0], min(sensor.get_range()[1], sensor_value + 1)):
                    pos_to_mark = (current_sensor_pos[0] + j * direction_vector[0], current_sensor_pos[1] + j * direction_vector[1])

                    if 0 <= pos_to_mark[0] <= NUM_COLS - 1 and 0 <= pos_to_mark[1] <= NUM_ROWS - 1:
                        if j != sensor_value:
                            self.explored_map[pos_to_mark[1]][pos_to_mark[0]] = Cell.FREE
                        else:
                            self.explored_map[pos_to_mark[1]][pos_to_mark[0]] = Cell.OBSTACLE
                            if self.obstacles.get(pos_to_mark) == None:
                                self.obstacles[pos_to_mark] = {0: 0, 1: 0, 2: 0, 3: 0}
                                self.removeObstacleSide(pos_to_mark)

        self.on_update_map()

    def move(self, movement, sense=True):
        super(ImageRecShort, self).move(movement, sense)

        if movement == Movement.FORWARD:
            self.snapObstacleSide()

    def run_exploration(self):
        self.start_time = time.time()
        self.sense_and_repaint()

        while True:
            if self.is_limit_exceeded:
                break

            # print_map(self.explored_map, [self.robot.pos])
            if self.entered_goal and self.robot.pos == START_POS:
                break

            if self.robot.pos == GOAL_POS:
                self.entered_goal = True

            if self.check_right():
                self.move(Movement.RIGHT)
                # self.snapObstacleSide()

            elif self.check_forward():
                self.move(Movement.FORWARD)
                # self.snapObstacleSide()

            elif self.check_left():
                self.move(Movement.LEFT)
                # self.snapObstacleSide()

            else:
                self.move(Movement.RIGHT)
                self.move(Movement.RIGHT)
                # self.snapObstacleSide()

        while True:
            if self.is_limit_exceeded:
                break

            unexplored_pos_to_check = self.find_unexplored_to_check()
            can_find = self.fastest_path_to_pos_to_check(unexplored_pos_to_check)

            if not can_find:
                break

        # Go back to start
        fp = FastestPath(self.explored_map, self.robot.direction, self.robot.pos, START_POS)
        movements = fp.movements if isinstance(self.robot, SimulatorBot) else fp.combined_movements()

        if movements is None:
            print("Can't go back to start?")

        for movement in movements:
            if not self.is_running:
                break

            self.move(movement, sense=False)



def main():
    with open("maps/sample_arena5.txt", "r") as f:
        strs = f.read().split("\n")

    map_real = generate_map(*strs)
    bot = SimulatorBot(START_POS, Direction.EAST, lambda m: None)
    bot.map = map_real
    exp = ImageRecShort(bot, lambda: None)
    exp.run_exploration()
    print(exp.obstacles)
    # print_map(exp.explored_map)
    # print_map(map_real)



if __name__ == '__main__':
    main()