"""
TP4 - Ejercicio 2.1 a) Paso temporal y conservación de la energía.

Sistema sin obstáculos, N = 300. Para cada dt (un archivo de output por dt):
  - Energía total E(t) = sum 1/2 m v^2 + sum 1/2 k xi^2 (partículas + pared)
  - Observable escalar: desvío relativo máximo de la energía
        delta_E(dt) = max_t |E(t) - E(0)| / E(0)
Se grafica E(t) para cada dt y delta_E en función de dt (ejes logarítmicos),
y se informa el dt más grande que cumple delta_E < TOL_ENERGIA.

Formato de cada archivo (frames consecutivos):
    t
    id x y vx vy estado      (N líneas)
El dt se lee del nombre del archivo:  ..._dt<valor>.txt  (ej: 2.1.a_dt5.0E-4.txt)

Ubicación esperada: <proyecto>/python_scripts/energia_vs_dt.py
Los datos se leen con path relativo al script (no depende del pwd).
"""
import os
import re
import glob

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter, MaxNLocator

# ==========================================
# CONSTANTES DE CONFIGURACIÓN
# ==========================================
SUBDIRECTORIO_DATOS = "../2.1.a"
OUTPUT_IMAGE_ENERGIA = "energia_vs_tiempo.png"
OUTPUT_IMAGE_DESVIO = "desvio_energia_vs_dt.png"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, SUBDIRECTORIO_DATOS))

FILE_RE = re.compile(r"_dt(.+)\.txt$")
FONT_SIZE = 16
TOL_ENERGIA = 1e-2            # criterio: desvío relativo máximo admitido
OBSTACULOS_XO = None          # None = sin obstáculos (2.1.a); o xo en m para incluirlos

# Parámetros físicos (enunciado)
R_DOMAIN = 0.51               # m
R_PART = 0.0175               # m
M = 0.025                     # kg
K = 1e4                       # N/m

plt.rcParams.update({
    "font.size": FONT_SIZE, "axes.labelsize": FONT_SIZE,
    "xtick.labelsize": FONT_SIZE, "ytick.labelsize": FONT_SIZE,
    "legend.fontsize": FONT_SIZE - 2, "figure.figsize": (9, 6.5),
})


# ----------------------------------------------------------------- lectura
def load_frames(path):
    """Devuelve (t[F], datos[F, N, 6]) con columnas id x y vx vy estado.
    N se infiere del archivo (las líneas de tiempo no tienen espacios)."""
    with open(path) as f:
        lines = [ln.strip().replace(",", ".") for ln in f if ln.strip()]
    is_time = [(" " not in ln) for ln in lines]
    times = np.array([float(ln) for ln, tm in zip(lines, is_time) if tm])
    rows = [ln.split() for ln, tm in zip(lines, is_time) if not tm]
    data = np.array(rows, dtype=float).reshape(len(times), -1, 6)
    return times, data


# ----------------------------------------------------------------- energía
def potential_energy(x, y, iu):
    """Energía potencial elástica de contactos: partículas, pared (y obstáculos)."""
    dx = x[iu[0]] - x[iu[1]]
    dy = y[iu[0]] - y[iu[1]]
    xi = np.clip(2 * R_PART - np.hypot(dx, dy), 0.0, None)
    pe = 0.5 * K * np.sum(xi ** 2)
    xi_w = np.clip(np.hypot(x, y) + R_PART - R_DOMAIN, 0.0, None)
    pe += 0.5 * K * np.sum(xi_w ** 2)
    if OBSTACULOS_XO is not None:
        for ox in (-OBSTACULOS_XO, OBSTACULOS_XO):
            xi_o = np.clip(2 * R_PART - np.hypot(x - ox, y), 0.0, None)
            pe += 0.5 * K * np.sum(xi_o ** 2)
    return pe


def total_energy(data):
    """E(t) para cada frame."""
    n = data.shape[1]
    iu = np.triu_indices(n, 1)
    ke = 0.5 * M * np.sum(data[:, :, 3] ** 2 + data[:, :, 4] ** 2, axis=1)
    pe = np.array([potential_energy(fr[:, 1], fr[:, 2], iu) for fr in data])
    return ke + pe


