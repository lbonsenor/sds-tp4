package ar.edu.itba.sds.entities;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class BillarSimulation {

    // Constantes del Enunciado (TP4 - Sistema 2)
    public static final double R_DOMAIN = 0.51;   // R = 0.51 m
    public static final double R_PART = 0.0175;   // r = 0.0175 m
    public static final double M = 0.025;           // m = 0.025 kg
    public static final double V0 = 1.0;               // v0 = 1 m/s
    public static final double K = 1e4;                // k = 10^4 N/m


    private final int nPart;
    private final double xo;
    private final double dt;
    private final double tMax;
    private final boolean withObstacles;

    private final List<Particle> particles;
    private final double[][] obstacles; // [ [x1, y1], [x2, y2] ]
    private final Random random;

    public BillarSimulation(int nPart, double xo, double dt, double tMax, boolean withObstacles) {
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

        for (int i = 0; i < nPart; i++) {
            boolean posValida = false;
            double x = 0, y = 0;

            while (!posValida) {
                // Posición uniforme dentro del dominio circular de radio (R - r)
                double rRand = (R_DOMAIN - R_PART) * Math.sqrt(random.nextDouble());
                double thetaRand = random.nextDouble() * 2 * Math.PI;
                x = rRand * Math.cos(thetaRand);
                y = rRand * Math.sin(thetaRand);

                posValida = true;

                // 1. Solapamiento con la pared
                if (Math.hypot(x, y) > (R_DOMAIN - R_PART)) {
                    posValida = false;
                    continue;
                }

                // 2. Solapamiento con obstáculos
                if (withObstacles) {
                    for (double[] obs : obstacles) {
                        if (Math.hypot(x - obs[0], y - obs[1]) < (2 * R_PART)) {
                            posValida = false;
                            break;
                        }
                    }
                    if (!posValida) continue;
                }

                // 3. Solapamiento con otras partículas ya posicionadas
                for (Particle p : particles) {
                    if (Math.hypot(x - p.getX(), y - p.getY()) < (2 * R_PART)) {
                        posValida = false;
                        break;
                    }
                }
            }

            // Velocidad inicial v0 con dirección uniforme [0, 2pi)
            double angle = random.nextDouble() * 2 * Math.PI;
            double vx = V0 * Math.cos(angle);
            double vy = V0 * Math.sin(angle);

            particles.add(new Particle(x,y, vx, vy,M,R_PART));
        }
    }

    private double[] calculateEnergies() {
        double ek = 0.0;
        double ep = 0.0;
        for (Particle p : particles) {
            ek += 0.5 * M * (p.getVx() * p.getVx() + p.getVy() * p.getVy());
        }
        for (int i = 0; i < nPart; i++) {
            Particle p1 = particles.get(i);
            double xi = p1.getX();
            double yi = p1.getY();

            for (int j = i + 1; j < nPart; j++) {
                Particle p2 = particles.get(j);
                double dist = Math.hypot(p2.getX() - xi, p2.getY() - yi);
                double xi_ij = (2 * R_PART) - dist;
                if (xi_ij > 0) {
                    ep += 0.5 * K * xi_ij * xi_ij;
                }
            }

            if (withObstacles) {
                for (double[] obs : obstacles) {
                    double dist = Math.hypot(obs[0] - xi, obs[1] - yi);
                    double xiObs = (2 * R_PART) - dist;
                    if (xiObs > 0) {
                        ep += 0.5 * K * xiObs * xiObs;
                    }
                }
            }

            double distCentro = Math.hypot(xi, yi);
            double xiW = distCentro + R_PART - R_DOMAIN;
            if (xiW > 0) {
                ep += 0.5 * K * xiW * xiW;
            }
        }

        return new double[]{ek, ep};
    }

    private double[][] calculateForce(double[][] pos) {
        double[][] forces = new double[nPart][2];

        for (int i = 0; i < nPart; i++) {
            double xi = pos[i][0];
            double yi = pos[i][1];

            // A) Choques Partícula - Partícula
            for (int j = i + 1; j < nPart; j++) {
                double xj = pos[j][0];
                double yj = pos[j][1];
                double dx = xj - xi;
                double dy = yj - yi;
                double dist = Math.hypot(dx, dy);

                double xi_ij = 2 * R_PART - dist;
                if (xi_ij > 0 && dist > 0) {
                    double ex = dx / dist;
                    double ey = dy / dist;

                    double fx = -K * xi_ij * ex;
                    double fy = -K * xi_ij * ey;

                    forces[i][0] += fx;
                    forces[i][1] += fy;
                    forces[j][0] -= fx;
                    forces[j][1] -= fy;
                }
            }

            // B) Choques Partícula - Obstáculos
            if (withObstacles) {
                for (double[] obs : obstacles) {
                    double dx = obs[0] - xi;
                    double dy = obs[1] - yi;
                    double dist = Math.hypot(dx, dy);

                    double xiObs = 2 * R_PART - dist;
                    if (xiObs > 0 && dist > 0) {
                        double ex = dx / dist;
                        double ey = dy / dist;

                        forces[i][0] += -K * xiObs * ex;
                        forces[i][1] += -K * xiObs * ey;
                    }
                }
            }

            // C) Choque Partícula - Pared (Partícula Imagen)
            double distCentro = Math.hypot(xi, yi);
            double xiW = distCentro + R_PART - R_DOMAIN;

            if (xiW > 0 && distCentro > 0) {
                double nx = xi / distCentro;
                double ny = yi / distCentro;

                forces[i][0] += -K * xiW * nx;
                forces[i][1] += -K * xiW * ny;
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
    public double execute(double dtOut, String archivoSalida){
        return execute(dtOut, archivoSalida, null);
    }

    public double execute(double dtOut, String archivoSalida, String archivoEnergia) {
        BufferedWriter writer = null;
        BufferedWriter energy = null;
        try {
            if (archivoSalida != null) {
                writer = new BufferedWriter(new FileWriter(archivoSalida));
            }
            if(archivoEnergia != null) {
                energy = new BufferedWriter(new FileWriter(archivoEnergia));
                energy.write("t\tEk\tEp\tEtot\n");
            }

            double t = 0.0;
            long pasos = 0;
            int nGuardado = Math.max(1, (int) Math.round(dtOut / dt));

            double dt2 = dt * dt;
            double dtX2 = 2.0 * dt;

            long tInicioClock = System.currentTimeMillis();

            while (t <= tMax) {
                double[][] posActuales = obtainMatrixPos();

                // 1. Verificación de conversión de estado (Fresca -> Usada)
                if (withObstacles) {
                    for (Particle p : particles) {
                        if (!p.isUsed()) {
                            for (double[] obs : obstacles) {
                                if (Math.hypot(p.getX() - obs[0], p.getY() - obs[1]) < (2 * R_PART)) {
                                    p.setUsed(true);
                                    break;
                                }
                            }
                        }
                    }
                }

                // 2. Exportación a archivo de texto (output primario)
                if (pasos % nGuardado == 0 && writer != null) {
                    writer.write(String.format("%.4f\n", t));
                    for (Particle p : particles) {
                        int color = p.isUsed() ? 1 : 0; // 0 = Fresca (Azul), 1 = Usada (Roja)
                        writer.write(String.format("%d %.6f %.6f %.6f %.6f %d\n",
                                p.getId(), p.getX(), p.getY(), p.getVx(), p.getVy(), color));
                    }

                    if(energy != null) {
                        double[] energies = calculateEnergies();
                        double ek = energies[0];
                        double ep = energies[1];
                        double etot = ek + ep;
                        energy.write(String.format("%.6f,%.6f,%.6f,%.6f\n", t, ek, ep, etot));
                    }
                }

                // 3. Cálculo de fuerzas en t
                double[][] fuerzas = calculateForce(posActuales);

                // 4. Integración de Verlet
                for (int i = 0; i < nPart; i++) {
                    Particle p = particles.get(i);

                    double ax = fuerzas[i][0] / M;
                    double ay = fuerzas[i][1] / M;

                    double xNext = 2.0 * p.getX() - p.getXPrev() + ax * dt2;
                    double yNext = 2.0 * p.getY() - p.getYPrev() + ay * dt2;

                    // Velocidad centrada v(t) = (r(t+dt) - r(t-dt)) / (2*dt)
                    p.setVx((xNext - p.getXPrev()) / dtX2);
                    p.setVy((yNext - p.getYPrev()) / dtX2);

                    p.setXPrev(p.getX());
                    p.setYPrev(p.getY());
                    p.setX(xNext);
                    p.setY(yNext);
                }

                t += dt;
                pasos++;
            }

            long tFinClock = System.currentTimeMillis();
            return (tFinClock - tInicioClock) / 1000.0; // Tiempo en segundos

        } catch (IOException e) {
            e.printStackTrace();
            return -1;
        } finally {
            if (writer != null) {
                try {
                    writer.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            if(energy != null) {
                try{
                    energy.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    // Método Main de Ejecución
    public static void main(String[] args) {
        int N = 100;
        double xo = 0.05;
        double dt = 1e-4;
        double tMax = 10.0;

        System.out.printf("Iniciando simulación en Java: N=%d, xo=%.3fm, dt=%.1ee s...\n", N, xo, dt);

        BillarSimulation sim = new BillarSimulation(N, xo, dt, tMax, true);
        //si no le pasas archivo energia no hace el calculo
        double tiempoEjecucion = sim.execute(0.05, "output_sistema2_java.txt", "output_sistema2_energia_java.txt");

        System.out.printf("Simulación finalizada en %.2f segundos.\n", tiempoEjecucion);
        System.out.println("Archivo generado: 'output_sistema2_java.txt'");
    }
}
