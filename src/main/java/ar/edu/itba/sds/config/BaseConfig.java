package ar.edu.itba.sds.config;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import picocli.CommandLine;
import tools.jackson.databind.DeserializationFeature;
import tools.jackson.databind.ObjectMapper;
import tools.jackson.databind.json.JsonMapper;

import java.io.File;
import java.io.IOException;
import java.util.concurrent.Callable;

@JsonIgnoreProperties(ignoreUnknown = true)
public abstract class BaseConfig implements Callable<Integer> {

    @CommandLine.Option(
            names = {"-c", "--config"},
            description = "Ruta al archivo de configuración JSON"
    )
    protected File configFile;

    protected void loadJsonConfig() throws IOException {
        if (configFile != null && configFile.exists()) {
            ObjectMapper mapper = JsonMapper.builder()
                    .enable(DeserializationFeature.ACCEPT_SINGLE_VALUE_AS_ARRAY)
                    .build();
            mapper.readerForUpdating(this).readValue(configFile);
        }
    }
}