# ----------------------------------------------------------------- formato
class SciFormatter(Formatter):
    """Ticks en notación científica (m x 10^e) con los decimales mínimos
    necesarios para que no haya ticks repetidos."""

    def set_locs(self, locs):
        locs = np.asarray(locs, dtype=float)
        self._dec = 5
        for d in range(0, 6):
            if len({self._fmt(x, d) for x in locs}) == len(locs):
                self._dec = d
                break

    @staticmethod
    def _fmt(x, d):
        if x == 0:
            return "$0$"
        e = int(np.floor(np.log10(abs(x))))
        m = x / 10 ** e
        if round(m, d) >= 10:
            m, e = m / 10, e + 1
        return rf"${m:.{d}f}\times10^{{{e}}}$"

    def __call__(self, x, pos=None):
        return self._fmt(x, getattr(self, "_dec", 1))


def sci_text(x):
    """Texto en notación científica para leyendas: 5 x 10^-4."""
    e = int(np.floor(np.log10(abs(x))))
    m = x / 10 ** e
    return rf"{m:g}\times10^{{{e}}}"


# ----------------------------------------------------------------- main
def main():
    files = [p for p in glob.glob(os.path.join(DATA_DIR, "*.txt")) if FILE_RE.search(p)]
    if not files:
        print(f"No se encontraron archivos *_dt<valor>.txt en '{DATA_DIR}'")
        return

    runs = {}   # dt -> (t, E)
    for p in files:
        dt = float(FILE_RE.search(p).group(1))
        t, data = load_frames(p)
        runs[dt] = (t, total_energy(data))
        print(f"  leído {os.path.basename(p)}: dt={dt:g} s, N={data.shape[1]}, "
              f"{len(t)} frames, t=[{t[0]:.2f}, {t[-1]:.2f}] s")

    dts = np.array(sorted(runs))

    # ---- observable: desvío relativo máximo y final
    dev_max, dev_fin = [], []
    print(f"\n  dt (s)      E0 (J)    max|dE|/E0   dE(t_f)/E0")
    for dt in dts:
        t, e = runs[dt]
        rel = (e - e[0]) / e[0]
        finite = np.all(np.isfinite(rel))
        dm = np.max(np.abs(rel)) if finite else np.inf
        dev_max.append(dm); dev_fin.append(rel[-1])
        print(f"  {dt:<9g} {e[0]:9.4f}   {dm:10.3e}   {rel[-1]:+10.3e}"
              f"{'' if finite else '   (valores no finitos: simulación inestable)'}")
    dev_max = np.array(dev_max)

    ok = dts[dev_max < TOL_ENERGIA]
    if ok.size:
        print(f"\ndt más grande con max|dE|/E0 < {TOL_ENERGIA:g}: {ok.max():g} s")
    else:
        print(f"\nNingún dt cumple max|dE|/E0 < {TOL_ENERGIA:g}")

    # ---- figura 1: E(t) para cada dt
    fig, ax = plt.subplots()
    cmap = plt.get_cmap("viridis")
    e0 = np.mean([runs[dt][1][0] for dt in dts])
    for i, dt in enumerate(dts[::-1]):                 # de mayor a menor dt
        t, e = runs[dt]
        col = cmap(i / max(len(dts) - 1, 1) * 0.9)
        ax.plot(t, e, color=col, lw=1.6, label=rf"$dt = {sci_text(dt)}$ s")
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Energía total (J)")
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
    ax.yaxis.set_major_formatter(SciFormatter())
    # Límites y: se ignoran los puntos de simulaciones explotadas (fuera de [0.3, 3] E0)
    vals = np.concatenate([e[np.isfinite(e) & (e > 0.3 * e0) & (e < 3 * e0)] for _, e in runs.values()])
    pad = 0.05 * (vals.max() - vals.min() + 1e-12)
    ax.set_ylim(vals.min() - pad, vals.max() + pad)
    ax.grid(alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(os.path.join(SCRIPT_DIR, OUTPUT_IMAGE_ENERGIA), dpi=200)

    # ---- figura 2: observable vs dt (log-log)
    fig, ax = plt.subplots()
    fin = np.isfinite(dev_max) & (dev_max > 0)
    ax.plot(dts[fin], dev_max[fin], "o-", color="#1f77b4", ms=9, lw=1.2, alpha=0.9)
    ax.axhline(TOL_ENERGIA, color="#d62728", ls="--", lw=1.5,
               label=rf"Tolerancia ${sci_text(TOL_ENERGIA)}$")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Paso temporal (s)")
    ax.set_ylabel("Desvío relativo máximo de la energía")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(os.path.join(SCRIPT_DIR, OUTPUT_IMAGE_DESVIO), dpi=200)

    print(f"\nGráficos guardados en '{SCRIPT_DIR}'")


if __name__ == "__main__":
    main()