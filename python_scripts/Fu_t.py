import os
import re
import glob
import numpy as np
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Directorio donde se encuentran los archivos del inciso 2.2
DIRECTORY = os.path.join(SCRIPT_DIR, "2.2")

def parse_simulation_file(file_path):
    """
    Parsea un archivo de salida de la simulación.
    Retorna dos arrays: tiempos (t) y la fracción de partículas usadas Fu(t).
    """
    times = []
    fu_list = []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    i = 0
    num_lines = len(lines)

    while i < num_lines:
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Detectar la línea que indica el tiempo t (ej: "0.0000" o "0.1000")
        parts = line.split()
        if len(parts) == 1:
            try:
                t = float(parts[0])
                i += 1

                # Leer las siguientes N líneas correspondientes a las partículas
                used_count = 0
                total_particles = 0

                while i < num_lines and len(lines[i].strip().split()) > 1:
                    p_data = lines[i].strip().split()
                    # La última columna indica si la partícula está usada (1) o fresca (0)
                    is_used = int(p_data[-1])
                    if is_used == 1:
                        used_count += 1
                    total_particles += 1
                    i += 1

                if total_particles > 0:
                    times.append(t)
                    fu_list.append(used_count / total_particles)
                continue
            except ValueError:
                pass
        i += 1

    return np.array(times), np.array(fu_list)

def process_and_plot_for_N(n_particles):
    """
    Procesa todos los archivos para un N dado, agrupa las iteraciones por obstD,
    calcula Fu medio y std, y genera un gráfico lineal con barras de error.
    """
    # Patrón para buscar archivos del N específico
    pattern = os.path.join(DIRECTORY, f"*N{n_particles}_*obstD_*.txt")
    files = glob.glob(pattern)

    if not files:
        print(f"No se encontraron archivos para N = {n_particles} en '{DIRECTORY}'.")
        return

    # Estructura: { obstD: { iter_id: (t_array, fu_array) } }
    data_by_obstd = {}

    for file_path in files:
        filename = os.path.basename(file_path)
        # Extraer el valor de obstD
        match_obstd = re.search(r"obstD_([0-9\.eE\-]+)", filename)
        if not match_obstd:
            continue
        obstd_val = float(match_obstd.group(1))

        # Parsear archivo
        t_arr, fu_arr = parse_simulation_file(file_path)
        if len(t_arr) == 0:
            continue

        if obstd_val not in data_by_obstd:
            data_by_obstd[obstd_val] = []
        data_by_obstd[obstd_val].append((t_arr, fu_arr))

    # Graficar
    plt.figure(figsize=(9, 6))

    # Ordenar los x_o (obstD) de menor a mayor
    sorted_obstd = sorted(data_by_obstd.keys())
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(sorted_obstd)))

    for idx, obstd in enumerate(sorted_obstd):
        runs = data_by_obstd[obstd]

        # Encontrar la grilla temporal común (usando el primer array de tiempo como referencia)
        ref_time = runs[0][0]
        fu_matrix = []

        for t_arr, fu_arr in runs:
            # Interpolar en caso de que algún paso temporal difiera levemente
            fu_interp = np.interp(ref_time, t_arr, fu_arr)
            fu_matrix.append(fu_interp)

        fu_matrix = np.array(fu_matrix)

        # Promedio y Desvío Estándar a lo largo de las iteraciones
        fu_mean = np.mean(fu_matrix, axis=0)
        fu_std = np.std(fu_matrix, axis=0, ddof=1) if len(runs) > 1 else np.zeros_like(fu_mean)

        # Muestreo de puntos para no saturar el gráfico con barras de error en cada dt
        step = max(1, len(ref_time) // 20)

        plt.errorbar(
            ref_time[::step],
            fu_mean[::step],
            yerr=fu_std[::step],
            label=f"$x_o = {obstd:.3f}$ m",
            color=colors[idx],
            fmt='-o',
            capsize=3,
            markersize=4,
            linewidth=1.5,
            alpha=0.85
        )

    plt.axhline(0.9, color='red', linestyle='--', linewidth=1, label=r"$F_u = 0.9$")
    plt.xlabel(r"$t \text{ [s]}$", fontsize=12)
    plt.ylabel(r"$\langle F_u(t) \rangle \text{ (Fracción Media de Partículas Usadas)}$", fontsize=12)
    plt.grid(True, ls="--", alpha=0.6)
    plt.legend(fontsize=9, loc='lower right', bbox_to_anchor=(1.0, 0.0))
    plt.ylim(-0.02, 1.05)

    plt.tight_layout()
    output_name = f"2_2_Fu_vs_t_N{n_particles}.png"
    plt.savefig(output_name, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Gráfico guardado exitosamente como '{output_name}'.")

if __name__ == "__main__":
    # Procesar y generar gráficos para ambas configuraciones
    process_and_plot_for_N(n_particles=20)
    process_and_plot_for_N(n_particles=100)