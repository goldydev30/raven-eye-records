#!/usr/bin/env python3
"""Generate the Raven Eye logo: a raven curled inside rotating rings of sacred geometry.

Usage: python3 scripts/build_logo.py

Writes:
  assets/js/logo.js         window.RER_LOGO, the animated inline SVG
  assets/img/raven-eye.svg  static copy
  assets/img/sigil.svg      favicon

Layers, back to front:
  1. sacred geometry (Flower of Life, hexagram, Metatron lines), turning slowly
  2. a braided knot ring, turning the other way
  3. an outer ring of Elder Futhark runes, turning with the geometry
  4. the raven, fixed: head at the top with an open beak, body and wing feathers
     sweeping clockwise around the circle, drawn as engraved ice-blue linework
  5. the eye: a burning amber eye whose glow breathes and glints (animated in CSS)
"""
import json, math, random, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
C = 200                     # centre of the 400 x 400 box
ICE, ICE_DIM, NAVY, INK = "#b4c9de", "#6f8aa6", "#0c1422", "#05070b"

def f(x):
    return ("%.1f" % x).rstrip("0").rstrip(".")

def polar(r, deg):
    a = math.radians(deg)
    return C + r * math.cos(a), C + r * math.sin(a)

# ---------- 1. sacred geometry ----------
def geometry():
    out = []
    r = 28
    centres = [(C, C)] + [polar(r, a) for a in range(-90, 270, 60)]
    centres += [polar(r * 2, a) for a in range(-90, 270, 60)] + [polar(r * math.sqrt(3), a) for a in range(-60, 300, 60)]
    for x, y in centres:
        out.append('<circle cx="%s" cy="%s" r="%s"/>' % (f(x), f(y), r))
    for rr in (r * 3, 112, 150):
        out.append('<circle cx="%s" cy="%s" r="%s"/>' % (C, C, f(rr)))
    for start in (-90, -30):  # hexagram
        pts = [polar(150, start + k * 120) for k in range(3)]
        out.append('<path d="M%s Z"/>' % " L".join("%s %s" % (f(x), f(y)) for x, y in pts))
    hexa = [polar(150, a) for a in range(-90, 270, 60)]  # Metatron spokes
    for i in range(6):
        for j in range(i + 2, 6):
            if j - i != 3:
                continue
            out.append('<path d="M%s %s L%s %s"/>' % (f(hexa[i][0]), f(hexa[i][1]), f(hexa[j][0]), f(hexa[j][1])))
    return '<g class="rer-geo" fill="none" stroke="%s" stroke-opacity=".28" stroke-width=".7">%s</g>' % (ICE_DIM, "".join(out))

# ---------- 2. braided ring ----------
def braid(r0=165, amp=6, n=30):
    def strand(sign, a0, a1, steps):
        pts = []
        for i in range(steps + 1):
            t = math.radians(a0 + (a1 - a0) * i / steps)
            rr = r0 + sign * amp * math.sin(n * t)
            pts.append((C + rr * math.cos(t), C + rr * math.sin(t)))
        return "M" + " L".join("%s %s" % (f(x), f(y)) for x, y in pts)
    def stroke(d):
        return ('<path d="%s" stroke="%s" stroke-width="6.4"/><path d="%s" stroke="%s" stroke-width="3.4"/>'
                '<path d="%s" stroke="%s" stroke-width="1.1" stroke-dasharray="1.6 2.2" stroke-opacity=".9"/>'
                % (d, INK, d, ICE_DIM, d, ICE))
    out = [stroke(strand(1, 0, 360, 720)), stroke(strand(-1, 0, 360, 720))]
    # over-under: re-draw strand A over every other crossing
    step = 180 / n
    for k in range(0, 2 * n, 2):
        a = k * step
        out.append(stroke(strand(1, a - step * .45, a + step * .45, 16)))
    edge = '<circle cx="%s" cy="%s" r="%s" stroke="%s" stroke-width=".8" stroke-opacity=".6"/>'
    return ('<g class="rer-braid" fill="none" stroke-linecap="round">%s%s%s</g>'
            % ("".join(out), edge % (C, C, r0 + amp + 5, ICE_DIM), edge % (C, C, r0 - amp - 5, ICE_DIM)))

