package ar.edu.itba.sds.Simulaciones.ejercicio2;

import ar.edu.itba.sds.entities.BillarSimulation;

import java.util.List;

public class inciso2 {
    public static void main(String[] args) {
        int n = 100;
        int n2 = 20;

        double dt = 1e-3;
        double tMax = 100;
        //0.4925 es R - r la maxima distancia posible
        List<Float> obstacleDists = List.of(0.0175f, 0.035f, 0.07f, 0.14f, 0.28f,0.4925f);


        for (Float dist : obstacleDists) {
            System.out.printf("Iniciando simulación ejercicio 2.2 N=%d, dist=%.4f\n", n, dist);
            for (int i = 0; i < 5; i++) {
                BillarSimulation sim = new BillarSimulation(n, dist, dt, tMax, true);
                double tiempoEjecucion = sim.execute(0.05, "2.2/2.2_N100_dt" + dt + "_" + i + ".txt");
            }

        }
        for (Float dist : obstacleDists) {
            System.out.printf("Iniciando simulación ejercicio 2.2 N=%d, dist=%.4f\n", n2, dist);
            for (int i = 0; i < 5; i++) {
                BillarSimulation sim = new BillarSimulation(n2, dist, dt, tMax, true);
                double tiempoEjecucion = sim.execute(0.05, "2.2/2.2_N20_dt" + dt + "_" + i + ".txt");
            }

        }
    }
}
