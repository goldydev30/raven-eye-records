#!/usr/bin/env python3
"""Generate the Raven Eye logo: a close-up of a raven's eye under a blood moon.

Usage: python3 scripts/build_logo.py

Writes:
  assets/js/logo.js         window.RER_LOGO, the inline SVG used on the homepage and About page
  assets/img/raven-eye.svg  static copy
  assets/img/sigil.svg      favicon

A black iris with a crimson rim reflects a red moon. Tiny head feathers ring the eye and
fade out into the page background, so the image has no edge. The eyelids are separate
groups; site.js closes them when the eye is hovered or tapped (.rer-eye.closed in style.css).
"""
import math, random, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
C, R = 200, 112          # centre and eyeball radius in a 400 x 400 box

def f(x):
    return ("%.1f" % x).rstrip("0").rstrip(".")

def P(r, a):
    return C + r * math.cos(a), C + r * math.sin(a)

def feathers(seed, base, sheen, sheen_rate, n=1500):
    """Tiny overlapping head feathers flowing around the eye toward the nape (right)."""
    random.seed(seed)
    out = []
    for _ in range(n):
        a = random.uniform(0, 2 * math.pi)
        r = math.sqrt(random.uniform((R + 26) ** 2, 205 ** 2))
        x, y = P(r, a)
        tang = a + math.pi / 2
        w = max(0, min(1, (190 - r) / 60))
        th = math.atan2(math.sin(tang) * w + math.sin(.12) * (1 - w), math.cos(tang) * w + math.cos(.12) * (1 - w))
        th += random.gauss(0, .15)
        ln = random.uniform(7, 15) * (.7 + (r - R) / 180)
        ex, ey = x + ln * math.cos(th), y + ln * math.sin(th)
        nx, ny = -math.sin(th), math.cos(th)
        mx, my = (x + ex) / 2 + nx * 2.2, (y + ey) / 2 + ny * 2.2
        lit = random.random()
        if lit < sheen_rate:
            col, op, sw = sheen, random.uniform(.35, .7), .9
        else:
            col, op, sw = base, random.uniform(.12, .45), random.uniform(.6, 1.1)
        out.append('<path d="M%s %sQ%s %s %s %s" stroke="%s" stroke-opacity="%s" stroke-width="%s"/>'
                   % (f(x), f(y), f(mx), f(my), f(ex), f(ey), col, f(op), f(sw)))
    return '<g fill="none" stroke-linecap="round">%s</g>' % "".join(out)

def skin_ring(seed, col):
    """Bare, wrinkled skin ring around the eye."""
    random.seed(seed)
    out = []
    for i in range(9):
        rr = R + 4 + i * 2.6
        a0 = random.uniform(0, 6.28)
        span = random.uniform(1.5, 4.5)
        x0, y0 = P(rr, a0); x1, y1 = P(rr, a0 + span)
        out.append('<path d="M%s %sA%s %s 0 %d 1 %s %s"/>' % (f(x0), f(y0), f(rr), f(rr), 1 if span > math.pi else 0, f(x1), f(y1)))
    return '<g fill="none" stroke="%s" stroke-opacity=".35" stroke-width=".7">%s</g>' % (col, "".join(out))

def iris_fibres(seed, col, op, pupil):
    random.seed(seed)
    out = []
    for i in range(360):
        a = i / 360 * 2 * math.pi + random.gauss(0, .006)
        r0 = pupil + random.uniform(0, 6)
        r1 = R - random.uniform(4, 22)
        x0, y0 = P(r0, a); x1, y1 = P(r1, a + random.gauss(0, .05))
        mx, my = P((r0 + r1) / 2, a + random.gauss(0, .04))
        out.append('<path d="M%s %sQ%s %s %s %s" stroke-opacity="%s"/>'
                   % (f(x0), f(y0), f(mx), f(my), f(x1), f(y1), f(random.uniform(op * .3, op))))
    # crypts: a ring of small dark flecks
    for _ in range(70):
        a = random.uniform(0, 6.28); r = random.uniform(pupil + 8, R - 14)
        x, y = P(r, a)
        out.append('<circle cx="%s" cy="%s" r="%s" fill="#000" fill-opacity=".35" stroke="none"/>' % (f(x), f(y), f(random.uniform(.8, 2.2))))
    return '<g fill="none" stroke="%s" stroke-width=".6">%s</g>' % (col, "".join(out))

def lids(skin, rim, seed):
    random.seed(seed)
    top_edge = "M60 %s Q200 %s 340 %s" % (f(C - R + 2), f(C - R + 42), f(C - R + 2))
    bot_edge = "M60 %s Q200 %s 340 %s" % (f(C + R - 4), f(C + R - 30), f(C + R - 4))
    top = "%s V-300 H60 Z" % top_edge
    bot = "%s V700 H60 Z" % bot_edge
    tex = []
    for _ in range(140):
        x = random.uniform(70, 330); y = random.uniform(10, C - R + 20)
        tex.append("M%s %sq5 3 10 1" % (f(x), f(y)))
    tex_b = []
    for _ in range(100):
        x = random.uniform(70, 330); y = random.uniform(C + R - 16, 390)
        tex_b.append("M%s %sq5 -3 10 -1" % (f(x), f(y)))
    return f'''<g class="rer-lid-bottom"><path d="{bot}" fill="{skin}"/><path d="{"".join(tex_b)}" fill="none" stroke="{rim}" stroke-opacity=".18" stroke-width=".6"/><path d="{bot_edge}" fill="none" stroke="{rim}" stroke-opacity=".5" stroke-width="1.6"/></g>
<g class="rer-lid-top"><path d="{top}" fill="{skin}"/><path d="{"".join(tex)}" fill="none" stroke="{rim}" stroke-opacity=".18" stroke-width=".6"/><path d="{top_edge}" fill="none" stroke="{rim}" stroke-opacity=".55" stroke-width="2"/><path d="{top_edge}" fill="none" stroke="#000" stroke-opacity=".6" stroke-width="7" transform="translate(0 -5)"/></g>'''

