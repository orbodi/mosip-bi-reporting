"""Vue d'ensemble v5 : refonte visuelle pour la présentation client (3 oct. 2026).

- Haut de page compact : titre, pastille de fraîcheur et filtres dans le bandeau bleu (plus de bandeau rouge ni de barre de filtres).
- Frise à chevrons resserrée, pertes en pastilles d'une ligne, chiffre clé 54,0 % en tête.
- 6 cartes de modules avec un visuel chacune (barre empilée, anneau, unités), 3 indicateurs et un lien.
- « À traiter » en grille de cartes compactes.
- Parcours par région inchangé sur le fond, mêmes cartes arrondies.
Le script (carte, tableau régional) vient de p_main_v2.
"""
import re
from common import *
import journey_flow as JF
import p_main, p_main_v2
import p_bio as BIO

NAVY, INK, MUTED = '#013781', '#071B35', '#4B5A6E'
C_BLUE, C_RED, C_ORANGE, C_AMBER, C_GREEN, C_GOLD = '#2A78D6', '#D03B3B', '#EC835A', '#FAB219', '#2E9E63', '#FCBA21'
CARD2 = 'background: #FFFFFF; border-radius: 14px; padding: 28px; box-sizing: border-box; box-shadow: 0 1px 2px rgba(7, 27, 53, 0.06), 0 8px 24px rgba(7, 27, 53, 0.06)'
SEV = {'Critique': ('#FCEBEB', '#6E1414', C_RED), 'Priorité élevée': ('#FDEEE7', '#7A3413', C_ORANGE), 'À surveiller': ('#FEF4DC', '#664700', C_AMBER)}
TRI = '<svg width="12" height="12" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; fill: {c}"><path d="M12 2 1 21h22L12 2z"></path></svg>'


def nf(n):
    return f'{n:,}'.replace(',', ' ')


def pc(x, d=1):
    return f'{x:.{d}f}'.replace('.', ',') + ' %'


def chip(level):
    bg, fg, ic = SEV[level]
    return (f'<span style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 9px; border-radius: 999px; background: {bg}; color: {fg}; '
            f'font-size: 12px; font-weight: 600; white-space: nowrap">{TRI.format(c=ic)}{level}</span>')


TEST_CHIP = ('<span style="display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 999px; background: #FCBA21; color: #071B35; '
             'font-size: 12px; font-weight: 600; white-space: nowrap">Données de test</span>')
ARROW = '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" style="fill: none; stroke: currentColor; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round"><path d="M5 12h14M13 6l6 6-6 6"></path></svg>'


def link(href, text):
    return f'<a class="v5-link" href="{href}">{text}{ARROW}</a>'


# =============== 1. Titre, pastille de fraîcheur et filtres dans le bandeau ===============
def pill_select(label, options, min_w):
    opts = ''.join(f'<option>{o}</option>' for o in options)
    return (f'<label class="v5-filter"><span>{label}</span><select style="min-width: {min_w}px">{opts}</select></label>')


TITLE = ('<div style="display: flex; flex-direction: column; align-items: flex-start; gap: 14px">\n'
         '<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px 18px">'
         '<h1 style="margin: 0; font-size: 30px; font-weight: 600; letter-spacing: -0.015em; color: #FFFFFF">Vue d’ensemble du parcours citoyen</h1>'
         '<a href="Technique.dc.html" class="v5-fresh"><svg width="15" height="15" viewBox="0 0 24 24" aria-hidden="true" style="fill: none; stroke: #D03B3B; stroke-width: 2.4; stroke-linecap: round"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>'
         'Données au 14/01/2026</a></div>\n'
         '<form aria-label="Filtres appliqués à toute la page" style="display: flex; flex-wrap: wrap; gap: 10px">'
         + pill_select('Période', ['Depuis le début', '7 derniers jours', '30 derniers jours', '90 derniers jours', 'Période personnalisée'], 150)
         + pill_select('Région', ['Toutes les régions', 'Grand Lomé', 'Maritime', 'Plateaux', 'Centrale', 'Kara', 'Savanes'], 150)
         + '</form>\n</div>\n')

# =============== 2. Frise du parcours ===============
LOSS = {
    'Impression': (f'{nf(JF.DEM - JF.IMP)} non imprimées', f'{nf(JF.DATT)} en attente, {nf(JF.DREJ)} rejetées'),
    'Remise': (f'{nf(JF.REM)} à remettre', f'{pc(JF.REM / JF.IMP * 100)} des cartes expédiées'),
}


