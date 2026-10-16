"""9 oct. : bleu adouci. Dernière couche du build, appliquée à toute la page.

Le marine de la charte #013781 (saturation 98 %) est remplacé par #1F4E8C,
plus doux et toujours à 8,3:1 sur blanc. Les pilules du bandeau (#1C4C94)
passent un ton au-dessus du bandeau pour rester visibles. Le bleu nuit des
textes (#071B35) et les bleus des graphiques ne changent pas.
"""
import re

NAVY = '#1F4E8C'
PILL = '#2D5E9E'
MAP = [
    (r'#013781\b', NAVY),
    (r'rgba\(\s*1\s*,\s*55\s*,\s*129\s*,', 'rgba(31,78,140,'),
    (r'#1C4C94\b', PILL),
]


def soften(html):
    for pat, new in MAP:
        html = re.sub(pat, new, html, flags=re.I)
    assert not re.search(r'#013781|rgba\(1,55,129', html, re.I)
    return html


def fix(name, html):
    return soften(html)
