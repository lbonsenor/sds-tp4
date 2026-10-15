package ar.edu.itba.sds.Simulaciones.ejercicio2;

import ar.edu.itba.sds.entities.BillarSimulation;

import java.util.List;

public class inciso1a {
    public static void main(String[] args) {
        int N = 300;

        List<Double> dts = List.of(1e-2, 5e-3, 1e-3, 5e-4, 1e-4, 5e-5);
        double tMax = 10.0;
        //aca la idea es que la energia se tiene que conservar. cuando hagas el grafico de energia vs dt
        //fijate el dt mas grande que veas q conserva la energia del sistema. elegis ese y lo usas
        //para los otros ejercicios. yo voy a usar 10^-3 a priori


        //Crea el directorio /2.1 antes de correr xq sino explota si ve q no existe
        //para todos estos crea el directorio antes de correrlo por favor
        //TODO el enunciado no especifica pero capaz deberiamos correr 5 o 10 veces cada dt y promediar?
        for (Double dt : dts) {
            System.out.printf("Iniciando simulación ejercicio 2.1.a N=300, dt=%.5f\n", dt);
            BillarSimulation sim = new BillarSimulation(N, 0, dt, tMax, false);
            double tiempoEjecucion = sim.execute(0.05, "2.1.a/2.1.a_dt" + dt+".txt", "2.1.a/2.1.a_energy_dt" + dt+".txt");
        }
    }
}
