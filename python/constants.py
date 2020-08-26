from enum import IntEnum

NUM_ROWS = 20
NUM_COLS = 15
START_POS = (1, 1)
GOAL_POS = (13, 18)

class Cell(IntEnum):
	UNEXPLORED = 0
	FREE = 1
	OBSTACLE = 2