ICONS_TL = dict(JF.TL_ICONS, gear='<svg {a}><circle cx="12" cy="12" r="3"></circle><circle cx="12" cy="12" r="6.6"></circle>'
                 '<path d="M12 2.4v2.8M12 18.8v2.8M2.4 12h2.8M18.8 12h2.8M5.2 5.2l2 2M16.8 16.8l2 2M5.2 18.8l2-2M16.8 7.2l2-2"></path></svg>')
# étape « Traitement des paquets » : traités, puis en cours, échoués, rejetés (somme = inscriptions)
assert JF.NIU + JF.EC + JF.ECH + JF.REJ == JF.INS
PAQUETS = ('<span style="display: flex; flex-direction: column; gap: 3px; margin-top: 8px; width: 158px; font-size: 12px; color: #4B5A6E">'
           + ''.join(f'<span style="display: flex; align-items: center; gap: 6px"><span aria-hidden="true" style="width: 8px; height: 8px; border-radius: 2px; background: {c}"></span>'
                     f'<span style="flex-grow: 1; text-align: left">{l}</span><strong style="font-weight: 600; color: #071B35">{nf(v)}</strong></span>'
                     for l, v, c in (('En cours', JF.EC, C_AMBER), ('Échoués', JF.ECH, C_ORANGE), ('Rejetés', JF.REJ, C_RED)))
           + '</span>')


def frieze():
    steps = [('Pré-inscription', 'rdv', 'Pré-inscriptions', JF.PRE), ('Inscription', 'user', 'Inscriptions', JF.INS),
             ('Traitement', 'gear', 'Paquets traités', JF.NIU), ('NIU', 'niu', 'NIU générés', JF.NIU), ('Demande', 'doc', 'Demandes d’impression', JF.DEM),
             ('Impression', 'print', 'Cartes imprimées et expédiées', JF.IMP), ('Remise', 'card', 'Cartes remises', JF.LIV)]
    seg = ['#013781', '#2A78D6', '#013781', '#2A78D6', '#013781', '#2A78D6', C_GOLD]
    cells = []
    for i, (band, icon, lab, val) in enumerate(steps):
        col, c = i + 1, seg[i]
        fg = INK if c == C_GOLD else '#FFFFFF'
        up = i % 2 == 1
        w = val / JF.INS * 100
        loss = LOSS.get(band)
        loss_html = (f'<span title="{loss[1]}" style="display: inline-flex; align-items: center; gap: 5px; margin-top: 6px; padding: 3px 9px; border-radius: 999px; '
                     f'background: #FEF4DC; color: #664700; font-size: 12px; font-weight: 600; white-space: nowrap">{TRI.format(c=C_AMBER)}{loss[0]}</span>'
                     f'<span style="font-size: 11.5px; color: {MUTED}; margin-top: 2px">{loss[1]}</span>') if loss else ''
        box = (f'<div style="display: flex; flex-direction: column; align-items: center; text-align: center; padding: 0 4px">'
               f'<span style="font-size: 12.5px; font-weight: 500; color: {MUTED}; line-height: 1.3">{lab}</span>'
               f'<span style="font-size: 26px; font-weight: 600; letter-spacing: -0.015em; line-height: 1.25; color: {INK}">{nf(val)}</span>'
               f'<span style="display: flex; align-items: center; gap: 8px; margin-top: 3px; font-size: 12px; color: {MUTED}">'
               f'<span aria-hidden="true" style="width: 64px; height: 5px; border-radius: 3px; background: #E3EAF3"><span style="display: block; width: {min(w, 100):.1f}%; height: 5px; border-radius: 3px; background: {c if c != C_GOLD else "#B07D00"}"></span></span>'
               f'{pc(w)}</span>{loss_html}{PAQUETS if band == "Traitement" else ""}</div>')
        pin = (f'<div aria-hidden="true" style="display: flex; flex-direction: {"column" if up else "column-reverse"}; align-items: center">'
               f'<span style="width: 54px; height: 54px; border-radius: 27px; background: {c}; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(7, 27, 53, 0.18)">'
               + ICONS_TL[icon].replace('{a}', JF._SV.replace('{c}', fg)) +
               f'</span><span style="width: 3px; height: 22px; background: {c}"></span></div>')
        clip = f'polygon(0 0, calc(100% - 16px) 0, 100% 50%, calc(100% - 16px) 100%, 0 100%{", 16px 50%" if i else ""})'
        bandcell = (f'<div style="grid-column: {col}; grid-row: 2; height: 44px; margin-left: {"0" if i == 0 else "-10px"}; padding: 0 18px 0 {"16px" if i == 0 else "28px"}; '
                    f'background: {c}; clip-path: {clip}; display: flex; align-items: center; color: {fg}; font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden">'
                    f'<span style="display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 10px; margin-right: 8px; font-size: 11px; '
                    f'background: {"rgba(255, 255, 255, 0.22)" if fg == "#FFFFFF" else "rgba(7, 27, 53, 0.12)"}">{col}</span>{band}</div>')
        top, bot = (pin, box) if up else (box, pin)
        cells.append(f'<div role="listitem" aria-label="Étape {col}, {band.lower()} : {lab} {nf(val)}" style="display: contents">'
                     f'<div style="grid-column: {col}; grid-row: 1; align-self: end; display: flex; justify-content: center; padding-bottom: {"0" if up else "10px"}">{top}</div>'
                     + bandcell +
                     f'<div style="grid-column: {col}; grid-row: 3; align-self: start; display: flex; justify-content: center; padding-top: {"10px" if up else "0"}">{bot}</div></div>')
    return ('<div class="parcours-flux" style="overflow-x: auto"><div role="list" aria-label="Parcours du citoyen en sept étapes" '
            'style="min-width: 1180px; display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); grid-template-rows: auto 44px auto; padding: 0 0 4px">'
            + ''.join(cells) + '</div></div>\n')


