package ar.edu.itba.sds.sims.ejercicio2;

import ar.edu.itba.sds.entities.BilliardsExp;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class inciso1b {
    public static void main(String[] args) throws IOException {
        List<Integer> ns = List.of(100,200,300,400,500,600);

        double dt = 1e-4;
        double tMax = 150;
        float obstacleDist = 0.0175f;
        List<Double> executionTimes = new ArrayList<>();

        //Crea el directorio /2.1 antes de correr xq sino explota si ve q no existe
        Files.createDirectories(Path.of("2.1.b"));
        Files.createDirectories(Path.of("2.1.b/execution_times"));



        //Hay que correr tmb los mismos n en el tp3 y comparar tiempos
        for (Integer n : ns) {
            BufferedWriter writer = new BufferedWriter(new FileWriter("2.1.b/execution_times/n" + n + "_dt" + dt + ".txt"));
            writer.write("N runCount time\n");

            for (int i = 0; i < 10; i++) {
                System.out.printf("Iniciando simulación ejercicio 2.1.b N=%d, dt=%.5f, i=%d\n", n, dt, i);
                BilliardsExp sim = new BilliardsExp(n, obstacleDist, dt, tMax, true);
                double tiempoEjecucion = sim.execute(0.05, "2.1.b/2.1.b_dt" + dt + "_N_"+ n +"_" + i + ".txt");
                writer.write(n + " " + i + " " + tiempoEjecucion + "\n");
            }
            try{
                writer.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

    }
}
