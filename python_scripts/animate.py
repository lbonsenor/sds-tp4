"""
TP4 - Animación del billar circular (sistema 2) a partir del output primario.

Lee un archivo de output con frames consecutivos:
    t
    id x y vx vy estado      (N líneas; estado 0 = fresca (azul), 1 = usada (roja))
y genera un .mp4 con el dominio, los obstáculos, las partículas y su velocidad.

Uso (desde cualquier directorio):
    python animar_billar.py                               # usa ARCHIVO_INPUT por defecto
    python animar_billar.py 2.1.b_dt5.0E-4_N_100_0.txt    # nombre dentro de SUBDIRECTORIO_DATOS
    python animar_billar.py ruta/al/archivo.txt --xo 0.2 --fps 30 --step 2

Requiere ffmpeg: si no está instalado en el sistema, `pip install imageio-ffmpeg`
(el script lo detecta solo).
"""
import os
import argparse

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.collections import EllipseCollection
from matplotlib.patches import Circle

# ==========================================
# CONSTANTES DE CONFIGURACIÓN
# ==========================================
SUBDIRECTORIO_DATOS = "../2.1.b"
ARCHIVO_INPUT = "2.1.b_dt5.0E-4_N_100_0.txt"
SUBDIRECTORIO_SALIDA = "."

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, SUBDIRECTORIO_DATOS))
OUTPUT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, SUBDIRECTORIO_SALIDA))

R_DOMAIN = 0.51        # m, radio del dominio
R_PART = 0.0175        # m, radio de partículas y obstáculos
XO_DEFAULT = 0.0175    # m, obstáculos en (-xo, 0) y (+xo, 0); 2.1.b usa xo = r
FPS_DEFAULT = 20       # dt_out = 0.05 s  ->  20 fps = tiempo real
STEP_DEFAULT = 1       # usar 1 de cada STEP frames guardados
ARROW_LEN = 0.04       # m de largo de flecha por cada 1 m/s de velocidad
DPI = 100

COLOR_FRESH = "#3b87c0"
COLOR_USED = "#d9373b"


# ----------------------------------------------------------------- lectura
def load_frames(path):
    """Devuelve (t[F], datos[F, N, 6]) con columnas id x y vx vy estado.
    N se infiere del archivo. No se usa la columna id (se asume orden fijo)."""
    with open(path) as f:
        lines = [ln.strip().replace(",", ".") for ln in f if ln.strip()]
    is_time = [(" " not in ln) for ln in lines]
    times = np.array([float(ln) for ln, tm in zip(lines, is_time) if tm])
    rows = [ln.split() for ln, tm in zip(lines, is_time) if not tm]
    n_frames = len(times)
    data = np.array(rows, dtype=float).reshape(n_frames, -1, 6)
    return times, data


def resolve_input(arg):
    if arg is None:
        return os.path.join(DATA_DIR, ARCHIVO_INPUT)
    if os.path.isfile(arg):
        return os.path.abspath(arg)
    return os.path.join(DATA_DIR, arg)


def setup_ffmpeg():
    """Usa el ffmpeg del sistema si existe; si no, el de imageio-ffmpeg."""
    import shutil
    if shutil.which("ffmpeg"):
        return
    try:
        import imageio_ffmpeg
        matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise SystemExit("No se encontró ffmpeg. Instalalo o ejecutá: pip install imageio-ffmpeg")


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Animación del billar circular (TP4)")
    ap.add_argument("archivo", nargs="?", default=None, help="output .txt (default: ARCHIVO_INPUT)")
    ap.add_argument("--xo", type=float, default=XO_DEFAULT, help="posición x de los obstáculos (m)")
    ap.add_argument("--fps", type=int, default=FPS_DEFAULT)
    ap.add_argument("--step", type=int, default=STEP_DEFAULT, help="usar 1 de cada STEP frames")
    ap.add_argument("--sin-obstaculos", action="store_true", help="no dibujar obstáculos (2.1.a, 2.3)")
    args = ap.parse_args()

    path = resolve_input(args.archivo)
    if not os.path.isfile(path):
        raise SystemExit(f"No existe el archivo '{path}'")
    setup_ffmpeg()

    times, data = load_frames(path)
    times, data = times[::args.step], data[::args.step]
    n_frames, n, _ = data.shape
    print(f"{os.path.basename(path)}: {n_frames} frames, N={n}, t=[{times[0]:.2f}, {times[-1]:.2f}] s")

    # ---- figura
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_aspect("equal")
    lim = R_DOMAIN * 1.03
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    ax.axis("off")
    ax.add_patch(Circle((0, 0), R_DOMAIN, fill=False, ec="black", lw=2))
    if not args.sin_obstaculos:
        for sx in (-1, 1):
            ax.add_patch(Circle((sx * args.xo, 0), R_PART, fc="black", ec="black", zorder=3))

    def colors(state):
        return np.where(state[:, None] > 0.5,
                        np.array(matplotlib.colors.to_rgba(COLOR_USED)),
                        np.array(matplotlib.colors.to_rgba(COLOR_FRESH)))

    f0 = data[0]
    parts = EllipseCollection(widths=2 * R_PART, heights=2 * R_PART, angles=0, units="xy",
                              offsets=f0[:, 1:3], offset_transform=ax.transData,
                              facecolors=colors(f0[:, 5]), edgecolors="none", zorder=4)
    ax.add_collection(parts)
    arrows = ax.quiver(f0[:, 1], f0[:, 2], f0[:, 3], f0[:, 4], angles="xy",
                       scale_units="xy", scale=1.0 / ARROW_LEN, width=0.004,
                       headwidth=4, headlength=4, headaxislength=3.5,
                       color=colors(f0[:, 5]), zorder=5)
    label = ax.text(-lim, lim, "", fontsize=16, va="top", ha="left")
    fig.tight_layout(pad=0.2)

    def update(k):
        fr = data[k]
        c = colors(fr[:, 5])
        parts.set_offsets(fr[:, 1:3])
        parts.set_facecolor(c)
        arrows.set_offsets(fr[:, 1:3])
        arrows.set_UVC(fr[:, 3], fr[:, 4])
        arrows.set_facecolor(c)
        label.set_text(f"t = {times[k]:.2f} s    Fu = {fr[:, 5].mean():.2f}")
        return parts, arrows, label

    anim = FuncAnimation(fig, update, frames=n_frames, blit=False)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(path))[0] + ".mp4")
    writer = FFMpegWriter(fps=args.fps, codec="libx264", extra_args=["-pix_fmt", "yuv420p"])
    anim.save(out, writer=writer, dpi=DPI,
              progress_callback=lambda i, total: print(f"\r  frame {i + 1}/{total}", end="") if i % 25 == 0 else None)
    print(f"\nVideo guardado en '{out}'  ({n_frames / args.fps:.1f} s de duración)")


if __name__ == "__main__":
    main()