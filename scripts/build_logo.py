#!/usr/bin/env python3
"""Generate the Raven Eye logo: a black metal raven clutching a bloody eyeball in its beak.

Usage: python3 scripts/build_logo.py

Writes:
  assets/js/logo.js         window.RER_LOGO (full emblem) and window.RER_MARK (cropped head)
  assets/img/raven-eye.svg  static full emblem
  assets/img/sigil.svg      static mark (favicon)

The raven is drawn in an ink style: a hand-placed head silhouette filled with hundreds of
jittered feather strokes that flow back from the beak, ragged black-metal tufts along the
outline, a hooked beak, and a narrowed, glowing eye whose lids the site animates. Every
line runs through an SVG displacement filter so it wobbles like hand-cut ink.
"""
import json, math, random, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BONE, INK, BLOOD = "#e8e0d0", "#050405", "#8f0c0e"

def f(x):
    return ("%.1f" % x).rstrip("0").rstrip(".")

# ---------- geometry (400 x 400 box, raven faces right) ----------
HEAD = [  # cubic segments of the head + neck silhouette
    ((60, 400), (70, 330), (85, 280), (100, 245)),      # back of neck
    ((100, 245), (110, 200), (118, 140), (150, 110)),   # back of head
    ((150, 110), (178, 86), (220, 90), (242, 118)),     # crown
    ((242, 118), (252, 132), (258, 142), (262, 150)),   # forehead to beak
    ((262, 150), (264, 175), (264, 200), (262, 222)),   # beak base
    ((262, 222), (250, 262), (232, 292), (226, 330)),   # throat
    ((226, 330), (222, 360), (230, 385), (242, 400)),   # chest
]
EYE = (207, 158)           # raven eye centre
BEAK_BASE = (266, 186)
BALL, BALL_R = (343, 236), 22

def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d for a, b, c, d in zip(p0, p1, p2, p3))

def head_path():
    d = "M%s %s" % tuple(map(f, HEAD[0][0]))
    for _, a, b, c in HEAD:
        d += " C%s %s %s %s %s %s" % tuple(map(f, a + b + c))
    return d + " L242 410 L50 410 Z"

def point_in_head(x, y, poly):
    inside = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside

def outline_points(step=60):
    pts = []
    for seg in HEAD:
        for i in range(step):
            pts.append(bez(*seg, i / step))
    pts += [(242, 410), (50, 410)]
    return pts

def feathers(poly, count):
    out = []
    bx, by = BEAK_BASE
    n = 0
    while n < count:
        x, y = random.uniform(55, 265), random.uniform(85, 400)
        if not point_in_head(x, y, poly):
            continue
        if math.hypot(x - EYE[0], (y - EYE[1]) * 1.6) < 20:
            continue  # keep the eye clear
        n += 1
        # tips point away from the beak, drooping as they go down the neck
        th = math.atan2(y - by, x - bx) + random.gauss(0, 0.14)
        th += 0.25 * max(0, (y - 220) / 180)
        ln = random.uniform(6, 13) * (1.25 if y > 250 else 1)
        bend = random.uniform(1, 3)
        ex, ey = x + ln * math.cos(th), y + ln * math.sin(th)
        nx, ny = -math.sin(th), math.cos(th)
        mx, my = (x + ex) / 2 + nx * bend, (y + ey) / 2 + ny * bend
        # light from the upper right: the crown and brow catch it, the neck falls to black
        lit = max(0.0, 1 - (y - 90) / 260) * (0.6 + 0.4 * (x - 60) / 205)
        r = random.random()
        if r < 0.12:
            col, op = "#7b5cc4", 0.25 + 0.5 * lit      # violet sheen
        elif r < 0.2:
            col, op = "#5a6fae", 0.2 + 0.4 * lit       # blue sheen
        elif r < 0.62:
            col, op = BONE, 0.05 + 0.45 * lit
        else:
            col, op = "#000", 0.6                       # dark cuts that break up the light
        out.append('<path d="M%s %sQ%s %s %s %s" stroke="%s" stroke-opacity="%s"/>'
                   % (f(x), f(y), f(mx), f(my), f(ex), f(ey), col, f(op)))
    return "".join(out)