PARCOURS = (f'<section aria-labelledby="parcours" style="position: relative; {CARD2}; padding: 32px 40px 30px; display: flex; flex-direction: column; gap: 18px">\n'
            + BRACKETS +
            '<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-end; gap: 12px 32px">'
            '<div><h2 id="parcours" style="margin: 0; font-size: 22px; font-weight: 600; letter-spacing: -0.01em; color: #071B35">De la pré-inscription à la carte en main</h2>'
            f'<p style="margin: 4px 0 0; font-size: 14px; color: {MUTED}">{nf(JF.INS)} inscrits, {nf(JF.LIV)} cartes remises.</p></div>'
            '<div style="display: flex; align-items: center; gap: 14px; padding: 10px 18px; border-radius: 12px; background: #FFF8E6">'
            f'<span style="font-size: 38px; font-weight: 600; letter-spacing: -0.02em; line-height: 1; color: {INK}">{pc(JF.LIV / JF.INS * 100)}</span>'
            '<span style="font-size: 13px; line-height: 1.35; color: #664700; max-width: 150px">des inscrits ont leur carte en main</span></div></div>\n'
            + frieze() + '</section>\n')


# =============== 3. Indicateurs clés par module ===============
def stackbar(parts, label):
    seg = ''.join(f'<span title="{l} : {pc(v)}" style="width: {v}%; background: {c}"></span>' for l, v, c in parts if v > 0)
    leg = ''.join(f'<span style="display: inline-flex; align-items: center; gap: 5px"><span style="width: 8px; height: 8px; border-radius: 2px; background: {c}"></span>{l} {pc(v)}</span>' for l, v, c in parts)
    return (f'<div style="display: flex; flex-direction: column; gap: 8px">'
            f'<div role="img" aria-label="{label} : ' + ', '.join(f'{l} {pc(v)}' for l, v, _ in parts) + '" style="display: flex; gap: 2px; height: 10px; border-radius: 5px; overflow: hidden; background: #EEF2F5">' + seg + '</div>'
            f'<div style="display: flex; flex-wrap: wrap; gap: 4px 12px; font-size: 12px; color: {MUTED}">{leg}</div></div>')


def ring(pct, color, track, label, caption):
    r, sw = 26, 8
    circ = 2 * 3.14159265 * r
    return (f'<div style="display: flex; align-items: center; gap: 12px">'
            f'<svg width="68" height="68" viewBox="0 0 68 68" role="img" aria-label="{label} : {pc(pct)}">'
            f'<circle cx="34" cy="34" r="{r}" fill="none" stroke="{track}" stroke-width="{sw}"></circle>'
            f'<circle cx="34" cy="34" r="{r}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-dasharray="{circ * pct / 100:.2f} {circ:.2f}" transform="rotate(-90 34 34)"></circle>'
            f'<text x="34" y="38" text-anchor="middle" font-family="Poppins, sans-serif" font-size="13" font-weight="600" fill="#071B35">{round(pct)}%</text></svg>'
            f'<span style="font-size: 12.5px; line-height: 1.4; color: {MUTED}">{caption}</span></div>')


def units(n, ok, label, caption):
    sq = ''.join(f'<span style="width: 16px; height: 16px; border-radius: 4px; background: {C_BLUE if k < ok else "#FCEBEB"}; '
                 f'{"" if k < ok else "box-shadow: inset 0 0 0 1.5px " + C_RED}"></span>' for k in range(n))
    return (f'<div style="display: flex; flex-direction: column; gap: 8px"><div role="img" aria-label="{label}" style="display: flex; flex-wrap: wrap; gap: 4px">{sq}</div>'
            f'<span style="display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: {MUTED}">{caption}</span></div>')


