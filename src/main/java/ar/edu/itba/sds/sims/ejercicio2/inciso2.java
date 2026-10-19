package ar.edu.itba.sds.sims.ejercicio2;

import ar.edu.itba.sds.entities.BilliardsExp;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class inciso2 {
    public static void main(String[] args) throws IOException {
        int n = 100;
        int n2 = 20;

        double dt = 5e-4;
        double tMax = 100;
        //0.4925 es R - r la maxima distancia posible
        List<Float> obstacleDists = List.of(0.0175f, 0.035f, 0.1f, 0.2f, 0.3f,0.4f,0.4925f);

        //Crea el directorio /2.2 antes de correr xq sino explota si ve q no existe
        Files.createDirectories(Path.of("2.2"));

        for (Float dist : obstacleDists) {
            System.out.printf("Iniciando simulación ejercicio 2.2 N=%d, dist=%.4f\n", n2, dist);
            for (int i = 0; i < 5; i++) {
                BilliardsExp sim = new BilliardsExp(n2, dist, dt, tMax, true);
                double tiempoEjecucion = sim.execute(0.1, "2.2/2.2_N20_dt" + dt + "_obstD_"+dist +"_iter_" + i + ".txt");
            }

        }

        for (Float dist : obstacleDists) {
            System.out.printf("Iniciando simulación ejercicio 2.2 N=%d, dist=%.4f\n", n, dist);
            for (int i = 0; i < 5; i++) {
                BilliardsExp sim = new BilliardsExp(n, dist, dt, tMax, true);
                double tiempoEjecucion = sim.execute(0.1, "2.2/2.2_N100_dt" + dt + "_obstD_"+dist +"_iter_" + i + ".txt");
            }

        }
    }
}
