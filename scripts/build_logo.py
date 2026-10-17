#!/usr/bin/env python3
"""Generate the Raven Eye logo: a narrowed, foreboding raven's eye cut like a woodblock.

Usage: python3 scripts/build_logo.py

Writes:
  assets/js/logo.js         window.RER_LOGO, the inline SVG used on the site
  assets/img/raven-eye.svg  static copy
  assets/img/sigil.svg      favicon

Black ink with bone-white cuts, in the manner of old black metal covers: jagged plumage
blades sweep back from the beak, a hard brow bears down on a slit of an eye, and the
iris smoulders a dull blood red. The eyelids are a separate group; site.js closes them
when a visitor hovers over the eye (see .rer-eye.closed in style.css).
"""
import json, math, random, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BONE, INK, BLOOD = "#d9d0bf", "#030203", "#8a0d10"

# The eye: a slit slanting down toward the beak on the left.
L, R = (118, 214), (292, 182)
UPPER_LID = "C160 186 236 160 %s %s" % R           # from L to R
LOWER_LID = "C254 214 176 236 %s %s" % L           # from R back to L
EYE = "M%s %s %s %s Z" % (L[0], L[1], UPPER_LID, LOWER_LID)
IRIS = (208, 200, 33)

def f(x):
    return ("%.1f" % x).rstrip("0").rstrip(".")

def _rake():
    """Shards fan back from the eye toward the nape, the way a raven's head feathers lie."""
    out = []
    for i, (deg, r, w) in enumerate([(-80, 176, 12), (-62, 188, 14), (-44, 190, 14), (-24, 192, 13), (-6, 196, 12),
                                     (14, 194, 13), (34, 192, 14), (54, 190, 15), (74, 184, 13), (96, 170, 12), (118, 150, 11)]):
        a = math.radians(deg)
        tip = (205 + r * math.cos(a) + 10, 198 + r * math.sin(a))
        base = (150 + i * 12, 198 + (i - 4.5) * 2.4) if i < 6 else (232 - (i - 6) * 26, 214 - (i - 6) * 1)
        mx, my = (base[0] + tip[0]) / 2, (base[1] + tip[1]) / 2
        dx, dy = tip[0] - base[0], tip[1] - base[1]
        ln = math.hypot(dx, dy)
        bend = (mx + dy / ln * ln * .12, my - dx / ln * ln * .12)   # sickle curve, hooked clockwise
        out.append((base, bend, tip, w))
    return out
SHARDS = _rake()
BROW = "M100 214 C150 196 222 180 386 92 C300 112 240 128 196 146 C164 160 136 176 120 188 Z"
BROW_CUTS = "M120 204 C190 174 260 140 380 96 M140 186 C200 160 270 130 376 98 M170 170 C230 146 300 118 372 100"

def brow():
    """The brow: a hooked blade pressing down on the upper lid."""
    return ('<path d="%s" fill="url(#rer-shard)" stroke="%s" stroke-width="2" stroke-linejoin="miter"/>' % (BROW, BONE) +
            '<path d="%s" fill="none" stroke="%s" stroke-width=".8" stroke-opacity=".4"/>' % (BROW_CUTS, BONE))

def shards(items=SHARDS):
    """Feather shards raking back from the eye, cut with a few engraved lines each."""
    bodies, cuts = [], []
    for (x0, y0), (cx, cy), (tx, ty), w in items:
        dx, dy = cx - x0, cy - y0
        ln = math.hypot(dx, dy)
        nx, ny = -dy / ln, dx / ln
        def edge(s):
            return (x0 + nx * w * s, y0 + ny * w * s, cx + nx * w * .8 * s, cy + ny * w * .8 * s)
        ax, ay, acx, acy = edge(1)
        bx, by, bcx, bcy = edge(-1)
        bodies.append('<path d="M%s %s Q%s %s %s %s Q%s %s %s %s Z"/>'
                      % (f(ax), f(ay), f(acx), f(acy), f(tx), f(ty), f(bcx), f(bcy), f(bx), f(by)))
        for s in (-.45, .1, .6):
            px, py, qx, qy = edge(s)
            cuts.append("M%s %sQ%s %s %s %s" % (f(px), f(py), f(qx), f(qy), f(tx + (px - x0) * .15), f(ty + (py - y0) * .15)))
    return ('<g fill="url(#rer-shard)" stroke="%s" stroke-width="1.8" stroke-linejoin="miter">%s</g>' % (BONE, "".join(bodies)) +
            '<path d="%s" fill="none" stroke="%s" stroke-width=".8" stroke-opacity=".38"/>' % ("".join(cuts), BONE))

