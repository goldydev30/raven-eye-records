#!/usr/bin/env python3
"""Generate the Raven Eye logo: a raven ouroboros, biting its own tail feathers.

Usage: python3 scripts/build_logo.py

Writes:
  assets/js/logo.js         window.RER_LOGO, the animated inline SVG
  assets/img/raven-eye.svg  static copy
  assets/img/sigil.svg      favicon

The raven's body forms the ring: its head sits at the top facing left, its back and wings
run clockwise round the circle, and its tail feathers sweep up the left side into its own
open beak. Outside it, a ring of letters spelling RAVEN EYE RECORDS turns slowly, and the
amber eye breathes and glints (both animated in style.css). Linework is engraved ice blue.
"""
import json, math, random, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
C = 200                     # centre of the 400 x 400 box
ICE, ICE_DIM, INK = "#b4c9de", "#6f8aa6", "#05070b"

def f(x):
    return ("%.1f" % x).rstrip("0").rstrip(".")

def polar(r, deg):
    a = math.radians(deg)
    return C + r * math.cos(a), C + r * math.sin(a)

def pts(points):
    return " L".join("%s %s" % (f(x), f(y)) for x, y in points)

# ---------- feathers ----------
def blade(a0, a1, r0, r1, w):
    """A feather: a tapered blade following an arc from angle a0 to a1, radius r0 to r1."""
    n = 30
    left, right, spine = [], [], []
    for i in range(n + 1):
        t = i / n
        a = a0 + (a1 - a0) * t
        r = r0 + (r1 - r0) * t
        x, y = polar(r, a)
        grow = min(1, t / .1)
        half = w / 2 * grow * (1 - max(0, (t - .25) / .75) ** 2.2) + .3
        nx, ny = math.cos(math.radians(a)), math.sin(math.radians(a))
        left.append((x + nx * half, y + ny * half))
        right.append((x - nx * half, y - ny * half))
        spine.append((x, y))
    outline = "M" + pts(left + right[::-1]) + " Z"
    shaft = "M" + pts(spine[1:-2])
    barbs = []
    for i in range(1, n - 1):
        (sx, sy), (lx, ly), (rx, ry) = spine[i], left[i + 1], right[i + 1]
        barbs.append("M%s %sL%s %s" % (f(sx), f(sy), f(sx + (lx - sx) * .85), f(sy + (ly - sy) * .85)))
        barbs.append("M%s %sL%s %s" % (f(sx), f(sy), f(sx + (rx - sx) * .85), f(sy + (ry - sy) * .85)))
    return ('<path d="%s" fill="url(#rer-feather)" stroke="%s" stroke-width="1.1"/>'
            '<path d="%s" stroke="%s" stroke-width=".9" fill="none"/>'
            '<path d="%s" stroke="%s" stroke-opacity=".7" stroke-width=".5" fill="none"/>'
            % (outline, ICE, shaft, ICE, "".join(barbs), ICE))

def body():
    """The body band behind the feathers: from the nape, clockwise to the base of the tail."""
    outer, inner = [], []
    for i in range(61):
        t = i / 60
        a = -78 + 220 * t
        outer.append(polar(150 - 18 * t ** 1.5, a))
        inner.append(polar(86 + 22 * t ** 1.2, a))
    return '<path d="M%s Z" fill="url(#rer-feather)" stroke="%s" stroke-width="1"/>' % (pts(outer + inner[::-1]), ICE)

def scales():
    random.seed(3)
    out = []
    for _ in range(90):
        a = random.uniform(-70, 10)
        r = random.uniform(92, 140)
        x, y = polar(r, a)
        tx, ty = polar(r, a + 4)
        out.append('<path d="M%s %s Q%s %s %s %s"/>' % (f(x), f(y), f((x + tx) / 2 + 2.5), f((y + ty) / 2 + 2.5), f(tx), f(ty)))
    return '<g fill="none" stroke="%s" stroke-opacity=".5" stroke-width=".6">%s</g>' % (ICE, "".join(out))

def wing():
    parts = []
    for i in range(6):   # long wing feathers along the back, outermost first
        lane = 146 - i * 9
        parts.append(blade(-50 + i * 4, 150 - i * 16, lane, lane - 10, 15))
    for i in range(4):   # coverts on the shoulder
        lane = 120 - i * 8
        parts.append(blade(-64 + i * 3, 20 - i * 14, lane, lane - 4, 12))
    return "".join(parts)

def tail():
    """Tail feathers sweeping up the left side, their tips caught in the beak."""
    parts = []
    for i, (lane, tip_r, tip_a) in enumerate([(138, 112, 247), (128, 109, 249), (118, 106, 251), (108, 104, 250), (98, 102, 248)]):
        parts.append(blade(118 + i * 4, tip_a, lane, tip_r, 15))
    return "".join(parts)

# ---------- head ----------
EYE = (212, 72)
HEAD = ("M178 70 C188 52 214 44 238 48 C256 51 270 60 280 72 C286 76 292 80 296 86 C288 86 284 88 280 92 "
        "C270 100 252 110 232 116 C214 114 196 108 184 98 Z")
UPPER = "M180 68 C162 70 142 78 124 96 C130 98 136 96 142 94 C156 90 170 90 186 92 Z"
LOWER = "M186 96 C170 102 154 110 138 120 C144 122 150 120 156 117 C168 112 180 108 190 106 Z"

