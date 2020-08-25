package entity;

import java.util.Arrays;

public class Graph {
    private Position[] nodes;
    private Integer[][] edges;
    private Double[] weights;

    public Graph(Position[] nodes, Integer[][] edges, Double[] weights) {
        this.nodes = nodes;
        this.edges = edges;
        this.weights = weights;
    }

    public Position[] getNodes() {
        return nodes;
    }

    public Integer[][] getEdges() {
        return edges;
    }

    public Double[] getWeights() {
        return weights;
    }

    public Integer[] aStarSearch(int source, int dest) {
        Double[] d = new Double[nodes.length];
        Integer[] pi = new Integer[nodes.length];
        boolean[] S = new boolean[nodes.length];

        Arrays.fill(d, null);
        Arrays.fill(pi, null);
        Arrays.fill(S, false);
        d[source] = 0.0;

        // Estimated cost from node to destination
        double[] h = new double[nodes.length];
        for (int i = 0; i < nodes.length; i++)
            h[i] = Position.computeEuclideanDistance(nodes[i], nodes[dest]);

        for (int i = 0; i < nodes.length; i++) {
            Double minF = null;
            int u = -1;

            for (int j = 0; j < nodes.length; j++) {
                if (d[j] != null && !S[j]) {
                    double f = d[j] + h[j];

                    if (minF == null || f < minF) {
                        minF = f;
                        u = j;
                    }
                }
            }

            if (u == -1 || u == dest)
                break;

            S[u] = true;

            for (int j = 0; j < edges.length; j++) {
                Integer[] edge = edges[j];
                int v;

                if (u == edge[0])
                    v = edge[1];
                else if (u == edge[1])
                    v = edge[0];
                else
                    continue;

                if (!S[v] && (d[v] == null || d[v] > d[u] + weights[j])) {
                    d[v] = d[u] + weights[j];
                    pi[v] = u;
                }
            }
        }

        return pi;
    }
}
