package ar.edu.itba.sds.oscillator;

public record OscillatorParams(double mass, double k, double gamma, double r0, double v0, double tf) {

    public static OscillatorParams defaults() {
        double m = 70.0, gamma = 100.0;
        return new OscillatorParams(m, 10000.0, gamma, 1.0, -gamma / (2.0 * m), 5.0);
    }

    public double gammaOver2m() {
        return gamma / (2.0 * mass);
    }

    public double omega() {
        double g = gammaOver2m();
        return Math.sqrt(k / mass - g * g);
    }

    public double amplitude() {
        return Math.sqrt(r0 * r0 + Math.pow((v0 + gammaOver2m() * r0) / omega(), 2));
    }

    public double acceleration(double r, double v) {
        double massInverse = 1.0 / mass;
        return (-k * r - gamma * v) * massInverse;
    }

    public double analyticalPosition(double t) {
        return amplitude() * Math.exp(-gammaOver2m() * t) * Math.cos(omega() * t);
    }

    public int steps(double dt) {
        return (int) Math.round(tf / dt);
    }
}