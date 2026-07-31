"""Erzeugt favicon.svg, favicon.ico und apple-touch-icon.png.

Aufruf aus dem Repo-Wurzelverzeichnis:

    python3 tools/favicon.py

Motiv ist die Klammer aus logo-header.svg, hell auf Salbeigruen. Bewusst nur
die einfache Klammer mit kraeftigerem Strich: die Doppelklammer des Logos
verschmiert bei 16 px zu einem Fleck, der Schriftzug ist dort ohnehin
unlesbar. Alle drei Dateien zeigen dasselbe Motiv.
"""
import os

from PIL import Image, ImageDraw

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAGE  = (127, 146, 122)          # --accent-dark #7f927a
LIGHT = (246, 243, 237)          # --bg #f6f3ed
S     = 8                        # Supersampling fuer die Rasterdateien

# Klammer wie in logo-header.svg (viewBox 600x150), ohne die zweite, versetzte Linie
PATH   = [(140, 20), (48, 20), (48, 115), (140, 115)]
STROKE = 9                       # statt 6 im Logo — haelt bei 16 px durch
PAD    = 0.16                    # Rand ringsum, Anteil der Kantenlaenge


def _fit(box):
    """Rechnet die Logo-Koordinaten in ein quadratisches Feld der Kantenlaenge box."""
    xs, ys = [p[0] for p in PATH], [p[1] for p in PATH]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w, h = x1 - x0, y1 - y0
    k = box * (1 - 2 * PAD) / max(w, h)
    ox = (box - w * k) / 2 - x0 * k
    oy = (box - h * k) / 2 - y0 * k
    return [(x * k + ox, y * k + oy) for x, y in PATH], STROKE * k


def raster(size):
    n = size * S
    im = Image.new('RGB', (n, n), SAGE)
    pts, sw = _fit(n)
    ImageDraw.Draw(im).line(pts, fill=LIGHT, width=max(1, round(sw)))
    return im.resize((size, size), Image.LANCZOS)


def svg():
    pts, sw = _fit(100)
    d = 'M ' + ' L '.join(f'{x:.2f} {y:.2f}' for x, y in pts)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" '
        'role="img" aria-label="Christian Lacina">\n'
        f'  <rect width="100" height="100" fill="#7f927a"/>\n'
        f'  <path d="{d}" fill="none" stroke="#f6f3ed" stroke-width="{sw:.2f}"/>\n'
        '</svg>\n')


if __name__ == '__main__':
    open(os.path.join(ROOT, 'favicon.svg'), 'w').write(svg())
    # .ico traegt mehrere Aufloesungen; Browser nehmen die passende
    raster(48).save(os.path.join(ROOT, 'favicon.ico'),
                    sizes=[(16, 16), (32, 32), (48, 48)])
    raster(180).save(os.path.join(ROOT, 'apple-touch-icon.png'), optimize=True)
    print('favicon.svg, favicon.ico, apple-touch-icon.png geschrieben')
