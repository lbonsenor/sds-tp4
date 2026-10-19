package ar.edu.itba.sds.telemetry;

@FunctionalInterface
public interface StepListener {
    void onStep(double t, double r);

    default StepListener andThen(StepListener next) {
        return (t, r) -> {
            onStep(t, r);
            next.onStep(t, r);
        };
    }
}