def minis(items):
    return ('<dl style="margin: 0; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; padding-top: 14px; border-top: 1px solid #EEF2F5">'
            + ''.join(f'<div style="display: flex; flex-direction: column; gap: 2px; min-width: 0"><dt style="font-size: 11.5px; line-height: 1.3; color: {MUTED}">{l}</dt>'
                      f'<dd style="margin: 0; font-size: 15px; font-weight: 600; color: {INK}; white-space: nowrap">{v}</dd></div>' for l, v in items)
            + '</dl>')


def mod_card(key, name, href, cta, big, big_label, visual, mini, level=None, test=False, big_color=INK):
    accent = SEV[level][2] if level else '#C5CFDA'
    chips = (chip(level) if level else '') + (TEST_CHIP if test else '')
    return (f'<article aria-labelledby="m-{key}" style="position: relative; border: 1px solid #E3EAF0; border-radius: 12px; padding: 20px 22px 16px; display: flex; flex-direction: column; gap: 14px; min-width: 0; background: #FFFFFF; overflow: hidden">'
            f'<span aria-hidden="true" style="position: absolute; left: 0; top: 0; right: 0; height: 4px; background: {accent}"></span>'
            f'<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px; min-height: 28px">'
            f'<div style="display: flex; align-items: center; gap: 10px">{p_main_v2.MOD_ICONS[key]}<h3 id="m-{key}" style="margin: 0; font-size: 16px; font-weight: 600; color: {INK}">{name}</h3></div>'
            f'<div style="display: flex; flex-wrap: wrap; gap: 6px">{chips}</div></div>'
            f'<div style="display: flex; flex-direction: column"><span style="font-size: 32px; font-weight: 600; letter-spacing: -0.02em; line-height: 1.15; color: {big_color}">{big}</span>'
            f'<span style="font-size: 13px; color: {MUTED}">{big_label}</span></div>'
            f'{visual}{minis(mini)}'
            f'<div style="margin-top: auto">{link(href, cta)}</div></article>')


_INS = JF.INS
CARDS = [
    mod_card('enrol', 'Enrôlement', 'Enrolement.dc.html', 'Voir l’enrôlement', nf(_INS), 'inscriptions',
             stackbar([('NIU générés', JF.NIU / _INS * 100, C_BLUE), ('En cours', JF.EC / _INS * 100, C_AMBER),
                       ('Rejetés', JF.REJ / _INS * 100, C_RED), ('Échoués', JF.ECH / _INS * 100, C_ORANGE)], 'Devenir des inscriptions'),
             [('Pré-inscriptions', nf(JF.PRE)), ('Délai jusqu’au NIU', '6,5 jours'), ('Mises à jour', nf(14740))], level='Priorité élevée'),
    mod_card('cartes', 'Cartes', 'Cartes.dc.html', 'Voir les cartes', nf(JF.LIV), 'cartes remises aux citoyens',
             ring(JF.LIV / JF.IMP * 100, C_BLUE, '#E3EAF3', 'Taux de remise des cartes expédiées', 'des cartes expédiées sont remises ; ' + nf(JF.REM) + ' attendent leur titulaire'),
             [('Expédiées', nf(JF.IMP)), ('À remettre', nf(JF.REM)), ('Délai NIU à carte', '34 jours')], level='Priorité élevée'),
    mod_card('abis', 'ABIS', 'Biometrie.dc.html', 'Voir l’ABIS', nf(BIO.DEDUP), 'recherches de doublons',
             stackbar([('Passées par l’ABIS', BIO.DEDUP / BIO.INSCRIPTIONS * 100, NAVY), ('Pas encore', 100 - BIO.DEDUP / BIO.INSCRIPTIONS * 100, '#C5CFDA')], 'Inscriptions passées par l’ABIS'),
             [('Doublons (HIT)', nf(BIO.HIT)), ('En adjudication', nf(BIO.ADJ_ATTENTE)), ('Taux d’erreur', pc((BIO.ERR_ID + BIO.ERR_INS) / (BIO.DEDUP + BIO.INSERT) * 100, 2))],
             level='À surveiller', test=True),
    mod_card('idps', 'IDPS', 'Idps.dc.html', 'Voir l’IDPS', '14', 'ordres d’impression reçus',
             units(14, 0, '14 ordres d’impression, aucun imprimé, 14 en erreur', TRI.format(c=C_RED) + '14 ordres en erreur, aucune carte imprimée'),
             [('Cartes imprimées', '0'), ('Taux d’échec', '100 %'), ('Dernier ordre', '03/07/2026')], level='Critique'),
    mod_card('auth', 'Authentifications', 'Usage.dc.html', 'Voir les authentifications', nf(510499), 'requêtes d’authentification',
             ring(215736 / 510499 * 100, C_BLUE, '#F3C2C2', 'Authentifications réussies', 'réussies ; en rouge, les ' + pc(294763 / 510499 * 100) + ' d’échecs'),
             [('Réussies', nf(215736)), ('Échouées', nf(294763)), ('Partenaires', '1')], level='Critique'),
    mod_card('tech', 'Qualité et technique', 'Technique.dc.html', 'Voir la qualité et la technique', '261 jours', 'sans nouvelles données',
             stackbar([('Non conformes', 3 / 7 * 100, C_RED), ('À vérifier', 2 / 7 * 100, C_AMBER), ('Conformes', 2 / 7 * 100, C_GREEN)], 'Contrôles de cohérence').replace(
                 '{} '.format('Non conformes') + pc(3 / 7 * 100), '3 non conformes').replace('À vérifier ' + pc(2 / 7 * 100), '2 à vérifier').replace('Conformes ' + pc(2 / 7 * 100), '2 conformes'),
             [('Compteurs faux', '3'), ('Paquets bloqués', nf(118402)), ('Dernière donnée', '14/01/2026')], big_color='#8A1F1F'),
]
MODULES = (f'<section aria-labelledby="modules" style="{CARD2}; display: flex; flex-direction: column; gap: 18px">\n'
           '<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 4px 24px">'
           f'<h2 id="modules" style="{H2}; font-size: 20px">Indicateurs clés par module</h2>'
           f'<p style="margin: 0; font-size: 13px; color: {MUTED}">Le liseré et la pastille reprennent l’alerte la plus grave du module.</p></div>\n'
           '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(340px, 100%), 1fr)); gap: 16px">\n'
           + '\n'.join(CARDS) + '\n</div>\n</section>\n')