# ---------- 3. rune ring ----------
RUNES = [
    [(0, -6, 0, 6), (0, -1, 5, -4), (0, -5, 5, -8)],                 # fehu
    [(0, 6, 0, -6), (0, -6, 5, -2), (5, -2, 5, 6)],                  # uruz
    [(0, -6, 0, 6), (0, -3, 4, 0), (4, 0, 0, 3)],                    # thurisaz
    [(0, -6, 0, 6), (0, -6, 4, -3), (0, -2, 4, 1)],                  # ansuz
    [(0, -6, 0, 6), (0, -6, 4, -3), (4, -3, 0, 0), (0, 0, 4, 6)],    # raidho
    [(4, -6, 0, 0), (0, 0, 4, 6)],                                   # kenaz
    [(-3, -6, 3, 6), (3, -6, -3, 6)],                                # gebo
    [(0, -6, 0, 6), (0, -6, 4, -3), (4, -3, 0, 0)],                  # wunjo
    [(-3, -6, -3, 6), (3, -6, 3, 6), (-3, -2, 3, 2)],                # hagalaz
    [(0, -6, 0, 6), (-3, -2, 3, 2)],                                 # nauthiz
    [(0, -6, 0, 6)],                                                 # isa
    [(-1, -6, -4, -2), (-4, -2, -1, 1), (1, -1, 4, 2), (4, 2, 1, 6)],  # jera
    [(0, -6, 0, 6), (0, -6, -4, -2), (0, -6, 4, -2)],                # tiwaz
    [(0, -6, 0, 6), (0, -1, -4, -6), (0, -1, 4, -6)],                # algiz
    [(-3, -6, 3, -1), (3, -1, -3, 1), (-3, 1, 3, 6)],                # sowilo
    [(0, -6, 0, 6), (0, -6, 4, -3), (4, -3, 0, 0), (0, 0, 4, 3), (4, 3, 0, 6)],  # berkano
    [(-3, 6, -3, -6), (-3, -6, 0, -2), (0, -2, 3, -6), (3, -6, 3, 6)],           # ehwaz
    [(-3, 6, -3, -6), (3, 6, 3, -6), (-3, -6, 3, -1), (3, -6, -3, -1)],          # mannaz
    [(0, -6, 0, 6), (0, -6, 4, -2)],                                 # laguz
    [(0, -6, -4, -1), (-4, -1, 3, 6), (0, -6, 4, -1), (4, -1, -3, 6)],           # othala
    [(-4, -6, -4, 6), (4, -6, 4, 6), (-4, -6, 4, 6), (4, -6, -4, 6)],            # dagaz
    [(-3, -6, -3, 6), (-3, -6, 3, -2), (3, -2, -3, 2), (-3, 2, 3, 6)],           # perthro-ish
    [(0, -6, 0, 6), (-4, -4, 4, 4)],                                 # eihwaz-ish
    [(-3, -2, 0, -6), (0, -6, 3, -2), (3, -2, 0, 2), (0, 2, -3, -2), (0, 2, 0, 6)],  # ingwaz-ish
]

def runes(r=186):
    out = []
    for i, glyph in enumerate(RUNES):
        a = -90 + i * 15
        x, y = polar(r, a)
        segs = "".join("M%s %sL%s %s" % (f(x1 * .62), f(y1 * .62), f(x2 * .62), f(y2 * .62)) for x1, y1, x2, y2 in glyph)
        out.append('<path transform="translate(%s %s) rotate(%s)" d="%s"/>' % (f(x), f(y), f(a + 90), segs))
        tx, ty = polar(r, a + 7.5)
        tx2, ty2 = polar(r - 3, a + 7.5)
        out.append('<path d="M%s %sL%s %s" stroke-width=".6"/>' % (f(tx), f(ty), f(tx2), f(ty2)))
    rings = ''.join('<circle cx="%s" cy="%s" r="%s" stroke-width=".7"/>' % (C, C, rr) for rr in (178, 194))
    return ('<g class="rer-runes" fill="none" stroke="%s" stroke-width="1.1" stroke-linecap="round" stroke-opacity=".8">%s%s</g>'
            % (ICE, rings, "".join(out)))

