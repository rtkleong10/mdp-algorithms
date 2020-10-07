from exploration import Exploration
from enums import Cell, Direction, Movement
from utils import print_map, generate_unexplored_map
from map_descriptor import generate_map
from fastest_path import FastestPath
from constants import START_POS, GOAL_POS, NUM_ROWS, NUM_COLS
from robots import SimulatorBot
import time

class ImageRecExploration(Exploration):
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

    def checkObstacleSide(self,pos,direction): #check for obstacles within the weird shape
        obstacles = []
        if direction==0:
            for i in range(-1,2):
                for j in range(3,4): #change to 2 grid away
                    if self.obstacles.get((pos[0]+i,pos[1]+j))!=None:
                        if self.obstacles[(pos[0]+i,pos[1]+j)].get(2)!=None:
                            self.obstacles[(pos[0]+i,pos[1]+j)].pop(2)
                            obstacles.append((pos[0]+i,pos[1]+j))
            if self.obstacles.get((pos[0],pos[1]+2))!=None:
                if self.obstacles[(pos[0],pos[1]+2)].get(2)!=None:
                    self.obstacles[(pos[0],pos[1]+2)].pop(2)
                    obstacles.append((pos[0],pos[1]+2))
        elif direction ==1:
            for i in range(3,4): #change to 2 grid away
                for j in range(-1,2):
                    if self.obstacles.get((pos[0]+i,pos[1]+j))!=None:
                        if self.obstacles[(pos[0]+i,pos[1]+j)].get(3)!=None:
                            self.obstacles[(pos[0]+i,pos[1]+j)].pop(3)
                            obstacles.append((pos[0]+i,pos[1]+j))
            if self.obstacles.get((pos[0]+2,pos[1]))!=None:
                if self.obstacles[(pos[0]+2,pos[1])].get(3)!=None:
                    self.obstacles[(pos[0]+2,pos[1])].pop(3)
                    obstacles.append((pos[0]+2,pos[1]))
        elif direction ==2:
            for i in range(-1,2):
                for j in range(-3,-2): #change to 2 grid away
                    if self.obstacles.get((pos[0]+i,pos[1]+j))!=None:
                        if self.obstacles[(pos[0]+i,pos[1]+j)].get(0)!=None:
                            self.obstacles[(pos[0]+i,pos[1]+j)].pop(0)
                            obstacles.append((pos[0]+i,pos[1]+j))
            if self.obstacles.get((pos[0],pos[1]-2))!=None:
                if self.obstacles[(pos[0],pos[1]-2)].get(0)!=None:
                    self.obstacles[(pos[0],pos[1]-2)].pop(0)
                    obstacles.append((pos[0],pos[1]-2))
        elif direction ==3:
            for i in range(-3,-2): #change to 2 grid away
                for j in range(-1,2):
                    if self.obstacles.get((pos[0]+i,pos[1]+j))!=None:
                        if self.obstacles[(pos[0]+i,pos[1]+j)].get(1)!=None:
                            self.obstacles[(pos[0]+i,pos[1]+j)].pop(1)
                            obstacles.append((pos[0]+i,pos[1]+j))
            if self.obstacles.get((pos[0]-2,pos[1]))!=None:
                if self.obstacles[(pos[0]-2,pos[1])].get(1)!=None:
                    self.obstacles[(pos[0]-2,pos[1])].pop(1)
                    obstacles.append((pos[0]-2,pos[1]))
        return obstacles

    def snapObstacleSide(self):
        print('here')
        direction = self.robot.direction
        pos = self.robot.pos
        #if left side got obstacles with sides never see before, take photo
        left = (direction-1)%4
        obstacles = self.checkObstacleSide(pos,left)
        if len(obstacles) != 0:
            self.on_take_photo(obstacles)
            print('left take photo')
        #if front got obstacles with sides never see before, turn and take photo
        obstacles = self.checkObstacleSide(pos,direction)
        front= False
        if len(obstacles) != 0:
            self.move(Movement.RIGHT)
            self.on_take_photo(obstacles)
            print('front take photo')
            front = True
        #if right side got obstacles with sides never see before, turn and take photo
        right = (direction+1)%4
        obstacles = self.checkObstacleSide(pos,right)
        right = False
        if len(obstacles) != 0:
            if not front:
                self.move(Movement.RIGHT)
            self.move(Movement.RIGHT)
            self.on_take_photo(obstacles)
            print('right take photo')
            right = True
        elif front:
            self.move(Movement.LEFT)
        # if back got obstacles....
        back = (direction+2)%4
        obstacles = self.checkObstacleSide(pos,back)
        if len(obstacles) != 0:
            if not right:
                self.move(Movement.LEFT)
            else:
                self.move(Movement.RIGHT)
            print('back take photo')
            self.on_take_photo(obstacles)
            self.move(Movement.RIGHT)
        elif right:
            self.move(Movement.LEFT)
            self.move(Movement.LEFT)

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
        super(ImageRecExploration, self).move(movement, sense)

        if movement == Movement.FORWARD:
            self.snapObstacleSide()

    def explore_unseen(self):
        while True:
            if self.is_limit_exceeded:
                break

            unseen_pos_to_check = self.find_unseen_to_check()
            can_find = self.fastest_path_to_pos_to_check(unseen_pos_to_check)

            if can_find:
                self.snapObstacleSide()

            else:
                break

    def run_exploration(self):
        self.start_time = time.time()
        self.sense_and_repaint()
        self.right_hug()
        self.explore_unexplored()
        self.explore_unseen()
        self.fastest_path_to_start()

    def find_unseen_to_check(self):
        pos_to_check = {}

        for obstacle_pos in self.obstacles:
            for obstacle_direction in self.obstacles[obstacle_pos]:
                for pos, direction in self.possible_photo_pos(obstacle_pos, obstacle_direction):
                    pos_to_check[pos] = direction

        return pos_to_check


    def possible_photo_pos(self, goal, direction):
        d = set()
        x, y = goal
        if direction == Direction.NORTH:
            arr = [(0, 2), (-1, 3), (0, 3), (1, 3)]
        elif direction == Direction.EAST:
            arr = [(2, 0), (3, -1), (3, 0), (3, 1)]
        elif direction == Direction.SOUTH:
            arr = [(0, -2), (-1, -3), (0, -3), (1, -3)]
        elif direction == Direction.WEST:
            arr = [(-2, 0), (-3, -1), (-3, 0), (-3, 1)]
        else:
            raise ValueError

        for i in arr:
            pos = (x + i[0], y + i[1])

            if self.is_pos_safe(pos):
                d.add((pos, None))

        return d

def main():
    with open("../maps/sample_arena5.txt", "r") as f:
        strs = f.read().split("\n")

    map_real = generate_map(*strs)
    bot = SimulatorBot(START_POS, Direction.EAST, lambda m: None)
    bot.map = map_real
    exp = ImageRecExploration(bot, lambda: None)
    exp.run_exploration()
    print(exp.obstacles)
    # print_map(exp.explored_map)
    # print_map(map_real)



if __name__ == '__main__':
    main()