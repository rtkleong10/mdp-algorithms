from fastest_path import map_real, add_virtual_boundaries, create_visibility_graph, dijkstra, START_POS, END_POS, timeit, a_star
from graphics import display_maze
import math

# TODO: Allow for waypoint (need to include in visibility graph)
def perform_fastest_path(map_real):
	map_virtual = add_virtual_boundaries(map_real)
	nodes, edges, weights = create_visibility_graph(map_virtual)
	source = nodes.index(START_POS)
	dest = nodes.index(END_POS)
	# d, pi = dijkstra(nodes, edges, weights, source, dest)
	d, pi = a_star(nodes, edges, weights, source, dest)


	print(nodes)
	print(edges)
	print(weights)
	print(pi)

	steps = []
	cur = dest

	while cur != None:
		steps.append(cur)
		cur = pi[cur]

	steps.reverse()

	# Remove intermediate steps with the same angle to prevent stops
	smoothed_steps = [nodes[steps[0]]]

	for i in range(1, len(steps) - 1):
		prev_pos = nodes[steps[i - 1]]
		cur_pos = nodes[steps[i]]
		next_pos = nodes[steps[i + 1]]

		theta0 = math.atan((cur_pos[1] - prev_pos[1]) / (cur_pos[0] - prev_pos[0]))
		theta1 = math.atan((next_pos[1] - cur_pos[1]) / (next_pos[0] - cur_pos[0]))

		# TODO: Tweak angle threshold (in radians)
		if abs(theta0 - theta1) > 0.01:
			smoothed_steps.append(cur_pos)

	if len(steps) > 1:
		smoothed_steps.append(nodes[steps[-1]])

	for i, step in enumerate(smoothed_steps):
		print("{}.".format(i + 1), step)

	display_maze(map_real, map_virtual, smoothed_steps, nodes, edges)

perform_fastest_path(map_real)