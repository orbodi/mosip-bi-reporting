"""Option A améliorée : parcours en flux, pertes qui se détachent vers le bas (SVG statique, 1232 px)."""

def nf(n):
    return f'{n:,}'.replace(',', ' ')


def pc(x):
    return f'{x:.1f}'.replace('.', ',') + ' %'


INS, PRE, NIU, DEM, IMP, LIV = 3278239, 606850, 3058886, 3113431, 3101590, 1770796
EC, ECH, REJ = 123639, 9218, 86496
DATT, DREJ = 11835, 6
REM = IMP - LIV

NAVY, MUTED, LINE = '#071B35', '#4B5A6E', '#DCE3E9'
NODE = ['#86B6EF', '#5598E7', '#2A78D6', '#1C5CAB', '#104281']
AMBER, ORANGE, RED = '#FAB219', '#EC835A', '#D03B3B'

W, TOP, H0, NW = 1232, 92, 150.0, 12
XS = [176, 436, 696, 956, W - NW]


def ico(kind, x, y, color):
    """Petites icônes d'état (14 px) : l'état n'est jamais porté par la couleur seule."""
    if kind == 'clock':
        return (f'<g transform="translate({x} {y})" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round">'
                f'<circle cx="7" cy="7" r="6"/><path d="M7 3.5 V7 L9.5 8.5"/></g>')
    if kind == 'x':
        return (f'<g transform="translate({x} {y})" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round">'
                f'<circle cx="7" cy="7" r="6"/><path d="M4.8 4.8 L9.2 9.2 M9.2 4.8 L4.8 9.2"/></g>')
    if kind == 'ban':
        return (f'<g transform="translate({x} {y})" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round">'
                f'<circle cx="7" cy="7" r="6"/><path d="M2.8 11.2 L11.2 2.8"/></g>')
    return f'<path transform="translate({x} {y})" d="M7 0.8 L13.6 12.8 H0.4 Z" fill="{color}"/>'


