package ar.edu.itba.sds.Simulaciones.ejercicio2;

import ar.edu.itba.sds.entities.BillarSimulation;

import java.util.List;

public class inciso3 {
    public static void main(String[] args) {
        int N = 100;

        double dt = 1e-3;
        double tMax = 50.0;

        //en teoria el observable lo dberias poder calcular con las velocidades
        //que ya te da el archivo output. asi que solo corro esto 15 veces
        //el tf lo podes variar pero no se cuando se llega al estacionario asi que puse 50 a priori
        for (int i = 0; i < 15; i++) {
            System.out.printf("Iniciando simulación ejercicio 2.3 N=100, dt=%.5f\n", dt);
            BillarSimulation sim = new BillarSimulation(N, 0, dt, tMax, false);
            double tiempoEjecucion = sim.execute(0.05, "2.3/2.3_dt" + dt+".txt");
        }
    }

}

