"""
TP4 - Ejercicio 2.4 a) Efecto de la densidad.

Lee los outputs de 2.1.b (sistema con obstáculos en contacto, N variable,
varias realizaciones) y calcula <t90> y <t100> en función de N.
(La densidad es rho = N / (pi R^2) con R fijo, o sea proporcional a N.)

Formato de cada archivo (frames consecutivos):
    t
    id x y vx vy estado      (N líneas; estado 0 = fresca, 1 = usada)

Ubicación esperada: <proyecto>/python_scripts/t90_t100_vs_density.py
Los datos se leen con path relativo al script (no depende del pwd).
"""
import re
import glob
import os
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter, MaxNLocator

# ==========================================
# CONSTANTES DE CONFIGURACIÓN
# ==========================================
SUBDIRECTORIO_DATOS = "../2.1.b"
OUTPUT_IMAGE_T90 = "t90_vs_N.png"
OUTPUT_IMAGE_T100 = "t100_vs_N.png"
OUTPUT_IMAGE_BOTH = "t90_t100_vs_N.png"
USE_SEM = False               # True: barras = error estándar de la media; False: desvío estándar
FONT_SIZE = 16

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, SUBDIRECTORIO_DATOS))

FRACS = {"t90": 0.9, "t100": 1.0}
FILE_RE = re.compile(r"_N_(\d+)_(\d+)\.txt$")

plt.rcParams.update({
    "font.size": FONT_SIZE, "axes.labelsize": FONT_SIZE,
    "xtick.labelsize": FONT_SIZE, "ytick.labelsize": FONT_SIZE,
    "legend.fontsize": FONT_SIZE, "figure.figsize": (9, 6.5),
})


# ----------------------------------------------------------------- lectura
def fu_curve(path, n):
    """Devuelve (t[k], Fu[k]) de un archivo de output primario."""
    with open(path) as f:
        lines = f.read().splitlines()
    block = n + 1
    n_frames = len(lines) // block
    t = np.empty(n_frames)
    used = np.empty(n_frames)
    for k in range(n_frames):
        base = k * block
        t[k] = float(lines[base])
        used[k] = sum(1 for ln in lines[base + 1: base + 1 + n]
                      if ln.split()[-1] == "1")
    return t, used / n


def first_time(t, fu, frac):
    """Primer instante en que Fu >= frac (NaN si nunca ocurre)."""
    idx = np.flatnonzero(fu >= frac - 1e-12)
    return t[idx[0]] if idx.size else np.nan


# ----------------------------------------------------------------- formato
class SciFormatter(Formatter):
    """Ticks en notación científica (m x 10^e) solo cuando es necesario.
    Para números ordinarios (ej: 24) usa notación decimal estándar."""

    def format_ticks(self, values):
        locs = np.asarray(values, dtype=float)
        dec = 0
        for d in range(0, 6):
            labels = {self._fmt(x, d) for x in locs}
            dec = d
            if len(labels) == len(locs):
                break
        return [self._fmt(x, dec) for x in locs]

    @staticmethod
    def _fmt(x, d):
        if x == 0:
            return "$0$"
        e = int(np.floor(np.log10(abs(x))))
        
        # Para números entre 0.1 y 999 se muestra formato decimal normal (ej: 24 o 24.4)
        if -1 <= e <= 2:
            val = round(x, d)
            if d == 0:
                return rf"${int(val)}$"
            return rf"${val:.{d}f}$"

        # Notación científica para el resto (m x 10^e)
        m = x / 10 ** e
        if round(m, d) >= 10:      # 9.99 -> 10.0
            m, e = m / 10, e + 1
        return rf"${m:.{d}f}\times10^{{{e}}}$"

    def __call__(self, x, pos=None):
        return self._fmt(x, 1)

def round_to_error(mean, err):
    """Redondea mean y err según la primera cifra significativa del error."""
    if not np.isfinite(err) or err <= 0:
        return f"{mean:.3g}", "-"
    e = int(np.floor(np.log10(err)))
    dec = max(0, -e)
    return f"{mean:.{dec}f}", f"{err:.{dec}f}"


def format_axes(ax, Ns, t_max, has_data):
    """Eje x: N (enteros, un tick por N simulado). Eje y: de 0 a 30."""
    ax.set_xlabel("Número de partículas")
    ax.set_xticks(Ns)
    ax.set_xticklabels([str(n) for n in Ns])
    pad = 0.5 * (Ns.max() - Ns.min()) / max(len(Ns) - 1, 1) if len(Ns) > 1 else 0.5 * Ns[0]
    ax.set_xlim(Ns.min() - pad, Ns.max() + pad)
    
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
    ax.yaxis.set_major_formatter(SciFormatter())
    
    # Fijamos el eje y de 0 a 30 (podes cambiar 30 por t_max si preferís que sea dinámico)
    ax.set_ylim(0, 150)
    
    ax.grid(alpha=0.3)