def beak():
    random.seed(13)
    bristles = []
    for _ in range(28):
        x, y = random.uniform(70, 132), random.uniform(178, 206)
        ln = random.uniform(14, 26)
        a = math.radians(random.uniform(-24, -6))
        bristles.append("M%s %sq%s %s %s %s" % (f(x), f(y), f(ln * .5), f(-3), f(math.cos(a) * ln), f(math.sin(a) * ln)))
    upper = "M152 176 C112 158 52 166 12 230 C50 222 96 216 130 213 Z"
    lower = "M130 217 C98 219 58 226 26 232 C60 242 106 248 148 236 Z"
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="2"/>' % (lower, INK, BONE) +
            '<path d="%s" fill="url(#rer-shard)" stroke="%s" stroke-width="2.2"/>' % (upper, BONE) +
            '<path d="M140 182 C104 172 62 180 30 214" fill="none" stroke="%s" stroke-width=".9" stroke-opacity=".45"/>' % BONE +
            '<path d="%s" fill="none" stroke="%s" stroke-width=".8" stroke-opacity=".5"/>' % ("".join(bristles), BONE))

def eye():
    cx, cy, r = IRIS
    rays = "".join("M%s %sL%s %s" % (f(cx + 17 * math.cos(a)), f(cy + 17 * math.sin(a)), f(cx + (r - 2) * math.cos(a)), f(cy + (r - 2) * math.sin(a)))
                   for a in (i / 48 * 2 * math.pi for i in range(48)))
    return f'''<clipPath id="rer-eyeclip"><path d="{EYE}"/></clipPath>
<path d="{EYE}" fill="#0c0405"/>
<g clip-path="url(#rer-eyeclip)">
<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#rer-iris)"/>
<path d="{rays}" stroke="{INK}" stroke-opacity=".45" stroke-width=".7"/>
<circle cx="{cx}" cy="{cy}" r="16" fill="{INK}"/>
<path d="M197 189 q5 -4 11 -3" fill="none" stroke="{BONE}" stroke-width="2.4" stroke-linecap="round" opacity=".85"/>
<rect x="100" y="150" width="200" height="34" fill="url(#rer-shade)"/>
<g class="rer-lids">
<path class="rer-lid-top" d="M{L[0]} {L[1]} {UPPER_LID} L310 {R[1]} V100 H100 V{L[1]} Z" fill="{INK}" stroke="{BONE}" stroke-width="2"/>
<path class="rer-lid-bottom" d="M{R[0]} {R[1]} {LOWER_LID} L100 {L[1]} V300 H310 V{R[1]} Z" fill="{INK}" stroke="{BONE}" stroke-width="1.4"/>
</g>
</g>
<path d="{EYE}" fill="none" stroke="{BONE}" stroke-width="2.2"/>
<path d="M{L[0]} {L[1]} l-16 6" stroke="{BONE}" stroke-width="1.6" stroke-linecap="round"/>'''

def build():
    svg = f'''<svg class="rer-eye" viewBox="0 0 400 400" role="img" aria-label="Raven Eye Records" xmlns="http://www.w3.org/2000/svg">
<defs>
<radialGradient id="rer-iris" cx="50%" cy="50%" r="50%"><stop offset=".45" stop-color="#2a0204"/><stop offset=".7" stop-color="{BLOOD}"/><stop offset=".9" stop-color="#4a0507"/><stop offset="1" stop-color="#160102"/></radialGradient>
<linearGradient id="rer-shard" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1a1414"/><stop offset="1" stop-color="#060405"/></linearGradient>
<linearGradient id="rer-shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK}" stop-opacity=".9"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></linearGradient>
<filter id="rer-ink" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="9"/><feDisplacementMap in="SourceGraphic" scale="2.2"/></filter>
</defs>
<g filter="url(#rer-ink)">
{shards()}
{beak()}
</g>
{eye()}
<g filter="url(#rer-ink)">{brow()}</g>
</svg>'''
    return " ".join(svg.split("\n"))

if __name__ == "__main__":
    svg = build()
    (ROOT / "assets/js/logo.js").write_text(
        "/* Generated by scripts/build_logo.py. The Raven Eye logo. */\n"
        "window.RER_LOGO = " + json.dumps(svg) + ";\n", encoding="utf-8")
    static = svg.replace('class="rer-eye"', 'width="512" height="512"', 1)
    (ROOT / "assets/img/raven-eye.svg").write_text(static, encoding="utf-8")
    fav = svg.replace('class="rer-eye"', 'width="64" height="64"', 1).replace('viewBox="0 0 400 400"', 'viewBox="80 90 250 220"', 1)
    (ROOT / "assets/img/sigil.svg").write_text(fav, encoding="utf-8")
    print("logo: %d bytes" % len(svg))
