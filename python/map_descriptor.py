import math
from constants import NUM_ROWS, NUM_COLS
from enums import Cell
from utils import print_map


def hex_to_bin(hex_str):
	bin_str = "{:b}".format(int(hex_str, 16))
	num_pad_bits = len(hex_str) * 4 - len(bin_str)
	return "0" * num_pad_bits + bin_str


def bin_to_hex(bin_str):
	hex_str = f"{int(bin_str, 2):X}"
	num_pad_bits = math.ceil(len(bin_str) / 4) - len(hex_str)
	return "0" * num_pad_bits + hex_str


def generate_map(explored_str, obstacle_str):
	map_grid = []

	explored_bin = hex_to_bin(explored_str)
	obstacle_bin = hex_to_bin(obstacle_str)

	explored_count = 2
	obstacle_count = 0

	for r in range(NUM_ROWS):
		row = []

		for c in range(NUM_COLS):
			is_explored = explored_bin[explored_count] == "1"
			explored_count += 1

			if is_explored:
				is_obstacle = obstacle_bin[obstacle_count] == "1"
				row.append(Cell.OBSTACLE if is_obstacle else Cell.FREE)
				obstacle_count += 1

			else:
				row.append(Cell.UNEXPLORED)

		map_grid.append(row)

	return map_grid


def generate_map_descriptor(map_grid):
	explored_bin = "11"
	obstacle_bin = ""

	for r in range(NUM_ROWS):
		for c in range(NUM_COLS):
			cell = map_grid[r][c]

			if cell == Cell.UNEXPLORED:
				explored_bin += "0"

			elif cell == Cell.FREE:
				explored_bin += "1"
				obstacle_bin += "0"

			elif cell == Cell.OBSTACLE:
				explored_bin += "1"
				obstacle_bin += "1"

	explored_bin += "11"

	if len(obstacle_bin) % 8 != 0:
		num_pad_bits = 8 - len(obstacle_bin) % 8
		obstacle_bin += "0" * num_pad_bits

	explored_str = bin_to_hex(explored_bin)
	obstacle_str = bin_to_hex(obstacle_bin)

	return explored_str, obstacle_str


def main():
	with open("maps/map1.txt", "r") as f:
		strs = f.read().split("\n")

	map_grid = generate_map(*strs)
	print(generate_map_descriptor(map_grid))
	print_map(map_grid)


if __name__ == "__main__":
	main()
