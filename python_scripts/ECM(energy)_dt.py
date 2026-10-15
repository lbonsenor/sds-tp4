import os
import re
import glob
import numpy as np
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Subir un nivel al directorio raíz del proyecto y apuntar a '2.1.a'
DIRECTORY = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "2.1.a"))
# E0 = 3.75  # Energía inicial esperada (J)

dts = []
ecms = []

# Buscar todos los archivos de energía dentro de la carpeta
search_path = os.path.join(DIRECTORY, "*energy_dt*.txt")
files = glob.glob(search_path)

if not files:
    print(f"No se encontraron archivos en '{search_path}'. Verificá el directorio.")
else:
    for file_path in files:
        filename = os.path.basename(file_path)

        # Extraer el valor de dt usando Expresiones Regulares
        match = re.search(r"dt([0-9\.eE\-]+)\.txt$", filename)
        if match:
            dt_val = float(match.group(1))
        else:
            continue

        # Cargar los datos del archivo ignorando comentarios/encabezados si los hay
        try:
            data = np.loadtxt(file_path, delimiter=',', skiprows=1)
            # Columna 3 (índice 3): Etot (t, Ek, Ep, Etot)
            e_tot = data[:, 3]
            E0 = e_tot[0]
            # Calcular el Error Cuadrático Medio (ECM) respecto a E0
            ecm = np.mean((e_tot - E0) ** 2)

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
    # Etiquetar cada punto con su valor de dt
    for dt_val, ecm_val in zip(dts, ecms):
        # Formato flotante o notación científica según el tamaño del número
        label = f"{dt_val:g}" if dt_val >= 1e-3 else f"{dt_val:.1e}"

        plt.annotate(
            label,
            (dt_val, ecm_val),
            textcoords="offset points",
            xytext=(0, 8),       # Desplazamiento de 8 puntos hacia arriba
            ha='center',          # Alineación horizontal centrada
            fontsize=9,
            color='darkblue'
        )

    # Etiquetas de los ejes
    plt.xlabel(r"$dt \text{ (s)}$", fontsize=12)
    plt.ylabel(r"$\text{ECM de Etot (J}^2\text{)}$", fontsize=12)

    plt.grid(True, which="both", ls="--", alpha=0.6)

    # Ajustes finales sin títulos (tal como solicitaste)
    plt.tight_layout()
    plt.savefig("ecm_vs_dt.png", dpi=300, bbox_inches="tight")
    plt.close()  # Libera la memoria del gráfico