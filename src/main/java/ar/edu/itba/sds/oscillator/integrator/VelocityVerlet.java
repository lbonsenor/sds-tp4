package ar.edu.itba.sds.oscillator.integrator;

import ar.edu.itba.sds.telemetry.StepListener;
import ar.edu.itba.sds.oscillator.OscillatorParams;

public class VelocityVerlet implements Integrator{
    @Override
    public String id() {
        return "velocity_verlet";
    }

    @Override
    public void integrate(OscillatorParams p, double dt, StepListener out) {
        double mInv = 1.0 / p.mass();
        double r = p.r0();
        double v = p.v0();
        double f = -p.k() * r - p.gamma() * v;
        double invDenom = 1.0 / (1.0 + p.gamma() * mInv * 0.5 * dt);

        out.onStep(0.0, r);
        int n = p.steps(dt);
        for (int i = 1; i <= n; i++) {
            double vHalf = v + f * mInv * 0.5 * dt;
            r = r + vHalf * dt;
            v = (vHalf - p.k() * r * mInv * 0.5 * dt) * invDenom;
            f = -p.k() * r - p.gamma() * v;
            out.onStep(i * dt, r);
        }
    }

}