def head():
    random.seed(11)
    marks = []
    for _ in range(60):
        x, y = random.uniform(186, 290), random.uniform(52, 112)
        if math.hypot(x - EYE[0], y - EYE[1]) < 11:
            continue
        marks.append('<path d="M%s %s q4 3 8 0"/>' % (f(x), f(y)))
    return ('<clipPath id="rer-headclip"><path d="%s"/></clipPath>' % HEAD +
            '<path d="%s" fill="url(#rer-feather)" stroke="%s" stroke-width="1.2"/>' % (HEAD, ICE) +
            '<g clip-path="url(#rer-headclip)" fill="none" stroke="%s" stroke-opacity=".45" stroke-width=".6">%s</g>' % (ICE, "".join(marks)) +
            '<path d="M196 64 C214 54 240 54 262 62 M198 90 C216 86 238 88 256 96" fill="none" stroke="%s" stroke-opacity=".55" stroke-width=".7"/>' % ICE)

def beak_upper():
    return ('<path d="%s" fill="url(#rer-beak)" stroke="%s" stroke-width="1.2"/>' % (UPPER, ICE) +
            '<path d="M180 74 C164 76 148 82 134 92" fill="none" stroke="%s" stroke-width=".7" stroke-opacity=".7"/>' % ICE)

def beak_lower():
    return '<path d="%s" fill="url(#rer-beak)" stroke="%s" stroke-width="1.2"/>' % (LOWER, ICE)

def eye():
    x, y = EYE
    return f'''<g class="rer-eye-glow"><circle cx="{x}" cy="{y}" r="14" fill="url(#rer-glow-grad)"/></g>
<circle cx="{x}" cy="{y}" r="6.5" fill="url(#rer-iris)" stroke="{INK}" stroke-width="1.3"/>
<circle class="rer-eye-core" cx="{x}" cy="{y}" r="2.3" fill="#ffe9a8"/>
<path class="rer-glint" d="M{x + 3} {y - 8} l1.1 3.3 3.3 1.1 -3.3 1.1 -1.1 3.3 -1.1 -3.3 -3.3 -1.1 3.3 -1.1 z" fill="#fff6dc"/>'''

# ---------- the turning ring of letters ----------
def letter_ring(r=178):
    words = ["RAVEN", "EYE", "RECORDS"]
    slots = []
    for w in words:
        slots += list(w) + ["•"]
    step = 360 / len(slots)
    out = []
    for i, ch in enumerate(slots):
        a = -90 + i * step
        x, y = polar(r, a)
        if ch == "•":
            out.append('<path transform="translate(%s %s) rotate(%s)" d="M0 -3 L2.4 0 L0 3 L-2.4 0 Z" fill="%s"/>'
                       % (f(x), f(y), f(a + 90), ICE))
        else:
            out.append('<text transform="translate(%s %s) rotate(%s)" text-anchor="middle" dominant-baseline="central">%s</text>'
                       % (f(x), f(y), f(a + 90), ch))
    rings = "".join('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="%s" stroke-opacity=".7"/>'
                    % (C, C, rr, ICE, sw) for rr, sw in ((162, 1), (165, .5), (194, 1)))
    return ('<g class="rer-letters">%s<g fill="%s" font-family="\'Germania One\', \'Cinzel\', Georgia, serif" font-size="21" letter-spacing="1">%s</g></g>'
            % (rings, ICE, "".join(out)))

def build():
    svg = f'''<svg class="rer-eye rer-ring" viewBox="0 0 400 400" role="img" aria-label="Raven Eye Records" xmlns="http://www.w3.org/2000/svg">
<defs>
<radialGradient id="rer-bg" cx="50%" cy="45%" r="55%"><stop offset="0" stop-color="#0d1626"/><stop offset=".7" stop-color="#070b13"/><stop offset="1" stop-color="{INK}"/></radialGradient>
<linearGradient id="rer-feather" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1b2c45"/><stop offset="1" stop-color="#0c1422"/></linearGradient>
<linearGradient id="rer-beak" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a3b55"/><stop offset="1" stop-color="#0a111d"/></linearGradient>
<radialGradient id="rer-iris" cx="45%" cy="45%" r="55%"><stop offset="0" stop-color="#fff3b0"/><stop offset=".35" stop-color="#ffc21a"/><stop offset=".75" stop-color="#ff5a12"/><stop offset="1" stop-color="#b3120f"/></radialGradient>
<radialGradient id="rer-glow-grad"><stop offset="0" stop-color="#ffb21a" stop-opacity=".9"/><stop offset=".4" stop-color="#ff4a12" stop-opacity=".45"/><stop offset="1" stop-color="#b3120f" stop-opacity="0"/></radialGradient>
<filter id="rer-ink" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="1" seed="4"/><feDisplacementMap in="SourceGraphic" scale=".9"/></filter>
</defs>
<circle cx="200" cy="200" r="198" fill="url(#rer-bg)"/>
{letter_ring()}
<g filter="url(#rer-ink)">
{body()}
{scales()}
{wing()}
{tail()}
{beak_lower()}
{head()}
{beak_upper()}
</g>
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
