"""Empreinte digitale de type « boucle », générée par un champ de phase (crêtes lisses + minuties).

Modèle : motif = cos(phase), phase = continue (boucle + crêtes basses horizontales) + spirales
(une spirale ±1 crée une fin de crête ou une bifurcation, comme sur une vraie empreinte).
Les crêtes sont les zones où cos(phase) > seuil ; on en extrait les contours pour un SVG rempli.
Dessin entièrement original, sans image source.
"""
import math, json
import numpy as np
from skimage import measure
from shapely.geometry import LineString

RX, RY = 1.0, 1.34            # demi-axes de la pulpe (unités normalisées)
LAM = 0.072                   # écartement des crêtes
YC = -0.28                    # hauteur du noyau


def smoothstep(a, b, t):
    t = np.clip((t - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def dist_segment(x, y, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    t = np.clip(((x - ax) * vx + (y - ay) * vy) / (vx * vx + vy * vy), 0, 1)
    return np.hypot(x - (ax + t * vx), y - (ay + t * vy))


def field(n=900, seed=7, extra=()):
    rng = np.random.default_rng(seed)
    xs = np.linspace(-1.12, 1.12, n)
    ys = np.linspace(-1.48, 1.48, int(n * 1.48 / 1.12))
    X, Y = np.meshgrid(xs, ys)
    # 1) boucle : distance à un axe légèrement incliné (anse ouverte vers le bas, à droite)
    loop = dist_segment(X, Y, -0.02, YC, 0.16, YC + 0.42)
    # 2) crêtes basses : arcs presque horizontaux
    low = (Y - (YC + 0.42)) + 0.10 * X * X - 0.05 * X + 0.30
    w = smoothstep(YC + 0.25, YC + 0.95, Y + 0.18 * X)
    g = (1 - w) * loop + w * np.maximum(low, 0.02 + 0.5 * loop * 0)  # mélange progressif
    # légère ondulation organique, à basse fréquence
    g = g + 0.012 * np.sin(3.1 * X + 1.3) * np.cos(2.3 * Y) + 0.008 * np.sin(5.7 * Y + 2.0 * X)
    phase = 2 * np.pi * g / LAM
    # 3) minuties : spirales ±1 placées dans la pulpe
    minu = [(-0.46, -0.62, 1), (0.52, -0.30, -1), (-0.62, 0.10, 1), (0.38, 0.32, 1),
            (-0.20, 0.62, -1), (0.66, 0.70, 1), (-0.70, 0.78, -1), (0.12, -0.92, 1), (0.05, 0.98, -1)]
    for mx, my, s in list(minu) + list(extra):
        phase = phase + s * np.arctan2(Y - my, X - mx)
    img = np.cos(phase)
    # pulpe : super-ellipse un peu plus large en bas
    shape = (np.abs(X / RX) ** 2.0 + np.abs((Y - 0.03) / RY) ** 2.0)
    img = np.where(shape <= 1.0, img, -1.0)
    return xs, ys, img, minu


def ridges_paths(scale=110.0, level=0.42, tol=0.35, n=900, extra=()):
    xs, ys, img, minu = field(n, extra=extra)
    pad = np.pad(img, 1, constant_values=-1.0)
    cs = measure.find_contours(pad, level)
    dx = xs[1] - xs[0]
    out = []
    for c in cs:
        r, k = c[:, 0] - 1, c[:, 1] - 1
        px = (xs[0] + k * dx) * scale
        py = (ys[0] + r * dx) * scale
        if len(px) < 4:
            continue
        ls = LineString(np.column_stack([px, py])).simplify(tol)
        pts = list(ls.coords)
        if len(pts) < 3:
            continue
        # aire minuscule = poussière : on l'ignore
        a = 0.5 * abs(sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts))))
        if a < 2.0:
            continue
        out.append('M' + 'L'.join('%.1f %.1f' % p for p in pts) + 'Z')
    mins = [(mx * scale, my * scale) for mx, my, _ in minu]
    return ' '.join(out), mins


if __name__ == '__main__':
    d, mins = ridges_paths()
    json.dump({'d': d, 'minutiae': mins}, open('print_pro.json', 'w'))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="400" viewBox="-150 -200 300 400">'
           '<rect x="-150" y="-200" width="300" height="400" fill="#013781"/>'
           '<path d="%s" fill="#FFFFFF" fill-rule="evenodd"/>' % d
           + ''.join('<circle cx="%.1f" cy="%.1f" r="4" fill="none" stroke="#FCBA21" stroke-width="1.5"/>' % m for m in mins)
           + '</svg>')
    open('print_pro_test.svg', 'w').write(svg)
    print(len(d))
