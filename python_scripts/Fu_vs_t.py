import os
import glob
import re
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def leer_evolucion_archivo(filepath, n):
    """
    Lee un archivo de simulación y devuelve dos listas:
    los tiempos y la fracción de partículas usadas en ese instante.
    """
    times = []
    fractions = []

    current_time = 0.0
    in_block = False
    usadas_en_bloque = 0

    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue

            # Cabecera de tiempo (ej: 0.1000)
            if len(parts) == 1:
                # Si veníamos de un bloque, guardamos los datos calculados
                if in_block:
                    times.append(current_time)
                    fractions.append(usadas_en_bloque / n)

                current_time = float(parts[0])
                usadas_en_bloque = 0
                in_block = True

            # Línea de partícula: id x y vx vy color
            elif len(parts) == 6:
                color = int(parts[5])
                if color == 1:
                    usadas_en_bloque += 1

        # Guardar el último bloque al terminar el archivo
        if in_block:
            times.append(current_time)
            fractions.append(usadas_en_bloque / n)

    return times, fractions


def graficar_evolucion(n, directorio="2.2"):
    """
    Busca los archivos de la iteración 0 para un N dado,
    calcula la evolución temporal y grafica todos los obstáculos con un gradiente de color.
    """
    # Buscamos solo los archivos que terminan en iter_0.txt para tener 1 sola realización
    patron = re.compile(rf".*_N{n}_.*_obstD_([0-9.eE+-]+)_iter_0\.txt")
    archivos = glob.glob(os.path.join(directorio, f"*_N{n}_*_iter_0.txt"))

    if not archivos:
        print(f"Advertencia: No se encontraron archivos para N={n} e iter_0 en '{directorio}'.")
        return

    datos_plot = []

    # Procesar cada archivo encontrado
    for filepath in archivos:
        match = patron.search(filepath)
        if match:
            dist = float(match.group(1))
            t, frac = leer_evolucion_archivo(filepath, n)
            datos_plot.append((dist, t, frac))

    # Ordenar por distancia del obstáculo
    datos_plot.sort(key=lambda x: x[0])

    if not datos_plot:
        return

    # --- Lógica para el gradiente de colores ---
    distancias = [item[0] for item in datos_plot]
    min_dist = min(distancias)
    max_dist = max(distancias)

    # Normalizamos los valores de distancia entre 0 y 1 para mapearlos a colores
    # (Si solo hubiera 1 distancia, evitamos división por cero)
    if max_dist == min_dist:
        norm = plt.Normalize(vmin=min_dist - 1, vmax=max_dist + 1)
    else:
        norm = plt.Normalize(vmin=min_dist, vmax=max_dist)

    # Elegir el colormap (viridis, plasma, inferno, coolwarm, etc.)
    cmap = plt.get_cmap('plasma')

    # Generar el gráfico
    plt.figure(figsize=(10, 6))

    for dist, t, frac in datos_plot:
        # Calcular el color específico para este valor de x_0
        color = cmap(norm(dist))

        plt.plot(t, frac, label=f'{dist}', linewidth=1.5, color=color)

    plt.title(f'$N = {n}$', fontsize=14)
    plt.xlabel('t(s)', fontsize=12)
    plt.ylabel('Fu', fontsize=12)

    # Línea punteada horizontal para mostrar el umbral del 90%
    plt.axhline(y=0.9, color='black', linestyle='--', alpha=0.6, label='Umbral 90%')

    plt.ylim(0, 1.05)
    plt.xlim(left=0)
    plt.grid(True, linestyle='--', alpha=0.7)

    # Ubicar la leyenda fuera si hay muchas curvas para no tapar los datos, o dentro si son pocas
    plt.legend(title="X0 (m)" ,fontsize=10, loc='lower right')
    plt.tight_layout()

    # Guardar gráfico
    salida = f'evolucion_k_N{n}.png'
    plt.savefig(salida, dpi=300)
    print(f"Gráfico generado exitosamente: {salida}")
    plt.close()


if __name__ == '__main__':
    # Carpeta donde están tus .txt
    carpeta_datos = "2.2"

    # Generar gráfico para N=20
    graficar_evolucion(20, directorio=carpeta_datos)

    # Generar gráfico para N=100
    graficar_evolucion(100, directorio=carpeta_datos)