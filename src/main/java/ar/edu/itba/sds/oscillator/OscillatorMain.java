package ar.edu.itba.sds.oscillator;

import ar.edu.itba.sds.config.BaseConfig;
import ar.edu.itba.sds.oscillator.integrator.*;
import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

import java.io.File;
import java.util.List;

@Command(
        name = "oscillator",
        mixinStandardHelpOptions = true,
        version = "1.0",
        description = "Punto 1: Integración del Oscilador Amortiguado para distintos dt"
)
public class OscillatorMain extends BaseConfig {

    @Option(names = {"--dts"}, split = ",", description = "Pasos temporales dt a evaluar")
    private List<Double> dts = List.of(1e-2, 5e-3, 1e-3, 5e-4, 1e-4, 5e-5);

    @Option(names = {"-o", "--output-dir"}, description = "Directorio de salida para CSVs")
    private File outputDir = new File("telemetry/oscillator");

    @Override
    public Integer call() throws Exception {
        loadJsonConfig();

        OscillatorParams p = OscillatorParams.defaults();
        System.out.println("=== SISTEMA 1: Oscilador Amortiguado ===");
        System.out.printf("Condiciones: m=%.1f kg | k=%.1f N/m | gamma=%.1f kg/s | tf=%.1f s%n",
                p.mass(), p.k(), p.gamma(), p.tf());
        System.out.println("Evaluando dts: " + dts);

        OscillatorExp experiment = new OscillatorExp(p, outputDir);

        List<Integrator> integrators = List.of(
                new VerletOriginal(),
                new VelocityVerlet(),
                new Beeman(),
                new EulerPredictorCorrector(),
                new Analytical());

        for (double dt : dts) {
            for (Integrator integrator : integrators) {
                experiment.run(integrator, dt);
            }
        }
        return 0;
    }

    public static void main(String[] args) {
        System.exit(new CommandLine(new OscillatorMain()).execute(args));
    }
}