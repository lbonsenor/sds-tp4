package ar.edu.itba.sds.Simulaciones.ejercicio2;

import ar.edu.itba.sds.entities.BillarSimulation;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class inciso1b {
    public static void main(String[] args) throws IOException {
        List<Integer> ns = List.of(100, 200, 300, 400, 500, 600, 700, 800, 900);

        double dt = 1e-3;
        double tMax = 30;
        float obstacleDist = 0.0175f;

        //Crea el directorio /2.1 antes de correr xq sino explota si ve q no existe
        Files.createDirectories(Path.of("2.1.b"));
        //Hay que correr tmb los mismos n en el tp3 y comparar tiempos
        for (Integer n : ns) {
            System.out.printf("Iniciando simulación ejercicio 2.1.b N=%d, dt=%.5f\n", n, dt);
            for (int i = 0; i < 10; i++) {
                BillarSimulation sim = new BillarSimulation(n, obstacleDist, dt, tMax, true);
                double tiempoEjecucion = sim.execute(0.05, "2.1.b/2.1.b_dt" + dt + "_" + i + ".txt");
            }

        }
    }
}
