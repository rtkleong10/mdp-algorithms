package entity;

public class Map {
    public static final int NUM_ROWS = 20;
    public static final int NUM_COLS = 15;
    public static final Position START_POS = new Position(1, 1);
    public static final Position GOAL_POS = new Position(18, 13);
    private Cell[][] grid;

    public Map() {
        grid = new Cell[NUM_ROWS][NUM_COLS];
    }

    public void reset() {
        // Unexplored by default
        for (int r = 0; r < NUM_ROWS; r++) {
            for (int c = 0; c < NUM_COLS; c++) {
                grid[r][c] = Cell.Unexplored;
            }
        }

        // Start zone and goal zone
        for (int i = -1; i <= 1; i++) {
            for (int j = -1; j <= 1; j++) {
                grid[START_POS.getR() + i][START_POS.getC() + i] = Cell.Free;
                grid[GOAL_POS.getR() + i][GOAL_POS.getC() + i] = Cell.Free;
            }
        }
    }

    public Cell getCell(int r, int c) {
        if (r < 0 || r >= NUM_ROWS || c < 0 || c >= NUM_COLS)
            return null;
        else
            return grid[r][c];
    }

    public void setCell(int r, int c, Cell cell) {
        if (r < 0 || r >= NUM_ROWS || c < 0 || c >= NUM_COLS)
            return;

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

                if (cell != Cell.Free) {
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
