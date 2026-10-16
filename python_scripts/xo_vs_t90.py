import os
import glob
import re
import numpy as np
import matplotlib.pyplot as plt


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

            # Si la línea tiene 1 solo elemento, es la cabecera del tiempo (ej: 0.1000)
            if len(parts) == 1:
                # Si en el bloque anterior ya llegamos al 90%, devolvemos el tiempo de ese bloque
                if usadas_en_bloque >= target_usadas:
                    return current_time

                current_time = float(parts[0])
                usadas_en_bloque = 0  # Reiniciamos el contador para el nuevo bloque

            # Si la línea tiene 6 elementos, es una partícula: id x y vx vy color
            elif len(parts) == 6:
                color = int(parts[5])
                if color == 1:
                    usadas_en_bloque += 1

        # Revisar el último bloque en caso de que termine allí
        if usadas_en_bloque >= target_usadas:
            return current_time

    # Si nunca llega al 90%, retornamos None o el tiempo máximo
    return None


def graficar_t90(n, directorio="2.2"):
    """
    Busca los archivos para un N dado, calcula el t90 promedio y grafica.
    """
    # Expresión regular para extraer la distancia del nombre del archivo
    # Ej: 2.2_N100_dt5.0E-4_obstD_0.035_iter_0.txt
    patron = re.compile(rf".*_N{n}_.*_obstD_([0-9.]+)_iter_.*\.txt")

    archivos = glob.glob(os.path.join(directorio, f"*_N{n}_*.txt"))
    if not archivos:
        print(f"No se encontraron archivos para N={n} en el directorio '{directorio}'.")
        return

    # Diccionario para agrupar los t90 por distancia: { distancia: [t90_iter0, t90_iter1, ...] }
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
        print("No se pudo calcular t90 para los archivos encontrados (ninguno llegó al 90%).")
        return

    # Procesar los datos para el gráfico
    distancias = sorted(datos_t90.keys())
    t90_means = []
    t90_stds = []

    for dist in distancias:
        tiempos = datos_t90[dist]
        t90_means.append(np.mean(tiempos))
        t90_stds.append(np.std(tiempos))

    # Generar el Gráfico
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

    salida = f't90_vs_distancia_N{n}.png'
    plt.savefig(salida, dpi=300)
    print(f"Gráfico generado exitosamente: {salida}")


if __name__ == '__main__':
    # Puedes cambiar este parámetro a 20 o 100
    N_PARAMETRO = 20

    # Asume que los archivos .txt están en una subcarpeta llamada "2.2"
    # Si están en la misma carpeta que el script, cambia "2.2" por "."
    graficar_t90(N_PARAMETRO, directorio="2.2")