# ----------------------------------------------------------------- main
def main():
    files = [p for p in glob.glob(os.path.join(DATA_DIR, "*.txt"))
             if FILE_RE.search(p)]
    if not files:
        print(f"No se encontraron archivos *_N_<N>_<iter>.txt en '{DATA_DIR}'")
        return

    times = {k: defaultdict(list) for k in FRACS}   # times[obs][N] -> [t por corrida]
    fu_final = defaultdict(list)
    t_max = 0.0
    for p in sorted(files):
        n = int(FILE_RE.search(p).group(1))
        t, fu = fu_curve(p, n)
        for obs, frac in FRACS.items():
            times[obs][n].append(first_time(t, fu, frac))
        fu_final[n].append(fu[-1])
        t_max = max(t_max, t[-1])
        print(f"  leído {os.path.basename(p)}  (t_max={t[-1]:.1f} s, Fu_final={fu[-1]:.2f})")

    Ns = np.array(sorted(times["t90"]))

    # ---- estadística
    stats = {}
    print("\n  N    obs    <t> (s)  err (s)  alcanzaron/total")
    for obs in FRACS:
        mean, err = [], []
        for n in Ns:
            v = np.array(times[obs][n])
            ok = v[np.isfinite(v)]
            m = ok.mean() if ok.size else np.nan
            s = ok.std(ddof=1) if ok.size > 1 else np.nan
            if USE_SEM and ok.size > 1:
                s /= np.sqrt(ok.size)
            mean.append(m); err.append(s)
            ms, es = round_to_error(m, s) if np.isfinite(m) else ("nan", "-")
            flag = "" if ok.size == v.size else \
                f"   <-- {v.size - ok.size} corrida(s) no llegan a Fu={FRACS[obs]} " \
                f"(Fu(t_f) medio = {np.mean(fu_final[n]):.2f})"
            print(f"{n:4d}   {obs:5s} {ms:>8s} {es:>8s}   {ok.size}/{v.size}{flag}")
        stats[obs] = (np.array(mean), np.array(err))

    # ---- mínimos
    for obs in FRACS:
        m = stats[obs][0]
        if np.any(np.isfinite(m)):
            i = np.nanargmin(m)
            print(f"\nMínimo de <{obs}>: N={Ns[i]} -> {m[i]:.2f} s")
        else:
            print(f"\n<{obs}>: ninguna corrida alcanzó Fu={FRACS[obs]} antes de t_f={t_max:.0f} s")

    # ---- figuras (sin título, ejes en palabras con unidades)
    style = {"t90": ("o", "#1f77b4"), "t100": ("s", "#d62728")}
    label = {"t90": r"$\langle t_{90}\rangle$", "t100": r"$\langle t_{100}\rangle$"}
    ylab = {"t90": "Tiempo medio al 90 % (s)", "t100": "Tiempo medio al 100 % (s)"}
    out = {"t90": OUTPUT_IMAGE_T90, "t100": OUTPUT_IMAGE_T100}

    for obs in FRACS:
        m, s = stats[obs]
        has = bool(np.any(np.isfinite(m)))
        fig, ax = plt.subplots()
        mk, col = style[obs]
        if has:
            ax.errorbar(Ns, m, yerr=s, fmt=mk, color=col, capsize=5, ms=9, lw=1.5)
            ax.plot(Ns, m, "-", color=col, alpha=0.35, lw=1)      # guía para el ojo
        ax.set_ylabel(ylab[obs])
        format_axes(ax, Ns, t_max, has)
        fig.tight_layout()
        fig.savefig(os.path.join(SCRIPT_DIR, out[obs]), dpi=200)

    # ---- figura conjunta t90 y t100
    fig, ax = plt.subplots()
    has_any = False
    for obs in FRACS:
        m, s = stats[obs]
        if not np.any(np.isfinite(m)):
            continue
        has_any = True
        mk, col = style[obs]
        ax.errorbar(Ns, m, yerr=s, fmt=mk, color=col, capsize=5, ms=9,
                    lw=1.5, label=label[obs])
        ax.plot(Ns, m, "-", color=col, alpha=0.35, lw=1)
    ax.set_ylabel("Tiempo medio (s)")
    format_axes(ax, Ns, t_max, has_any)
    if has_any:
        ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(SCRIPT_DIR, OUTPUT_IMAGE_BOTH), dpi=200)
    print(f"\nGráficos guardados en '{SCRIPT_DIR}'")


if __name__ == "__main__":
    main()