def tufts(poly):
    """Ragged feather spikes bristling off the back of the head and the throat."""
    out = []
    for seg_i, seg in enumerate(HEAD):
        if seg_i in (3, 4):
            continue  # not on the forehead or beak base
        for i in range(26):
            t = random.random()
            x, y = bez(*seg, t)
            x2, y2 = bez(*seg, min(1, t + 0.01))
            tx, ty = x2 - x, y2 - y
            l = math.hypot(tx, ty) or 1
            nx, ny = ty / l, -tx / l               # outward normal on the back of the head
            if seg_i >= 5:
                nx, ny = -nx, -ny                  # throat runs the other way
            ln = random.uniform(8, 26) * (1.3 if seg_i in (1, 2) else 1)
            sweep = random.uniform(-0.6, 0.2) if seg_i < 5 else random.uniform(0.2, 0.9)
            ang = math.atan2(ny, nx) + sweep
            w = random.uniform(2, 5)
            ex, ey = x + ln * math.cos(ang), y + ln * math.sin(ang)
            px, py = -math.sin(ang) * w, math.cos(ang) * w
            out.append('<path d="M%s %s L%s %s L%s %s Z" fill="#070506"/>'
                       % (f(x + px), f(y + py), f(ex), f(ey), f(x - px), f(y - py)))
            if random.random() < 0.45:
                out.append('<path d="M%s %s L%s %s" stroke="%s" stroke-opacity="%s" stroke-width=".6"/>'
                           % (f(x), f(y), f(x + (ex - x) * .9), f(y + (ey - y) * .9), BONE, f(random.uniform(.1, .35))))
    return "".join(out)

def bristles():
    """Nasal bristles covering the base of the beak, pointing toward the tip."""
    out = []
    # dark feather spikes that break the line where the head meets the beak
    for _ in range(46):
        y = random.uniform(146, 226)
        x = 256 + random.uniform(-4, 4)
        th = math.radians(random.uniform(-4, 18) if y < 205 else random.uniform(10, 40))
        ln = random.uniform(14, 34) if y < 190 else random.uniform(8, 18)
        w = random.uniform(2, 4.5)
        ex, ey = x + ln * math.cos(th), y + ln * math.sin(th)
        px, py = -math.sin(th) * w, math.cos(th) * w
        out.append('<path d="M%s %s L%s %s L%s %s Z" fill="#070506" stroke="none"/>'
                   % (f(x + px), f(y + py), f(ex), f(ey), f(x - px), f(y - py)))
    for _ in range(130):
        x, y = random.uniform(244, 270), random.uniform(146, 188)
        th = math.radians(random.uniform(5, 22))
        ln = random.uniform(16, 34)
        ex, ey = x + ln * math.cos(th), y + ln * math.sin(th)
        out.append('<path d="M%s %sQ%s %s %s %s" stroke="%s" stroke-opacity="%s" stroke-width="%s"/>'
                   % (f(x), f(y), f((x + ex) / 2), f((y + ey) / 2 - 2), f(ex), f(ey),
                      random.choice((BONE, "#000", "#000")), f(random.uniform(.25, .7)), f(random.uniform(.5, 1.2))))
    return "".join(out)

def brow():
    """Heavy brow feathers slanting down toward the beak: the scowl."""
    out = []
    for _ in range(40):
        x = random.uniform(180, 236)
        y = 141 + (x - 180) * 0.2 + random.uniform(-5, 2)
        th = math.radians(random.uniform(8, 26))
        ln = random.uniform(8, 16)
        ex, ey = x + ln * math.cos(th), y + ln * math.sin(th)
        out.append('<path d="M%s %sQ%s %s %s %s" stroke="%s" stroke-opacity="%s" stroke-width="%s"/>'
                   % (f(x), f(y), f((x + ex) / 2), f((y + ey) / 2 - 1.5), f(ex), f(ey),
                      random.choice((BONE, "#000")), f(random.uniform(.3, .75)), f(random.uniform(.6, 1.3))))
    return "".join(out)

