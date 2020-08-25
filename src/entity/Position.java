package entity;

public class Position {
    private int r;
    private int c;

    public Position(int r, int c) {
        this.r = r;
        this.c = c;
    }

    public int getR() {
        return r;
    }

    public int getC() {
        return c;
    }

    public static double computeEuclideanDistance(Position p0, Position p1) {
        return Math.sqrt(Math.pow((double) p1.getR() - (double) p0.getR(), 2) + Math.pow((double) p1.getC() - (double) p0.getC(), 2));
    }

    public static double computeAngle(Position p0, Position p1) {
        return Math.atan(((double) p1.getR() - (double) p0.getR()) / ((double) p1.getC() - (double) p0.getC()));
    }

    @Override
    public boolean equals(Object o) {
        if (this == o)
            return true;

        if (o == null || getClass() != o.getClass())
            return false;

        Position position = (Position) o;
        return r == position.r && c == position.c;
    }

    @Override
    public String toString() {
        return "(" + c + ", " + r + ")";
    }
}