def svg():
    vals = [INS, NIU, DEM, IMP, LIV]
    names = [['Inscriptions'], ['NIU générés'], ['Demandes', 'd’impression'], ['Cartes imprimées', 'et expédiées'], ['Cartes livrées']]
    h = [v / INS * H0 for v in vals]
    o = []

    def head(x, lines, value, anchor='start'):
        y0 = TOP - 34 - 17 * (len(lines) - 1)
        t = ''.join(f'<text x="{x}" y="{y0 + 17 * k}" text-anchor="{anchor}" font-size="12.5" font-weight="500" fill="{MUTED}">{ln}</text>'
                    for k, ln in enumerate(lines))
        return t + f'<text x="{x}" y="{TOP - 12}" text-anchor="{anchor}" font-size="19" font-weight="600" fill="{NAVY}">{value}</text>'

    # pré-inscriptions : affluent facultatif (contour pointillé)
    hp = PRE / INS * H0
    o.append(f'<path d="M24 {TOP} L{XS[0]} {TOP} L{XS[0]} {TOP + hp:.1f} L24 {TOP + hp:.1f} Z" fill="#B4BFCB" fill-opacity="0.5"><title>Pré-inscriptions en ligne : {nf(PRE)} (étape facultative)</title></path>')
    o.append(head(24, ['Pré-inscriptions'], nf(PRE)))
    o.append(f'<text x="24" y="{TOP + hp + 18:.1f}" font-size="12" fill="{MUTED}">Étape facultative</text>')

    # bandes principales + taux de passage
    for i in range(4):
        x0, x1 = XS[i] + NW, XS[i + 1]
        a, b = h[i], h[i + 1]
        keep = min(a, b)
        mx = (x0 + x1) / 2
        o.append(f'<path d="M{x0} {TOP} L{x1} {TOP} L{x1} {TOP + b:.1f} C {mx} {TOP + b:.1f} {mx} {TOP + keep:.1f} {x0} {TOP + keep:.1f} Z" '
                 f'fill="{NODE[i + 1]}" fill-opacity="0.22"><title>{" ".join(names[i])} → {" ".join(names[i + 1])} : {nf(vals[i + 1])}</title></path>')
        rate = vals[i + 1] / vals[i] * 100
        drop = rate < 80
        pw = 72 if drop else 64
        px, py = mx - pw / 2, TOP + min(keep, b) / 2 - 13
        bg, fg, bd = ('#FCEBEB', '#8A1F1F', '#F2C4C4') if drop else ('#FFFFFF', NAVY, LINE)
        arrow = (f'<path d="M{px + 10} {py + 10} l4 6 l4 -6" fill="none" stroke="{fg}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
                 if drop else '')
        o.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="{pw}" height="26" rx="13" fill="{bg}" stroke="{bd}"/>{arrow}'
                 f'<text x="{px + pw / 2 + (7 if drop else 0):.1f}" y="{py + 17.5:.1f}" text-anchor="middle" font-size="12.5" font-weight="600" fill="{fg}">{pc(rate)}</text>')
    # noeuds + en-têtes
    for i, x in enumerate(XS):
        o.append(f'<rect x="{x}" y="{TOP}" width="{NW}" height="{h[i]:.1f}" rx="2" fill="{NODE[i]}"><title>{" ".join(names[i])} : {nf(vals[i])}</title></rect>')
        last = i == 4
        o.append(head(x + (NW if last else 0), names[i], nf(vals[i]), 'end' if last else 'start'))

    # pertes : rubans qui descendent vers une étiquette
    Y_END = TOP + H0 + 58

    def ribbon(x_from, y_bottom, t, color, x_to, tip):
        t = max(t, 1.6)
        y_top = y_bottom - t
        d = (f'M{x_from} {y_top:.1f} C {x_to + t:.1f} {y_top:.1f} {x_to + t:.1f} {y_top:.1f} {x_to + t:.1f} {Y_END} '
             f'L {x_to:.1f} {Y_END} C {x_to:.1f} {y_bottom:.1f} {x_to:.1f} {y_bottom:.1f} {x_from} {y_bottom:.1f} Z')
        o.append(f'<path d="{d}" fill="{color}"><title>{tip}</title></path>')
        return t

    def card(x, y, title, rows, width):
        rh = 22
        o.append(f'<text x="{x}" y="{y + 16}" font-size="12.5" font-weight="600" fill="{NAVY}">{title}</text>')
        for k, (kind, color, lab, val, extra) in enumerate(rows):
            yy = y + 28 + k * rh
            o.append(ico(kind, x, yy, color))
            o.append(f'<text x="{x + 22}" y="{yy + 11.5}" font-size="12.5" fill="{MUTED}">{lab}</text>')
            o.append(f'<text x="{x + width}" y="{yy + 11.5}" text-anchor="end" font-size="13" font-weight="600" fill="{NAVY}">{val}</text>')
            if extra:
                o.append(f'<text x="{x + width + 10}" y="{yy + 11.5}" font-size="12" fill="{MUTED}">{extra}</text>')

    # 1) inscriptions sans NIU
    x0, yb = XS[0] + NW, TOP + h[0]
    t1 = ribbon(x0, yb, REJ / INS * H0, RED, XS[0] + 30, f'Paquets rejetés : {nf(REJ)}')
    t2 = ribbon(x0, yb - t1, ECH / INS * H0, ORANGE, XS[0] + 40, f'Paquets échoués : {nf(ECH)}')
    ribbon(x0, yb - t1 - t2, EC / INS * H0, AMBER, XS[0] + 48, f'Paquets en cours de traitement : {nf(EC)}')
    card(XS[0] + 26, Y_END + 6, f'{nf(EC + ECH + REJ)} inscriptions sans NIU', [
        ('clock', '#B07A00', 'En cours de traitement', nf(EC), pc(EC / INS * 100)),
        ('x', ORANGE, 'Échoués', nf(ECH), pc(ECH / INS * 100)),
        ('ban', RED, 'Rejetés', nf(REJ), pc(REJ / INS * 100)),
    ], 250)
    # 2) demandes non imprimées
    x0, yb = XS[2] + NW, TOP + h[2]
    t1 = ribbon(x0, yb, DREJ / INS * H0, RED, XS[2] + 30, f'Demandes d’impression rejetées : {nf(DREJ)}')
    ribbon(x0, yb - t1, DATT / INS * H0, AMBER, XS[2] + 40, f'Demandes en attente d’impression : {nf(DATT)}')
    card(XS[2] + 26, Y_END + 6, f'{nf(DATT + DREJ)} demandes non imprimées', [
        ('clock', '#B07A00', 'En attente d’impression', nf(DATT), ''),
        ('ban', RED, 'Rejetées', nf(DREJ), ''),
    ], 236)
    # 3) cartes à remettre (la perte principale)
    x0, yb = XS[3] + NW, TOP + h[3]
    t = REM / INS * H0
    ribbon(x0, yb, t, AMBER, XS[3] + 34, f'Cartes expédiées non remises : {nf(REM)}')
    cx, cy = XS[3] + 34, Y_END + 6
    o.append(ico('warn', cx, cy + 4, '#EC835A'))
    o.append(f'<text x="{cx + 22}" y="{cy + 16}" font-size="12.5" font-weight="600" fill="{NAVY}">Cartes à remettre</text>'
             f'<text x="{cx}" y="{cy + 44}" font-size="24" font-weight="600" fill="{NAVY}">{nf(REM)}</text>'
             f'<text x="{cx}" y="{cy + 64}" font-size="12.5" fill="{MUTED}">{pc(REM / IMP * 100)} des cartes expédiées</text>')

    HT = Y_END + 6 + 28 + 3 * 22 + 8
    return (f'<svg viewBox="0 0 {W} {HT}" role="img" aria-label="Parcours du citoyen : {nf(INS)} inscriptions, {nf(NIU)} NIU générés, '
            f'{nf(DEM)} demandes d’impression, {nf(IMP)} cartes imprimées et expédiées, {nf(LIV)} cartes livrées ; {nf(REM)} cartes restent à remettre." '
            f'style="display: block; width: 100%; height: auto; font-family: Poppins, sans-serif">' + ''.join(o) + '</svg>')


