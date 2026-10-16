#!/usr/bin/env python3
"""Generate the Raven Eye logo: a close-up raven's eye in a woodcut / ink-engraving style.

Usage: python3 scripts/build_logo.py

Writes:
  assets/js/logo.js       window.RER_LOGO, the animated inline SVG used across the site
  assets/img/raven-eye.svg  a static copy (favicon, social images)

Feathers are drawn as hundreds of short jittered ink strokes that flow back from the beak
and swirl around the eye, then roughened with an SVG displacement filter so every line
wobbles like a hand-cut block. The eyelids are separate groups the site animates.
"""
import json, math, random, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
random.seed(1914)  # fixed seed: the drawing is the same on every build

CX, CY, R_EYE = 100, 100, 30   # eye centre and radius in a 200x200 box
BONE, INK = "#e8e0d0", "#050405"

def f(x):
    return ("%.1f" % x).rstrip("0").rstrip(".")

def flow(x, y):
    """Feather direction: sweep from beak (left) to nape (right), curling around the eye."""
    dx, dy = x - CX, y - CY
    d = math.hypot(dx, dy) or 1
    swirl = math.atan2(dy, dx) + math.pi / 2          # tangent around the eye
    back = math.radians(8)                            # general backward sweep
    w = max(0.0, min(1.0, (70 - d) / 45))             # closer to the eye => more swirl
    ax = math.cos(swirl) * w + math.cos(back) * (1 - w)
    ay = math.sin(swirl) * w + math.sin(back) * (1 - w)
    return math.atan2(ay, ax)

def feather_strokes(count=1400, rmax=97, bristles=True):
    out = []
    # Overlapping scallops: each "feather" is a small arc whose tip points along the flow.
    for _ in range(count):
        a = random.uniform(0, 2 * math.pi)
        r = math.sqrt(random.uniform((R_EYE + 13) ** 2, rmax ** 2))
        x, y = CX + r * math.cos(a), CY + r * math.sin(a)
        th = flow(x, y) + random.gauss(0, 0.12)
        ln = random.uniform(5, 11) * (0.75 + r / 160)
        bend = random.uniform(1.2, 3.2) * random.choice((1, 1))
        ex, ey = x + ln * math.cos(th), y + ln * math.sin(th)
        nx, ny = -math.sin(th), math.cos(th)
        mx, my = (x + ex) / 2 + nx * bend, (y + ey) / 2 + ny * bend
        # outer feathers fade, a few catch the light (the raven's blue-violet sheen)
        light = random.random()
        near = 1 - (r - R_EYE) / (97 - R_EYE)
        if light < 0.07:
            col, op, w = "#8797c4", 0.5, 0.8
        elif light < 0.6:
            col, op, w = BONE, 0.22 + 0.5 * near, 0.75
        else:
            col, op, w = BONE, 0.08 + 0.22 * near, 0.55
        out.append('<path d="M%s %sQ%s %s %s %s" stroke="%s" stroke-opacity="%s" stroke-width="%s"/>'
                   % (f(x), f(y), f(mx), f(my), f(ex), f(ey), col, f(op), w))
    # rictal bristles: long stiff hairs sweeping from the beak (lower left) toward the eye
    for _ in range(70 if bristles else 0):
        x = random.uniform(2, 40); y = random.uniform(125, 185)
        th = math.radians(random.uniform(-40, -18))
        ln = random.uniform(18, 34)
        ex, ey = x + ln * math.cos(th), y + ln * math.sin(th)
        out.append('<path d="M%s %sQ%s %s %s %s" stroke="%s" stroke-opacity="%s" stroke-width=".6"/>'
                   % (f(x), f(y), f((x + ex) / 2), f((y + ey) / 2 + 2), f(ex), f(ey), BONE, f(random.uniform(.15, .4))))
    return "".join(out)

def ring_hatch():
    """Bare skin ring around the eye: dense short radial cuts."""
    out = []
    for i in range(140):
        a = i / 140 * 2 * math.pi + random.gauss(0, 0.01)
        r1 = R_EYE + random.uniform(1.5, 3)
        r2 = R_EYE + random.uniform(7, 11)
        out.append('<path d="M%s %sL%s %s"/>' % (f(CX + r1 * math.cos(a)), f(CY + r1 * math.sin(a)),
                                                f(CX + r2 * math.cos(a)), f(CY + r2 * math.sin(a))))
    return '<g stroke="%s" stroke-opacity=".32" stroke-width=".5">%s</g>' % (BONE, "".join(out))

def iris_fibres():
    out = []
    for i in range(90):
        a = i / 90 * 2 * math.pi + random.gauss(0, 0.02)
        r1, r2 = random.uniform(13, 16), random.uniform(24, R_EYE - 1)
        out.append('<path d="M%s %sL%s %s"/>' % (f(CX + r1 * math.cos(a)), f(CY + r1 * math.sin(a)),
                                                f(CX + r2 * math.cos(a)), f(CY + r2 * math.sin(a))))
    return '<g stroke="#7a4a2c" stroke-opacity=".13" stroke-width=".4">%s</g>' % "".join(out)

