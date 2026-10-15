package ar.edu.itba.sds.telemetry;

import com.opencsv.bean.CsvBindByName;

public class RunConfig {
    @CsvBindByName(column = "run_id")
    private String runId;

    @CsvBindByName(column = "dt")
    private double dt;

    @CsvBindByName(column = "tf")
    private float tf;

    public RunConfig(String runId, double dt, float tf) {
        this.runId = runId;
        this.dt = dt;
        this.tf = tf;
    }

    public String getRunId() {
        return runId;
    }

    public void setRunId(String runId) {
        this.runId = runId;
    }

    public double getDt() {
        return dt;
    }

    public void setDt(double dt) {
        this.dt = dt;
    }

    public float getTf() {
        return tf;
    }

    public void setTf(float tf) {
        this.tf = tf;
    }

    @Override
    public String toString() {
        return "RunConfig{" +
                "runId='" + runId + '\'' +
                ", dt=" + dt +
                ", tf=" + tf +
                '}';
    }
}
