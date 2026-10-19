package ar.edu.itba.sds.oscillator.integrator;

import ar.edu.itba.sds.telemetry.StepListener;
import ar.edu.itba.sds.oscillator.OscillatorParams;

public class EulerPredictorCorrector implements Integrator{
    @Override
    public String id() {
        return "euler_pc";
    }

    @Override
    public void integrate(OscillatorParams p, double dt, StepListener out) {
        double r = p.r0();
        double v = p.v0();
        double a = p.acceleration(r, v);

        out.onStep(0.0, r);
        int n = p.steps(dt);
        for (int i = 1; i <= n; i++) {
            double vPred = v + a * dt;
            double rPred = r + v * dt;
            double aPred = p.acceleration(rPred, vPred);
            v = v + aPred * dt;
            r = r + v * dt;
            a = p.acceleration(r, v);
            out.onStep(i * dt, r);
        }
    }

}