def beak_hatch():
    out = []
    for i in range(16):
        y0 = 156 + i * 3
        out.append('<path d="M%s %s Q%s %s %s %s"/>' % (f(268), f(y0), f(318), f(y0 + 4 + i * .8), f(352 - i * 1.5), f(y0 + 22 + i * .6)))
    return '<g stroke="%s" stroke-opacity=".09" stroke-width=".5" fill="none">%s</g>' % (BONE, "".join(out))

def veins():
    out = []
    cx, cy = BALL
    for _ in range(14):
        a = random.uniform(0, 2 * math.pi)
        x, y = cx + BALL_R * math.cos(a), cy + BALL_R * math.sin(a)
        d = "M%s %s" % (f(x), f(y))
        for _ in range(3):
            a2 = math.atan2(cy - y, cx - x) + random.gauss(0, .5)
            step = random.uniform(3, 6)
            x, y = x + step * math.cos(a2), y + step * math.sin(a2)
            if math.hypot(x - cx - 6, y - cy + 4) < 11:
                break
            d += " L%s %s" % (f(x), f(y))
        out.append('<path d="%s"/>' % d)
    return '<g stroke="#a0121a" stroke-opacity=".75" stroke-width=".6" fill="none" stroke-linejoin="round">%s</g>' % "".join(out)

