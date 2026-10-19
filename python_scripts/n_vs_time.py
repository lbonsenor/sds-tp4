import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# CONSTANTES DE CONFIGURACIÓN
# ==========================================
SUBDIRECTORIO_TP3 = "."
ARCHIVO_CSV_TP3 = "run_config.csv"
SUBDIRECTORIO_TP4 = "."
PATRON_TXT_TP4 = "*.txt"
OUTPUT_IMAGE = "comparacion_tiempos_ejecucion.png"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    # 1. Cargar datos de TP3
    path_csv = os.path.abspath(os.path.join(SCRIPT_DIR, SUBDIRECTORIO_TP3, ARCHIVO_CSV_TP3))
    try:
        df_tp3 = pd.read_csv(path_csv)
        df_tp3['TIME_SECONDS'] = df_tp3['EXECUTION_TIME_MS'] / 1000.0
        tp3_stats = df_tp3.groupby('N')['TIME_SECONDS'].agg(['mean', 'std']).reset_index()
        tp3_stats = tp3_stats.sort_values('N')
        print("Datos TP3 cargados con éxito.")
    except Exception as e:
        print(f"Error al leer '{path_csv}': {e}")
        return

    # 2. Cargar datos de TP4
    dir_tp4 = os.path.abspath(os.path.join(SCRIPT_DIR, SUBDIRECTORIO_TP4))
    archivos_txt = glob.glob(os.path.join(dir_tp4, PATRON_TXT_TP4))
    dfs_tp4 = []

    for f in archivos_txt:
        try:
            df = pd.read_csv(f, sep=r'\s+')
            if all(col in df.columns for col in ['N', 'runCount', 'time']):
                dfs_tp4.append(df)
        except Exception:
            continue

    if not dfs_tp4:
        print(f"No se encontraron archivos .txt válidos en '{dir_tp4}'.")
        return

    df_tp4 = pd.concat(dfs_tp4, ignore_index=True)
    tp4_stats = df_tp4.groupby('N')['time'].agg(['mean', 'std']).reset_index()
    tp4_stats = tp4_stats.sort_values('N')
    print(f"Datos TP4 cargados con éxito desde {len(dfs_tp4)} archivo(s).")

    # 3. Generar Gráfico
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.errorbar(tp3_stats['N'], tp3_stats['mean'], yerr=tp3_stats['std'],
                fmt='-o', capsize=5, label='Event-Driven (TP3)',
                color='blue', markersize=6, linewidth=2)

    ax.errorbar(tp4_stats['N'], tp4_stats['mean'], yerr=tp4_stats['std'],
                fmt='-s', capsize=5, label='Time-Driven (TP4)',
                color='red', markersize=6, linewidth=2)

    ax.set_title('Comparación de Tiempos de Ejecución vs Cantidad de Partículas (N)', fontsize=14)
    ax.set_xlabel('Cantidad de Partículas (N)', fontsize=12)
    ax.set_ylabel('Tiempo de Ejecución (Segundos)', fontsize=12)
    ax.set_yscale('log')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(fontsize=11)
    plt.tight_layout()

    ruta_salida = os.path.join(SCRIPT_DIR, OUTPUT_IMAGE)
    plt.savefig(ruta_salida, dpi=300)
    print(f"Gráfico guardado exitosamente en: {ruta_salida}")
    plt.close()


if __name__ == '__main__':
    main()