def lid(top):
    """An eyelid: an ink-dark shape with engraved lines following its curved edge."""
    s = -1 if top else 1
    # Covers a full half of the eye plus margin; its leading edge is a gentle curve.
    edge_y = CY
    far_y = CY + s * (R_EYE + 14)
    body = ('<path d="M%s %s Q%s %s %s %s L%s %s L%s %s Z" fill="#0b0809"/>'
            % (f(CX - R_EYE - 6), f(edge_y), f(CX), f(edge_y + (8 if top else -5)),
               f(CX + R_EYE + 6), f(edge_y), f(CX + R_EYE + 6), f(far_y), f(CX - R_EYE - 6), f(far_y)))
    lines = []
    for k in range(1, 8):
        off = s * k * 3.4
        lines.append('<path d="M%s %s Q%s %s %s %s"/>'
                     % (f(CX - R_EYE - 4), f(edge_y + off), f(CX), f(edge_y + off + (8 if top else -5) * (1 - k / 9)),
                        f(CX + R_EYE + 4), f(edge_y + off)))
    # small feathers on the lid itself, flowing away from the rim
    for _ in range(60):
        x = random.uniform(CX - R_EYE, CX + R_EYE)
        y = edge_y + s * random.uniform(4, R_EYE + 8)
        th = math.radians(random.uniform(-15, 15)) + (0 if random.random() < .5 else math.pi)
        ln = random.uniform(4, 8)
        ex, ey = x + ln * math.cos(th), y + ln * math.sin(th) + s * 1.5
        lines.append('<path d="M%s %sQ%s %s %s %s" stroke-opacity="%s"/>' % (f(x), f(y), f((x + ex) / 2), f((y + ey) / 2 - s * 1.6), f(ex), f(ey), f(random.uniform(.15, .4))))
    hatch = '<g stroke="%s" stroke-opacity=".12" stroke-width=".55" fill="none" stroke-linecap="round">%s</g>' % (BONE, "".join(lines))
    rim = ('<path d="M%s %s Q%s %s %s %s" stroke="%s" stroke-opacity=".75" stroke-width="1.3" fill="none"/>'
           % (f(CX - R_EYE - 6), f(edge_y), f(CX), f(edge_y + (8 if top else -5)), f(CX + R_EYE + 6), f(edge_y), BONE))
    return body + hatch + rim

def build(mark=False):
    random.seed(1914)
    feathers = feather_strokes(380, 60, False) if mark else feather_strokes()
    box = "52 52 96 96" if mark else "0 0 200 200"
    svg = f'''<svg class="rer-eye{" rer-mark" if mark else ""}" viewBox="{box}" role="img" aria-label="Raven Eye Records" xmlns="http://www.w3.org/2000/svg">
<defs>
<filter id="rer-rough" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".06" numOctaves="2" seed="7"/><feDisplacementMap in="SourceGraphic" scale="2.2"/></filter>
<radialGradient id="rer-iris" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#000"/><stop offset=".6" stop-color="#070303"/><stop offset=".9" stop-color="#140906"/><stop offset=".97" stop-color="#26130a"/><stop offset="1" stop-color="#0a0504"/></radialGradient>
<radialGradient id="rer-vignette" cx="50%" cy="50%" r="50%"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".85"/></radialGradient>
<clipPath id="rer-disc"><circle cx="100" cy="100" r="98"/></clipPath>
<clipPath id="rer-eyeball"><circle cx="{CX}" cy="{CY}" r="{R_EYE}"/></clipPath>
</defs>
<g clip-path="url(#rer-disc)">
<rect width="200" height="200" fill="{INK}"/>
<g fill="none" stroke-linecap="round" filter="url(#rer-rough)">{feathers}</g>
<circle cx="100" cy="100" r="98" fill="url(#rer-vignette)"/>
</g>
<g filter="url(#rer-rough)">
<circle cx="{CX}" cy="{CY}" r="{R_EYE + 11}" fill="#0a0708"/>
{ring_hatch()}
<circle cx="{CX}" cy="{CY}" r="{R_EYE + 1.2}" fill="none" stroke="{BONE}" stroke-opacity=".55" stroke-width="1.1"/>
</g>
<g clip-path="url(#rer-eyeball)">
<g class="rer-eye-iris">
<circle cx="{CX}" cy="{CY}" r="{R_EYE}" fill="url(#rer-iris)"/>
{iris_fibres()}
<circle class="rer-eye-pupil" cx="{CX}" cy="{CY}" r="13" fill="#000"/>
<ellipse cx="{CX - 10}" cy="{CY - 11}" rx="5.2" ry="3.6" transform="rotate(-30 {CX - 10} {CY - 11})" fill="{BONE}" fill-opacity=".9"/>
<circle cx="{CX + 9}" cy="{CY + 10}" r="1.7" fill="#c21d22" fill-opacity=".55"/>
</g>
<g class="rer-lid rer-lid-top" transform="translate(0 -44)" filter="url(#rer-rough)">{lid(True)}</g>
<g class="rer-lid rer-lid-bottom" transform="translate(0 44)" filter="url(#rer-rough)">{lid(False)}</g>
</g>
</svg>'''
    return " ".join(svg.split("\n"))

if __name__ == "__main__":
    svg, mark = build(), build(mark=True)
    (ROOT / "assets/js/logo.js").write_text(
        "/* Generated by scripts/build_logo.py. The animated Raven Eye logo (full) and mark (small sizes). */\n"
        "window.RER_LOGO = " + json.dumps(svg) + ";\n"
        "window.RER_MARK = " + json.dumps(mark) + ";\n", encoding="utf-8")
    (ROOT / "assets/img/raven-eye.svg").write_text(svg.replace('class="rer-eye"', 'width="512" height="512"', 1), encoding="utf-8")
    (ROOT / "assets/img/sigil.svg").write_text(mark.replace('class="rer-eye rer-mark"', 'width="64" height="64"', 1), encoding="utf-8")
    print("logo: %d bytes, mark: %d bytes" % (len(svg), len(mark)))
