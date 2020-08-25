package model;

public class Map {
    public static final int NUM_ROWS = 20;
    public static final int NUM_COLS = 15;
    private Cell[][] grid;

    public Map() {
        grid = new Cell[NUM_ROWS][NUM_COLS];

        for (int r = 0; r < NUM_ROWS; r++) {
            for (int c = 0; c < NUM_COLS; c++) {
                grid[r][c] = new Cell();
            }
        }
    }

    public Cell getCell(int r, int c) {
        return grid[r][c];
    }

    public Map generateVirtualMap() {
        Map virtualMap = new Map();

        // Create base map
        for (int r = 0; r < NUM_ROWS; r++) {
            for (int c = 0; c < NUM_COLS; c++) {
                CellType cellType = getCell(r, c).getCellType();

                if (cellType == CellType.Free)
                    virtualMap.getCell(r, c).setCellType(CellType.Free);
                else
                    virtualMap.getCell(r, c).setCellType(CellType.Obstacle);
            }
        }

        // Add virtual boundary to walls
        for (int r = 0; r < NUM_ROWS; r++) {
            virtualMap.getCell(r, 0).setCellType(CellType.Obstacle);
            virtualMap.getCell(r, NUM_COLS - 1).setCellType(CellType.Obstacle);
        }

        for (int c = 0; c < NUM_COLS; c++) {
            virtualMap.getCell(0, c).setCellType(CellType.Obstacle);
            virtualMap.getCell(NUM_ROWS - 1, c).setCellType(CellType.Obstacle);
        }

        // Add virtual boundary around obstacles
        for (int r = 0; r < NUM_ROWS; r++) {
            for (int c = 0; c < NUM_COLS; c++) {
                CellType cellType = getCell(r, c).getCellType();

                if (cellType == CellType.Obstacle) {
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
                        virtualMap.getCell(pos[0], pos[1]).setCellType(CellType.Obstacle);
                }
            }
        }

        return virtualMap;
    }
}
