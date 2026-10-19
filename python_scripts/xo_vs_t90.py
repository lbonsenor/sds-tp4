import os
import glob
import re
import numpy as np
import matplotlib.pyplot as plt


def calcular_t90_archivo(filepath, n):
    target_usadas = int(n * 0.9)
    current_time = 0.0

    with open(filepath, 'r') as f:
        usadas_en_bloque = 0
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue

            if len(parts) == 1:
                if usadas_en_bloque >= target_usadas:
                    return current_time

                current_time = float(parts[0])
                usadas_en_bloque = 0

            elif len(parts) == 6:
                color = int(parts[5])
                if color == 1:
                    usadas_en_bloque += 1

        if usadas_en_bloque >= target_usadas:
            return current_time

    return None


def graficar_t90(n, subdirectorio="2.2"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    directorio = os.path.abspath(os.path.join(script_dir, "..", subdirectorio))

    patron = re.compile(rf".*_N{n}_.*_obstD_([0-9.]+)_iter_.*\.txt")

    archivos = glob.glob(os.path.join(directorio, f"*_N{n}_*.txt"))
    if not archivos:
        print(f"No se encontraron archivos para N={n} en el directorio '{directorio}'.")
        return

    datos_t90 = {}

    for filepath in archivos:
        match = patron.search(filepath)
        if match:
            dist = float(match.group(1))
            t90 = calcular_t90_archivo(filepath, n)

            if t90 is not None:
                if dist not in datos_t90:
                    datos_t90[dist] = []
                datos_t90[dist].append(t90)

    if not datos_t90:
        print("No se pudo calcular t90 para los archivos encontrados.")
        return

    distancias = sorted(datos_t90.keys())
    t90_means = []
    t90_stds = []

    for dist in distancias:
        tiempos = datos_t90[dist]
        t90_means.append(np.mean(tiempos))
        t90_stds.append(np.std(tiempos))

    plt.figure(figsize=(10, 6))
    plt.errorbar(distancias, t90_means, yerr=t90_stds, fmt='-o',
                 capsize=5, color='teal', markersize=8, linewidth=2,
                 label=f'N = {n}')

    plt.title(f'Tiempo para alcanzar el 90% de partículas usadas ($t_{{90}}$) vs Posición del Obstáculo', fontsize=14)
    plt.xlabel('Distancia del obstáculo al origen ($x_o$) [m]', fontsize=12)
    plt.ylabel('$t_{90}$ [segundos]', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.ylim(0, 35)

    salida = os.path.join(script_dir, f't90_vs_distancia_N{n}.png')
    plt.savefig(salida, dpi=300)
    print(f"Gráfico generado exitosamente: {salida}")


if __name__ == '__main__':
    N_PARAMETRO = 100
    graficar_t90(N_PARAMETRO, subdirectorio="2.2")