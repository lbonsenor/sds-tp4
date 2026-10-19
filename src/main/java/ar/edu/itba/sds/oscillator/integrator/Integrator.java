package ar.edu.itba.sds.oscillator.integrator;

import ar.edu.itba.sds.telemetry.StepListener;
import ar.edu.itba.sds.oscillator.OscillatorParams;

public interface Integrator {
    String id();

    void integrate(OscillatorParams p, double dt, StepListener out);
}
