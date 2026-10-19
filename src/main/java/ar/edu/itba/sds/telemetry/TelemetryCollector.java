package ar.edu.itba.sds.telemetry;

import ar.edu.itba.sds.utils.CsvExporter;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class TelemetryCollector implements StepListener{
    private final List<OscilatorTelemetry> samples = new ArrayList<>();

    @Override
    public void onStep(double t, double r) {
        samples.add(new OscilatorTelemetry(t, r));
    }

    public void export(File target) {
        CsvExporter.exportTelemetry(samples, target, false);
    }

}
