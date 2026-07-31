"""Erzeugt die Vorschaubilder fuer geteilte Links und Suchmaschinen.

    og-image.jpg         1200x630, Nachbau der Hero-Section: Hero-Foto links,
                         Verlauf in den Hero-Ton, Logo rechts — schema.org, Google
    og-image-square.jpg  400x400, nur Portrait — og:image fuer WhatsApp & Co.,
                         klein und quadratisch, damit die Vorschau als schmale
                         Miniatur statt als bildschirmfuellende Karte erscheint

Aufruf aus dem Repo-Wurzelverzeichnis:

    python3 tools/og-image.py

Braucht Pillow. Laeuft nur lokal; die Ergebnisse sind eingecheckt, das Skript
selbst wird nie ausgeliefert.

Wenn sich die Berufsbezeichnung aendert (ab 1.10.2026 "in Fachausbildung unter
Lehrsupervision"), TITLE unten anpassen — und dieselbe Zeile im heroLogo-SVG in
index.html, damit Seite und Vorschaubild zusammenpassen.
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Hero-Motiv in voller Aufloesung. Das ausgelieferte new5-hero-superwide-improved.jpg
# ist nur 2032x528 gross und muesste fuer 1200x630 hochskaliert werden — das Ergebnis
# war sichtbar matschig. Diese Vorlage zeigt dasselbe Motiv mit 1672x941.
HERO = os.path.expanduser(
    '~/Library/CloudStorage/OneDrive-Personal/Docs/Psychotherapieausbildung/Praxis/'
    'Website/pictures/new-hero-picture-improved.png')
# Quellfoto fuer die quadratische Variante liegt ausserhalb des Repos im OneDrive
SRC = os.path.expanduser(
    '~/Library/CloudStorage/OneDrive-Personal/Docs/Psychotherapieausbildung/Praxis/'
    'Website/pictures/Fotos Conny/Chris/nachbearbeitet/Portrait_Visitenkarte2.png')
OUT = os.path.join(ROOT, 'og-image.jpg')
OUT_SQ = os.path.join(ROOT, 'og-image-square.jpg')

W, H = 1200, 630
TINT = (235, 237, 227)          # --hero-tint
INK = (47, 44, 40)              # Schriftfarbe des Logos
MARK = (127, 146, 122)          # Klammer-Signet
GB = '/System/Library/Fonts/Supplemental/Georgia Bold.ttf'
G  = '/System/Library/Fonts/Supplemental/Georgia.ttf'
NAME = 'Christian Lacina'
TITLE = 'Psychotherapeut in Ausbildung unter Supervision'

# --- Foto auf Bildhoehe bringen und links anschlagen, Rest ist Hero-Ton. Das Motiv
#     ist schmaler als 1200px; ab 90% Breite deckt der Verlauf ohnehin alles ab. ---
hero = Image.open(HERO).convert('RGB')
hero = hero.resize((round(hero.width * H / hero.height), H), Image.LANCZOS)
canvas = Image.new('RGB', (W, H), TINT)
canvas.paste(hero, (0, 0))

# --- Verlauf nach rechts in den Hero-Ton, gleiche Stuetzstellen wie im CSS ---
STOPS = [(0.00, 0.0), (0.25, 0.0), (0.30, 0.017), (0.35, 0.064), (0.40, 0.135),
         (0.45, 0.226), (0.50, 0.330), (0.55, 0.442), (0.60, 0.558), (0.65, 0.670),
         (0.70, 0.775), (0.75, 0.865), (0.80, 0.936), (0.85, 0.983), (0.90, 1.0),
         (1.00, 1.0)]
veil = Image.new('RGB', (W, H), TINT)
mask = Image.new('L', (W, 1))
for x in range(W):
    f = x / (W - 1)
    for (fa, aa), (fb, ab) in zip(STOPS, STOPS[1:]):
        if fa <= f <= fb:
            t = 0 if fb == fa else (f - fa) / (fb - fa)
            mask.putpixel((x, 0), round(255 * (aa + (ab - aa) * t)))
            break
canvas = Image.composite(veil, canvas, mask.resize((W, H)))

# --- Logo rechts, Geometrie 1:1 aus dem heroLogo-SVG (viewBox 45 0 680 185) ---
k = 520 / 680                                   # auf der Seite 560px breit, hier etwas kleiner
X0, Y0 = 665, round((H - 185 * k) / 2)          # rechte Spalte, vertikal zentriert


SS = 3                                          # dreifach zeichnen und verkleinern


def p(x, y):
    """SVG-Koordinate in Bildkoordinate (viewBox beginnt bei x=45), SS-fach."""
    return ((X0 + (x - 45) * k) * SS, (Y0 + y * k) * SS)


layer = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
d = ImageDraw.Draw(layer)
hw = 6 * k * SS / 2                             # halbe Strichstaerke

# Striche als Rechtecke. Am Knick wird bis in die Ecke hinein verlaengert, damit
# der Stoss spitz zulaeuft wie im SVG (stroke-linejoin: miter); freie Enden
# bleiben buendig (stroke-linecap: butt).
def stroke(x1, y1, x2, y2, ext1=False, ext2=False):
    ax, ay = p(x1, y1)
    bx, by = p(x2, y2)
    if ax == bx:                                # senkrecht
        lo = min(ay, by) - (hw if (ext1 if ay < by else ext2) else 0)
        hi = max(ay, by) + (hw if (ext2 if ay < by else ext1) else 0)
        d.rectangle([ax - hw, lo, ax + hw, hi], fill=MARK)
    else:                                       # waagrecht
        lo = min(ax, bx) - (hw if (ext1 if ax < bx else ext2) else 0)
        hi = max(ax, bx) + (hw if (ext2 if ax < bx else ext1) else 0)
        d.rectangle([lo, ay - hw, hi, ay + hw], fill=MARK)


# aeussere Klammer: oben, links, unten — an den beiden Ecken verlaengert
stroke(48, 20, 179, 20, ext1=True)
stroke(48, 20, 48, 150, ext1=True, ext2=True)
stroke(48, 150, 179, 150, ext1=True)
# innere Klammer: links, unten
stroke(72, 40, 72, 170, ext2=True)
stroke(72, 170, 158, 170, ext1=True)

d.text(p(96, 89.5), NAME, font=ImageFont.truetype(GB, round(50 * k * SS)),
       fill=INK, anchor='ls')
d.text(p(96, 120.5), TITLE, font=ImageFont.truetype(G, round(18 * k * SS)),
       fill=INK, anchor='ls')

# Vor dem Verkleinern mit Alpha multiplizieren ('RGBa'), sonst mischt sich das
# Schwarz der durchsichtigen Flaechen in die Kanten und alles wirkt schmutzig
logo = layer.convert('RGBa').resize((W, H), Image.LANCZOS).convert('RGBA')
canvas.paste(logo, (0, 0), logo)

canvas.save(OUT, 'JPEG', quality=92, optimize=True, progressive=True, subsampling=0)
print(f'{OUT} geschrieben — {W}x{H}')

# --- Quadratischer Ausschnitt direkt aus dem Portraitfoto (ohne Schriftzug),
#     Kopf und Schultern mit Luft nach unten, damit das Kinn nicht anschneidet ---
Image.open(SRC).convert('RGB').crop((20, 150, 900, 1030)).resize(
    (400, 400), Image.LANCZOS).save(
    OUT_SQ, 'JPEG', quality=88, optimize=True, progressive=True, subsampling=0)
print(f'{OUT_SQ} geschrieben — 400x400')
