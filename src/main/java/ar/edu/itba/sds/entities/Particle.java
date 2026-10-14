package ar.edu.itba.sds.entities;

public class Particle {

    private static int nextId = 0;

    private final int id;
    private double vx, vy;
    private double posX, posY;
    private double xPrev, yPrev;
    private boolean used;
    private final double m;
    private final double r;

    public Particle(int id, double posX, double posY, double vx, double vy, boolean used, double m, double r){
        this.id = id;
        this.vx = vx;
        this.vy = vy;
        this.posX = posX;
        this.posY = posY;
        this.used = used;
        this.m = m;
        this.r = r;
    }

    public Particle(double posX, double posY, double vx, double vy,  double m, double r){
        this(nextId++, posX,posY,vx,vy,false, m, r);
    }

    // Getters y Setters
    public int getId() { return id; }
    public double getX() { return posX; }
    public void setX(double x) { this.posX = x; }
    public double getY() { return posY; }
    public void setY(double y) { this.posY = y; }
    public double getVx() { return vx; }
    public void setVx(double vx) { this.vx = vx; }
    public double getVy() { return vy; }
    public void setVy(double vy) { this.vy = vy; }
    public double getXPrev() { return xPrev; }
    public void setXPrev(double xPrev) { this.xPrev = xPrev; }
    public double getYPrev() { return yPrev; }
    public void setYPrev(double yPrev) { this.yPrev = yPrev; }
    public boolean isUsed() { return used; }
    public void setUsed(boolean used) { this.used = used; }
}