def blood_moon_reflection(p):
    return (f'<circle cx="176" cy="140" r="26" fill="url(#{p}-moon)" filter="url(#{p}-soft)"/>'
            f'<circle cx="168" cy="132" r="4" fill="#fff" fill-opacity=".85" filter="url(#{p}-soft)"/>'
            f'<circle cx="250" cy="256" r="3.5" fill="#ff8a7a" fill-opacity=".45" filter="url(#{p}-soft)"/>')

VARIANTS = {
    "bloodmoon": dict(
        bg="#050304", feather="#8f8686", sheen="#8a1a1c", sheen_rate=.07, skin="#0b0809", rim="#a99",
        iris=[(0, "#000"), (.4, "#030102"), (.7, "#0b0405"), (.86, "#1a0506"), (.94, "#7a0c10"), (1, "#1a0203")],
        fibre="#9a1d21", fibre_op=.16, pupil=50, limbal="#3a0507", reflection=blood_moon_reflection),
}

def build(name):
    v = VARIANTS[name]
    p = "rer-" + name
    stops = "".join('<stop offset="%s" stop-color="%s"/>' % (o, c) for o, c in v["iris"])
    seed = sum(map(ord, name))
    return f'''<svg class="rer-eye" viewBox="0 0 400 400" role="img" aria-label="Raven Eye Records" xmlns="http://www.w3.org/2000/svg">
<defs>
<radialGradient id="{p}-iris" cx="50%" cy="50%" r="50%">{stops}</radialGradient>
<radialGradient id="{p}-gloss" cx="35%" cy="25%" r="70%"><stop offset="0" stop-color="#fff" stop-opacity=".16"/><stop offset=".5" stop-color="#fff" stop-opacity=".03"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<radialGradient id="{p}-shade" cx="50%" cy="50%" r="50%"><stop offset=".78" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".85"/></radialGradient>
<radialGradient id="{p}-fade" cx="50%" cy="50%" r="50%"><stop offset=".72" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<radialGradient id="{p}-moon"><stop offset="0" stop-color="#ff9a6a" stop-opacity=".95"/><stop offset=".6" stop-color="#c0221c" stop-opacity=".8"/><stop offset="1" stop-color="#6e0b0e" stop-opacity="0"/></radialGradient>
<filter id="{p}-soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.4"/></filter>
<filter id="{p}-blur" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="3"/></filter>
<mask id="{p}-mask"><circle cx="{C}" cy="{C}" r="200" fill="url(#{p}-fade)"/></mask>
<clipPath id="{p}-ball"><circle cx="{C}" cy="{C}" r="{R}"/></clipPath>
<clipPath id="{p}-lidclip"><circle cx="{C}" cy="{C}" r="{R + 3}"/></clipPath>
</defs>
<g mask="url(#{p}-mask)">{feathers(seed, v["feather"], v["sheen"], v["sheen_rate"])}</g>
<circle cx="{C}" cy="{C}" r="{R + 22}" fill="{v["skin"]}" filter="url(#{p}-blur)"/>
{skin_ring(seed, v["rim"])}
<g clip-path="url(#{p}-ball)">
<circle cx="{C}" cy="{C}" r="{R}" fill="url(#{p}-iris)"/>
{iris_fibres(seed, v["fibre"], v["fibre_op"], v["pupil"])}
<circle cx="{C}" cy="{C}" r="{v["pupil"]}" fill="#000" filter="url(#{p}-soft)"/>
<circle cx="{C}" cy="{C}" r="{R - 3}" fill="none" stroke="{v["limbal"]}" stroke-width="12" filter="url(#{p}-blur)"/>
<circle cx="{C}" cy="{C}" r="{R}" fill="url(#{p}-shade)"/>
{v["reflection"](p)}
<circle cx="{C}" cy="{C}" r="{R}" fill="url(#{p}-gloss)"/>
</g>
<g clip-path="url(#{p}-lidclip)">{lids(v["skin"], v["rim"], seed)}</g>
</svg>'''.replace("\n", " ")

if __name__ == "__main__":
    svg = build("bloodmoon")
    (ROOT / "assets/js/logo.js").write_text(
        "/* Generated by scripts/build_logo.py. The Raven Eye logo. */\n"
        "window.RER_LOGO = " + json.dumps(svg) + ";\n", encoding="utf-8")
    (ROOT / "assets/img/raven-eye.svg").write_text(svg.replace('class="rer-eye"', 'width="512" height="512"', 1), encoding="utf-8")
    fav = svg.replace('class="rer-eye"', 'width="64" height="64"', 1).replace('viewBox="0 0 400 400"', 'viewBox="70 70 260 260"', 1)
    (ROOT / "assets/img/sigil.svg").write_text(fav, encoding="utf-8")
    print("logo: %d bytes" % len(svg))
