import os
import glob
import re
import numpy as np
import matplotlib.pyplot as plt


def calcular_tk_archivo(filepath, n, k):
    """
    Lee un archivo de simulación y devuelve el instante tk
    donde la fracción 'k' de partículas tienen color 1.
    """
    target_usadas = int(n * k)
    current_time = 0.0

    with open(filepath, 'r') as f:
        usadas_en_bloque = 0
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue

            # Cabecera de tiempo (ej: 0.1000)
            if len(parts) == 1:
                if usadas_en_bloque >= target_usadas:
                    return current_time

                current_time = float(parts[0])
                usadas_en_bloque = 0

                # Línea de partícula: id x y vx vy color
            elif len(parts) == 6:
                color = int(parts[5])
                if color == 1:
                    usadas_en_bloque += 1

        # Revisión del último bloque
        if usadas_en_bloque >= target_usadas:
            return current_time

    return None


def graficar_tk_vs_n(k, directorio="2.1.b"):
    """
    Busca los archivos, agrupa por N, calcula promedios y grafica <tk> vs N.
    """
    # Expresión regular para extraer N del nombre (ej: 2.1.b_dt5.0E-4_N_100_0.txt)
    patron = re.compile(r"2\.1\.b_dt.*_N_(\d+)_.*\.txt")

    # Buscar todos los archivos que coincidan con la nomenclatura
    archivos = glob.glob(os.path.join(directorio, "2.1.b_dt*_N_*.txt"))
    if not archivos:
        print(f"No se encontraron archivos en el directorio '{directorio}'.")
        return

    # Agrupar los tiempos por N: { N: [tk_iter0, tk_iter1, ...] }
    datos_tk = {}

    for filepath in archivos:
        match = patron.search(filepath)
        if match:
            n_part = int(match.group(1))
            tk = calcular_tk_archivo(filepath, n_part, k)

            if tk is not None:
                if n_part not in datos_tk:
                    datos_tk[n_part] = []
                datos_tk[n_part].append(tk)

    if not datos_tk:
        print(f"No se pudo calcular tk (ningún archivo alcanzó la fracción k={k}).")
        return

    # Ordenar los N de menor a mayor y calcular estadísticas
    ns = sorted(datos_tk.keys())
    tk_means = []
    tk_stds = []

    for n in ns:
        tiempos = datos_tk[n]
        tk_means.append(np.mean(tiempos))
        tk_stds.append(np.std(tiempos))

    # Generar el Gráfico
    plt.figure(figsize=(10, 6))
    plt.errorbar(ns, tk_means, yerr=tk_stds, fmt='-o',
                 capsize=5, color='darkorange', markersize=8, linewidth=2,
                 label=f'Fracción $k = {k}$')

    plt.title(f'Tiempo promedio para alcanzar fracción $k={k}$ vs $N$', fontsize=14)
    plt.xlabel('Número de partículas ($N$)', fontsize=12)
    plt.ylabel(f't_{k} [segundos]', fontsize=12)

    # Opcional: configurar escala logarítmica si N varía en varios órdenes de magnitud
    # plt.xscale('log')
    # plt.yscale('log')

    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.tight_layout()

    salida = f'tk_vs_N_k{k}.png'
    plt.savefig(salida, dpi=300)
    print(f"Gráfico generado exitosamente: {salida}")



if __name__ == '__main__':
    # Define la fracción 'k' (ej: 0.5 para el 50%, 0.9 para el 90%)
    K_PARAMETRO = 0.9

    # Ajusta el nombre del directorio donde están guardados tus archivos .txt
    DIRECTORIO_ARCHIVOS = "2.1.b"

    graficar_tk_vs_n(K_PARAMETRO, directorio=DIRECTORIO_ARCHIVOS)