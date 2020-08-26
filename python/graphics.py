import pygame
from fastest_path import euclidean_distance

LINE_WIDTH = 10
BLOCK_SIZE = 40

BLACK = (0, 0, 0)
LIGHT_GREY = (237, 237, 237)
DARK_GREY = (200, 200, 200)
WHITE = (255, 255, 255)
LIGHT_RED = (255, 180, 180)
RED = (255, 0, 0)
BLUE = (0, 180, 255)
GREEN = (180, 230, 230)
WINDOW_HEIGHT = BLOCK_SIZE * 20
WINDOW_WIDTH = BLOCK_SIZE * 15

def display_maze(map_real, map_virtual, steps, nodes, edges):
    global SCREEN, CLOCK
    pygame.init()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    win.fill(BLACK)
    current_distance = 0

    while True:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        draw_map(win, map_real, map_virtual)
        # draw_edges(win, len(map_real), nodes, edges)
        draw_steps(win, len(map_real), steps)
        if draw_robot(win, len(map_real), steps, current_distance):
            current_distance = 10
        else:
            current_distance += 10

        pygame.display.update()


def draw_map(win, map_real, map_virtual):
    for y in range(len(map_real)):
        for x in range(len(map_real[y])):
            real = map_real[y][x]
            virtual = map_virtual[y][x]

            rect = pygame.Rect(x * BLOCK_SIZE, (len(map_real) - 1 - y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)

            if (x in range(0, 3) and y in range(0, 3)) or (x in range(12, 15) and y in range(17, 20)):
                pygame.draw.rect(win, BLUE, rect, 0)
            elif real == 1:
                pygame.draw.rect(win, BLACK, rect, 0)
            elif virtual == 1:
                pygame.draw.rect(win, DARK_GREY, rect, 0)
            else:
                pygame.draw.rect(win, WHITE, rect, 0)

            pygame.draw.rect(win, LIGHT_GREY, rect, LINE_WIDTH // 3)

def draw_edges(win, num_rows, nodes, edges):
    for edge in edges:
        node0 = nodes[edge[0]]
        node1 = nodes[edge[1]]
        start_pos = (node0[0] * BLOCK_SIZE + BLOCK_SIZE // 2, (num_rows - 1 - node0[1]) * BLOCK_SIZE + BLOCK_SIZE // 2)
        end_pos = (node1[0] * BLOCK_SIZE + BLOCK_SIZE // 2, (num_rows - 1 - node1[1]) * BLOCK_SIZE + BLOCK_SIZE // 2)
        pygame.draw.line(win, GREEN, start_pos, end_pos, LINE_WIDTH // 3)

def draw_steps(win, num_rows, steps):
    end_pos = None
    for i in range(len(steps) - 1):
        start_pos = (steps[i][0] * BLOCK_SIZE + BLOCK_SIZE // 2, (num_rows - 1 - steps[i][1]) * BLOCK_SIZE + BLOCK_SIZE // 2)
        end_pos = (steps[i + 1][0] * BLOCK_SIZE + BLOCK_SIZE // 2, (num_rows - 1 - steps[i + 1][1]) * BLOCK_SIZE + BLOCK_SIZE // 2)
        pygame.draw.line(win, LIGHT_RED, start_pos, end_pos, LINE_WIDTH)
        pygame.draw.circle(win, LIGHT_RED, start_pos, LINE_WIDTH, 0)

    if end_pos:
        pygame.draw.circle(win, LIGHT_RED, end_pos, LINE_WIDTH, 0)

def draw_robot(win, num_rows, steps, current_distance):
    total_distance = 0

    for i in range(len(steps) - 1):
        start_pos = (steps[i][0] * BLOCK_SIZE + BLOCK_SIZE // 2, (num_rows - 1 - steps[i][1]) * BLOCK_SIZE + BLOCK_SIZE // 2)
        end_pos = (steps[i + 1][0] * BLOCK_SIZE + BLOCK_SIZE // 2, (num_rows - 1 - steps[i + 1][1]) * BLOCK_SIZE + BLOCK_SIZE // 2)

        dist = euclidean_distance(start_pos, end_pos)

        if current_distance <= total_distance + dist:
            percent = (current_distance - total_distance) / dist
            pos = ((end_pos[0] - start_pos[0]) * percent + start_pos[0], (end_pos[1] - start_pos[1]) * percent + start_pos[1])
            pygame.draw.circle(win, RED, pos, BLOCK_SIZE, 0)
            return False

        total_distance += dist

    return True