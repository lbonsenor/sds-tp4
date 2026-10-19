import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

m = 0.025
v0 = 1.0
E_cin_inicial = 0.5 * m * (v0 ** 2)

script_dir = os.path.dirname(os.path.abspath(__file__))
DIRECTORY = os.path.abspath(os.path.join(script_dir, "..", "2.3"))
file_pattern = os.path.join(DIRECTORY, "2.3_dt5.0E-4_iter_*.txt")

def maxwell_boltzmann_2d(v, kbT):
    return (m * v / kbT) * np.exp(-m * (v**2) / (2.0 * kbT))

def leer_archivo_simulacion(filepath):
    datos_por_tiempo = {}
    with open(filepath, 'r') as f:
        lines = f.readlines()

    idx = 0
    num_lines = len(lines)

    while idx < num_lines:
        linea = lines[idx].strip()
        if not linea:
            idx += 1
            continue

        t = float(linea)
        idx += 1

        velocidades_t = []
        for _ in range(100):
            if idx >= num_lines:
                break
            part_line = lines[idx].strip().split()
            if len(part_line) >= 6:
                vx = float(part_line[3])
                vy = float(part_line[4])
                v = np.sqrt(vx**2 + vy**2)
                velocidades_t.append(v)
            idx += 1

        if len(velocidades_t) == 100:
            if t not in datos_por_tiempo:
                datos_por_tiempo[t] = []
            datos_por_tiempo[t].extend(velocidades_t)

    return datos_por_tiempo

archivos = glob.glob(file_pattern)

if not archivos:
    print(f"Error: No se encontraron archivos con el patrón '{file_pattern}'.")
    exit()

todas_las_corridas = {}

for file in archivos:
    datos_file = leer_archivo_simulacion(file)
    for t, v_list in datos_file.items():
        if t not in todas_las_corridas:
            todas_las_corridas[t] = []
        todas_las_corridas[t].extend(v_list)

tiempos_disponibles = sorted(todas_las_corridas.keys())
v_max = 3.0
num_bins = 30
bins = np.linspace(0, v_max, num_bins + 1)
bin_centers = 0.5 * (bins[:-1] + bins[1:])
bin_width = bins[1] - bins[0]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
tiempos_objetivo = [0.0, 0.05, 0.15, 0.30,0.50, 1.0, 5.0]

def buscar_tiempo_cercano(t_deseado, lista_tiempos):
    return min(lista_tiempos, key=lambda t: abs(t - t_deseado))

tiempos_a_mostrar = [buscar_tiempo_cercano(t, tiempos_disponibles) for t in tiempos_objetivo]

for t in tiempos_a_mostrar:
    vels = todas_las_corridas[t]
    hist, _ = np.histogram(vels, bins=bins, density=True)
    ax1.plot(bin_centers, hist, label=f"$t = {t:.2f}$ s", linewidth=1.8)

ax1.set_xlabel("$v$ (m/s)", fontsize=11)
ax1.set_ylabel("$f(v)$", fontsize=11)
# ax1.set_title("Evolución temporal de $f(v)$", fontsize=12, fontweight='bold')
ax1.grid(True, linestyle="--", alpha=0.6)
ax1.legend()

t_corte_estacionario = tiempos_disponibles[-1] / 2.0
vels_estacionario = []

for t in tiempos_disponibles:
    if t >= t_corte_estacionario:
        vels_estacionario.extend(todas_las_corridas[t])

f_estacionario, _ = np.histogram(vels_estacionario, bins=bins, density=True)

popt, pcov = curve_fit(maxwell_boltzmann_2d, bin_centers, f_estacionario, p0=[E_cin_inicial])
kbT_ajustado = popt[0]

v_smooth = np.linspace(0, v_max, 200)

ax2.bar(bin_centers, f_estacionario, width=bin_width, alpha=0.5, color='gray',
        edgecolor='black', label="Simulación (Estacionario)")
ax2.plot(v_smooth, maxwell_boltzmann_2d(v_smooth, kbT_ajustado), 'r-', linewidth=2.5,
         label=f"Ajuste M-B 2D\n($k_B T = {kbT_ajustado:.5f}$ J)")

ax2.set_xlabel("$v$ (m/s)", fontsize=11)
ax2.set_ylabel("$f(v)$", fontsize=11)
# ax2.set_title("Ajuste de Maxwell-Boltzmann (Estado Estacionario)", fontsize=12, fontweight='bold')
ax2.grid(True, linestyle="--", alpha=0.6)
ax2.legend()

plt.tight_layout()
salida = os.path.join(script_dir, "resultado_2.3_velocidades.png")
plt.savefig(salida, dpi=300)
print(f"Gráfico guardado exitosamente en: {salida}")