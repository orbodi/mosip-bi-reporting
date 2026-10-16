"""Motif d'empreintes digitales original (généré procéduralement), pour le fond de la maquette."""
import math, random

W, H = 60.0, 80.0          # demi-axes de la pulpe du doigt

def inside(x, y):
    return (x / W) ** 2 + ((y - 4) / H) ** 2 <= 1.0

def ridges(seed, n=17, sp=4.4):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        r = 5 + i * sp
        steps = max(40, int(r * 1.6))
        gaps = set()
        for _ in range(1 if i < 5 else 2):
            g = rnd.randrange(steps)
            gaps.update({g, (g + 1) % steps})
        seg, segs = [], []
        for k in range(steps + 1):
            t = 2 * math.pi * k / steps
            wob = 1 + 0.03 * math.sin(4 * t + i * 0.9 + seed) + 0.02 * math.sin(9 * t + seed)
            x = r * wob * math.cos(t) * 1.0
            y = r * wob * math.sin(t) * 1.22 - 8
            if y > 0:                                   # bas du doigt : crêtes plus plates
                y = y * (1 + 0.28 * min(1, y / 60))
            if i < 3 and math.sin(t) > 0.55:            # petite boucle ouverte au centre
                k_in = False
            else:
                k_in = inside(x, y) and (k % steps) not in gaps
            if k_in:
                seg.append((x, y))
            else:
                if len(seg) > 2: segs.append(seg)
                seg = []
        if len(seg) > 2: segs.append(seg)
        for s in segs:
            out.append('M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in s))
    # crêtes basses presque horizontales, sous le tourbillon
    for j in range(5):
        y0 = 62 + j * 4.2
        pts = [(x, y0 - 0.0035 * x * x + 1.5 * math.sin(x / 9 + j)) for x in [v * 2.0 for v in range(-30, 31)]]
        pts = [p for p in pts if inside(*p)]
        if len(pts) > 2:
            out.append('M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts))
    return ' '.join(out)

def fp(cx, cy, rot, scale, seed):
    return (f'<g transform="translate({cx} {cy}) rotate({rot}) scale({scale})"><path d="{ridges(seed)}" fill="none" '
            f'stroke="#013781" stroke-opacity="0.07" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></g>')

def brackets(cx, cy, w, h, L=16):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    d = (f'M{x0} {y0 + L} L{x0} {y0} L{x0 + L} {y0} M{x1 - L} {y0} L{x1} {y0} L{x1} {y0 + L} '
         f'M{x1} {y1 - L} L{x1} {y1} L{x1 - L} {y1} M{x0 + L} {y1} L{x0} {y1} L{x0} {y1 - L}')
    return f'<path d="{d}" fill="none" stroke="#FCBA21" stroke-opacity="0.3" stroke-width="2.5" stroke-linecap="round"/>'

S = 560
body = (fp(150, 160, -12, 1.15, 3) + brackets(150, 165, 175, 225)
        + fp(430, 430, 18, 0.85, 11) + fp(-130, 430, 18, 0.85, 11) + fp(430, -130, 18, 0.85, 11) + fp(-130, -130, 18, 0.85, 11))
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">{body}</svg>'
open('fond-empreintes.svg', 'w').write(svg)
print(len(svg))
