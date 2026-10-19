package ar.edu.itba.sds.oscillator;

import ar.edu.itba.sds.oscillator.integrator.Integrator;
import ar.edu.itba.sds.telemetry.TelemetryCollector;

import java.io.File;

public class OscillatorExp {
    private final OscillatorParams params;
    private final File outputDir;

    public OscillatorExp(OscillatorParams params, File outputDir) {
        this.params = params;
        this.outputDir = outputDir;
    }

    public void run(Integrator integrator, double dt) {
        TelemetryCollector collector = new TelemetryCollector();
        integrator.integrate(params, dt, collector);
        collector.export(new File(outputDir, integrator.id() + "_dt_" + dt + ".csv"));
    }

}
