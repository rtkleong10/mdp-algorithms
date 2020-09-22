from exploration_class import Exploration
from enums import Cell, Direction, Movement
from utils import print_map, generate_unexplored_map
from map_descriptor import generate_map
from fastest_path import FastestPath
from constants import START_POS, GOAL_POS, NUM_ROWS, NUM_COLS
from robots import SimulatorBot
import time

class ImageRegAlgo(Exploration):
    def __init__(self, robot, on_update_map=None, explored_map=None, coverage_limit=None, time_limit=None):
        super().__init__(robot, on_update_map=on_update_map, explored_map=explored_map, coverage_limit=coverage_limit, time_limit=time_limit)
        self.obstacles ={} # {(pos):{0:0,1:0,2:0,3:0}} 0,1,2,3 represents each side

    # check if any of the obstacle side is blocked by another obstacle
    def removeObstacleSide(self,pos): #pos must be tuple
        for i in range(1,4):
            if self.obstacles.get((pos[0]+i,pos[1]))!=None:
                if self.obstacles[pos].get(1)!=None:
                    self.obstacles[pos].pop(1)
                if self.obstacles[(pos[0]+i,pos[1])].get(3)!=None:
                    self.obstacles[(pos[0]+i,pos[1])].pop(3)
            if self.obstacles.get((pos[0]-i,pos[1]))!=None:
                if self.obstacles[pos].get(3)!=None:
                    self.obstacles[pos].pop(3)
                if self.obstacles[(pos[0]-i,pos[1])].get(1)!=None:
                    self.obstacles[(pos[0]-i,pos[1])].pop(1)
            if self.obstacles.get((pos[0],pos[1]+1))!=None:
                if self.obstacles[pos].get(0)!=None:
                    self.obstacles[pos].pop(0)
                if self.obstacles[(pos[0],pos[1]+1)].get(2)!=None:
                    self.obstacles[(pos[0],pos[1]+1)].pop(2)
            if self.obstacles.get((pos[0]+i,pos[1]-1))!=None:
                if self.obstacles[pos].get(2)!=None:
                    self.obstacles[pos].pop(2)
                if self.obstacles[(pos[0]+i,pos[1]-1)].get(0)!=None:
                    self.obstacles[(pos[0]+i,pos[1]-1)].pop(0)

    def checkObstacleSide(self,pos,direction): #check for obstacles within the weird shape
        obstacle = False
        if direction==0:
            for i in range(-1,2):
                for j in range(3,5):
                    if self.obstacles.get((pos[0]+i,pos[1]+j))!=None:
                        if self.obstacles[(pos[0]+i,pos[1]+j)].get(2)!=None:
                            self.obstacles[(pos[0]+i,pos[1]+j)].pop(2)
                            obstacle = True
            if self.obstacles.get((pos[0],pos[1]+2))!=None:
                if self.obstacles[(pos[0],pos[1]+2)].get(2)!=None:
                    self.obstacles[(pos[0],pos[1]+2)].pop(2)
                    obstacle = True     
        elif direction ==1:
            for i in range(3,5):
                for j in range(-1,2):
                    if self.obstacles.get((pos[0]+i,pos[1]+j))!=None:
                        if self.obstacles[(pos[0]+i,pos[1]+j)].get(3)!=None:
                            self.obstacles[(pos[0]+i,pos[1]+j)].pop(3)
                            obstacle = True
            if self.obstacles.get((pos[0]+2,pos[1]))!=None:
                if self.obstacles[(pos[0]+2,pos[1])].get(3)!=None:
                    self.obstacles[(pos[0]+2,pos[1])].pop(3)
                    obstacle = True
        elif direction ==2:
            for i in range(-1,2):
                for j in range(-4,-3):
                    if self.obstacles.get((pos[0]+i,pos[1]+j))!=None:
                        if self.obstacles[(pos[0]+i,pos[1]+j)].get(0)!=None:
                            self.obstacles[(pos[0]+i,pos[1]+j)].pop(0)
                            obstacle = True
            if self.obstacles.get((pos[0],pos[1]-2))!=None:
                if self.obstacles[(pos[0],pos[1]-2)].get(0)!=None:
                    self.obstacles[(pos[0],pos[1]-2)].pop(0)
                    obstacle = True
        elif direction ==3:
            for i in range(-4,-3):
                for j in range(-1,2):
                    if self.obstacles.get((pos[0]+i,pos[1]+j))!=None:
                        if self.obstacles[(pos[0]+i,pos[1]+j)].get(1)!=None:
                            self.obstacles[(pos[0]+i,pos[1]+j)].pop(1)
                            obstacle = True
            if self.obstacles.get((pos[0]-2,pos[1]))!=None:
                if self.obstacles[(pos[0]-2,pos[1])].get(1)!=None:
                    self.obstacles[(pos[0]-2,pos[1])].pop(1)
                    obstacle = True
        return obstacle
        




    
    def snapObstacleSide(self):
        print('here')
        direction = self.robot.direction
        pos = self.robot.pos
        #if left side got obstacles with sides never see before, take photo
        left = (direction-1)%4
        check = self.checkObstacleSide(pos,left)
        if check:
            print('left take photo')
        #if front got obstacles with sides never see before, turn and take photo
        check = self.checkObstacleSide(pos,direction)
        front= False
        if check:
            self.move(Movement.RIGHT)
            print('front take photo')
            front = True
        #if right side got obstacles with sides never see before, turn and take photo
        right = (direction+1)%4
        check = self.checkObstacleSide(pos,right)
        if check:
            if not front:
                self.move(Movement.RIGHT)
            self.move(Movement.RIGHT)
            print('right take photo')
            self.move(Movement.LEFT)
            self.move(Movement.LEFT)
        elif front:
            self.move(Movement.LEFT)
        # if back got obstacles....
        back = (direction+2)%4
        check = self.checkObstacleSide(pos,back)
        if check:
            self.move(Movement.LEFT)
            print('back take photo')
            self.move(Movement.RIGHT)
    
    def sense_and_repaint(self):
        self.on_update_map()
        sensor_values = self.robot.sense()

		# TODO: Handle empty sensor_values (sensor_values = [])
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
                            if self.obstacles.get(pos_to_mark)==None:
                                self.obstacles[pos_to_mark] = {0:0,1:0,2:0,3:0}
                                self.removeObstacleSide(pos_to_mark)

    def run_exploration(self):
        self.start_time = time.time()
        self.sense_and_repaint()

        while True:
            if self.is_limit_exceeded:
                break

            print_map(self.explored_map, [self.robot.pos])
            print()
            if self.entered_goal and self.robot.pos == START_POS:
                break

            if self.robot.pos == GOAL_POS:
                self.entered_goal = True

            if self.check_right():
                self.move(Movement.RIGHT)
                # self.snapObstacleSide()

            elif self.check_forward():
                self.move(Movement.FORWARD)
                self.snapObstacleSide()

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

            can_find = self.find_unexplored()
            if not can_find:
                break

        # Go back to start
        fp = FastestPath(self.explored_map, self.robot.direction, self.robot.pos, START_POS)
        movements = fp.movements

        if movements is None:
            print("Can't go back to start?")

        for movement in movements:
            self.move(movement)

def main():
    with open("maps/sample_arena5.txt", "r") as f:
	    strs = f.read().split("\n")
    
    map_real = generate_map(*strs)
    bot = SimulatorBot(START_POS, Direction.EAST, lambda m: None)
    bot.map = map_real
    exp = ImageRegAlgo(bot, lambda: None)
    exp.run_exploration()
    print(exp.obstacles)
	# print_map(exp.explored_map)
	# print_map(map_real)
    


if __name__ == '__main__':
	main()