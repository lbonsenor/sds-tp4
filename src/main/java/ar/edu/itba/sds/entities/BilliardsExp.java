package ar.edu.itba.sds.entities;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class BilliardsExp {

    public static final double R_DOMAIN = 0.51;   // R = 0.51 m
    public static final double R_PART = 0.0175;   // r = 0.0175 m
    public static final double M = 0.025;         // m = 0.025 kg
    public static final double V0 = 1.0;          // v0 = 1 m/s
    public static final double K = 1e4;           // k = 10^4 N/m

    private static final double DIAMETER = 2 * R_PART;
    private static final double DIAMETER_SQ = DIAMETER * DIAMETER;

    private final int nPart;
    private final double xo;
    private final double dt;
    private final double tMax;
    private final boolean withObstacles;

    private final List<Particle> particles;
    private final double[][] obstacles;
    private final Random random;

    public BilliardsExp(int nPart, double xo, double dt, double tMax, boolean withObstacles) {
        this.nPart = nPart;
        this.xo = xo;
        this.dt = dt;
        this.tMax = tMax;
        this.withObstacles = withObstacles;
        this.particles = new ArrayList<>();
        this.random = new Random();

        if (withObstacles) {
            this.obstacles = new double[][]{ {-this.xo, 0.0}, {this.xo, 0.0} };
        } else {
            this.obstacles = new double[0][0];
        }

        initParticles();
        initVerletStepZero();
    }

    private void initParticles() {
        particles.clear();
        List<double[]> validPositions = new ArrayList<>();
        double eps = 1e-5;
        double diam = 2 * R_PART + eps;
        double dy = diam * Math.sqrt(3) / 2.0;

        int row = 0;
        for (double y = -R_DOMAIN; y <= R_DOMAIN; y += dy) {
            double xOffset = (row % 2 == 0) ? 0 : (diam / 2.0);
            for (double x = -R_DOMAIN + xOffset; x <= R_DOMAIN; x += diam) {
                if (x * x + y * y > (R_DOMAIN - R_PART) * (R_DOMAIN - R_PART)) continue;

                boolean overlapObs = false;
                if (withObstacles) {
                    for (double[] obs : obstacles) {
                        double dx = x - obs[0];
                        double dyObs = y - obs[1];
                        if (dx * dx + dyObs * dyObs < DIAMETER_SQ) {
                            overlapObs = true;
                            break;
                        }
                    }
                }
                if (overlapObs) continue;
                validPositions.add(new double[]{x, y});
            }
            row++;
        }

        if (nPart > validPositions.size()) {
            throw new RuntimeException("Límite físico excedido: " + nPart + " > " + validPositions.size());
        }

        java.util.Collections.shuffle(validPositions, random);
        for (int i = 0; i < nPart; i++) {
            double[] pos = validPositions.get(i);
            double angle = random.nextDouble() * 2 * Math.PI;
            particles.add(new Particle(pos[0], pos[1], V0 * Math.cos(angle), V0 * Math.sin(angle), M, R_PART));
        }
    }

    private double[][] calculateForce(double[][] pos) {
        double[][] forces = new double[nPart][2];

        for (int i = 0; i < nPart; i++) {
            double xi = pos[i][0];
            double yi = pos[i][1];

            // A) Partícula - Partícula
            for (int j = i + 1; j < nPart; j++) {
                double dx = pos[j][0] - xi;
                double dy = pos[j][1] - yi;
                double dist2 = dx * dx + dy * dy;

                if (dist2 < DIAMETER_SQ && dist2 > 0) {
                    double dist = Math.sqrt(dist2);
                    double xi_ij = DIAMETER - dist;
                    if (xi_ij > 0) {
                        double fx = -K * xi_ij * (dx / dist);
                        double fy = -K * xi_ij * (dy / dist);
                        forces[i][0] += fx;
                        forces[i][1] += fy;
                        forces[j][0] -= fx;
                        forces[j][1] -= fy;
                    }
                }
            }

            // B) Partícula - Obstáculos
            if (withObstacles) {
                for (double[] obs : obstacles) {
                    double dx = obs[0] - xi;
                    double dy = obs[1] - yi;
                    double dist2 = dx * dx + dy * dy;

                    if (dist2 < DIAMETER_SQ && dist2 > 0) {
                        double dist = Math.sqrt(dist2);
                        double xiObs = DIAMETER - dist;
                        if (xiObs > 0) {
                            forces[i][0] += -K * xiObs * (dx / dist);
                            forces[i][1] += -K * xiObs * (dy / dist);
                        }
                    }
                }
            }

            // C) Partícula - Pared
            double distCentro2 = xi * xi + yi * yi;
            double rWall = R_DOMAIN - R_PART;
            if (distCentro2 > rWall * rWall) {
                double distCentro = Math.sqrt(distCentro2);
                double xiW = distCentro + R_PART - R_DOMAIN;
                if (xiW > 0 && distCentro > 0) {
                    forces[i][0] += -K * xiW * (xi / distCentro);
                    forces[i][1] += -K * xiW * (yi / distCentro);
                }
            }
        }
        return forces;
    }

    private void initVerletStepZero() {
        double[][] posActuales = obtainMatrixPos();
        double[][] fuerzas0 = calculateForce(posActuales);
        double dt2_2 = (dt * dt) / 2.0;
        for (int i = 0; i < nPart; i++) {
            Particle p = particles.get(i);
            double ax = fuerzas0[i][0] / M;
            double ay = fuerzas0[i][1] / M;
            p.setXPrev(p.getX() - p.getVx() * dt + ax * dt2_2);
            p.setYPrev(p.getY() - p.getVy() * dt + ay * dt2_2);
        }
    }

    private double[][] obtainMatrixPos() {
        double[][] pos = new double[nPart][2];
        for (int i = 0; i < nPart; i++) {
            pos[i][0] = particles.get(i).getX();
            pos[i][1] = particles.get(i).getY();
        }
        return pos;
    }

    public double execute(double dtOut, String outFile) {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(outFile))) {
            double t = 0.0;
            long steps = 0;
            int nGuardado = Math.max(1, (int) Math.round(dtOut / dt));
            double dt2 = dt * dt;
            double dtX2 = 2.0 * dt;

            long tInicio = System.currentTimeMillis();

            while (t <= tMax) {
                double[][] posActuales = obtainMatrixPos();

                if (withObstacles) {
                    for (Particle p : particles) {
                        if (!p.isUsed()) {
                            for (double[] obs : obstacles) {
                                double dx = p.getX() - obs[0];
                                double dy = p.getY() - obs[1];
                                if (dx * dx + dy * dy < DIAMETER_SQ) {
                                    p.setUsed(true);
                                    break;
                                }
                            }
                        }
                    }
                }

                if (steps % nGuardado == 0) {
                    writer.write(String.format("%.4f\n", t));
                    for (Particle p : particles) {
                        writer.write(String.format("%d %.6f %.6f %.6f %.6f %d\n",
                                p.getId(), p.getX(), p.getY(), p.getVx(), p.getVy(), p.isUsed() ? 1 : 0));
                    }
                }

                double[][] fuerzas = calculateForce(posActuales);

                for (int i = 0; i < nPart; i++) {
                    Particle p = particles.get(i);
                    double xNext = 2.0 * p.getX() - p.getXPrev() + (fuerzas[i][0] / M) * dt2;
                    double yNext = 2.0 * p.getY() - p.getYPrev() + (fuerzas[i][1] / M) * dt2;

                    p.setVx((xNext - p.getXPrev()) / dtX2);
                    p.setVy((yNext - p.getYPrev()) / dtX2);
                    p.setXPrev(p.getX());
                    p.setYPrev(p.getY());
                    p.setX(xNext);
                    p.setY(yNext);
                }

                t += dt;
                steps++;
            }
            return (System.currentTimeMillis() - tInicio) / 1000.0;
        } catch (IOException e) {
            e.printStackTrace();
            return -1;
        }
    }
}