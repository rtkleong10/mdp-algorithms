package control;

import entity.Cell;
import entity.Graph;
import entity.Map;
import entity.Position;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class FastestPathController {
    public static final int SOURCE_NODE = 0;
    public static final int DEST_NODE = 1;

    private Map map;
    private List<Position> obstacleVertices;

    public FastestPathController(Map map) {
        this.map = map.generateVirtualMap();
        this.obstacleVertices = computeObstacleVertices();
    }

    public Position[] computeFastestPath(Position source, Position dest) {
        Graph g = generateVisibilityGraph(source, dest);
        Integer[] pi = g.aStarSearch(SOURCE_NODE, DEST_NODE);
        Position[] nodes = g.getNodes();

        return computeSteps(pi, nodes);
    }

    private List<Position> computeObstacleVertices() {
        List<Position> vertices = new ArrayList<>();

        for (int r = 0; r < Map.NUM_ROWS; r++) {
            for (int c = 0; c < Map.NUM_COLS; c++) {
                if (map.getCell(r, c) == Cell.Free) {
                    Cell top = map.getCell(r + 1, c);
                    Cell bottom = map.getCell(r - 1, c);
                    Cell left = map.getCell(r, c - 1);
                    Cell right = map.getCell(r, c + 1);
                    Cell topLeft = map.getCell(r + 1, c - 1);
                    Cell topRight = map.getCell(r + 1, c + 1);
                    Cell bottomLeft = map.getCell(r - 1, c - 1);
                    Cell bottomRight = map.getCell(r - 1, c + 1);

                    // ? ? ?
                    // 1   ?
                    // ? 1 ?
                    if ((right == Cell.Obstacle || left == Cell.Obstacle) && (bottom == Cell.Obstacle || top == Cell.Obstacle))
                        vertices.add(new Position(r, c));

                        // ? ? ?
                        // 0 ? ?
                        // 1 0 ?
                    else if ((bottomRight == Cell.Obstacle && right == Cell.Free && bottom == Cell.Free) ||
                            (bottomLeft == Cell.Obstacle && left == Cell.Free && bottom == Cell.Free) ||
                            (topRight == Cell.Obstacle && right == Cell.Free && top == Cell.Free) ||
                            (topLeft == Cell.Obstacle && left == Cell.Free && top == Cell.Free))
                        vertices.add(new Position(r, c));
                }
            }
        }

        return vertices;
    }

    private Graph generateVisibilityGraph(Position source, Position dest) {
        // Nodes
        List<Position> nodes = new ArrayList<>(obstacleVertices);

        // Add source node & destination node at the correct index
        nodes.remove(source);
        nodes.remove(dest);

        nodes.add(SOURCE_NODE, source);
        nodes.add(DEST_NODE, dest);

        // Edges & Weights
        List<Integer[]> edges = new ArrayList<>();
        List<Double> weights = new ArrayList<>();

        for (int i = 0; i < nodes.size(); i++) {
            Position p0 = nodes.get(i);

            for (int j = i + 1; j < nodes.size(); j++) {
                Position p1 = nodes.get(j);

                if (!doesEdgeIntersectWithObstacle(p0, p1)) {
                    Integer[] edge = {i, j};
                    edges.add(edge);
                    weights.add(Position.computeEuclideanDistance(p0, p1));
                }
            }
        }

        Position[] nodesArr = nodes.toArray(new Position[0]);
        Integer[][] edgesArr = edges.toArray(new Integer[0][]);
        Double[] weightsArr = weights.toArray(new Double[0]);

        return new Graph(nodesArr, edgesArr, weightsArr);
    }

    private boolean doesEdgeIntersectWithObstacle (Position p0, Position p1) {
        // Bounding box
        int c0 = Math.min(p0.getC(), p1.getC());
        int c1 = Math.max(p0.getC(), p1.getC());
        int r0 = Math.min(p0.getR(), p1.getR());
        int r1 = Math.max(p0.getR(), p1.getR());

        // Vertical line
        if (p1.getC() == p0.getC()) {
            int c = p0.getC();

            for (int r = r0; r <= r1; r++) {
                if (map.getCell(r, c) == Cell.Obstacle)
                    return true;
            }

        } else if (p1.getR() == p0.getR()) {
            int r = p0.getR();

            for (int c = c0; c <= c1; c++) {
                if (map.getCell(r, c) == Cell.Obstacle)
                    return true;
            }

        } else {
            double gradient = ((double) p1.getR() - p0.getR()) / ((double) p1.getC() - p0.getC());
            double intercept = p0.getR() - (gradient * p0.getC());

            for (int r = r0; r <= r1; r++) {
                for (int c = c0; c <= c1; c++) {
                    if (map.getCell(r, c) == Cell.Obstacle) {
                        double perpendicularDistance = Math.abs(gradient * c - r + intercept) / Math.sqrt(Math.pow(gradient, 2) + 1);
                        if (perpendicularDistance <= 1.414)
                            return true;
                    }
                }
            }
        }

        return false;
    }

    private Position[] computeSteps(Integer[] pi, Position[] nodes) {
        // Get step nodes
        List<Integer> stepNodes = new ArrayList<>();
        int cur = DEST_NODE;
        stepNodes.add(cur);

        while (pi[cur] != null) {
            cur = pi[cur];
            stepNodes.add(cur);
        }

        Collections.reverse(stepNodes);
        Integer[] stepNodesArr = stepNodes.toArray(new Integer[0]);

        // Remove intermediate steps with the same angle & convert nodes into positions
        List<Position> stepPos = new ArrayList<>();
        stepPos.add(nodes[stepNodesArr[0]]);

        for (int i = 1; i < stepNodesArr.length - 1; i++) {
            Position prevPos = nodes[stepNodesArr[i - 1]];
            Position curPos = nodes[stepNodesArr[i]];
            Position nextPos = nodes[stepNodesArr[i + 1]];

            double theta0 = Position.computeAngle(prevPos, curPos);
            double theta1 = Position.computeAngle(curPos, nextPos);

            if (Math.abs(theta0 - theta1) > 0.01)
                stepPos.add(curPos);
        }

        if (stepNodesArr.length > 1)
            stepPos.add(nodes[stepNodesArr[stepNodesArr.length - 1]]);

        return stepPos.toArray(new Position[0]);
    }
}