# =============== 3 bis. Indicateurs par module, v6 : un seul panneau à filets ===============
# Retours client : les cartes « sentaient l'IA ». Choix : un panneau unique découpé en 6 cellules par des filets
# (plus de cartes dans la carte, plus de liserés colorés ni de pastilles), statut en texte + icône, nom du module cliquable,
# un seul visuel par cellule choisi selon la nature de la donnée (jauge pour un taux, barre empilée pour une répartition,
# unités pour un petit effectif), trois chiffres secondaires alignés en colonnes.
ST = {  # statut : (icône, couleur de l'icône, couleur du texte)
    'Critique': ('<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0"><circle cx="12" cy="12" r="10" fill="#D03B3B"></circle><path d="M12 7v6M12 16.5v.5" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round"></path></svg>', '#8A1F1F'),
    'Priorité élevée': ('<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0"><path d="M12 2.5 1.5 21h21L12 2.5z" fill="#EC835A"></path><path d="M12 9.5v5M12 17.5v.3" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round"></path></svg>', '#8A3D14'),
    'À surveiller': ('<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0"><path d="M12 2.5 1.5 21h21L12 2.5z" fill="#FAB219"></path><path d="M12 9.5v5M12 17.5v.3" stroke="#071B35" stroke-width="2.2" stroke-linecap="round"></path></svg>', '#6B4A00'),
}
CHEV = '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; fill: none; stroke: currentColor; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round"><path d="M9 6l6 6-6 6"></path></svg>'
TRACK = '#DCE6F2'


def status(level):
    ic, col = ST[level]
    return f'<span style="display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px; font-weight: 500; color: {col}; white-space: nowrap">{ic}{level}</span>'


def meter(pct, fill, caption, right=''):
    return (f'<div style="display: flex; flex-direction: column; gap: 8px">'
            f'<div role="meter" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{pct:.1f}" aria-label="{caption}" title="{caption} : {pc(pct)}" '
            f'style="height: 8px; border-radius: 4px; background: {TRACK}; overflow: hidden"><span style="display: block; width: {pct:.2f}%; height: 8px; border-radius: 4px; background: {fill}"></span></div>'
            f'<div style="display: flex; justify-content: space-between; gap: 12px; font-size: 12.5px; color: {MUTED}">'
            f'<span><strong style="font-weight: 600; color: {INK}">{pc(pct)}</strong> {caption}</span>{right}</div></div>')


