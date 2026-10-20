import os
import glob
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import xticks


def calcular_t90_archivo(filepath, n):
    """
    Lee un archivo de simulación y devuelve el instante t90
    donde el 90% de las partículas tienen color 1.
    """
    target_usadas = int(n * 0.9)
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
                usadas_en_bloque = 0  # Reiniciamos el contador para el nuevo bloque

            # Línea de partícula: id x y vx vy color
            elif len(parts) == 6:
                color = int(parts[5])
                if color == 1:
                    usadas_en_bloque += 1

        # Revisar el último bloque en caso de que termine allí
        if usadas_en_bloque >= target_usadas:
            return current_time

    return None


def graficar_t90(directorio="2.2"):
    """
    Busca los archivos para N=20 y N=100, calcula el t90 promedio y los grafica juntos.
    """
    n_values = [20, 100]
    colores = {20: 'blue', 100: 'red'}
    datos_por_n = {}

    # 1. Procesar los archivos para cada N
    for n in n_values:
        patron = re.compile(rf".*_N{n}_.*_obstD_([0-9.eE+-]+)_iter_.*\.txt")
        archivos = glob.glob(os.path.join(directorio, f"*_N{n}_*.txt"))

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

        if datos_t90:
            datos_por_n[n] = datos_t90
        else:
            print(f"Advertencia: No se encontraron o no se pudo calcular t90 para N={n}.")

    # Si ninguna de las dos series tiene datos, interrumpimos
    if not datos_por_n:
        print("Error: No se obtuvieron datos válidos para graficar.")
        return

    # 2. Generar el Gráfico
    plt.figure(figsize=(10, 6))

    for n, datos_t90 in datos_por_n.items():
        distancias = sorted(datos_t90.keys())
        t90_means = [np.mean(datos_t90[d]) for d in distancias]
        t90_stds = [np.std(datos_t90[d]) for d in distancias]

        plt.errorbar(distancias, t90_means, yerr=t90_stds, fmt='-o',
                     capsize=5, color=colores[n], markersize=8, linewidth=2,
                     label=f'N = {n}')


    plt.xlabel('X0 (m)', fontsize=12)
    plt.ylabel('t90 (s)', fontsize=12)

    # Escala fija en el eje Y hasta 35 segundos
    plt.ylim(0, 35)
    ticks = np.arange(0, 0.4925, 0.05)
    ticks = np.append(ticks , 0.4925)
    print(ticks)
    xticks(ticks, rotation=45)



    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.tight_layout()

    salida = 't90_vs_distancia_N20_N100.png'
    plt.savefig(salida, dpi=300)
    print(f"Gráfico generado exitosamente: {salida}")
    plt.show()


if __name__ == '__main__':
    graficar_t90(directorio="2.2")