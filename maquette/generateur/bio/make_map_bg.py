"""Fond de la carte du Togo (5 oct. 2026) : la même empreinte que le bandeau (print_pro), en crêtes bleu ANID très légères
sur blanc, fondue sur les bords, avec trois minuties cerclées de jaune reliées par un trait, comme dans le bandeau."""
import math
import print_pro as P

W, H = 400, 540
SCALE = 182.0
CX, CY, ROT = 200.0, 262.0, -8.0
LEVEL = 0.62
EXTRA = ((0.05, -0.12, 1), (-0.62, -0.30, -1), (0.70, -0.05, 1))


def to_box(x, y):
    a = math.radians(ROT)
    return (CX + x * math.cos(a) - y * math.sin(a), CY + x * math.sin(a) + y * math.cos(a))


def build(opacity=0.11):
    d, mins = P.ridges_paths(scale=SCALE, level=LEVEL, extra=EXTRA, tol=0.45)
    pts = [to_box(x, y) for x, y in mins] + [to_box(x * SCALE, y * SCALE) for x, y, _ in EXTRA[1:]]
    # minuties visibles autour du pays (le Togo occupe la bande centrale) : côté gauche et côté droit
    ok = [p for p in pts if 70 < p[1] < H - 70]
    left = sorted([p for p in ok if p[0] < 115], key=lambda p: p[1])
    right = sorted([p for p in ok if p[0] > 300], key=lambda p: p[1])
    pick = ([left[0]] if left else []) + ([right[len(right) // 2]] if right else []) + ([left[-1]] if len(left) > 1 else [])
    defs = ('<defs><radialGradient id="f" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="182" '
            'gradientTransform="translate(%.0f %.0f) rotate(%.0f) scale(1 1.36)">'
            '<stop offset="0" stop-color="#fff"/><stop offset="0.55" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
            '<mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="%d" height="%d"><rect width="%d" height="%d" fill="url(#f)"/></mask></defs>'
            ) % (CX, CY, ROT, W, H, W, H)
    g = ('<g mask="url(#m)"><path transform="translate(%.1f %.1f) rotate(%.1f)" d="%s" fill="#013781" fill-opacity="%.3f" fill-rule="evenodd"/></g>'
         % (CX, CY, ROT, d, opacity))
    gold = ''
    if len(pick) >= 2:
        gold = ('<path d="M%s" fill="none" stroke="#FCBA21" stroke-opacity="0.55" stroke-width="1"/>' % ' L'.join('%.1f %.1f' % p for p in pick)
                + ''.join('<circle cx="%.1f" cy="%.1f" r="5" fill="#fff" stroke="#E0A100" stroke-opacity="0.85" stroke-width="1.4"/>'
                          '<circle cx="%.1f" cy="%.1f" r="1.6" fill="#E0A100"/>' % (x, y, x, y) for x, y in pick))
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H) + defs + g + gold + '</svg>'
    return svg, pick


if __name__ == '__main__':
    svg, pick = build()
    open('fond-carte-empreinte.svg', 'w').write(svg)
    print(len(svg), [(round(x), round(y)) for x, y in pick])
