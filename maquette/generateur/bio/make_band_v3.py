"""Bandeau v3 : une seule empreinte réaliste (crêtes lisses), fondue dans le bleu ANID,
avec quelques minuties repérées en jaune ANID comme sur un relevé biométrique."""
import math, sys
import print_pro as P

W, H = 1440, 230
SCALE = 150.0                     # 1 unité normalisée = 150 px  -> empreinte ~ 400 px de haut
CX, CY, ROT = 1205.0, 92.0, -16.0  # centre de la pulpe, rotation en degrés
LEVEL = 0.62
EXTRA = ((0.05, -0.12, 1), (-0.62, -0.30, -1), (0.70, -0.05, 1))  # noyau + 2 minuties dans la partie visible
VISIBLE_Y = 100                   # sous cette hauteur, la première carte recouvre le bandeau (écran 1440)


def to_band(x, y):
    a = math.radians(ROT)
    return (CX + x * math.cos(a) - y * math.sin(a), CY + x * math.sin(a) + y * math.cos(a))


def build(opacity=0.2, show_minutiae=True):
    d, mins = P.ridges_paths(scale=SCALE, level=LEVEL, extra=EXTRA, tol=0.4)
    pts = [to_band(x, y) for x, y in mins] + [to_band(x * SCALE, y * SCALE) for x, y, _ in EXTRA[1:]]
    vis = [p for p in pts if 0 < p[1] < VISIBLE_Y - 8 and 900 < p[0] < W - 10]
    vis.sort(key=lambda p: p[0])
    defs = ('<defs>'
            '<radialGradient id="pulpe" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="152" gradientTransform="translate(%.0f %.0f) rotate(%.0f) scale(1 1.36)">'
            '<stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="0.45" stop-color="#fff" stop-opacity="1"/>'
            '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
            '<linearGradient id="gauche" x1="900" y1="0" x2="1160" y2="0" gradientUnits="userSpaceOnUse">'
            '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>'
            '<mask id="fondu" maskUnits="userSpaceOnUse" x="0" y="0" width="%d" height="%d">'
            '<rect width="%d" height="%d" fill="url(#pulpe)"/></mask>'
            '<mask id="fondu2" maskUnits="userSpaceOnUse" x="0" y="0" width="%d" height="%d">'
            '<rect width="%d" height="%d" fill="url(#gauche)"/></mask>'
            '</defs>') % (CX, CY, ROT, W, H, W, H, W, H, W, H)
    print_g = ('<g mask="url(#fondu2)"><g mask="url(#fondu)"><path transform="translate(%.1f %.1f) rotate(%.1f)" d="%s" '
               'fill="#FFFFFF" fill-opacity="%.2f" fill-rule="evenodd"/></g></g>') % (CX, CY, ROT, d, opacity)
    gold = ''
    if show_minutiae and len(vis) >= 2:
        line = 'M' + ' L'.join('%.1f %.1f' % p for p in vis)
        gold = ('<path d="%s" fill="none" stroke="#FCBA21" stroke-opacity="0.4" stroke-width="1"/>' % line
                + ''.join('<circle cx="%.1f" cy="%.1f" r="5" fill="none" stroke="#FCBA21" stroke-opacity="0.9" stroke-width="1.5"/>'
                          '<circle cx="%.1f" cy="%.1f" r="1.6" fill="#FCBA21"/>' % (x, y, x, y) for x, y in vis))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H)
           + defs + print_g + gold + '</svg>')
    return svg, pts, vis


if __name__ == '__main__':
    svg, pts, vis = build()
    open('bande-empreintes-v3.svg', 'w').write(svg)
    print(len(svg), 'minuties visibles :', [(round(x), round(y)) for x, y in vis])
    print('toutes :', [(round(x), round(y)) for x, y in pts])
