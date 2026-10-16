import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def main():
    # =========================================================
    # 1. Cargar y procesar datos de TP3 (Event-Driven - CSV)
    # =========================================================
    try:
        df_tp3 = pd.read_csv('run_config.csv')
        # Convertir a segundos para que sea comparable con TP4
        df_tp3['TIME_SECONDS'] = df_tp3['EXECUTION_TIME_MS'] / 1000.0

        # Agrupar por N para obtener el promedio y la desviación estándar
        tp3_stats = df_tp3.groupby('N')['TIME_SECONDS'].agg(['mean', 'std']).reset_index()
        tp3_stats = tp3_stats.sort_values('N')
        print("Datos TP3 cargados con éxito.")
    except Exception as e:
        print(f"Error al leer run_config.csv: {e}")
        return

    # =========================================================
    # 2. Cargar y procesar datos de TP4 (Time-Driven - TXT)
    # =========================================================
    archivos_txt = glob.glob("*.txt")
    dfs_tp4 = []

    for f in archivos_txt:
        try:
            # Leer el archivo txt asumiendo que los valores están separados por espacios
            df = pd.read_csv(f, sep=r'\s+')
            # Verificar que sea el archivo correcto viendo si tiene las columnas necesarias
            if all(col in df.columns for col in ['N', 'runCount', 'time']):
                dfs_tp4.append(df)
        except Exception:
            continue

    if not dfs_tp4:
        print("No se encontraron archivos .txt con el formato esperado ('N runCount time').")
        return

    # Combinar todos los txt en un solo DataFrame
    df_tp4 = pd.concat(dfs_tp4, ignore_index=True)

    # Agrupar por N para obtener el promedio y la desviación estándar
    tp4_stats = df_tp4.groupby('N')['time'].agg(['mean', 'std']).reset_index()
    tp4_stats = tp4_stats.sort_values('N')
    print(f"Datos TP4 cargados con éxito desde {len(dfs_tp4)} archivo(s).")

    # =========================================================
    # 3. Generar el Gráfico Comparativo
    # =========================================================
    fig, ax = plt.subplots(figsize=(10, 6))

    # Graficar TP3 (Event-Driven)
    ax.errorbar(tp3_stats['N'], tp3_stats['mean'], yerr=tp3_stats['std'],
                fmt='-o', capsize=5, label='Event-Driven (TP3)',
                color='blue', markersize=6, linewidth=2)

    # Graficar TP4 (Time-Driven)
    ax.errorbar(tp4_stats['N'], tp4_stats['mean'], yerr=tp4_stats['std'],
                fmt='-s', capsize=5, label='Time-Driven (TP4)',
                color='red', markersize=6, linewidth=2)

    # Configuración del gráfico
    ax.set_title('Comparación de Tiempos de Ejecución vs Cantidad de Partículas (N)', fontsize=14)
    ax.set_xlabel('Cantidad de Partículas (N)', fontsize=12)
    ax.set_ylabel('Tiempo de Ejecución (Segundos)', fontsize=12)

    # Escala logarítmica (Opcional pero recomendada):
    # Generalmente los simuladores moleculares escalan de forma cuadrática O(N^2)
    # Descomenta la siguiente línea si la diferencia entre TP3 y TP4 es demasiado grande visualmente
    ax.set_yscale('log')

    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(fontsize=11)

    plt.tight_layout()

    # Guardar gráfico
    ruta_salida = 'comparacion_tiempos_ejecucion.png'
    plt.savefig(ruta_salida, dpi=300)
    print(f"Gráfico guardado exitosamente en: {ruta_salida}")

    # Cierra la figura en caso de ser ejecutado en entornos no interactivos
    plt.close()


if __name__ == '__main__':
    main()