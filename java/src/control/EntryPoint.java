package control;

import entity.Cell;
import entity.Map;
import entity.MapDescriptor;
import entity.Position;

public class EntryPoint {
    public static void main(String[] args) {
        // From Map Descriptor Format pdf
        // String[] strs = {"FFC07F80FF01FE03FFFFFFF3FFE7FFCFFF9C7F38FE71FCE3F87FF0FFE1FFC3FF87FF0E0E1C1F","00000100001C80000000001C0000080000060001C00000080000"};

        // From algorithms slides
        String[] strs = {"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF", "001000200040070000000038001000000004000820107E300400000000610080200040008000"};
        Map map = MapDescriptor.generateMap(strs);
        String[] result = MapDescriptor.generateMapDescriptor(map);

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

        FastestPathController fp = new FastestPathController(map);
        Position[] steps = fp.computeFastestPath(new Position(1, 1), new Position(18, 13));

        for (int i = 0; i < steps.length; i++) {
            System.out.println((i + 1) + ": " + steps[i].getC() + ", " + steps[i].getR());
        }
    }
}
