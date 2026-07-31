"""Erzeugt og-image.jpg — das Vorschaubild fuer geteilte Links (WhatsApp, Signal, ...).

Aufruf aus dem Repo-Wurzelverzeichnis:

    python3 tools/og-image.py

Braucht Pillow, numpy und scipy. Laeuft nur lokal; das Ergebnis (og-image.jpg)
ist eingecheckt, das Skript selbst wird nie ausgeliefert.

Wenn sich die Berufsbezeichnung aendert (ab 1.10.2026 "in Fachausbildung unter
Lehrsupervision"), nur TITLE unten anpassen und neu laufen lassen. Die
Schriftgroessen passen sich selbst an die Silhouette im Foto an.
"""
import os

import numpy as np
from scipy.ndimage import gaussian_filter1d, median_filter
from PIL import Image, ImageDraw, ImageFont

# Quellfoto liegt ausserhalb des Repos im OneDrive-Ordner der Praxis
SRC = os.path.expanduser(
    '~/Library/CloudStorage/OneDrive-Personal/Docs/Psychotherapieausbildung/Praxis/'
    'Website/pictures/Fotos Conny/Chris/nachbearbeitet/Portrait_Visitenkarte2.png')
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'og-image.jpg')
W, H = 1200, 630
GB = '/System/Library/Fonts/Supplemental/Georgia Bold.ttf'
G  = '/System/Library/Fonts/Supplemental/Georgia.ttf'

# --- Portrait: Zuschnitt endet oberhalb der hellen Hintergrundkante (y~1050) ---
im = Image.open(SRC).convert('RGB')
port = im.crop((0, 100, 947, 1040)).resize((635, H), Image.LANCZOS)
pw = port.width
px = W - pw
P = np.asarray(port, dtype=np.float64)

# --- Hintergrundreferenz aus den aeussersten 30 px, robust geglaettet ---
ref = np.median(P[:, :30, :], axis=1)
ref = median_filter(ref, size=(31, 1), mode='nearest')
ref = gaussian_filter1d(ref, sigma=30, axis=0, mode='nearest')

bg = np.repeat(ref[:, None, :], px, axis=1)
bg *= np.linspace(0.955, 1.0, px)[None, :, None]
bg += np.random.default_rng(7).normal(0.0, 1.1, bg.shape)

canvas = Image.new('RGB', (W, H))
canvas.paste(Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)), (0, 0))
canvas.paste(port, (px, 0))

# --- Naht weich ueberblenden ---
B, x0 = 80, px - 40
reg  = np.asarray(canvas.crop((x0, 0, x0 + B, H)), dtype=np.float64)
lcol = np.asarray(canvas.crop((x0 - 1, 0, x0, H)), dtype=np.float64)
rcol = np.asarray(canvas.crop((x0 + B, 0, x0 + B + 1, H)), dtype=np.float64)
t = np.linspace(0, 1, B)[None, :, None]
wgt = (np.sin(np.pi * (t - 0.5)) * 0.5 + 0.5) * 0.5
canvas.paste(Image.fromarray(np.clip(
    reg * (1 - wgt) + (lcol * (1 - t) + rcol * t) * wgt, 0, 255).astype(np.uint8)), (x0, 0))

# --- Silhouette: bis wohin darf Text je Zeile laufen ---
dev = np.sqrt(((P - np.median(P[:, :30, :], axis=(0, 1))) ** 2).sum(axis=2))
sil = np.array([np.flatnonzero(dev[y] > 26)[:1].tolist() or [pw] for y in range(H)],
               dtype=float).ravel()
sil = gaussian_filter1d(sil, sigma=6, mode='nearest') + px      # Canvas-Koordinaten

# --- Lockup: Name + zweizeilige Berufsbezeichnung (Verhaeltnis 1.45 wie Visitenkarte) ---
X, GAPR = 62, 34
NAME  = 'Christian Lacina'
TITLE = ['Psychotherapeut in Ausbildung', 'unter Supervision']

size_title = 40
size_name  = round(size_title * 1.45)                            # 58
lh   = round(size_title * 1.32)
gapn = round(size_name * 0.42)
block_h = size_name + gapn + lh * len(TITLE)
y0 = (H - block_h) // 2

def budget(a, b):
    return sil[max(0, a):min(H, b)].min() - X - GAPR

# Zeilen einzeln gegen die Silhouette pruefen und noetigenfalls verkleinern
while ImageFont.truetype(GB, size_name).getlength(NAME) > budget(y0, y0 + size_name):
    size_name -= 1
ty = y0 + size_name + gapn
while any(ImageFont.truetype(G, size_title).getlength(t_) > budget(ty + i * lh, ty + (i + 1) * lh)
          for i, t_ in enumerate(TITLE)):
    size_title -= 1

d = ImageDraw.Draw(canvas)
d.text((X, y0), NAME, font=ImageFont.truetype(GB, size_name), fill=(255, 255, 255))
f_title = ImageFont.truetype(G, size_title)
for i, t_ in enumerate(TITLE):
    d.text((X, ty + i * lh), t_, font=f_title, fill=(226, 232, 224))

canvas.save(OUT, 'JPEG', quality=92, optimize=True, progressive=True, subsampling=0)
print(f'{OUT} geschrieben — Name {size_name}px, Berufsbezeichnung {size_title}px')