# ---------- 4. the raven ----------
def blade(a0, a1, r0, r1, w, flip=1):
    """A feather: a tapered blade following an arc from angle a0 to a1, radius r0 to r1."""
    n = 26
    left, right, spine = [], [], []
    for i in range(n + 1):
        t = i / n
        a = a0 + (a1 - a0) * t
        r = r0 + (r1 - r0) * t
        x, y = polar(r, a)
        grow = min(1, t / .12)
        half = w / 2 * grow * (1 - max(0, (t - .2) / .8) ** 2.4) + .3
        nx, ny = math.cos(math.radians(a)), math.sin(math.radians(a))
        left.append((x + nx * half, y + ny * half))
        right.append((x - nx * half, y - ny * half))
        spine.append((x, y))
    outline = "M" + " L".join("%s %s" % (f(x), f(y)) for x, y in left + right[::-1]) + " Z"
    shaft = "M" + " L".join("%s %s" % (f(x), f(y)) for x, y in spine[1:-2])
    barbs = []
    for i in range(1, n - 1):
        (sx, sy), (lx, ly), (rx, ry) = spine[i], left[i + 1], right[i + 1]
        barbs.append("M%s %sL%s %s" % (f(sx), f(sy), f(sx + (lx - sx) * .85), f(sy + (ly - sy) * .85)))
        barbs.append("M%s %sL%s %s" % (f(sx), f(sy), f(sx + (rx - sx) * .85), f(sy + (ry - sy) * .85)))
    return ('<path d="%s" fill="url(#rer-feather)" stroke="%s" stroke-width="1.1"/><path d="%s" stroke="%s" stroke-width=".9" fill="none"/>'
            '<path d="%s" stroke="%s" stroke-opacity=".75" stroke-width=".55" fill="none"/>'
            % (outline, ICE, shaft, ICE, "".join(barbs), ICE))

def spiral(cx, cy, r, turns=2.4, start=0):
    pts = []
    for i in range(80):
        t = i / 79
        a = start + t * turns * 2 * math.pi
        rr = r * t
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return "M" + " L".join("%s %s" % (f(x), f(y)) for x, y in pts)

def raven():
    random.seed(7)
    parts = []
    # long primaries sweep round the bottom and into the braid
    # each feather keeps its own lane round the circle so its body and barbs stay visible
    for i in range(7):  # primaries: outermost first, tips fanning round to the bottom left
        lane = 150 - i * 10.5
        parts.append(blade(-20 - i * 2, 192 - i * 14, lane, lane - 6, 15))
    for i in range(5):  # secondaries
        lane = 128 - i * 10
        parts.append(blade(-44 - i * 3, 64 - i * 13, lane, lane - 5, 13))
    for i in range(4):  # coverts on the shoulder
        lane = 104 - i * 8
        parts.append(blade(-56 - i * 2, 12 - i * 12, lane, lane - 4, 11))
    # body mass behind the coverts: a crescent from the nape down the right side
    body = []
    for i in range(41):
        a = -72 + 150 * i / 40
        body.append(polar(150 - 8 * (i / 40), a))
    for i in range(41):
        a = 78 - 150 * i / 40
        body.append(polar(76 + 10 * (i / 40), a))
    body_d = "M" + " L".join("%s %s" % (f(x), f(y)) for x, y in body) + " Z"
    # small scale feathers on the breast and shoulder
    scales = []
    for _ in range(70):
        a = random.uniform(-58, 30)
        r = random.uniform(84, 128)
        x, y = polar(r, a)
        tx, ty = polar(r, a + 5)
        scales.append('<path d="M%s %s Q%s %s %s %s"/>' % (f(x), f(y), f((x + tx) / 2 + 3), f((y + ty) / 2), f(tx), f(ty)))
    head = ("M206 98 C220 78 250 70 276 74 C292 76 304 82 314 90 L334 84 L320 98 L340 102 L320 108 "
            "C322 126 314 142 300 154 C286 166 272 174 262 178 C250 168 238 156 228 144 L216 154 L218 138 L204 142 Z")
    upper = "M208 96 C178 96 136 102 94 124 C102 128 112 128 122 125 C152 120 184 122 212 126 Z"
    lower = "M212 134 C190 146 164 162 136 186 C140 188 146 186 150 184 C176 168 198 156 218 146 Z"
    knot = ("M150 110 C160 104 172 116 160 118 C150 120 146 108 156 106 M172 108 C182 102 194 114 182 116 "
            "C172 118 168 106 178 104")
    parts_back = ('<path d="%s" fill="%s" stroke="%s" stroke-width="1"/>' % (body_d, NAVY, ICE) +
                  '<g fill="none" stroke="%s" stroke-opacity=".45" stroke-width=".6">%s</g>' % (ICE, "".join(scales)))
    head_scales = []
    for _ in range(90):
        x, y = random.uniform(214, 330), random.uniform(78, 176)
        if math.hypot(x - EYE[0], y - EYE[1]) < 13 or math.hypot(x - 268, y - 108) < 16:
            continue
        head_scales.append('<path d="M%s %s q4 3 8 0"/>' % (f(x), f(y)))
    headg = ('<clipPath id="rer-headclip"><path d="%s"/></clipPath>' % head +
             '<path d="%s" fill="url(#rer-feather)" stroke="%s" stroke-width="1.2"/>' % (head, ICE) +
             '<g clip-path="url(#rer-headclip)" fill="none" stroke="%s" stroke-opacity=".45" stroke-width=".6">%s</g>' % (ICE, "".join(head_scales)) +
             '<path d="%s" fill="none" stroke="%s" stroke-width=".9" stroke-opacity=".85"/>' % (spiral(268, 108, 15, 2.6, 0.4), ICE) +
             '<path d="M226 104 C240 92 262 88 284 92 M236 118 C252 110 272 110 290 116 M244 134 C258 128 274 128 290 134" '
             'fill="none" stroke="%s" stroke-opacity=".5" stroke-width=".6"/>' % ICE +
             '<path d="%s" fill="%s" stroke="%s" stroke-width="1.2"/>' % (lower, NAVY, ICE) +
             '<path d="%s" fill="%s" stroke="%s" stroke-width="1.2"/>' % (upper, NAVY, ICE) +
             '<path d="M206 106 C176 106 142 112 110 122" fill="none" stroke="%s" stroke-width=".7" stroke-opacity=".7"/>' % ICE +

             '<path d="M214 140 C196 150 172 164 150 180" fill="none" stroke="%s" stroke-width=".6" stroke-opacity=".6"/>' % ICE)
    return parts_back + "".join(parts) + headg

