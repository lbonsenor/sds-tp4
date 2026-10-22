import pandas as pd
import matplotlib.pyplot as plt
import os

# Set the path to the folder where your CSV files are located.
# Replace this string with your actual directory path (e.g., "C:/Users/Name/Project/outputs" or "../data")
data_dir = "../telemetry/oscillator"  # Update this path as needed

# Dictionary with labels and their respective filenames for dt = 10^-4
archivos = {
    "Analítica": "analytical_solution_dt_1.0E-4.csv",
    "Verlet Original": "verlet_original_dt_1.0E-4.csv",
    "Velocity Verlet": "velocity_verlet_dt_1.0E-4.csv",
    "Euler Predictor-Corrector": "euler_pc_dt_1.0E-4.csv",
    "Beeman": "beeman_dt_1.0E-4.csv"
}

# Dictionary to configure visual styles for each algorithm
estilos = {
    # CAMBIO: zorder bajó a 1 (se dibuja al fondo) y agregamos alpha=0.3 (semitransparente)
    "Analítica": {"color": "black", "linestyle": "-", "linewidth": 3, "zorder": 1, "alpha": 0.3},

    # CAMBIO: Las demás líneas pasan a zorder más altos para ir al frente
    "Verlet Original": {"color": "blue", "linestyle": "--", "linewidth": 1.5, "zorder": 2},
    "Velocity Verlet": {"color": "red", "linestyle": "-.", "linewidth": 1.5, "zorder": 3},
    "Euler Predictor-Corrector": {"color": "green", "linestyle": ":", "linewidth": 1.5, "zorder": 4},
    "Beeman": {"color": "orange", "linestyle": "--", "linewidth": 1.5, "zorder": 5}
}

plt.figure(figsize=(10, 6))

# Load the data and plot iteratively
for etiqueta, nombre_archivo in archivos.items():
    # Join the directory path with the filename
    ruta_completa = os.path.join(data_dir, nombre_archivo)

    if os.path.exists(ruta_completa):
        df = pd.read_csv(ruta_completa)
        # Assuming the columns are 'T' (time) and 'R' (position)
        plt.plot(df['T'], df['R'], label=etiqueta, **estilos[etiqueta])
    else:
        print(f"Warning: File not found at {ruta_completa}")

# Titles, labels, and formatting
# plt.title(r"Oscilador Amortiguado - Evolución Temporal (dt = $1.0 \times 10^{-4}$ s)", fontsize=14)
plt.xlabel("Tiempo (s)", fontsize=12)
plt.ylabel("Posición (m)", fontsize=12)

# Grid and legend
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(loc="upper right", fontsize=10)
plt.tight_layout()

# Save the high-resolution image and display
plt.savefig("evolucion_temporal_dt_1E-4.png", dpi=300)