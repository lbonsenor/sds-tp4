package ar.edu.itba.sds.sims.ejercicio2;

import ar.edu.itba.sds.entities.BilliardsExp;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class inciso3 {
    public static void main(String[] args) throws IOException {
        int N = 100;

        double dt = 5e-4;
        double tMax = 50.0;

        //Crea el directorio /2.1 antes de correr xq sino explota si ve q no existe
        Files.createDirectories(Path.of("2.3"));

        //en teoria el observable lo dberias poder calcular con las velocidades
        //que ya te da el archivo output. asi que solo corro esto 15 veces
        //el tf lo podes variar pero no se cuando se llega al estacionario asi que puse 50 a priori
        for (int i = 0; i < 15; i++) {
            System.out.printf("Iniciando simulación ejercicio 2.3 N=100, dt=%.5f\n", dt);
            BilliardsExp sim = new BilliardsExp(N, 0, dt, tMax, false);
            double tiempoEjecucion = sim.execute(0.05, "2.3/2.3_dt" + dt+ "_iter_"+ i + ".txt");
        }
    }

}

