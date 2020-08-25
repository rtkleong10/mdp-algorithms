package model;

// TODO: Consider separating cell type from image stuff
public class Cell {
    private CellType cellType;
    private boolean image;
    private int imageId;

    public CellType getCellType() {
        return cellType;
    }

    public void setCellType(CellType cellType) {
        this.cellType = cellType;
    }

    public boolean hasImage() {
        return image;
    }

    public void setHasImage(boolean image) {
        this.image = image;
    }

    public int getImageId() {
        return imageId;
    }

    public void setImageId(int imageId) {
        this.imageId = imageId;
    }
}
