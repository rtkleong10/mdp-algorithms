package control;

import entity.Cell;
import entity.Graph;
import entity.Map;
import entity.Position;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class FastestPath {
    public static Position[] computeFastestPath(Map map, Position source, Position dest) {
        Map virtualMap = map.generateVirtualMap();
        Graph g = generateVisibilityGraph(virtualMap, source, dest);

        int sourceNode = -1;
        int destNode = -1;

        Position[] nodes = g.getNodes();

        for (int i = 0; i < nodes.length; i++) {
            if (sourceNode != -1 && destNode != -1)
                break;

            if (nodes[i].equals(source))
                sourceNode = i;

            if (nodes[i].equals(dest))
                destNode = i;
        }

        Integer[] pi = g.aStarSearch(sourceNode, destNode);

        // Get steps
        List<Integer> steps = new ArrayList<>();
        int cur = destNode;
        steps.add(cur);

        while (pi[cur] != null) {
            cur = pi[cur];
            steps.add(cur);
        }

        Collections.reverse(steps);
        Integer[] stepsArr = steps.toArray(new Integer[0]);

        // Remove intermediate steps with the same angle
        List<Position> stepPositions = new ArrayList<>();
        stepPositions.add(nodes[stepsArr[0]]);

        for (int i = 1; i < stepsArr.length - 1; i++) {
            Position prevPos = nodes[stepsArr[i - 1]];
            Position curPos = nodes[stepsArr[i]];
            Position nextPos = nodes[stepsArr[i + 1]];

            double theta0 = Position.computeAngle(prevPos, curPos);
            double theta1 = Position.computeAngle(curPos, nextPos);

            if (Math.abs(theta0 - theta1) > 0.01)
                stepPositions.add(curPos);
        }

        if (stepsArr.length > 1)
            stepPositions.add(nodes[stepsArr[stepsArr.length - 1]]);

        return stepPositions.toArray(new Position[0]);
    }

    private static Graph generateVisibilityGraph(Map map, Position source, Position dest) {
        // Nodes
        List<Position> nodes = getObstacleVertices(map);

        if (!nodes.contains(source))
            nodes.add(source);

        if (!nodes.contains(dest))
            nodes.add(dest);

        // Edges & Weights
        List<Integer[]> edges = new ArrayList<>();
        List<Double> weights = new ArrayList<>();

        for (int i = 0; i < nodes.size(); i++) {
            Position p0 = nodes.get(i);

            for (int j = i + 1; j < nodes.size(); j++) {
                Position p1 = nodes.get(j);

                if (!doesEdgeIntersectWithObstacle(p0, p1, map)) {
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

    private static List<Position> getObstacleVertices(Map map) {
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

    private static boolean doesEdgeIntersectWithObstacle (Position p0, Position p1, Map map) {
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
}
