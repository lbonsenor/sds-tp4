package ar.edu.itba.sds.oscillator.integrator;

import ar.edu.itba.sds.telemetry.StepListener;
import ar.edu.itba.sds.oscillator.OscillatorParams;

public class Beeman implements Integrator{
    @Override
    public String id() {
        return "beeman";
    }

    @Override
    public void integrate(OscillatorParams p, double dt, StepListener out) {
        double r = p.r0();
        double v = p.v0();
        double a = p.acceleration(r, v);

        double rPrev = r - v * dt + 0.5 * a * dt * dt;
        double vPrev = v - a * dt;
        double aPrev = p.acceleration(rPrev, vPrev);

        out.onStep(0.0, r);
        int n = p.steps(dt);
        for (int i = 1; i <= n; i++) {
            double rNext = r + v * dt + (2.0 / 3.0) * a * dt * dt - (1.0 / 6.0) * aPrev * dt * dt;
            double vPred = v + 1.5 * a * dt - 0.5 * aPrev * dt;
            double aNext = p.acceleration(rNext, vPred);
            double vNext = v + (1.0 / 3.0) * aNext * dt + (5.0 / 6.0) * a * dt - (1.0 / 6.0) * aPrev * dt;

            aPrev = a;
            a = p.acceleration(rNext, vNext);
            r = rNext;
            v = vNext;
            out.onStep(i * dt, r);
        }
    }

}
