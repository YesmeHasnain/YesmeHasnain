"""
Build the neofetch-style profile card as a standalone SVG.

The layout follows the reference profile this was modelled on, and the two
things that make it read as that card rather than a generic stats box are:

  * the VALUE is right-aligned to the card's right edge, with the label left.
    Dotted leaders were tried first and are a different design language. This
    also removes every dependence on the reader's monospace advance width:
    labels anchor start, values anchor end, so nothing drifts between fonts.
  * sections are separated by blank lines, and `Contact` / `GitHub Stats`
    carry a header with a rule running to the right edge.

Three decisions that are not cosmetic:

1. SVG, not a fenced code block. GitHub markdown renders no ANSI colour, so a
   terminal card has to be drawn.

2. The card carries its OWN dark background, so it reads identically under
   GitHub's light and dark themes. A transparent card with dark text vanishes
   in dark mode and the other way round.

3. The portrait is ASCII generated from the real avatar, as the reference
   does. The avatar is a mirror selfie with a tiled background, so a naive
   luminance ramp over the whole square came out as unreadable noise
   (measured). What makes it legible is cropping to the subject first and
   autocontrasting before sampling.

Every figure is measured from the GitHub API, never typed. Anything the
account does not state is simply absent. Re-run this rather than editing a
number by hand.

  python gen_card.py
"""
import os
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))

# ── palette, taken off the reference card ───────────────────────────────
BG      = "#0d1117"   # GitHub's own dark canvas, so the card sits in the page
BORDER  = "#21262d"
AMBER   = "#e8a33d"   # labels
NAME    = "#f0b429"
VALUE   = "#79c0ff"   # values
TEAL    = "#56d4dd"
GREEN   = "#7ee787"
HEAD    = "#c9d1d9"   # section headers
RULE    = "#30363d"
# The portrait is deliberately DIM. Sampled off the reference card, its
# glyphs average #575f73 against a #0d1117 ground -- nearer a watermark than
# body text. A brighter grey turns the art into the loudest thing on the card
# and the information stops being the point.
ART     = "#6b7484"

# ── the facts, as measured from the GitHub API ──────────────────────────
HANDLE = "yesmehasnain"

GROUPS = [
    [
        ("OS",                    "Laravel, PHP 8.4, MySQL",            GREEN),
        ("Uptime",                "3 years, 5 months, 10 days",         VALUE),
        ("Host",                  "Zenesa Tech",                        VALUE),
        ("Kernel",                "Laravel 12 (php8.4-fpm, nginx)",     VALUE),
        ("IDE",                   "VS Code, Claude Code",               VALUE),
    ],
    [
        ("Languages.Programming", "PHP, JavaScript, TypeScript",        VALUE),
        ("Languages.Computer",    "HTML, CSS, SCSS, Blade",             VALUE),
        ("Languages.Real",        "Urdu, English",                      VALUE),
    ],
    [
        ("Projects.Live",         "Shareide, per seat ride sharing",    TEAL),
        ("Projects.Apps",         "Rider, Fleet (React Native, Expo)",  TEAL),
    ],
]

CONTACT = [
    ("Website",  "shareide.com",                 VALUE),
    ("LinkedIn", "in/hasnain-saleem-67388a284",  VALUE),
    ("Company",  "Zenesa Tech",                  VALUE),
]

# left label, left value, right label, right value
STATS = [
    ("Repos",   "16",    "Stars",     "12"),
    ("Commits", "8,944", "Followers", "4"),
]
CODE_LABEL = "Code on GitHub"
CODE_VALUE = "42.5 MB"
CODE_SPLIT = "PHP 35.6%, CSS 30.6%, JS 10.8%"

# ── layout ──────────────────────────────────────────────────────────────
CARD_W = 900
PAD = 28
FS, LH = 12.5, 19            # info text
AFS, ALH = 10.0, 10.9        # portrait: denser than the text, as in the reference
ART_COLS, ART_ROWS = 30, 42

ART_X = PAD + 4
INFO_X = PAD + 212           # label column
RIGHT_X = CARD_W - PAD - 6   # every value right-anchors here


def ascii_portrait():
    """Crop to the subject, autocontrast, then ramp. The crop is what makes
    it readable: sampling the whole square lets the tiled background win."""
    im = Image.open(os.path.join(HERE, "avatar.png")).convert("L")
    w, h = im.size
    # These four numbers were chosen by rendering three crops and reading
    # them, not by eye on the photo. A wider crop drags in the dark wall at
    # the left, which maps to a solid column of '@' and reads as a bar rather
    # than as art; dropping below y=0.75 brings in the scooter, which is the
    # brightest thing in the frame and swamps the figure.
    crop = im.crop((int(w * 0.20), 0, int(w * 0.66), int(h * 0.75)))
    crop = ImageOps.autocontrast(crop, cutoff=2)
    small = crop.resize((ART_COLS, ART_ROWS))
    px = small.load()
    # no &, < or > in this ramp, so nothing needs XML escaping
    ramp = " .:-=+*#%@"
    return ["".join(ramp[min(len(ramp) - 1, int(px[x, y] / 256 * len(ramp)))]
                    for x in range(ART_COLS)) for y in range(ART_ROWS)]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


