"""
Build the neofetch-style profile card as a standalone SVG.

Three decisions that are not cosmetic:

1. SVG, not a fenced code block. GitHub markdown renders no ANSI colour, so a
   terminal card has to be drawn.

2. The card carries its OWN dark background, so it reads identically under
   GitHub's light and dark themes. A transparent card with dark text vanishes
   in dark mode and the other way round.

3. The "HS" mark is drawn as <rect> cells, NOT as U+2588 FULL BLOCK text.
   An SVG in a README is loaded as an IMAGE, so no webfont reaches it and the
   reader's own monospace has to carry every glyph -- and plenty of them have
   no FULL BLOCK, which would show tofu. Rects also sit flush; text blocks
   left a line-gap between rows and the letters came out striped (measured:
   font-size 14 on a 20px line leaves ~6px of hole).

Every figure is measured from the GitHub API, never typed. Anything the
account does not state -- email, city, editor -- is simply absent.
"""

W = r"C:\Users\1\AppData\Local\Temp\ghprof"

# ── palette: GitHub's own dark canvas, so the card sits in the page ──────
BG, BORDER = "#0d1117", "#30363d"
GOLD, TEXT, DIM = "#f0b429", "#c9d1d9", "#6e7681"
CYAN, GREEN = "#56d4dd", "#7ee787"

# ── the "HS" mark as a bitmap, 5 wide per letter ────────────────────────
# The S has OPEN corners on purpose. A 5x7 block "S" with square corners is
# pixel-for-pixel a block "5" -- rendered once with filled corners and it read
# as "H5". Dropping the four corner cells is what makes it an S.
GLYPHS = {
    "H": ["1...1", "1...1", "1...1", "11111", "1...1", "1...1", "1...1"],
    "S": [".1111", "1....", "1....", ".111.", "....1", "....1", "1111."],
}
MARK = "HS"

# ── the facts, as measured ──────────────────────────────────────────────
LANGS = [
    ("PHP",        35.6, "#8993be"),
    ("CSS",        30.6, "#563d7c"),
    ("JavaScript", 10.8, "#f1e05a"),
    ("SCSS",        8.1, "#c6538c"),
    ("HTML",        8.0, "#e34c26"),
    ("TypeScript",  2.5, "#3178c6"),
    ("Blade",       2.2, "#f7523f"),
]

ROWS = [
    ("OS",       "Laravel · PHP 8",                GREEN),
    ("Host",     "Zenesa Tech",                    TEXT),
    ("Uptime",   "3 years, 5 months",              TEXT),
    ("Shell",    "bash · artisan",                 TEXT),
    ("Stack",    "Laravel · React Native · MySQL", CYAN),
    ("Repos",    "15 public",                      TEXT),
    ("Building", "Shareide · per seat ride sharing", GOLD),
    ("Live",     "shareide.com",                   CYAN),
]

# ── layout ──────────────────────────────────────────────────────────────
FS, LH = 14, 20
PAD = 26
CARD_W, CARD_H = 820, 384
CELL, GAP = 15, 2                      # mark cell size
MARK_X, MARK_Y = PAD + 22, PAD + 60
INFO_X = PAD + 230

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")

out = []
A = out.append

A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{CARD_H}" '
  f'viewBox="0 0 {CARD_W} {CARD_H}" role="img" '
  f'aria-label="Hasnain Saleem, Laravel developer at Zenesa Tech, building '
  f'Shareide, a per seat ride sharing app for Pakistan">')
A('<title>hasnain@github</title>')
A(f'<rect x="1" y="1" width="{CARD_W-2}" height="{CARD_H-2}" rx="12" '
  f'fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>')

# title bar, so it reads as a terminal rather than a box
for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
    A(f'<circle cx="{PAD + i*18}" cy="{PAD}" r="6" fill="{c}"/>')
A(f'<text x="{PAD + 66}" y="{PAD + 4.5}" font-family="monospace" font-size="12" '
  f'fill="{DIM}">hasnain@github: ~</text>')