if __name__ == '__main__':
    print(len(svg()))


def rows_html():
    """Version mobile et tablette : une ligne par étape, pertes en retrait (base = inscriptions)."""
    icons = {
        'clock': '<svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true" style="flex-shrink: 0"><g fill="none" stroke="#B07A00" stroke-width="1.8" stroke-linecap="round"><circle cx="7" cy="7" r="6"></circle><path d="M7 3.5 V7 L9.5 8.5"></path></g></svg>',
        'x': '<svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true" style="flex-shrink: 0"><g fill="none" stroke="#EC835A" stroke-width="1.8" stroke-linecap="round"><circle cx="7" cy="7" r="6"></circle><path d="M4.8 4.8 L9.2 9.2 M9.2 4.8 L4.8 9.2"></path></g></svg>',
        'ban': '<svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true" style="flex-shrink: 0"><g fill="none" stroke="#D03B3B" stroke-width="1.8" stroke-linecap="round"><circle cx="7" cy="7" r="6"></circle><path d="M2.8 11.2 L11.2 2.8"></path></g></svg>',
        'warn': '<svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true" style="flex-shrink: 0"><path d="M7 0.8 L13.6 12.8 H0.4 Z" fill="#EC835A"></path></svg>',
    }
    rows = [
        ('Pré-inscriptions', PRE, '#B4BFCB', None),
        ('Inscriptions', INS, NODE[0], None),
        ('En cours de traitement', EC, AMBER, 'clock'),
        ('Échoués', ECH, ORANGE, 'x'),
        ('Rejetés', REJ, RED, 'ban'),
        ('NIU générés', NIU, NODE[1], None),
        ('Demandes d’impression', DEM, NODE[2], None),
        ('En attente d’impression', DATT, AMBER, 'clock'),
        ('Rejetées', DREJ, RED, 'ban'),
        ('Cartes imprimées et expédiées', IMP, NODE[3], None),
        ('Cartes livrées', LIV, NODE[4], None),
        ('Cartes à remettre', REM, AMBER, 'warn'),
    ]
    out = ['<div class="parcours-lignes" role="table" aria-label="Parcours du citoyen" style="flex-direction: column; font-variant-numeric: tabular-nums">']
    for lab, v, col, ic in rows:
        sub = ic is not None
        pad = '18px' if sub else '0'
        share = pc(v / INS * 100) if v >= 1000 else '&lt; 0,1 %'
        w = max(0.6, v / INS * 100)
        out.append(
            f'<div role="row" style="display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: 4px 12px; padding: 8px 0 8px {pad}; border-top: 1px solid #EEF2F5">'
            f'<span role="rowheader" style="display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: {400 if sub else 600}; color: {MUTED if sub else NAVY}">'
            f'{icons[ic] if sub else ""}{lab}</span>'
            f'<span role="cell" style="text-align: right; white-space: nowrap"><strong style="font-weight: 600; color: {NAVY}">{nf(v)}</strong>'
            f' <span style="font-size: 12px; color: {MUTED}">{share}</span></span>'
            f'<span aria-hidden="true" style="grid-column: 1 / -1; height: 8px; background: #EEF2F5; border-radius: 0 4px 4px 0">'
            f'<span style="display: block; height: 8px; width: {w:.1f}%; background: {col}; border-radius: 0 4px 4px 0"></span></span>'
            '</div>')
    out.append('</div>')
    return '\n'.join(out)


