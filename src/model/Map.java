package model;

public class Map {
    public static final int NUM_ROWS = 20;
    public static final int NUM_COLS = 15;
    private Cell[][] grid;

    public Map() {
        grid = new Cell[NUM_ROWS][NUM_COLS];

        for (int r = 0; r < NUM_ROWS; r++) {
            for (int c = 0; c < NUM_COLS; c++) {
                grid[r][c] = Cell.Unexplored;
            }
        }
    }

    public Cell getCell(int r, int c) {
        return grid[r][c];
    }

    public void setCell(int r, int c, Cell cell) {
        grid[r][c] = cell;
    }

    public Map generateVirtualMap() {
        Map virtualMap = new Map();

        // Create base map
        for (int r = 0; r < NUM_ROWS; r++) {
            for (int c = 0; c < NUM_COLS; c++) {
                Cell cell = getCell(r, c);

                if (cell == Cell.Free)
                    virtualMap.setCell(r, c, Cell.Free);
                else
                    virtualMap.setCell(r, c, Cell.Obstacle);
            }
        }

        // Add virtual boundary to walls
        for (int r = 0; r < NUM_ROWS; r++) {
            virtualMap.setCell(r, 0, Cell.Obstacle);
            virtualMap.setCell(r, NUM_COLS - 1, Cell.Obstacle);
        }

        for (int c = 0; c < NUM_COLS; c++) {
            virtualMap.setCell(0, c, Cell.Obstacle);
            virtualMap.setCell(NUM_ROWS - 1, c, Cell.Obstacle);
        }

        // Add virtual boundary around obstacles
        for (int r = 0; r < NUM_ROWS; r++) {
            for (int c = 0; c < NUM_COLS; c++) {
                Cell cell = getCell(r, c);

                if (cell == Cell.Obstacle) {
                    int[][] posToMark = {
                            {r - 1, c - 1},
                            {r, c - 1},
                            {r + 1, c - 1},
                            {r - 1, c },
                            {r + 1, c},
                            {r - 1, c + 1},
                            {r, c + 1},
                            {r + 1, c + 1},
                    };

                    for (int[] pos : posToMark)
                        virtualMap.setCell(pos[0], pos[1], Cell.Obstacle);
                }
            }
        }

        return virtualMap;
    }
}
