package ar.edu.itba.sds;

import ar.edu.itba.sds.config.BaseConfig;
import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

import java.io.File;
import java.util.List;

@Command(
        name = "oscillator",
        mixinStandardHelpOptions = true,
        version = "1.0",
        description = "Punto 1: Evaluación de error cuadrático medio (ECM) vs dt para el Oscilador Amortiguado"
)
public class OscillatorMain extends BaseConfig {

    // Parámetros Fijos
    private final double mass = 70.0;
    private final double k = 10000.0;
    private final double gamma = 100.0;
    private final double r0 = 1.0;
    private final double v0 = -gamma / (2.0 * mass);
    private final double tf = 5.0;


    // Parametros auxiliares fijos
    private final double gammaOver2m = gamma / (2.0 * mass);
    private final double omega0Squared = k / mass;
    private final double omega = Math.sqrt(omega0Squared - gammaOver2m * gammaOver2m);
    private final double constA = Math.sqrt(r0 * r0 + Math.pow((v0 + gammaOver2m * r0) / omega, 2));





    // Parámetro Variable
    @Option(names = {"--dts"}, split = ",", description = "Pasos temporales dt a evaluar")
    private List<Double> dts = List.of(1e-2, 5e-3, 1e-3, 5e-4, 1e-4, 5e-5, 1e-5);

    @Option(names = {"-o", "--output-dir"}, description = "Directorio de salida para CSVs")
    private File outputDir = new File("telemetry/oscillator");

    @Override
    public Integer call() throws Exception {
        loadJsonConfig();

        System.out.println("=== SISTEMA 1: Oscilador Amortiguado ===");
        System.out.printf("Condiciones: m=%.1f kg | k=%.1f N/m | gamma=%.1f kg/s | tf=%.1f s%n", mass, k, gamma, tf);
        System.out.println("Evaluando dts: " + dts);

//        for (double dt : dts) {
//            runVerletOriginalOscillatorForDt(dt);
//        }
        runVelocityVerletOscillatorForDt(dts.getFirst());
        return 0;
    }

    private void runVelocityVerletOscillatorForDt(double dt) {
        double massInverse = 1/mass;
        double ft = -k * r0 - gamma * v0;
        double fPlusT;
        double rt = r0;
        double rPlusT;
        double vt = v0;
        double vPlusT;
        double vPlusHalfT;
        double vPlusTInverseDenominator = 1 / (1.0 + gamma * massInverse * 0.5 * dt);
        double totalT = 0;
        int counter = 0;
        while (totalT < tf)
        {
            counter++;

            vPlusHalfT = vt + (ft * massInverse) * 0.5 * dt;
            rPlusT = rt + vPlusHalfT * dt;
            vPlusT = (vPlusHalfT - k * rPlusT * massInverse * 0.5 * dt) * vPlusTInverseDenominator;
            fPlusT = -k * rPlusT - gamma * vPlusT;
            rt = rPlusT;
            vt = vPlusT;
            ft = fPlusT;

            totalT += dt;
            if(counter == 25){
                System.out.println("totalT : " + totalT + "rt : " + rt + "vt : " + vt);
                System.out.println("Analytical : " + getAnalyticalOscillatorPosition(totalT)+ " Error : " + Math.abs(getAnalyticalOscillatorPosition(totalT) - rt));
                System.out.println();
                counter = 0;
            }
        }
    }

    private double getAnalyticalOscillatorPosition(double t) {
        return constA * Math.exp(-gammaOver2m * t) * Math.cos(omega * t);
    }

    //Currently only original verlet algorithm
    private void runVerletOriginalOscillatorForDt(double dt) {
        double massInverse = 1/mass;
        double f0 = -k * r0 - gamma * v0;
        double rMinusT = r0 - v0*dt + (f0/(2 * mass)) * dt * dt;
        double rt = r0;
        double rPlusT;

        double totalT = 0;
        int counter = 0;
        while (totalT < tf)
        {
            counter++;
            rPlusT = ((2 - k * dt * dt * massInverse) * rt - (1 - gamma * dt * 0.5 * massInverse) * rMinusT) / (1 + gamma * dt * 0.5 * massInverse);
            rMinusT = rt;
            rt = rPlusT;
            totalT += dt;

            if(counter == 25){
                System.out.println("totalT : " + totalT + "rt : " + rt);
                System.out.println("Analytical : " + getAnalyticalOscillatorPosition(totalT)+ " Error : " + Math.abs(getAnalyticalOscillatorPosition(totalT) - rt));
                System.out.println();
                counter = 0;
            }
        }
    }

    public static void main(String[] args) {
        int exitCode = new CommandLine(new OscillatorMain()).execute(args);
        System.exit(exitCode);
    }
}
