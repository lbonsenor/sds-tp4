import os
import re
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Directorio donde están guardados los archivos CSV
DATA_DIR = "../telemetry/oscillator"
OUTPUT_IMAGE = "ecm_vs_dt.png"

# Métodos numéricos a comparar
NUMERICAL_METHODS = {
    "beeman": "Beeman",
    "euler_pc": "Euler Predictor-Corrector",
    "verlet_original": "Verlet Original",
    "velocity_verlet": "Velocity Verlet"
}

def load_csv(filepath):
    """Carga un archivo CSV asumiendo columnas R y T (o variantes en minúsculas)."""
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.upper()
    return df

def extract_dt_from_filename(filename):
    """Extrae el valor numérico de dt desde el nombre del archivo."""
    # Busca patrones numéricos en notación decimal o científica (ej: 0.01, 1.0E-4, 1e-05)
    match = re.search(r'(\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)', filename)
    if match:
        return float(match.group(1))
    return None

def main():
    # 1. Identificar todos los archivos analíticos disponibles para determinar los dt evaluados
    analytical_files = glob.glob(os.path.join(DATA_DIR, "analytical_solution_dt_*.csv"))

    if not analytical_files:
        print(f"Error: No se encontraron archivos analíticos en '{DATA_DIR}'")
        return

    # Mapear dt -> ruta del archivo analítico
    analytical_map = {}
    for filepath in analytical_files:
        filename = os.path.basename(filepath)
        dt = extract_dt_from_filename(filename)
        if dt is not None:
            analytical_map[dt] = filepath

    dts = sorted(analytical_map.keys())
    print(f"Pasos temporales (dt) detectados: {dts}")

    # Estructura para almacenar resultados: { método: { dt: ecm_value } }
    results = {method: {} for method in NUMERICAL_METHODS.keys()}

    # 2. Procesar cada dt y calcular el ECM para los 4 métodos
    for dt in dts:
        ana_path = analytical_map[dt]
        df_ana = load_csv(ana_path)

        for method_key in NUMERICAL_METHODS.keys():
            # Buscar el archivo correspondiente al método y este dt específico
            # Formatos posibles: e.g., 'beeman_dt_0.01.csv' o 'verlet_original_0.01.csv'
            pattern_with_dt = os.path.join(DATA_DIR, f"{method_key}_dt_*{dt}*.csv")
            pattern_simple = os.path.join(DATA_DIR, f"{method_key}_*{dt}*.csv")

            matching_files = glob.glob(pattern_with_dt) + glob.glob(pattern_simple)
            # Eliminar duplicados manteniendo orden
            matching_files = list(dict.fromkeys(matching_files))

            if not matching_files:
                # Intento de búsqueda alternativa basada en el valor float exacto
                all_method_files = glob.glob(os.path.join(DATA_DIR, f"{method_key}*.csv"))
                for f in all_method_files:
                    f_dt = extract_dt_from_filename(os.path.basename(f))
                    if f_dt is not None and np.isclose(f_dt, dt):
                        matching_files.append(f)
                        break

            if matching_files:
                num_path = matching_files[0]
                df_num = load_csv(num_path)

                # Unir por tiempo 'T' para asegurar alineación perfecta de las filas
                merged = pd.merge(df_num, df_ana, on="T", suffixes=("_num", "_ana"))

                # Calcular Error Cuadrático Medio: ECM = (1/N) * sum((r_num - r_ana)^2)
                diff = merged["R_num"] - merged["R_ana"]
                ecm = np.mean(diff ** 2)

                results[method_key][dt] = ecm
            else:
                print(f"Advertencia: No se encontró archivo para el método '{method_key}' con dt={dt}")

    # 3. Graficar los resultados en escala Log-Log
    plt.figure(figsize=(9, 6))

    markers = ['o', 's', '^', 'd']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    for (method_key, method_label), marker, color in zip(NUMERICAL_METHODS.items(), markers, colors):
        dt_values = []
        ecm_values = []

        for dt in dts:
            if dt in results[method_key]:
                dt_values.append(dt)
                ecm_values.append(results[method_key][dt])

        if dt_values:
            plt.plot(
                dt_values,
                ecm_values,
                label=method_label,
                marker=marker,
                color=color,
                linewidth=1.8,
                markersize=6
            )

    # Configuración de ejes y escala
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('$dt$ (s)', fontsize=12)
    plt.ylabel('$ECM$ ($m^2$)', fontsize=12)
    # plt.title('Oscilador Amortiguado: $ECM$ vs. Paso Temporal ($dt$)', fontsize=14, fontweight='bold')
    plt.grid(True, which="both", linestyle="--", alpha=0.6)
    plt.legend(fontsize=10, loc='best')
    plt.tight_layout()

    # Guardar el gráfico resultante como imagen
    plt.savefig(OUTPUT_IMAGE, dpi=300)
    print(f"\n¡Gráfico guardado exitosamente como '{OUTPUT_IMAGE}'!")

if __name__ == "__main__":
    main()