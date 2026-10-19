import os
import re
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# CONSTANTES DE CONFIGURACIÓN
# ==========================================
SUBDIRECTORIO_DATOS = "../telemetry/oscillator"
OUTPUT_IMAGE = "ecm_vs_dt.png"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, SUBDIRECTORIO_DATOS))

NUMERICAL_METHODS = {
    "beeman": "Beeman",
    "euler_pc": "Euler Predictor-Corrector",
    "verlet_original": "Verlet Original",
    "velocity_verlet": "Velocity Verlet"
}


def load_csv(filepath):
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.upper()
    return df


def extract_dt_from_filename(filename):
    match = re.search(r'(\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)', filename)
    if match:
        return float(match.group(1))
    return None


def main():
    analytical_files = glob.glob(os.path.join(DATA_DIR, "analytical_solution_dt_*.csv"))

    if not analytical_files:
        print(f"Error: No se encontraron archivos analíticos en '{DATA_DIR}'")
        return

    analytical_map = {}
    for filepath in analytical_files:
        filename = os.path.basename(filepath)
        dt = extract_dt_from_filename(filename)
        if dt is not None:
            analytical_map[dt] = filepath

    dts = sorted(analytical_map.keys())
    print(f"Pasos temporales (dt) detectados: {dts}")

    results = {method: {} for method in NUMERICAL_METHODS.keys()}

    for dt in dts:
        ana_path = analytical_map[dt]
        df_ana = load_csv(ana_path)

        for method_key in NUMERICAL_METHODS.keys():
            pattern_with_dt = os.path.join(DATA_DIR, f"{method_key}_dt_*{dt}*.csv")
            pattern_simple = os.path.join(DATA_DIR, f"{method_key}_*{dt}*.csv")

            matching_files = glob.glob(pattern_with_dt) + glob.glob(pattern_simple)
            matching_files = list(dict.fromkeys(matching_files))

            if not matching_files:
                all_method_files = glob.glob(os.path.join(DATA_DIR, f"{method_key}*.csv"))
                for f in all_method_files:
                    f_dt = extract_dt_from_filename(os.path.basename(f))
                    if f_dt is not None and np.isclose(f_dt, dt):
                        matching_files.append(f)
                        break

            if matching_files:
                num_path = matching_files[0]
                df_num = load_csv(num_path)
                merged = pd.merge(df_num, df_ana, on="T", suffixes=("_num", "_ana"))
                diff = merged["R_num"] - merged["R_ana"]
                ecm = np.mean(diff ** 2)
                results[method_key][dt] = ecm
            else:
                print(f"Advertencia: No se encontró archivo para el método '{method_key}' con dt={dt}")

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
            plt.plot(dt_values, ecm_values, label=method_label, marker=marker,
                     color=color, linewidth=1.8, markersize=6)

    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('$dt$ (s)', fontsize=12)
    plt.ylabel('$ECM$ ($m^2$)', fontsize=12)
    plt.grid(True, which="both", linestyle="--", alpha=0.6)
    plt.legend(fontsize=10, loc='best')
    plt.tight_layout()

    salida_img = os.path.join(SCRIPT_DIR, OUTPUT_IMAGE)
    plt.savefig(salida_img, dpi=300)
    print(f"\n¡Gráfico guardado exitosamente como '{salida_img}'!")


if __name__ == "__main__":
    main()