def split(parts, label):
    """Barre de répartition : segments séparés par 2 px, chaque segment nommé dessous avec sa valeur."""
    seg = ''.join(f'<span title="{l} : {pc(v)}" style="flex: {v} 1 0; min-width: 3px; background: {c}"></span>' for l, v, c in parts)
    leg = ''.join(f'<span style="display: inline-flex; align-items: center; gap: 6px; white-space: nowrap"><span aria-hidden="true" style="width: 8px; height: 8px; border-radius: 2px; background: {c}"></span>'
                  f'{l} <strong style="font-weight: 600; color: {INK}">{pc(v)}</strong></span>' for l, v, c in parts)
    return (f'<div style="display: flex; flex-direction: column; gap: 9px">'
            f'<div role="img" aria-label="{label} : ' + ', '.join(f'{l} {pc(v)}' for l, v, _ in parts) + '" style="display: flex; gap: 2px; height: 8px; border-radius: 4px; overflow: hidden">' + seg + '</div>'
            f'<div style="display: flex; flex-wrap: wrap; gap: 4px 14px; font-size: 12.5px; color: {MUTED}">{leg}</div></div>')


def blocks(items, label, caption):
    """Petit effectif : un bloc par unité, couleur de statut et légende en texte."""
    sq = ''.join(f'<span title="{t}" style="flex: 1 1 0; max-width: 22px; height: 18px; border-radius: 3px; background: {c}"></span>' for t, c in items)
    return (f'<div style="display: flex; flex-direction: column; gap: 9px"><div role="img" aria-label="{label}" style="display: flex; gap: 3px">{sq}</div>'
            f'<div style="font-size: 12.5px; color: {MUTED}">{caption}</div></div>')


def figures(items):
    return ('<dl style="margin: 0; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; padding-top: 16px; border-top: 1px solid #EDF1F5">'
            + ''.join(f'<div style="min-width: 0; display: flex; flex-direction: column"><dt style="flex-grow: 1; font-size: 12px; line-height: 1.35; color: {MUTED}">{l}</dt>'
                      f'<dd style="margin: 3px 0 0; font-size: 16px; font-weight: 600; color: {INK}; font-variant-numeric: tabular-nums; white-space: nowrap">{v}</dd></div>' for l, v in items)
            + '</dl>')


def cell(key, name, href, value, unit, visual, figs, level=None, test=False):
    tag = ('<span style="padding: 2px 8px; border-radius: 4px; border: 1px solid #D9A300; color: #6B4A00; font-size: 11.5px; font-weight: 600; white-space: nowrap">Données de test</span>' if test else '')
    return (f'<article aria-labelledby="m-{key}" class="v6-cell">'
            f'<header style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 6px 12px">'
            f'<h3 id="m-{key}" style="margin: 0"><a class="v6-mod" href="{href}">{name}{CHEV}</a></h3>'
            f'<span style="display: inline-flex; align-items: center; gap: 10px">{tag}{status(level) if level else ""}</span></header>'
            f'<p style="margin: 0; display: flex; flex-wrap: wrap; align-items: baseline; gap: 2px 10px">'
            f'<span style="font-size: 38px; font-weight: 600; letter-spacing: -0.025em; line-height: 1.05; color: {INK}">{value}</span>'
            f'<span style="font-size: 14px; color: {MUTED}">{unit}</span></p>'
            f'{visual}{figures(figs)}</article>')


