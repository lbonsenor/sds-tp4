package ar.edu.itba.sds.Utils;

import com.opencsv.CSVWriter;
import com.opencsv.bean.StatefulBeanToCsv;
import com.opencsv.bean.StatefulBeanToCsvBuilder;
import com.opencsv.exceptions.CsvDataTypeMismatchException;
import com.opencsv.exceptions.CsvRequiredFieldEmptyException;

import java.io.*;
import java.util.Collection;

public class CsvExporter {

    private static final String TELEMETRY_DIR = "telemetry";

    public static <T> void exportTelemetry(Collection<T> records, File targetFile, boolean append) {
        ensureDirectoryExists(targetFile.getParent());

        boolean fileExists = targetFile.exists() && targetFile.length() > 0;
        boolean skipHeader = append && fileExists;

        String csvContent = renderToCsv(records);
        if (csvContent == null) {
            return; // error already logged in renderToCsv
        }
        if (skipHeader) {
            csvContent = stripFirstLine(csvContent);
        }

        try (Writer writer = new FileWriter(targetFile, append)) {
            writer.write(csvContent);
        } catch (IOException e) {
            System.err.println("Error writing telemetry records: " + e.getMessage());
        }
    }

    /**
     * Convenient string-path helper overload.
     */
    public static <T> void exportTelemetry(Collection<T> records, String fileName, boolean append) {
        exportTelemetry(records, new File(TELEMETRY_DIR, fileName), append);
    }

    private static <T> String renderToCsv(Collection<T> records) {
        StringWriter buffer = new StringWriter();
        try {
            StatefulBeanToCsv<T> beanToCsv = new StatefulBeanToCsvBuilder<T>(buffer)
                    .withQuotechar(CSVWriter.NO_QUOTE_CHARACTER)
                    .withSeparator(',')
                    .build();
            beanToCsv.write(records.iterator());
        } catch (CsvDataTypeMismatchException | CsvRequiredFieldEmptyException e) {
            System.err.println("Error exporting telemetry records: " + e.getMessage());
            return null;
        }
        return buffer.toString();
    }

    private static String stripFirstLine(String csvContent) {
        int firstNewline = csvContent.indexOf('\n');
        return firstNewline >= 0 ? csvContent.substring(firstNewline + 1) : "";
    }

    private static void ensureDirectoryExists(String path) {
        if (path == null) return;
        File dir = new File(path);
        if (!dir.exists()) dir.mkdirs();
    }
}