# ---------- 5. the eye ----------
EYE = (238, 104)

def eye():
    x, y = EYE
    return f'''<g class="rer-eye-glow"><circle cx="{x}" cy="{y}" r="16" fill="url(#rer-glow-grad)"/></g>
<circle cx="{x}" cy="{y}" r="7.5" fill="url(#rer-iris)" stroke="{INK}" stroke-width="1.4"/>
<circle cx="{x}" cy="{y}" r="2.6" fill="#ffe9a8" class="rer-eye-core"/>
<path class="rer-glint" d="M{x + 3} {y - 9} l1.2 3.6 3.6 1.2 -3.6 1.2 -1.2 3.6 -1.2 -3.6 -3.6 -1.2 3.6 -1.2 z" fill="#fff6dc"/>'''

def build():
    svg = f'''<svg class="rer-eye rer-ring" viewBox="0 0 400 400" role="img" aria-label="Raven Eye Records" xmlns="http://www.w3.org/2000/svg">
<defs>
<radialGradient id="rer-bg" cx="50%" cy="45%" r="55%"><stop offset="0" stop-color="#0d1626"/><stop offset=".7" stop-color="#070b13"/><stop offset="1" stop-color="{INK}"/></radialGradient>
<radialGradient id="rer-iris" cx="45%" cy="45%" r="55%"><stop offset="0" stop-color="#fff3b0"/><stop offset=".35" stop-color="#ffc21a"/><stop offset=".75" stop-color="#ff5a12"/><stop offset="1" stop-color="#b3120f"/></radialGradient>
<radialGradient id="rer-glow-grad"><stop offset="0" stop-color="#ffb21a" stop-opacity=".9"/><stop offset=".4" stop-color="#ff4a12" stop-opacity=".45"/><stop offset="1" stop-color="#b3120f" stop-opacity="0"/></radialGradient>
<linearGradient id="rer-feather" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1b2c45"/><stop offset="1" stop-color="#0c1422"/></linearGradient>
<filter id="rer-ink" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="1" seed="4"/><feDisplacementMap in="SourceGraphic" scale=".9"/></filter>
</defs>
<circle cx="200" cy="200" r="198" fill="url(#rer-bg)"/>
{geometry()}
{braid()}
{runes()}
<g filter="url(#rer-ink)">{raven()}</g>
{eye()}
</svg>'''
    return " ".join(svg.split("\n"))

if __name__ == "__main__":
    svg = build()
    (ROOT / "assets/js/logo.js").write_text(
        "/* Generated by scripts/build_logo.py. The Raven Eye logo. */\n"
        "window.RER_LOGO = " + json.dumps(svg) + ";\n", encoding="utf-8")
    (ROOT / "assets/img/raven-eye.svg").write_text(svg.replace('class="rer-eye rer-ring"', 'width="512" height="512"', 1), encoding="utf-8")
    (ROOT / "assets/img/sigil.svg").write_text(svg.replace('class="rer-eye rer-ring"', 'width="64" height="64"', 1), encoding="utf-8")
    print("logo: %d bytes" % len(svg))