def svg_simple(v2=False):
    """Format retenu le 2 oct. 2026 : l'esquisse A (sans pastilles de taux ni encadrés de pertes)."""
    H0, top, nw = 140.0, 74.0, 12
    BLUES = ['#86B6EF', '#5598E7', '#2A78D6', '#1C5CAB', '#104281']
    xs = [170, 420, 670, 920, 1170]
    vals = [INS, NIU, DEM, IMP, LIV]
    names = [['Inscriptions'], ['NIU générés'], ['Demandes', 'd’impression'], ['Cartes imprimées', 'et expédiées'], ['Cartes livrées']]
    h = [v / INS * H0 for v in vals]
    out = []
    hp = PRE / INS * H0
    out.append(f'<path d="M30 {top} L{xs[0]} {top} L{xs[0]} {top + hp:.1f} L30 {top + hp:.1f} Z" fill="#B4BFCB" fill-opacity="0.6">'
               f'<title>Pré-inscriptions : {nf(PRE)}</title></path>')

    def label(x, lines, value, anchor='start'):
        y = top - 14 - 18 * len(lines)
        t = ''.join(f'<text x="{x}" y="{y + 16 * k}" text-anchor="{anchor}" font-size="12.5" fill="{MUTED}" font-weight="500">{ln}</text>'
                    for k, ln in enumerate(lines))
        return t + f'<text x="{x}" y="{top - 10}" text-anchor="{anchor}" font-size="16" font-weight="600" fill="{NAVY}">{value}</text>'

    out.append(label(30, ['Pré-inscriptions'], nf(PRE)))
    for i in range(4):
        x0, x1 = xs[i] + nw, xs[i + 1]
        a, b = h[i], h[i + 1]
        keep = min(a, b)
        mx = (x0 + x1) / 2
        out.append(f'<path d="M{x0} {top} L{x1} {top} L{x1} {top + b:.1f} C {mx} {top + b:.1f} {mx} {top + keep:.1f} {x0} {top + keep:.1f} Z" '
                   f'fill="{BLUES[i]}" fill-opacity="0.35"><title>{" ".join(names[i])} → {" ".join(names[i + 1])} : {nf(vals[i + 1])}</title></path>')
    for i, x in enumerate(xs):
        out.append(f'<rect x="{x}" y="{top}" width="{nw}" height="{h[i]:.1f}" rx="2" fill="{BLUES[i]}"><title>{" ".join(names[i])} : {nf(vals[i])}</title></rect>')
        out.append(label(x + (nw if i == 4 else 0), names[i], nf(vals[i]), 'end' if i == 4 else 'start'))
    Y_END = 262

    def leak(x_from, y_bottom, t, color, x_to, lab, value, sub=''):
        t = max(t, 1.5)
        y_top = y_bottom - t
        d = (f'M{x_from} {y_top:.1f} C {x_to + t:.1f} {y_top:.1f} {x_to + t:.1f} {y_top:.1f} {x_to + t:.1f} {Y_END} '
             f'L {x_to:.1f} {Y_END} C {x_to:.1f} {y_bottom:.1f} {x_to:.1f} {y_bottom:.1f} {x_from} {y_bottom:.1f} Z')
        out.append(f'<path d="{d}" fill="{color}" fill-opacity="0.85"><title>{lab} : {value}</title></path>')
        out.append(f'<text x="{x_to:.1f}" y="{Y_END + 20}" font-size="12.5" fill="{MUTED}">{lab}</text>'
                   f'<text x="{x_to:.1f}" y="{Y_END + 38}" font-size="15" font-weight="600" fill="{NAVY}">{value}</text>'
                   + (f'<text x="{x_to:.1f}" y="{Y_END + 55}" font-size="12" fill="{MUTED}">{sub}</text>' if sub else ''))

    yb = top + h[0]
    t_ec, t_ech, t_rej = EC / INS * H0, ECH / INS * H0, REJ / INS * H0
    x0 = xs[0] + nw
    leak(x0, yb, t_rej, RED, 200, 'Rejetés', nf(REJ))
    leak(x0, yb - t_rej, t_ech, ORANGE, 290, 'Échoués', nf(ECH))
    leak(x0, yb - t_rej - 1.5, t_ec, AMBER, 370, 'En cours', nf(EC))
    if v2:
        leak(xs[2] + nw, top + h[2], (DEM - IMP) / INS * H0, AMBER, 720, 'Demandes non imprimées', nf(DEM - IMP), f'{nf(DATT)} en attente, {nf(DREJ)} rejetées')
        leak(xs[3] + nw, top + h[3], REM / INS * H0, AMBER, 990, 'Cartes encore à remettre', nf(REM), pc(REM / IMP * 100) + ' des cartes expédiées')
    else:
        leak(xs[2] + nw, top + h[2], 1.5, RED, 720, 'Demandes rejetées', nf(DREJ), f'{nf(DATT)} en attente d’impression')
        leak(xs[3] + nw, top + h[3], REM / INS * H0, AMBER, 990, 'Cartes à remettre', nf(REM), pc(REM / IMP * 100) + ' des cartes expédiées')
    return (f'<svg viewBox="0 0 {W} 340" role="img" aria-label="Parcours du citoyen : {nf(PRE)} pré-inscriptions, {nf(INS)} inscriptions '
            f'({nf(REJ)} rejetées, {nf(ECH)} échouées, {nf(EC)} en cours), {nf(NIU)} NIU générés, {nf(DEM)} demandes d’impression '
            f'({nf(DREJ)} rejetées, {nf(DATT)} en attente), {nf(IMP)} cartes imprimées et expédiées, {nf(LIV)} cartes livrées, {nf(REM)} cartes à remettre." '
            f'style="display: block; width: 100%; height: auto; font-family: Poppins, sans-serif">' + ''.join(out) + '</svg>')


