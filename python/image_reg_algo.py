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
        super().__init__(robot, on_update_map=None, explored_map=None, coverage_limit=None, time_limit=None)
        self.obstacles ={} # {(pos):{0:0,1:0,2:0,3:0}} 0,1,2,3 represents each side

    # check if any of the obstacle side is blocked by another obstacle
    def removeObstacleSide(self,pos): #pos must be tuple
        for i in range(1,4):
            if self.obstacles.get((pos[0]+i,pos[1]))!=None:
                self.obstacles[pos].pop(1)
                self.obstacles[(pos[0]+i,pos[1])].pop(3)
            if self.obstacles.get((pos[0]-i,pos[1]))!=None:
                self.obstacles[pos].pop(3)
                self.obstacles[(pos[0]-i,pos[1])].pop(1)
            if self.obstacles.get((pos[0],pos[1]+1))!=None:
                self.obstacles[pos].pop(0)
                self.obstacles[(pos[0],pos[1]+1)].pop(2)
            if self.obstacles.get((pos[0]+i,pos[1]-1))!=None:
                self.obstacles[pos].pop(2)
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
        direction = self.robot.direction
        pos = self.robot.pos
        #if left side got obstacles with sides never see before, take photo
        left = (direction-1)%4
        check = self.checkObstacleSide(pos,left)
        #if check take photo
        right = (direction+1)%4
        check = self.checkObstacleSide(pos,right)
        #if check turn twice and take photo, then turn back
        check = self.checkObstacleSide(pos,direction)
        #if check turn right and take photo then turn back
        


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