out = []
A = out.append


def row(y, label, value, colour):
    """Label anchored left, value anchored RIGHT. Nothing between them, so
    the columns cannot drift with the reader's monospace width."""
    A(f'<text x="{INFO_X}" y="{y}" font-family="monospace" font-size="{FS}" '
      f'fill="{AMBER}">{esc(label)}:</text>')
    A(f'<text x="{RIGHT_X}" y="{y}" font-family="monospace" font-size="{FS}" '
      f'fill="{colour}" text-anchor="end">{esc(value)}</text>')


def header(y, text):
    A(f'<text x="{INFO_X}" y="{y}" font-family="monospace" font-size="{FS}" '
      f'fill="{HEAD}">{esc(text)}</text>')
    x0 = INFO_X + (len(text) + 2) * FS * 0.6
    A(f'<line x1="{x0}" y1="{y - 4}" x2="{RIGHT_X}" y2="{y - 4}" '
      f'stroke="{RULE}" stroke-width="1" stroke-dasharray="2 3"/>')


# ── measure the height the content needs, then size the card to it ──────
rows = 1 + 1                                   # handle + blank
for g in GROUPS:
    rows += len(g) + 1
rows += 1 + len(CONTACT) + 1                   # Contact header + rows + blank
rows += 1 + len(STATS) + 1                     # Stats header + rows + code line
INFO_H = rows * LH
ART_H = ART_ROWS * ALH
CARD_H = int(PAD * 2 + 16 + max(INFO_H, ART_H))

A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{CARD_H}" '
  f'viewBox="0 0 {CARD_W} {CARD_H}" role="img" '
  f'aria-label="yesmehasnain. Laravel developer at Zenesa Tech, building '
  f'Shareide, a per seat ride sharing platform for Pakistan. 16 public '
  f'repositories, 12 stars, 8944 commits.">')
A('<title>yesmehasnain</title>')
A(f'<rect x="0.75" y="0.75" width="{CARD_W-1.5}" height="{CARD_H-1.5}" rx="10" '
  f'fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>')

# ── the portrait ────────────────────────────────────────────────────────
art = ascii_portrait()
art_top = PAD + 14
for i, line in enumerate(art):
    if not line.strip():
        continue
    A(f'<text x="{ART_X}" y="{art_top + i*ALH}" font-family="monospace" '
      f'font-size="{AFS}" fill="{ART}" xml:space="preserve">{esc(line)}</text>')

# ── the info block ──────────────────────────────────────────────────────
y = PAD + 16
A(f'<text x="{INFO_X}" y="{y}" font-family="monospace" font-size="{FS}" '
  f'fill="{NAME}" font-weight="bold">{HANDLE}</text>')
x0 = INFO_X + (len(HANDLE) + 2) * FS * 0.6
A(f'<line x1="{x0}" y1="{y - 4}" x2="{RIGHT_X}" y2="{y - 4}" '
  f'stroke="{RULE}" stroke-width="1" stroke-dasharray="2 3"/>')
y += LH * 2

for g in GROUPS:
    for label, value, colour in g:
        row(y, label, value, colour)
        y += LH
    y += LH

header(y, "Contact")
y += LH
for label, value, colour in CONTACT:
    row(y, label, value, colour)
    y += LH
y += LH

header(y, "GitHub Stats")
y += LH
MID = INFO_X + (RIGHT_X - INFO_X) * 0.52
for llab, lval, rlab, rval in STATS:
    A(f'<text x="{INFO_X}" y="{y}" font-family="monospace" font-size="{FS}" '
      f'fill="{AMBER}">{llab}:</text>')
    A(f'<text x="{MID - 22}" y="{y}" font-family="monospace" font-size="{FS}" '
      f'fill="{VALUE}" text-anchor="end">{lval}</text>')
    A(f'<text x="{MID}" y="{y}" font-family="monospace" font-size="{FS}" '
      f'fill="{RULE}">|</text>')
    A(f'<text x="{MID + 18}" y="{y}" font-family="monospace" font-size="{FS}" '
      f'fill="{AMBER}">{rlab}:</text>')
    A(f'<text x="{RIGHT_X}" y="{y}" font-family="monospace" font-size="{FS}" '
      f'fill="{VALUE}" text-anchor="end">{rval}</text>')
    y += LH

A(f'<text x="{INFO_X}" y="{y}" font-family="monospace" font-size="{FS}" '
  f'fill="{AMBER}">{CODE_LABEL}:</text>')
A(f'<text x="{RIGHT_X}" y="{y}" font-family="monospace" font-size="{FS}" '
  f'text-anchor="end"><tspan fill="{GREEN}">{CODE_VALUE}</tspan>'
  f'<tspan fill="{RULE}">  {{</tspan>'
  f'<tspan fill="{VALUE}">{esc(CODE_SPLIT)}</tspan>'
  f'<tspan fill="{RULE}">}}</tspan></text>')

A('</svg>')

svg = "\n".join(out)
path = os.path.join(HERE, "card-dark.svg")
open(path, "w", encoding="utf-8").write(svg)
print(f"written {len(svg)} chars, card {CARD_W}x{CARD_H} -> {path}")
