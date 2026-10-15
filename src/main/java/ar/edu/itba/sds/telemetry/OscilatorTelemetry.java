package ar.edu.itba.sds.telemetry;

import com.opencsv.bean.CsvBindByName;

public class OscilatorTelemetry {



    @CsvBindByName(column = "t")
    private double t;

    @CsvBindByName(column = "r")
    private double r;

    public OscilatorTelemetry( double t, double r) {
        this.t = t;
        this.r = r;
    }



    public double getT() {
        return t;
    }

    public void setT(double t) {
        this.t = t;
    }

    public double getR() {
        return r;
    }

    public void setR(double r) {
        this.r = r;
    }

    @Override
    public String toString() {
        return "OscilatorTelemetry{" +
                "t=" + t +
                ", r=" + r +
                '}';
    }
}
