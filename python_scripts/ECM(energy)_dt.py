import os
import re
import glob
import numpy as np
import matplotlib.pyplot as plt

# Constantes físicas del sistema (TP4 - Sistema 2)
R_DOMAIN = 0.51
R_PART = 0.0175
M = 0.025
K = 1e4
DIAMETER = 2 * R_PART

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Directorio donde se encuentran los outputs primarios de trayectorias (ej. carpeta 2.1.a)
DIRECTORY = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "2.1.a"))

dts = []
ecms = []

# Buscar los archivos de trayectorias generados por Java (ej. 2.1.a_dt*.txt)
search_path = os.path.join(DIRECTORY, "*_dt*.txt")
files = glob.glob(search_path)

if not files:
    print(f"No se encontraron archivos en '{search_path}'. Verificá el directorio.")
else:
    for file_path in files:
        filename = os.path.basename(file_path)

        # Extraer el valor de dt usando Expresiones Regulares del nombre del archivo de trayectorias
        match = re.search(r"dt([0-9\.eE\-]+)\.txt$", filename)
        if match:
            dt_val = float(match.group(1))
        else:
            continue

        try:
            # Leer el archivo de trayectorias estructurado por fotogramas
            with open(file_path, 'r') as f:
                lines = f.readlines()

            times = []
            e_tot_list = []
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue
                
                # Cada bloque de fotograma comienza con el tiempo t (línea individual)
                try:
                    t = float(line)
                except ValueError:
                    i += 1
                    continue
                
                i += 1
                positions = []
                velocities = []
                
                # Las líneas subsiguientes corresponden a las partículas del fotograma
                # Formato en Java: id x y vx vy color
                while i < len(lines) and len(lines[i].split()) == 6:
                    parts = lines[i].split()
                    x, y = float(parts[1]), float(parts[2])
                    vx, vy = float(parts[3]), float(parts[4])
                    positions.append([x, y])
                    velocities.append([vx, vy])
                    i += 1
                
                if not positions:
                    continue
                
                positions = np.array(positions)
                velocities = np.array(velocities)
                n = len(positions)

                # --- POSTPROCESAMIENTO DE OBSERVABLES (Energía en el fotograma) ---
                # 1. Energía Cinética
                ek = 0.5 * M * np.sum(velocities**2)
                
                # 2. Energía Potencial (Partícula - Partícula y Partícula - Pared)
                ep = 0.0
                for p_idx in range(n):
                    xi, yi = positions[p_idx]
                    
                    # Interacción con otras partículas
                    for j in range(p_idx + 1, n):
                        dx = positions[j][0] - xi
                        dy = positions[j][1] - yi
                        dist2 = dx * dx + dy * dy
                        if dist2 < DIAMETER * DIAMETER and dist2 > 0:
                            dist = np.sqrt(dist2)
                            xi_ij = DIAMETER - dist
                            if xi_ij > 0:
                                ep += 0.5 * K * (xi_ij ** 2)
                    
                    # Interacción con la pared (Partícula Imagen)
                    dist_centro2 = xi * xi + yi * yi
                    r_wall = R_DOMAIN - R_PART
                    if dist_centro2 > r_wall * r_wall:
                        dist_centro = np.sqrt(dist_centro2)
                        xi_w = dist_centro + R_PART - R_DOMAIN
                        if xi_w > 0 and dist_centro > 0:
                            ep += 0.5 * K * (xi_w ** 2)

                e_tot = ek + ep
                times.append(t)
                e_tot_list.append(e_tot)

            if e_tot_list:
                e_tot_arr = np.array(e_tot_list)
                E0 = e_tot_arr[0] # Energía total inicial de referencia
                
                # Calcular el Error Cuadrático Medio (ECM) de la energía total respecto a E0
                ecm = np.mean((e_tot_arr - E0) ** 2)

                dts.append(dt_val)
                ecms.append(ecm)
                print(f"Archivo: {filename} | dt: {dt_val} | ECM: {ecm:.6e}")

        except Exception as e:
            print(f"Error procesando {filename}: {e}")

# Ordenar por dt ascendente para graficar correctamente
if dts:
    dts, ecms = zip(*sorted(zip(dts, ecms)))

    # Graficar ECM vs dt en escala logarítmica
    plt.figure(figsize=(7, 5))
    plt.loglog(dts, ecms, 'o-', color='navy', linewidth=2, markersize=7)
    
    for dt_val, ecm_val in zip(dts, ecms):
        label = f"{dt_val:g}" if dt_val >= 1e-3 else f"{dt_val:.1e}"
        plt.annotate(
            label,
            (dt_val, ecm_val),
            textcoords="offset points",
            xytext=(0, 8),
            ha='center',
            fontsize=9,
            color='darkblue'
        )

    plt.xlabel(r"$dt \text{ (s)}$", fontsize=12)
    plt.ylabel(r"$\text{ECM de Etot (J}^2\text{)}$", fontsize=12)
    plt.grid(True, which="both", ls="--", alpha=0.6)

    plt.tight_layout()
    plt.savefig("ecm_vs_dt.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Gráfico generado con éxito: ecm_vs_dt.png")