# ---------------------------------------------------------------------------
# v4.4 (2 oct. 2026) : format « frise à chevrons » demandé par l'utilisateur.
# Bande de 6 chevrons ; pour chaque étape, une pastille d'icône d'un côté de la bande et les chiffres de l'autre, en alternance.
# ---------------------------------------------------------------------------
_SV = 'width="28" height="28" viewBox="0 0 24 24" aria-hidden="true" style="fill: none; stroke: {c}; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round"'
TL_ICONS = {
    'rdv': '<svg {a}><rect x="3" y="5" width="18" height="16" rx="2"></rect><path d="M3 10h18M8 3v4M16 3v4"></path><path d="M9 15l2 2 4-4"></path></svg>',
    'user': '<svg {a}><circle cx="12" cy="8" r="4"></circle><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"></path></svg>',
    'niu': '<svg {a}><rect x="3" y="4" width="18" height="16" rx="2"></rect><path d="M9 8l-1.5 8M15 8l-1.5 8M7 10.5h10M6.5 13.5h10"></path></svg>',
    'doc': '<svg {a}><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><path d="M14 3v6h6M8 13h8M8 17h5"></path></svg>',
    'print': '<svg {a}><path d="M6 9V3h12v6"></path><rect x="3" y="9" width="18" height="8" rx="2"></rect><path d="M7 14h10v7H7z"></path></svg>',
    'card': '<svg {a}><rect x="2" y="5" width="20" height="14" rx="2"></rect><circle cx="8" cy="12" r="2.5"></circle><path d="M13 10h6M13 14h3"></path><path d="M15.5 16.5l1.5 1.5 3-3"></path></svg>',
}
_WARN = ('<svg width="12" height="12" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; margin-top: 3px; fill: #FAB219"><path d="M12 2 1 21h22L12 2z"></path></svg>')


