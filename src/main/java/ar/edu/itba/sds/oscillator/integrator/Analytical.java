package ar.edu.itba.sds.oscillator.integrator;

import ar.edu.itba.sds.telemetry.StepListener;
import ar.edu.itba.sds.oscillator.OscillatorParams;

public class Analytical implements Integrator{
    @Override
    public String id() {
        return "analytical_solution";
    }

    @Override
    public void integrate(OscillatorParams p, double dt, StepListener out) {
        out.onStep(0.0, p.r0());
        int n = p.steps(dt);
        for (int i = 1; i <= n; i++) {
            double t = i * dt;
            out.onStep(t, p.analyticalPosition(t));
        }
    }

}