CELLS = [
    cell('enrol', 'Enrôlement', 'Enrolement.dc.html', nf(JF.INS), 'inscriptions',
         split([('NIU', JF.NIU / JF.INS * 100, NAVY), ('En cours', JF.EC / JF.INS * 100, C_AMBER), ('Rejetés', JF.REJ / JF.INS * 100, C_RED),
                ('Échoués', JF.ECH / JF.INS * 100, C_ORANGE)], 'Devenir des inscriptions'),
         [('Pré-inscriptions', nf(JF.PRE)), ('Délai jusqu’au NIU', '6,5 jours'), ('Mises à jour', nf(14740))], level='Priorité élevée'),
    cell('cartes', 'Cartes', 'Cartes.dc.html', nf(JF.LIV), 'cartes remises',
         meter(JF.LIV / JF.IMP * 100, NAVY, 'des cartes expédiées', f'<span>{nf(JF.REM)} à remettre</span>'),
         [('Demandes d’impression', nf(JF.DEM)), ('Cartes expédiées', nf(JF.IMP)), ('Délai NIU à carte', '34 jours')], level='Priorité élevée'),
    cell('abis', 'ABIS', 'Biometrie.dc.html', nf(BIO.DEDUP), 'recherches de doublons',
         meter(BIO.DEDUP / BIO.INSCRIPTIONS * 100, NAVY, 'des inscriptions dédupliquées'),
         [('Doublons confirmés', nf(BIO.HIT)), ('En adjudication', nf(BIO.ADJ_ATTENTE)), ('Taux d’erreur', pc((BIO.ERR_ID + BIO.ERR_INS) / (BIO.DEDUP + BIO.INSERT) * 100, 2))],
         level='À surveiller', test=True),
    cell('idps', 'IDPS', 'Idps.dc.html', '14', 'ordres d’impression',
         blocks([(f'Ordre {k + 1} : en erreur', C_RED) for k in range(14)], '14 ordres d’impression, tous en erreur',
                f'<strong style="font-weight: 600; color: {INK}">14 en erreur</strong>, aucune carte imprimée'),
         [('Cartes imprimées', '0'), ('Taux d’échec', '100\u00a0%'), ('Dernier ordre', '03/07/2026')], level='Critique'),
    cell('auth', 'Authentifications', 'Usage.dc.html', nf(510499), 'requêtes',
         split([('Réussies', 215736 / 510499 * 100, NAVY), ('Échouées', 294763 / 510499 * 100, C_RED)], 'Résultat des authentifications'),
         [('Réussies', nf(215736)), ('Échouées', nf(294763)), ('Partenaires', '1')], level='Critique'),
    cell('tech', 'Qualité et technique', 'Technique.dc.html', '261', 'jours sans nouvelles données',
         blocks([('Non conforme', C_RED)] * 3 + [('À vérifier', C_AMBER)] * 2 + [('Conforme', C_GREEN)] * 2, 'Contrôles de cohérence : 3 non conformes, 2 à vérifier, 2 conformes',
                f'Contrôles : <strong style="font-weight: 600; color: {INK}">3 non conformes</strong>, 2 à vérifier, 2 conformes'),
         [('Compteurs faux', '3'), ('Paquets bloqués', nf(118402)), ('Dernière donnée', '14/01/2026')], level='Critique'),
]
MODULES = (f'<section aria-labelledby="modules" style="background: #FFFFFF; border-radius: 14px; box-shadow: 0 1px 2px rgba(7, 27, 53, 0.06), 0 8px 24px rgba(7, 27, 53, 0.06); overflow: hidden">\n'
           f'<div style="padding: 24px 28px 20px"><h2 id="modules" style="{H2}; font-size: 20px">Indicateurs clés par module</h2></div>\n'
           '<div class="v6-grid">\n' + '\n'.join(CELLS) + '\n</div>\n</section>\n')

CSS6 = ('.v6-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;background:#E6EBF0;border-top:1px solid #E6EBF0}'
        '.v6-cell{background:#FFFFFF;padding:22px 28px 24px;display:flex;flex-direction:column;gap:16px;min-width:0}'
        '.v6-mod{display:inline-flex;align-items:center;gap:4px;min-height:32px;font-size:15px;font-weight:600;color:#071B35;text-decoration:none}'
        '.v6-mod svg{color:#8A97A8}.v6-mod:hover{color:#013781}.v6-mod:hover svg{color:#013781}'
        '@media (max-width:1100px){.v6-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}'
        '@media (max-width:700px){.v6-grid{grid-template-columns:minmax(0,1fr)}.v6-cell{padding:20px}}')


# =============== 4. À traiter ===============
ALERTS = [
    ('Critique', 'Authentification', '57,7 % des authentifications échouent', f'{nf(294763)} vérifications refusées, toutes chez un seul partenaire.', 'Analyser les échecs', 'Usage.dc.html'),
    ('Critique', 'IDPS', '14 ordres IDPS sur 14 en échec', '14 cartes non produites par ce circuit.', 'Examiner les erreurs', 'Idps.dc.html'),
    ('Priorité élevée', 'Cartes', f'{nf(1330794)} cartes expédiées non remises', '42,9 % des cartes produites n’ont pas atteint leur titulaire.', 'Localiser les cartes', 'Cartes.dc.html'),
    ('Priorité élevée', 'Enrôlement', f'{nf(118402)} paquets bloqués depuis plus de 30 jours', '3,6 % des inscrits attendent toujours leur NIU.', 'Voir les paquets bloqués', 'Technique.dc.html'),
    ('À surveiller', 'ABIS', f'{nf(2353)} dossiers en attente d’adjudication', '640 attendent depuis plus de 7 jours : leur NIU est bloqué.', 'Voir l’adjudication', 'Biometrie.dc.html#adjudication'),
    ('À surveiller', 'Cartes', f'{nf(11835)} demandes d’impression en attente', 'Cartes pas encore lancées en production.', 'Voir les demandes', 'Cartes.dc.html'),
]


def alert_card(level, module, title_, impact, cta, href):
    bg, fg, ic = SEV[level]
    return (f'<article style="position: relative; display: flex; flex-direction: column; gap: 8px; padding: 16px 18px 14px 20px; border-radius: 12px; background: #FFFFFF; border: 1px solid #E3EAF0; overflow: hidden">'
            f'<span aria-hidden="true" style="position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: {ic}"></span>'
            f'<div style="display: flex; align-items: center; gap: 8px">{chip(level)}<span style="font-size: 12px; color: {MUTED}">{module}</span></div>'
            f'<h3 style="margin: 0; font-size: 15.5px; font-weight: 600; line-height: 1.35; color: {INK}">{title_}</h3>'
            f'<p style="margin: 0; font-size: 13px; line-height: 1.45; color: {MUTED}"><span style="font-weight: 600; color: {INK}">Impact :</span> {impact}</p>'
            f'<div style="margin-top: auto; padding-top: 2px">{link(href, cta)}</div></article>')


