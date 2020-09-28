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
	robot_direction = Direction((direction - 1) % 4)

	if direction == Direction.NORTH:
		arr = [(x, y + 2), (x - 1, y + 3), (x, y + 3), (x + 1, y + 3)]
	elif direction == Direction.EAST:
		arr = [(x + 2, y), (x + 3, y - 1), (x + 3, y), (x + 3, y + 1)]
	elif direction == Direction.SOUTH:
		arr = [(x, y - 2), (x - 1, y - 3), (x, y - 3), (x + 1, y - 3)]
	elif direction == Direction.WEST:
		arr = [(x - 2, y), (x - 3, y - 1), (x - 3, y), (x - 3, y + 1)]
	else:
		raise ValueError

	for i in arr:
		pos = (x + i[0], y + i[1])

		if self.is_pos_safe(pos):
			d.add((pos, robot_direction))

	return d