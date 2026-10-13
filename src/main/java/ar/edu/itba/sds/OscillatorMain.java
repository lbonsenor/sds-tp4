package ar.edu.itba.sds;

import ar.edu.itba.sds.config.BaseConfig;
import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

import java.io.DataOutput;
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

        for (double dt : dts) {
            runOscillatorForDt(dt);
        }
        return 0;
    }

    //Currently only original verlet algorithm
    private void runOscillatorForDt(double dt) {
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
                counter = 0;
            }
        }
    }

    public static void main(String[] args) {
        int exitCode = new CommandLine(new OscillatorMain()).execute(args);
        System.exit(exitCode);
    }
}
