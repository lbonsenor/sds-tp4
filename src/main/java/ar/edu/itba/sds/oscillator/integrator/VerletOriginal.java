package ar.edu.itba.sds.oscillator.integrator;

import ar.edu.itba.sds.telemetry.StepListener;
import ar.edu.itba.sds.oscillator.OscillatorParams;

public class VerletOriginal implements Integrator{
    @Override
    public String id() {
        return "verlet_original";
    }

    @Override
    public void integrate(OscillatorParams p, double dt, StepListener out) {
        double mInv = 1.0 / p.mass();
        double f0 = -p.k() * p.r0() - p.gamma() * p.v0();
        double r = p.r0();
        double rPrev = r - p.v0() * dt + 0.5 * f0 * mInv * dt * dt;

        double denom = 1.0 + p.gamma() * dt * 0.5 * mInv;
        double c1 = 2.0 - p.k() * dt * dt * mInv;
        double c2 = 1.0 - p.gamma() * dt * 0.5 * mInv;

        out.onStep(0.0, r);
        int n = p.steps(dt);
        for (int i = 1; i <= n; i++) {
            double rNext = (c1 * r - c2 * rPrev) / denom;
            rPrev = r;
            r = rNext;
            out.onStep(i * dt, r);
        }
    }

}