# ── the mark ────────────────────────────────────────────────────────────
x0 = MARK_X
for ch in MARK:
    g = GLYPHS[ch]
    for r, row in enumerate(g):
        for c, bit in enumerate(row):
            if bit != "1":
                continue
            A(f'<rect x="{x0 + c*(CELL+GAP)}" y="{MARK_Y + r*(CELL+GAP)}" '
              f'width="{CELL}" height="{CELL}" rx="2.5" fill="{GOLD}"/>')
    x0 += 5*(CELL+GAP) + (CELL+GAP)    # one blank column between letters

mark_w = len(MARK)*5*(CELL+GAP) + (CELL+GAP) - GAP
mark_bottom = MARK_Y + 7*(CELL+GAP)
A(f'<line x1="{MARK_X}" y1="{mark_bottom + 16}" x2="{MARK_X + mark_w}" '
  f'y2="{mark_bottom + 16}" stroke="{BORDER}" stroke-width="1.5"/>')
A(f'<text x="{MARK_X + mark_w/2}" y="{mark_bottom + 40}" text-anchor="middle" '
  f'font-family="monospace" font-size="13" fill="{DIM}" '
  f'letter-spacing="3">HASNAIN</text>')

# ── the info block ──────────────────────────────────────────────────────
y = PAD + 50
A(f'<text x="{INFO_X}" y="{y}" font-family="monospace" font-size="{FS}" '
  f'xml:space="preserve">'
  f'<tspan fill="{GOLD}" font-weight="bold">hasnain</tspan>'
  f'<tspan fill="{TEXT}">@</tspan>'
  f'<tspan fill="{GOLD}" font-weight="bold">github</tspan></text>')
y += 8
A(f'<line x1="{INFO_X}" y1="{y}" x2="{INFO_X + 330}" y2="{y}" '
  f'stroke="{BORDER}" stroke-width="1.5"/>')
y += LH + 2

for label, value, colour in ROWS:
    # dots pad the label so the values line up in whatever monospace the
    # reader has -- a fixed x for the value would drift between fonts
    pad = (label + " ").ljust(11, ".")
    A(f'<text x="{INFO_X}" y="{y}" font-family="monospace" font-size="{FS}" '
      f'xml:space="preserve">'
      f'<tspan fill="{DIM}">{pad}</tspan> '
      f'<tspan fill="{colour}">{esc(value)}</tspan></text>')
    y += LH

# ── languages: the measured split ───────────────────────────────────────
y += 14
A(f'<text x="{INFO_X}" y="{y}" font-family="monospace" font-size="{FS}" '
  f'fill="{DIM}" xml:space="preserve">Languages ..</text>')
y += 12

BAR_W, BAR_H = 440, 9
A(f'<clipPath id="barclip"><rect x="{INFO_X}" y="{y}" width="{BAR_W}" '
  f'height="{BAR_H}" rx="4.5"/></clipPath>')
A('<g clip-path="url(#barclip)">')
x = INFO_X
for name, pct, colour in LANGS:
    w = BAR_W * pct / 100.0
    A(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{BAR_H}" fill="{colour}"/>')
    x += w
A(f'<rect x="{x:.1f}" y="{y}" width="{BAR_W}" height="{BAR_H}" fill="{BORDER}"/>')
A('</g>')
y += BAR_H + 21

for chunk in (LANGS[:4], LANGS[4:]):
    cx = INFO_X
    for name, pct, colour in chunk:
        A(f'<circle cx="{cx+4}" cy="{y-4.5}" r="4" fill="{colour}"/>')
        A(f'<text x="{cx+14}" y="{y}" font-family="monospace" font-size="12" '
          f'fill="{TEXT}">{name} {pct}%</text>')
        cx += 14 + int(len(f"{name} {pct}%") * 12 * 0.6) + 18
    y += 18

# ── neofetch's own colour row ───────────────────────────────────────────
sw_y = CARD_H - PAD - 8
for i, c in enumerate(("#ff7b72", "#f0b429", "#7ee787", "#56d4dd",
                       "#79c0ff", "#d2a8ff", "#c9d1d9", "#6e7681")):
    A(f'<rect x="{MARK_X + i*20}" y="{sw_y}" width="16" height="10" rx="2" fill="{c}"/>')

A('</svg>')

svg = "\n".join(out)
open(W + r"\card-dark.svg", "w", encoding="utf-8").write(svg)
print("written", len(svg), "chars")