n_act = sum(1 for a in ALERTS if a[0] != 'À surveiller')
ATRAITER = (f'<section aria-labelledby="traiter" style="{CARD2}; display: flex; flex-direction: column; gap: 18px">\n'
            '<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px 24px">'
            f'<h2 id="traiter" style="{H2}; font-size: 20px">À traiter</h2>'
            '<div style="display: flex; gap: 8px">'
            f'<span style="padding: 4px 12px; border-radius: 999px; background: #FCEBEB; color: #6E1414; font-size: 13px; font-weight: 600">{n_act} actions requises</span>'
            f'<span style="padding: 4px 12px; border-radius: 999px; background: #FEF4DC; color: #664700; font-size: 13px; font-weight: 600">{len(ALERTS) - n_act} à surveiller</span></div></div>\n'
            '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(340px, 100%), 1fr)); gap: 14px">\n'
            + '\n'.join(alert_card(*a) for a in ALERTS) + '\n</div>\n</section>\n')

# =============== 5. Parcours par région (repris, habillage harmonisé) ===============
REGIONS = re.search(r'<section aria-labelledby="regions".*?</section>', p_main_v2.BODY, re.S).group(0)
REGIONS = REGIONS.replace(CARD, CARD2, 1)
_lk = '<a href="Enrolement.dc.html" style="display: inline-flex; align-items: center; min-height: 44px; font-size: 13px; font-weight: 600">Explorer le territoire</a>'
assert REGIONS.count(_lk) == 1
REGIONS = REGIONS.replace(_lk, link('Enrolement.dc.html', 'Explorer le territoire'))
REGIONS = REGIONS.replace('padding: 16px 18px; border-radius: 6px; background: #F1F4F6', 'padding: 18px 20px; border-radius: 12px; background: #F4F7FA')
assert CARD2 in REGIONS
REGIONS = REGIONS.replace(f'<h2 id="regions" style="{H2}">', f'<h2 id="regions" style="{H2}; font-size: 20px">', 1)

BODY = TITLE + PARCOURS + MODULES + ATRAITER + REGIONS
SCRIPT = p_main_v2.SCRIPT

CSS = ('.v5-link{display:inline-flex;align-items:center;gap:6px;min-height:36px;font-size:13px;font-weight:600;color:#013781;text-decoration:none}'
       '.v5-link:hover{text-decoration:underline;color:#071B35}'
       '.v5-fresh{display:inline-flex;align-items:center;gap:7px;padding:6px 12px;border-radius:999px;background:#FCEBEB;color:#8A1F1F;font-size:13px;font-weight:600;text-decoration:none;white-space:nowrap}'
       '.v5-fresh:hover{background:#FFFFFF;color:#6E1414}'
       '.v5-filter{display:inline-flex;align-items:center;gap:8px;height:40px;padding:0 6px 0 14px;border-radius:999px;background:#1C4C94;border:1px solid rgba(255,255,255,.28);color:rgba(255,255,255,.78);font-size:12.5px;font-weight:500}'
       '.v5-filter select{height:38px;border:0;background:transparent;color:#FFFFFF;font-family:inherit;font-size:14px;font-weight:600;cursor:pointer}'
       '.v5-filter select:focus-visible{outline:2px solid #FCBA21;outline-offset:2px}'
       '.v5-filter option{color:#071B35}')


def build():
    html = page('Vue d’ensemble du parcours citoyen', 'Main.dc.html', p_main.FILTERS, BODY, SCRIPT, 2690, '')
    for blk in (bandeau('Main.dc.html'), filters(p_main.FILTERS)):
        assert html.count(blk) == 1
        html = html.replace(blk, '')
    html = html.replace('\n</style>\n</helmet>', '\n' + p_main_v2.CSS + '\n' + CSS + CSS6 + '\n</style>\n</helmet>', 1)
    html = html.replace('<div class="bande-bio" aria-hidden="true" style="height: 230px"></div>\n<main style="position: relative; max-width: 1376px; margin: -230px auto 0; padding: 40px 32px 56px;',
                        '<div class="bande-bio" aria-hidden="true" style="height: 220px"></div>\n<main style="position: relative; max-width: 1376px; margin: -220px auto 0; padding: 30px 32px 56px;', 1)
    return html
