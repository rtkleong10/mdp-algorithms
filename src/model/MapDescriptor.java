package model;

public class MapDescriptor {
    public static void main(String[] args) {
        String[] strs = {"FFC07F80FF01FE03FFFFFFF3FFE7FFCFFF9C7F38FE71FCE3F87FF0FFE1FFC3FF87FF0E0E1C1F", "00000100001C80000000001C0000080000060001C00000080000"};
        Map map = generateMap(strs);
        String[] result = generateMapDescriptor(map);

        for (int r = Map.NUM_ROWS - 1; r >= 0; r--) {
            for (int c = 0; c < Map.NUM_COLS; c++) {
                Cell cellType = map.getCell(r, c);
                switch (cellType) {
                    case Unexplored:
                        System.out.print("?");
                        break;

                    case Free:
                        System.out.print("0");
                        break;

                    case Obstacle:
                        System.out.print("1");
                        break;

                    default:
                        break;
                }
            }

            System.out.println();
        }

        System.out.println(result[0]);
        System.out.println(result[1]);
    }

    private static String binToHex(String binStr) {
        // Add padding to binary string
        int numPadBits = 8 - binStr.length() % 8;
        String binStrPadded = numPadBits == 8 ? binStr : "0".repeat(numPadBits) + binStr;

        StringBuilder hexStr = new StringBuilder();

        for (int i = 0; i < binStrPadded.length(); i += 4) {
            String hexDigitBin = binStrPadded.substring(i, i + 4);
            int hexDigitValue = Integer.parseInt(hexDigitBin, 2);
            String hexDigit = Integer.toString(hexDigitValue, 16);
            hexStr.append(hexDigit);
        }

        return hexStr.toString().toUpperCase();
    }

    private static String hexToBin(String hexStr) {
        StringBuilder binStr = new StringBuilder();

        for (int i = 0; i < hexStr.length(); i++) {
            String hexDigit = Character.toString(hexStr.charAt(i));
            int hexDigitValue = Integer.parseInt(hexDigit, 16);
            String hexDigitBin = Integer.toString(hexDigitValue, 2);

            int numPadBits = 4 - hexDigitBin.length();
            binStr.append("0".repeat(numPadBits) + hexDigitBin);
        }

        return binStr.toString();
    }

    public static Map generateMap(String[] strs) {
        String exploredBin = hexToBin(strs[0]);
        System.out.println(exploredBin);
        String obstaclesBin = hexToBin(strs[1]);

        int exploredCount = 2;
        int obstaclesCount = 0;

        Map map = new Map();

        for (int r = 0; r < Map.NUM_ROWS; r++) {
            for (int c = 0; c < Map.NUM_COLS; c++) {
                if (exploredBin.charAt(exploredCount) == '0') {
                    map.setCell(r, c, Cell.Unexplored);
                } else {
                    if (obstaclesBin.charAt(obstaclesCount) == '0')
                        map.setCell(r, c, Cell.Free);
                    else
                        map.setCell(r, c, Cell.Obstacle);

                    obstaclesCount++;
                }

                exploredCount++;
            }
        }

        return map;
    }

    public static String[] generateMapDescriptor(Map map) {
        String[] strs = new String[2];

        StringBuilder exploredBin = new StringBuilder();
        StringBuilder obstaclesBin = new StringBuilder();

        exploredBin.append("11");

        for (int r = 0; r < Map.NUM_ROWS; r++) {
            for (int c = 0; c < Map.NUM_COLS; c++) {
                Cell cell = map.getCell(r, c);
                switch (cell) {
                    case Unexplored:
                        exploredBin.append("0");
                        break;

                    case Free:
                        exploredBin.append("1");
                        obstaclesBin.append("0");
                        break;

                    case Obstacle:
                        exploredBin.append("1");
                        obstaclesBin.append("1");
                        break;

                    default:
                        break;
                }
            }
        }

        exploredBin.append("11");

        strs[0] = binToHex(exploredBin.toString());
        strs[1] = binToHex(obstaclesBin.toString());

        return strs;
    }
}