def timeline_html():
    steps = [
        # (libellé bande, icône, libellé chiffre, valeur, sous-titre, pertes)
        ('Pré-inscription', 'rdv', 'Pré-inscriptions', PRE, pc(PRE / INS * 100) + ' des inscriptions', []),
        ('Inscription', 'user', 'Inscriptions', INS, 'Base du parcours', []),
        ('NIU', 'niu', 'NIU générés', NIU, pc(NIU / INS * 100) + ' des inscriptions',
         [f'<strong style="font-weight: 600">{nf(INS - NIU)}</strong> sans NIU : {nf(EC)} en cours, {nf(ECH)} échoués, {nf(REJ)} rejetés']),
        ('Demande', 'doc', 'Demandes d’impression', DEM, pc(DEM / INS * 100) + ' des inscriptions', []),
        ('Impression', 'print', 'Cartes imprimées et expédiées', IMP, pc(IMP / INS * 100) + ' des inscriptions',
         [f'<strong style="font-weight: 600">{nf(DEM - IMP)}</strong> demandes non imprimées : {nf(DATT)} en attente, {nf(DREJ)} rejetées']),
        ('Remise', 'card', 'Cartes remises', LIV, pc(LIV / INS * 100) + ' des inscriptions',
         [f'<strong style="font-weight: 600">{nf(REM)}</strong> cartes encore à remettre, soit {pc(REM / IMP * 100)} des cartes expédiées']),
    ]
    seg_colors = ['#013781', '#2A78D6', '#013781', '#2A78D6', '#013781', '#FCBA21']
    n = len(steps)
    cells = []
    for i, (band, icon, lab, val, sub, losses) in enumerate(steps):
        col = i + 1
        c = seg_colors[i]
        fg = '#071B35' if c == '#FCBA21' else '#FFFFFF'
        up = i % 2 == 1  # icône au-dessus pour les étapes 2, 4, 6 ; chiffres au-dessus pour 1, 3, 5
        w = val / INS * 100
        box = (f'<div style="display: flex; flex-direction: column; align-items: center; gap: 2px; text-align: center; padding: 0 6px; max-width: 220px; margin: 0 auto">'
               f'<span style="font-size: 13px; font-weight: 500; color: {MUTED}">{lab}</span>'
               f'<span style="font-size: 24px; font-weight: 600; letter-spacing: -0.01em; line-height: 1.2; color: {NAVY}">{nf(val)}</span>'
               f'<span aria-hidden="true" style="width: 120px; height: 4px; border-radius: 2px; background: #E3EAF3; margin: 4px 0 2px"><span style="display: block; width: {w:.1f}%; height: 4px; border-radius: 2px; background: {c if c != "#FCBA21" else "#B07D00"}"></span></span>'
               f'<span style="font-size: 12px; color: {MUTED}">{sub}</span>'
               + ''.join(f'<span style="display: flex; gap: 5px; align-items: flex-start; text-align: left; margin-top: 4px; font-size: 12px; line-height: 1.4; color: {MUTED}">{_WARN}<span>{l}</span></span>' for l in losses)
               + '</div>')
        pin = (f'<div aria-hidden="true" style="display: flex; flex-direction: {"column" if up else "column-reverse"}; align-items: center">'
               f'<span style="width: 60px; height: 60px; border-radius: 30px; background: {c}; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 6px rgba(7, 27, 53, 0.18)">'
               + TL_ICONS[icon].replace('{a}', _SV.replace('{c}', fg)) +
               f'</span><span style="width: 4px; height: 26px; background: {c}"></span></div>')
        notch = '' if i == 0 else '16px 50%, '
        clip = (f'polygon(0 0, calc(100% - 16px) 0, 100% 50%, calc(100% - 16px) 100%, 0 100%{", 16px 50%" if i else ""})')
        bandcell = (f'<div style="grid-column: {col}; grid-row: 2; height: 46px; margin-left: {"0" if i == 0 else "-10px"}; padding: 0 {"20px" if i == n - 1 else "18px"} 0 {"16px" if i == 0 else "28px"}; '
                    f'background: {c}; clip-path: {clip}; display: flex; align-items: center; color: {fg}; font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden">'
                    f'<span style="display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 10px; margin-right: 8px; font-size: 11px; '
                    f'background: {"rgba(255, 255, 255, 0.2)" if fg == "#FFFFFF" else "rgba(7, 27, 53, 0.12)"}">{col}</span>{band}</div>')
        top = box if not up else pin
        bot = pin if not up else box
        cells.append(f'<div role="listitem" aria-label="Étape {col}, {band.lower()} : {lab} {nf(val)}" style="display: contents">'
                     f'<div style="grid-column: {col}; grid-row: 1; align-self: end; display: flex; justify-content: center; padding-bottom: {"0" if up else "12px"}">{top}</div>'
                     + bandcell +
                     f'<div style="grid-column: {col}; grid-row: 3; align-self: start; display: flex; justify-content: center; padding-top: {"12px" if up else "0"}">{bot}</div></div>')
    return ('<div class="parcours-flux" style="overflow-x: auto"><div role="list" aria-label="Parcours du citoyen en six étapes" '
            'style="min-width: 1040px; display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); grid-template-rows: auto 46px auto; padding: 4px 0 12px">'
            + ''.join(cells) + '</div></div>\n')