def build(mark=False):
    random.seed(1914)
    poly = outline_points()
    feather_strokes = feathers(poly, 900 if mark else 1700)
    box = "176 118 200 200" if mark else "0 0 400 400"
    ex, ey = EYE
    bx, by = BALL
    svg = f'''<svg class="rer-eye rer-raven{" rer-mark" if mark else ""}" viewBox="{box}" style="--lid:9px" role="img" aria-label="Raven Eye Records" xmlns="http://www.w3.org/2000/svg">
<defs>
<filter id="rer-rough" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".05" numOctaves="2" seed="13"/><feDisplacementMap in="SourceGraphic" scale="2.6"/></filter>
<filter id="rer-smoke"><feTurbulence type="fractalNoise" baseFrequency=".012" numOctaves="4" seed="3"/><feColorMatrix values="0 0 0 0 .35  0 0 0 0 .05  0 0 0 0 .05  0 0 0 .9 -.25"/></filter>
<filter id="rer-glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="4"/></filter>
<radialGradient id="rer-moon" cx="66%" cy="30%" r="55%"><stop offset="0" stop-color="#5a0a0c" stop-opacity=".95"/><stop offset=".45" stop-color="#2a0506" stop-opacity=".7"/><stop offset="1" stop-color="#050405" stop-opacity="0"/></radialGradient>
<radialGradient id="rer-vignette" cx="50%" cy="50%" r="50%"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".9"/></radialGradient>
<linearGradient id="rer-beak" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a4850"/><stop offset=".35" stop-color="#1c1b20"/><stop offset="1" stop-color="#060507"/></linearGradient>
<radialGradient id="rer-ball" cx="62%" cy="38%" r="65%"><stop offset="0" stop-color="#f1e9dc"/><stop offset=".6" stop-color="#d9c4b4"/><stop offset=".9" stop-color="#9c6458"/><stop offset="1" stop-color="#4a1212"/></radialGradient>
<radialGradient id="rer-iris" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ff5a3c"/><stop offset=".45" stop-color="#d11a1f"/><stop offset="1" stop-color="#4a0306"/></radialGradient>
<radialGradient id="rer-dead" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#9fb4bf"/><stop offset=".8" stop-color="#55707e"/><stop offset="1" stop-color="#1d2a30"/></radialGradient>
<clipPath id="rer-disc"><circle cx="200" cy="200" r="196"/></clipPath>
<clipPath id="rer-head"><path d="{head_path()}"/></clipPath>
<clipPath id="rer-eyeball"><path d="M187 150 Q206 145 226 162 Q205 168 187 150 Z"/></clipPath>
</defs>
<g clip-path="url(#rer-disc)">
<rect width="400" height="400" fill="{INK}"/>
<rect width="400" height="400" filter="url(#rer-smoke)" opacity=".8"/>
<rect width="400" height="400" fill="url(#rer-moon)"/>
<g stroke="#000" stroke-linecap="round" fill="none" opacity=".9" filter="url(#rer-rough)">
<path d="M400 40 C360 60 340 58 318 80 M352 52 C350 36 360 26 372 18 M330 70 C322 58 326 44 318 34 M400 96 C376 100 364 112 350 108" stroke-width="2.4"/>
<path d="M0 60 C30 76 46 70 70 94 M34 72 C30 56 18 48 8 44 M52 84 C58 70 54 58 62 48" stroke-width="2.2"/>
</g>
<g filter="url(#rer-rough)">
<path d="{head_path()}" fill="#070506"/>
<g fill="none" stroke-linecap="round">{tufts(poly)}</g>
<g clip-path="url(#rer-head)" fill="none" stroke-linecap="round" stroke-width=".75">{feather_strokes}</g>
</g>
<g filter="url(#rer-rough)">
<path d="M258 212 C286 214 314 224 334 238 C318 250 290 246 258 234 Z" fill="url(#rer-beak)"/>
<path d="M262 216 C290 219 312 228 330 239" stroke="{BONE}" stroke-opacity=".3" stroke-width=".8" fill="none"/>
</g>
<g class="rer-prey" filter="url(#rer-rough)">
<path d="M{f(bx - 14)} {f(by + 16)} C{f(bx - 26)} {f(by + 40)} {f(bx - 6)} {f(by + 58)} {f(bx - 18)} {f(by + 86)} C{f(bx - 24)} {f(by + 100)} {f(bx - 14)} {f(by + 112)} {f(bx - 16)} {f(by + 124)}" stroke="#5a0709" stroke-width="5" fill="none" stroke-linecap="round"/>
<path d="M{f(bx - 14)} {f(by + 16)} C{f(bx - 26)} {f(by + 40)} {f(bx - 6)} {f(by + 58)} {f(bx - 18)} {f(by + 86)}" stroke="#c0262b" stroke-opacity=".5" stroke-width="1.3" fill="none"/>
<circle cx="{bx}" cy="{by}" r="{BALL_R}" fill="url(#rer-ball)"/>
{veins()}
<circle cx="{f(bx + 7)}" cy="{f(by - 4)}" r="10" fill="url(#rer-dead)"/>
<circle cx="{f(bx + 7)}" cy="{f(by - 4)}" r="10" fill="none" stroke="#0d1418" stroke-width="1.2"/>
<circle cx="{f(bx + 7)}" cy="{f(by - 4)}" r="4.3" fill="#020303"/>
<ellipse cx="{f(bx + 3)}" cy="{f(by - 9)}" rx="2.6" ry="1.7" fill="#fff" fill-opacity=".9"/>
<path d="M{f(bx - 20)} {f(by + 10)} C{f(bx - 12)} {f(by + 24)} {f(bx + 8)} {f(by + 26)} {f(bx + 18)} {f(by + 14)} C{f(bx + 10)} {f(by + 30)} {f(bx - 10)} {f(by + 30)} {f(bx - 20)} {f(by + 10)} Z" fill="{BLOOD}" fill-opacity=".95"/>
<path d="M{f(bx + 2)} {f(by + 24)} C{f(bx + 1)} {f(by + 38)} {f(bx + 6)} {f(by + 44)} {f(bx + 3)} {f(by + 52)} C{f(bx)} {f(by + 56)} {f(bx - 3)} {f(by + 50)} {f(bx - 1)} {f(by + 40)} Z" fill="{BLOOD}"/>
<path d="M{f(bx + 12)} {f(by + 20)} C{f(bx + 12)} {f(by + 30)} {f(bx + 15)} {f(by + 33)} {f(bx + 13)} {f(by + 38)} C{f(bx + 11)} {f(by + 40)} {f(bx + 9)} {f(by + 36)} {f(bx + 10)} {f(by + 30)} Z" fill="{BLOOD}"/>
<ellipse class="rer-drip" cx="{f(bx + 2)}" cy="{f(by + 60)}" rx="2.4" ry="3.6" fill="{BLOOD}"/>
</g>
<g filter="url(#rer-rough)">
<path d="M256 148 C300 146 346 164 372 200 C380 212 378 226 366 234 C364 222 354 214 334 210 C304 204 278 206 258 210 Z" fill="url(#rer-beak)"/>
{beak_hatch()}
<path d="M258 149 C302 147 346 166 371 201" stroke="{BONE}" stroke-opacity=".55" stroke-width="1.1" fill="none"/>
<path d="M366 234 C364 224 356 216 336 211" stroke="{BLOOD}" stroke-width="2.4" fill="none" stroke-linecap="round"/>
<path d="M362 230 C360 238 362 244 359 250" stroke="{BLOOD}" stroke-width="2" fill="none" stroke-linecap="round"/>
<g fill="none" stroke-linecap="round">{bristles()}</g>
</g>
<ellipse cx="{f(ex + 2)}" cy="{f(ey)}" rx="20" ry="9" fill="#c0141a" opacity=".55" filter="url(#rer-glow)" class="rer-eye-glow"/>
<g clip-path="url(#rer-eyeball)">
<rect x="180" y="140" width="52" height="34" fill="#1a0203"/>
<circle cx="{f(ex)}" cy="{f(ey - 1)}" r="9" fill="url(#rer-iris)"/>
<ellipse cx="{f(ex)}" cy="{f(ey - 1)}" rx="1.4" ry="7" fill="#000"/>
<circle cx="{f(ex - 4)}" cy="{f(ey - 4)}" r="1.3" fill="#fff" fill-opacity=".9"/>
<g class="rer-lid rer-lid-top" transform="translate(0 -9)"><path d="M178 132 L236 132 L236 158 Q206 148 178 150 Z" fill="#070506"/><path d="M186 150 Q206 146 228 161" stroke="{BONE}" stroke-opacity=".5" stroke-width=".8" fill="none"/></g>
<g class="rer-lid rer-lid-bottom" transform="translate(0 9)"><path d="M178 154 Q206 172 236 160 L236 180 L178 180 Z" fill="#070506"/></g>
</g>
<path d="M186 150 Q206 145 227 162 Q205 168 186 150 Z" fill="none" stroke="#000" stroke-width="1.6" filter="url(#rer-rough)"/>
<g fill="none" stroke-linecap="round" filter="url(#rer-rough)">{brow()}</g>
<rect width="400" height="400" fill="url(#rer-vignette)"/>
</g>
<circle cx="200" cy="200" r="196" fill="none" stroke="{BONE}" stroke-opacity=".25" stroke-width="1.5" filter="url(#rer-rough)"/>
</svg>'''
    return " ".join(svg.split("\n"))

if __name__ == "__main__":
    svg, mark = build(), build(mark=True)
    (ROOT / "assets/js/logo.js").write_text(
        "/* Generated by scripts/build_logo.py. The Raven Eye logo (full) and mark (small sizes). */\n"
        "window.RER_LOGO = " + json.dumps(svg) + ";\n"
        "window.RER_MARK = " + json.dumps(mark) + ";\n", encoding="utf-8")
    (ROOT / "assets/img/raven-eye.svg").write_text(svg.replace('class="rer-eye rer-raven"', 'width="512" height="512"', 1), encoding="utf-8")
    (ROOT / "assets/img/sigil.svg").write_text(mark.replace('class="rer-eye rer-raven rer-mark"', 'width="64" height="64"', 1), encoding="utf-8")
    print("logo: %d bytes, mark: %d bytes" % (len(svg), len(mark)))
