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
         '<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px 18px; align-self: stretch">'
         '<h1 style="margin: 0; font-size: 30px; font-weight: 600; letter-spacing: -0.015em; color: #FFFFFF">Vue d’ensemble du parcours citoyen</h1>'
         '<span class="v5-fresh"><svg width="13" height="13" viewBox="0 0 24 24" aria-hidden="true" style="fill: none; stroke: #071B35; stroke-width: 2.4; stroke-linecap: round"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>'
         'Dernière mise à jour : 14/01/2026 à 11h59</span></div>\n'
         '<form aria-label="Filtres appliqués à toute la page" style="display: flex; flex-wrap: wrap; gap: 10px">'
         + pill_select('Période', ['Depuis le début', '7 derniers jours', '30 derniers jours', '90 derniers jours', 'Période personnalisée'], 150)
         + pill_select('Région', ['Toutes les régions', 'Grand Lomé', 'Maritime', 'Plateaux', 'Centrale', 'Kara', 'Savanes'], 150)
         + '</form>\n</div>\n')

# =============== 2. Frise du parcours ===============
LOSS = {
    'Impression': (f'{nf(JF.DEM - JF.IMP)} non imprimées', f'{nf(JF.DATT)} en attente, {nf(JF.DREJ)} rejetées'),
    'Remise': (f'{nf(JF.REM)} à remettre', f'{pc(JF.REM / JF.IMP * 100)} des cartes expédiées'),
}


# 5 oct. : pertes retirées de la frise à la demande (« 11 841 non imprimées… » et « 1 330 794 à remettre… »)
LOSS = {}


ICONS_TL = dict(JF.TL_ICONS, gear='<svg {a}><circle cx="12" cy="12" r="3"></circle><circle cx="12" cy="12" r="6.6"></circle>'
                 '<path d="M12 2.4v2.8M12 18.8v2.8M2.4 12h2.8M18.8 12h2.8M5.2 5.2l2 2M16.8 16.8l2 2M5.2 18.8l2-2M16.8 7.2l2-2"></path></svg>')
# étape « Traitement des paquets » : traités, puis en cours, échoués, rejetés (somme = inscriptions)
assert JF.NIU + JF.EC + JF.ECH + JF.REJ == JF.INS
PAQUETS = ('<span class="fz-paq">'
           + ''.join(f'<span style="display: flex; align-items: center; gap: 6px"><span aria-hidden="true" style="width: 8px; height: 8px; border-radius: 2px; background: {c}"></span>'
                     f'<span style="flex-grow: 1; text-align: left">{l}</span><strong style="font-weight: 600; color: #071B35">{nf(v)}</strong></span>'
                     for l, v, c in (('En cours', JF.EC, C_AMBER), ('Échoués', JF.ECH, C_ORANGE), ('Rejetés', JF.REJ, C_RED)))
           + '</span>')


def frieze():
    """Frise à 7 étapes. v8 (5 oct.) : tout passe par des classes (CSS_FZ) pour s'adapter à la largeur de la carte :
    large (frise complète), compacte (chiffres et pastilles réduits, puis numéros seuls dans les chevrons),
    verticale sous 1 000 px (une étape par ligne, pastille ronde reliée par un rail). Plus de défilement horizontal."""
    steps = [('Pré-inscription', 'rdv', 'Pré-inscriptions', JF.PRE), ('Inscription', 'user', 'Inscriptions', JF.INS),
             ('Traitement', 'gear', 'Paquets traités', JF.NIU + JF.ECH + JF.REJ), ('NIU', 'niu', 'NIU générés', JF.NIU), ('Demande', 'doc', 'Demandes d’impression', JF.DEM),
             ('Impression', 'print', 'Cartes imprimées et expédiées', JF.IMP), ('Remise', 'card', 'Cartes remises', JF.LIV)]
    seg = ['#013781', '#2368C2', '#013781', '#2368C2', '#013781', '#2368C2', C_GOLD]
    cells = []
    for i, (band, icon, lab, val) in enumerate(steps):
        col, c = i + 1, seg[i]
        gold = c == C_GOLD
        fg = INK if gold else '#FFFFFF'
        up = i % 2 == 1
        w = val / JF.INS * 100
        loss = LOSS.get(band)
        loss_html = (f'<span class="fz-loss" title="{loss[1]}">{TRI.format(c=C_AMBER)}{loss[0]}</span>'
                     f'<span class="fz-lossd">{loss[1]}</span>') if loss else ''
        box = (f'<div class="fz-box">'
               f'<span class="fz-name"><span class="fz-num" style="background: {c}; color: {fg}">{col}</span>{band}</span>'
               f'<span class="fz-lab">{lab}</span><span class="fz-val">{nf(val)}</span>'
               + ('' if band == 'Inscription' else
                  f'<span class="fz-pct"><span aria-hidden="true" class="fz-track"><span style="width: {min(w, 100):.1f}%; background: {"#B07D00" if gold else c}"></span></span>{pc(w)}</span>') +
               f'{loss_html}{PAQUETS if band == "Traitement" else ""}</div>')
        pin = (f'<div aria-hidden="true" class="fz-pin"><span class="fz-dot" style="background: {c}">'
               + ICONS_TL[icon].replace('{a}', JF._SV.replace('{c}', fg)) +
               f'</span><span class="fz-stem" style="background: {c}"></span></div>')
        clip = f'polygon(0 0, calc(100% - 16px) 0, 100% 50%, calc(100% - 16px) 100%, 0 100%{", 16px 50%" if i else ""})'
        bandcell = (f'<div class="fz-band{" fz-first" if i == 0 else ""}" style="background: {c}; color: {fg}; clip-path: {clip}">'
                    f'<span class="fz-num" style="background: {"#FFFFFF" if fg == "#FFFFFF" else "rgba(7, 27, 53, 0.12)"}; color: {c if fg == "#FFFFFF" else INK}">{col}</span>'
                    f'<span class="fz-bt">{band}</span></div>')
        cells.append(f'<div role="listitem" aria-label="Étape {col}, {band.lower()} : {lab} {nf(val)}" class="fz-step {"fz-up" if up else "fz-down"}" style="--c: {col}">'
                     f'{pin}{bandcell}{box}</div>')
    return ('<div class="parcours-flux"><div role="list" aria-label="Parcours du citoyen en sept étapes" class="fz-list">'
            + ''.join(cells) + '</div></div>\n')


CSS_FZ = (
    # large : frise complète sur 3 rangées (pastille, chevrons, chiffres en alternance haut et bas)
    '.fz-list{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));grid-template-rows:auto 44px auto;padding:0 0 4px}'
    '.fz-step{display:contents}.fz-pin,.fz-band,.fz-box{grid-column:var(--c)}'
    '.fz-band{grid-row:2;height:44px;margin-left:-10px;padding:0 18px 0 28px;box-sizing:border-box;display:flex;align-items:center;font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden}'
    '.fz-band.fz-first{margin-left:0;padding-left:16px}'
    '.fz-num{flex-shrink:0;display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:10px;font-size:11px;font-weight:600}'
    '.fz-band .fz-num{margin-right:8px}'
    '.fz-pin{display:flex;flex-direction:column;align-items:center;justify-self:center}'
    '.fz-up .fz-pin{grid-row:1;align-self:end}.fz-down .fz-pin{grid-row:3;align-self:start;flex-direction:column-reverse}'
    '.fz-dot{width:54px;height:54px;border-radius:27px;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 10px rgba(7,27,53,.18)}'
    '.fz-stem{width:3px;height:22px}'
    '.fz-box{min-width:0;display:flex;flex-direction:column;align-items:center;text-align:center;padding:0 4px}'
    '.fz-up .fz-box{grid-row:3;align-self:start;padding-top:10px}.fz-down .fz-box{grid-row:1;align-self:end;padding-bottom:10px}'
    '.fz-name{display:none}'
    '.fz-lab{font-size:12.5px;font-weight:500;line-height:1.3;color:#4B5A6E}'
    '.fz-val{font-size:26px;font-weight:600;letter-spacing:-0.015em;line-height:1.25;color:#071B35;white-space:nowrap;font-variant-numeric:tabular-nums}'
    '.fz-pct{display:flex;align-items:center;gap:8px;margin-top:3px;font-size:12px;color:#4B5A6E}'
    '.fz-track{flex-shrink:0;width:64px;height:5px;border-radius:3px;background:#E3EAF3}.fz-track>span{display:block;height:5px;border-radius:3px}'
    '.fz-loss{display:inline-flex;align-items:center;gap:5px;margin-top:6px;padding:3px 9px;border-radius:999px;background:#FEF4DC;color:#664700;font-size:12px;font-weight:600;white-space:nowrap}'
    '.fz-lossd{margin-top:2px;font-size:11.5px;color:#4B5A6E}'
    '.fz-paq{display:flex;flex-direction:column;gap:3px;margin-top:8px;width:158px;max-width:100%;font-size:12px;color:#4B5A6E}'
    # compacte : la frise tient dans la carte jusqu'à 1 000 px
    '@media (max-width:1339px){.fz-card{padding-left:28px !important;padding-right:28px !important}'
    '.fz-list{grid-template-rows:auto 40px auto}.fz-band{height:40px;margin-left:-8px;padding:0 8px 0 22px;font-size:12px}.fz-band.fz-first{padding-left:12px}'
    '.fz-band .fz-num{margin-right:6px}.fz-dot{width:44px;height:44px;border-radius:22px}.fz-dot svg{width:22px;height:22px}.fz-stem{height:16px}'
    '.fz-lab{font-size:11.5px}.fz-val{font-size:21px}.fz-pct{gap:6px;font-size:11.5px}.fz-track{width:40px}'
    '.fz-loss{white-space:normal;padding:3px 7px;font-size:11px;line-height:1.3}.fz-lossd{font-size:11px}.fz-paq{font-size:11.5px}}'
    '@media (max-width:1179px){.fz-bt{display:none}.fz-band{justify-content:center;padding-left:18px}.fz-band.fz-first{padding-left:4px}.fz-band .fz-num{margin-right:0}}'
    # verticale : une étape par ligne, rail à gauche
    '@media (max-width:999px){.fz-card{padding:24px 20px !important}'
    '.fz-list{display:flex;flex-direction:column;padding:0}'
    '.fz-step{display:grid;grid-template-columns:44px minmax(0,1fr);column-gap:16px;position:relative;padding-bottom:22px}'
    '.fz-step:last-child{padding-bottom:0}'
    '.fz-step::before{content:"";position:absolute;left:21px;top:44px;bottom:0;width:2px;background:#DCE6F2}.fz-step:last-child::before{display:none}'
    '.fz-step .fz-band,.fz-step .fz-stem{display:none}'
    '.fz-step .fz-pin{grid-column:1;grid-row:1;align-self:start}'
    '.fz-step .fz-box{grid-column:2;grid-row:1;align-self:start;align-items:flex-start;text-align:left;padding:2px 0 0}'
    '.fz-name{display:inline-flex;align-items:center;gap:8px;margin-bottom:4px;font-size:13px;font-weight:600;color:#071B35}'
    '.fz-val{font-size:24px}.fz-lab{font-size:12.5px}.fz-pct{font-size:12px}.fz-track{width:64px}.fz-paq{width:220px}}'
)


PARCOURS = (f'<section aria-labelledby="parcours" class="fz-card" style="position: relative; {CARD2}; padding: 32px 40px 30px; display: flex; flex-direction: column; gap: 18px">\n'
            + BRACKETS +
            '<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-end; gap: 12px 32px">'
            '<div><h2 id="parcours" style="margin: 0; font-size: 22px; font-weight: 600; letter-spacing: -0.01em; color: #071B35">De la pré-inscription à la carte en main</h2>'
            f'<p style="margin: 4px 0 0; font-size: 14px; color: {MUTED}">Du rendez-vous à la remise de la carte, en sept étapes.</p></div>'
            '<div style="display: flex; align-items: center; gap: 14px; padding: 10px 18px; border-radius: 12px; background: #FFF8E6">'
            f'<span class="fz-hero" style="font-size: 38px; font-weight: 600; letter-spacing: -0.02em; line-height: 1; color: {INK}; white-space: nowrap; font-variant-numeric: tabular-nums">{nf(JF.LIV)}</span>'
            f'<span style="font-size: 13px; line-height: 1.35; color: #664700; max-width: 170px">cartes en main, soit {pc(JF.LIV / JF.INS * 100)} des inscrits</span></div></div>\n'
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

# =============== 4 bis. À traiter, v7 : liste priorisée dans un panneau à filets ===============
# Même langage que les modules : plus de cartes, de liserés ni de pastilles. Une ligne par action, triée par gravité :
# statut (texte + icône) et module | chiffre clé aligné | constat et conséquence | action.
# Ajout de la ligne « Qualité et technique » : le module est Critique, il doit avoir son action.
TODO = [
    ('Critique', 'Qualité et technique', '261 jours', 'sans nouvelles données dans le BI',
     'Alimentation arrêtée le 14/01/2026 : tous les chiffres de cette page sont figés à cette date.', 'Voir la fraîcheur', 'Technique.dc.html#fraicheur', False),
    ('Critique', 'Authentifications', pc(294763 / 510499 * 100), 'des authentifications échouent',
     f'{nf(294763)} vérifications refusées, toutes chez un seul partenaire.', 'Analyser les échecs', 'Usage.dc.html', False),
    ('Critique', 'IDPS', '14 sur 14', 'ordres d’impression en échec', 'Aucune carte produite par ce circuit.', 'Examiner les erreurs', 'Idps.dc.html', False),
    ('Priorité élevée', 'Cartes', nf(JF.REM), 'cartes expédiées non remises',
     f'{pc(JF.REM / JF.IMP * 100)} des cartes expédiées n’ont pas atteint leur titulaire.', 'Localiser les cartes', 'Cartes.dc.html', False),
    ('Priorité élevée', 'Enrôlement', nf(118402), 'paquets bloqués depuis plus de 30 jours',
     f'{pc(118402 / JF.INS * 100)} des inscrits attendent toujours leur NIU.', 'Voir les paquets bloqués', 'Technique.dc.html', False),
    ('À surveiller', 'ABIS', nf(BIO.ADJ_ATTENTE), 'dossiers en attente d’adjudication',
     '640 attendent depuis plus de 7 jours : leur NIU est bloqué.', 'Voir l’adjudication', 'Biometrie.dc.html#adjudication', True),
    ('À surveiller', 'Cartes', nf(JF.DATT), 'demandes d’impression en attente', 'Cartes pas encore lancées en production.', 'Voir les demandes', 'Cartes.dc.html', False),
]
assert JF.REM == 1330794 and BIO.ADJ_ATTENTE == 2353 and JF.DATT == 11835
_ORDER = list(ST)
assert [t[0] for t in TODO] == sorted((t[0] for t in TODO), key=_ORDER.index)
TEST_TAG = '<span class="v7-test">Données de test</span>'


def todo_row(level, module, fig, title_, impact, cta, href, test):
    return (f'<li class="v7-row">'
            f'<div class="v7-st">{status(level)}<span class="v7-modname">{module}{TEST_TAG if test else ""}</span></div>'
            f'<h3 class="v7-ttl"><span class="v7-fig">{fig}</span> <span class="v7-txt">{title_}</span></h3>'
            f'<p class="v7-imp">{impact}</p>'
            f'<a class="v7-act" href="{href}">{cta}{CHEV}</a></li>')


_counts = {lv: sum(1 for t in TODO if t[0] == lv) for lv in _ORDER}
_plural = {'Critique': ('critique', 'critiques'), 'Priorité élevée': ('priorité élevée', 'priorités élevées'), 'À surveiller': ('à surveiller', 'à surveiller')}
COUNTS = ''.join(f'<span>{ST[lv][0]}<strong>{n}</strong> {_plural[lv][n > 1]}</span>' for lv, n in _counts.items() if n)
ATRAITER = (f'<section aria-labelledby="traiter" class="v7-panel">\n'
            f'<div class="v7-head"><div><h2 id="traiter" style="{H2}; font-size: 20px">À traiter</h2>'
            f'<p style="margin: 4px 0 0; font-size: 13px; color: {MUTED}">Classé par gravité. Chaque ligne mène au module concerné.</p></div>'
            f'<p class="v7-count">{COUNTS}</p></div>\n'
            '<ol class="v7-list">\n' + '\n'.join(todo_row(*t) for t in TODO) + '\n</ol>\n</section>\n')

# =============== 5 bis. Parcours par région : même panneau que les modules ===============
PANEL = 'background: #FFFFFF; border-radius: 14px; box-shadow: 0 1px 2px rgba(7, 27, 53, 0.06), 0 8px 24px rgba(7, 27, 53, 0.06)'


def swap1(text, old, new):
    assert text.count(old) == 1, old[:80]
    return text.replace(old, new)


R = swap1(REGIONS, f'style="{CARD2}; display: flex; flex-direction: column; gap: 16px">', 'class="v7-panel">')
R = swap1(R, '<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 4px 24px">\n<div>\n<h2 id="regions"',
          '<div class="v7-head">\n<div>\n<h2 id="regions"')
R = swap1(R, '<p style="margin: 2px 0 0; font-size: 13px; color: #4B5A6E">Part des inscrits', f'<p style="margin: 4px 0 0; font-size: 13px; color: {MUTED}">Part des inscrits')
R = swap1(R, link('Enrolement.dc.html', 'Explorer le territoire'), f'<a class="v7-act" href="Enrolement.dc.html">Explorer le territoire{CHEV}</a>')
R = swap1(R, '<div style="display: flex; flex-wrap: wrap; gap: 24px 32px; align-items: flex-start">',
          '<div class="v7-pbody" style="display: flex; flex-wrap: wrap; gap: 24px 32px; align-items: flex-start">')
# barres du tableau : même épaisseur et même rail que les jauges des modules
R = swap1(R, '<span style="position: relative; flex-grow: 1; height: 12px; background: #E3EAF3; border-radius: 0 4px 4px 0"><span style="display: block; height: 12px; width: {{r.w}}%; background: #2A78D6; border-radius: 0 4px 4px 0"></span><span aria-hidden="true" style="position: absolute; left: 50%; top: -4px; width: 2px; height: 20px; background: #071B35"></span></span>',
          f'<span style="position: relative; flex-grow: 1; height: 8px; background: {TRACK}; border-radius: 4px"><span style="display: block; height: 8px; width: {{{{r.w}}}}%; background: #2A78D6; border-radius: 4px"></span><span aria-hidden="true" style="position: absolute; left: 50%; top: -5px; width: 2px; height: 18px; border-radius: 1px; background: #071B35"></span></span>')
# trois encadrés gris : remplacés par une ligne « À retenir » à filets (libellé, valeur, explication)
_tiles = re.search(r'<div style="margin-top: 20px; display: grid; grid-template-columns: repeat\(auto-fit, minmax\(200px, 1fr\)\); gap: 12px">\n(?:<div style="padding: 18px 20px.*?</div>\n){3}</div>\n', R, re.S)
assert _tiles and _tiles.group(0).count('padding: 18px 20px') == 3
_gl, _tot = 690000, JF.LIV
assert round(_gl / _tot * 100) == 39 and round(1020000 / JF.INS * 100) == 31
KEYS = ('<dl class="v7-keys" aria-label="À retenir">'
        '<div><dt>Écart entre régions</dt><dd><span class="v7-kv">25,7 points</span>entre le Grand Lomé (67,6 %) et les Savanes (41,9 %).</dd></div>'
        '<div><dt>Poids du Grand Lomé</dt><dd><span class="v7-kv">39 %</span>des cartes livrées, pour 31 % des inscriptions.</dd></div>'
        '<div><dt>Sous le seuil de 50 %</dt><dd><span class="v7-kv">3 régions</span>Savanes, Kara et Centrale.</dd></div></dl>\n')
R = R.replace(_tiles.group(0), '')  # 5 oct. : ligne « À retenir » retirée à la demande de l'utilisateur
# 5 oct. : colonne « Écart à la moyenne » retirée du tableau à la demande de l'utilisateur (avec sa ligne de légende)
R = swap1(R, '<span role="columnheader">Inscrits avec carte</span><span role="columnheader" style="text-align: right">Écart à la moyenne</span>',
          '<span role="columnheader">Inscrits avec carte</span>')
R = swap1(R, '\n<span role="cell" style="text-align: right; font-weight: 500">{{r.ecart}}</span>', '')
R = swap1(R, '<span>Écart en points par rapport à la moyenne nationale (54,0 %)</span>', '')
assert R.count('minmax(100px, 1fr) 84px 84px 84px minmax(160px, 1.6fr) 76px') == 2
R = R.replace('minmax(100px, 1fr) 84px 84px 84px minmax(160px, 1.6fr) 76px', 'minmax(100px, 1fr) 84px 84px 84px minmax(180px, 1.8fr)')
R = swap1(R, 'aria-label="Parcours par région" style="min-width: 660px;', 'aria-label="Parcours par région" style="min-width: 580px;')
assert 'Écart' not in R and 'r.ecart' not in R
# 5 oct. : légende « Seuil de vigilance : 50 % / Sous le seuil » retirée à la demande de l'utilisateur
_leg = re.search(r'<div style="display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 4px 20px; padding: 10px 8px 0; border-top: 1px solid #EEF2F5; font-size: 12px; color: #4B5A6E">.*?Sous le seuil</span></div>', R, re.S)
assert _leg and 'Seuil de vigilance' in _leg.group(0) and _leg.group(0).count('<div') == 1
R = R.replace(_leg.group(0), '')
assert 'Seuil de vigilance' not in R
# 5 oct. : « Inscrits avec carte » sans barre ni triangle, seulement le pourcentage (demande de l'utilisateur)
_cell = re.search(r'<span role="cell" style="display: flex; align-items: center; gap: 10px">\n.*?\{\{r\.part\}\}</span>\n</span>', R, re.S)
assert _cell and _cell.group(0).count('<span role="cell"') == 1
R = R.replace(_cell.group(0), '<span role="cell" style="text-align: right; font-weight: {{r.cardWeight}}">{{r.part}}</span>')
R = swap1(R, '<span role="columnheader">Inscrits avec carte</span>', '<span role="columnheader" style="text-align: right">Inscrits avec carte</span>')
assert R.count('minmax(100px, 1fr) 84px 84px 84px minmax(180px, 1.8fr)') == 2
R = R.replace('minmax(100px, 1fr) 84px 84px 84px minmax(180px, 1.8fr)', 'minmax(110px, 1.3fr) repeat(4, minmax(84px, 1fr))')
R = swap1(R, 'aria-label="Parcours par région" style="min-width: 580px;', 'aria-label="Parcours par région" style="min-width: 480px;')
# plus aucun repère de seuil dans le tableau : le sous-titre ne cite plus que la moyenne nationale
R = swap1(R, 'Part des inscrits qui ont reçu leur carte, comparée à la moyenne nationale de 54,0 % et au seuil de vigilance de 50 %.',
          'Part des inscrits qui ont reçu leur carte, par région (moyenne nationale : 54,0 %).')
assert 'r.under' not in R and 'r.w}}' not in R
# 5 oct. : tableau à côté de la carte à toutes les largeurs d'écran d'ordinateur (il passait sous la carte sous 1 290 px).
# Grille à deux colonnes : carte 540 px puis 450 px (liste des zones resserrée, tableau compact) ; empilé seulement sous 1 000 px.
R = swap1(R, '<div class="v7-pbody" style="display: flex; flex-wrap: wrap; gap: 24px 32px; align-items: flex-start">\n<div style="flex: 0 1 540px; max-width: 100%; min-width: 0">',
          '<div class="v7-pbody v7-reg">\n<div class="v7-reg-map">')
R = swap1(R, '<aside aria-label="Zones de la carte" class="carte-aside" style="flex-basis: 200px">', '<aside aria-label="Zones de la carte" class="carte-aside">')
R = swap1(R, '<div style="flex: 1 1 600px; min-width: 0; overflow-x: auto">\n<div role="table" aria-label="Parcours par région" style="min-width: 480px; font-variant-numeric: tabular-nums">',
          '<div class="v7-reg-tab">\n<div role="table" aria-label="Parcours par région" class="v7-table">')
R = swap1(R, '<div role="row" style="display: grid; grid-template-columns: minmax(110px, 1.3fr) repeat(4, minmax(84px, 1fr)); gap: 12px; padding: 6px 8px; font-size: 12px; color: #4B5A6E">',
          '<div role="row" class="v7-tr v7-th">')
R = swap1(R, '<div role="row" style="display: grid; grid-template-columns: minmax(110px, 1.3fr) repeat(4, minmax(84px, 1fr)); gap: 12px; align-items: center; padding: 10px 8px; border-top: 1px solid #EEF2F5; background: {{r.bg}}; border-radius: 4px">',
          '<div role="row" class="v7-tr" style="background: {{r.bg}}">')
REGIONS = R

# =============== 3 ter. Indicateurs par module, v9 (5 oct.) : cartes compactes ===============
# Inspiré des cartes de services du site de l'ANID (capture fournie) : cartes séparées à fin liseré jaune, coins arrondis,
# grande icône bicolore (contour bleu ANID, aplats jaunes) à gauche, texte à droite. Chaque carte est un lien vers son onglet.
# Contenu réduit à l'essentiel : nom du module et état, chiffre principal avec son unité, une ligne de contexte.
_N, _G1, _G2 = '#013781', '#FFE7A3', '#FCBA21'
_IA = f'width="52" height="52" viewBox="0 0 48 48" aria-hidden="true" style="flex-shrink: 0; fill: none; stroke: {_N}; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round"'
ICONS9 = {
    'enrol': (f'<svg {_IA}><rect x="8" y="5" width="26" height="34" rx="3" fill="{_G1}"></rect><circle cx="21" cy="17" r="4.5" fill="{_G2}"></circle>'
              f'<path d="M13 31c0-4.6 3.6-7.6 8-7.6s8 3 8 7.6z" fill="{_G2}"></path>'
              f'<circle cx="35" cy="36" r="7.5" fill="#FFFFFF"></circle><path d="M35 32.5v7M31.5 36h7"></path></svg>'),
    'cartes': (f'<svg {_IA}><rect x="4" y="10" width="40" height="28" rx="4" fill="{_G1}"></rect><path d="M4 14a4 4 0 0 1 4-4h8v28H8a4 4 0 0 1-4-4z" fill="{_G2}" stroke="none"></path>'
               f'<rect x="4" y="10" width="40" height="28" rx="4"></rect><rect x="9" y="17" width="11" height="13" rx="2" fill="#FFFFFF"></rect>'
               f'<path d="M25 19h13M25 24h13M25 29h8"></path></svg>'),
    # ABIS : empreinte de type boucle, crêtes régulières, deux minuties repérées en jaune comme dans le bandeau
    'abis': (f'<svg {_IA}><circle cx="24" cy="24" r="20" fill="{_G1}" stroke="none"></circle>'
             f'<path d="M12.6 20.6c2.1-5.1 6.5-8.4 11.4-8.4s9.3 3.3 11.4 8.4"></path>'
             f'<path d="M14 31.5v-5.2c0-6.3 4.5-11 10-11s10 4.7 10 11v3.2"></path>'
             f'<path d="M17.6 35.5v-9c0-4.2 2.9-7.4 6.4-7.4s6.4 3.2 6.4 7.4v7.4"></path>'
             f'<path d="M21.1 37.8V26.5c0-2 1.3-3.6 2.9-3.6s2.9 1.6 2.9 3.6v11.2"></path>'
             f'<path d="M17.6 35.5 34 29.5" stroke="#D99A00" stroke-width="1.1" stroke-opacity="0.8"></path>'
             f'<circle cx="17.6" cy="35.5" r="2.4" fill="#FFFFFF" stroke="#D99A00" stroke-width="1.6"></circle>'
             f'<circle cx="34" cy="29.5" r="2.4" fill="#FFFFFF" stroke="#D99A00" stroke-width="1.6"></circle></svg>'),
    'idps': (f'<svg {_IA}><rect x="14" y="5" width="20" height="12" rx="1.5" fill="#FFFFFF"></rect><rect x="5" y="16" width="38" height="18" rx="4" fill="{_G1}"></rect>'
             f'<rect x="13" y="27" width="22" height="15" rx="1.5" fill="{_G2}"></rect><path d="M18 33h12M18 37.5h8"></path><circle cx="36.5" cy="21.5" r="1.2" fill="{_N}"></circle></svg>'),
    'auth': (f'<svg {_IA}><path d="M24 4.5 39.5 10.5v11c0 10.4-6.6 17.6-15.5 21.5C15.1 39.1 8.5 31.9 8.5 21.5v-11z" fill="{_G1}"></path>'
             f'<path d="M24 4.5 8.5 10.5v11c0 10.4 6.6 17.6 15.5 21.5z" fill="{_G2}" stroke="none"></path>'
             f'<path d="M24 4.5 39.5 10.5v11c0 10.4-6.6 17.6-15.5 21.5C15.1 39.1 8.5 31.9 8.5 21.5v-11z"></path><path d="m16.5 23.5 5.2 5.2 10-10.4" stroke-width="2.6"></path></svg>'),
    'tech': (f'<svg {_IA}><path d="M6 10v24c0 2.8 6.3 5 14 5s14-2.2 14-5V10" fill="{_G1}"></path><ellipse cx="20" cy="10" rx="14" ry="5" fill="{_G2}"></ellipse>'
             f'<path d="M6 18c0 2.8 6.3 5 14 5s14-2.2 14-5M6 26c0 2.8 6.3 5 14 5s14-2.2 14-5"></path>'
             f'<circle cx="36" cy="35" r="8.5" fill="#FFFFFF"></circle><path d="M36 30.5V35l3 2"></path></svg>'),
}
assert set(ICONS9) == set(p_main_v2.MOD_ICONS)


def card9(key, name, href, value, unit, sub, level, test=False):
    tag = TEST_TAG if test else ''
    return (f'<a class="v9-card" href="{href}">{ICONS9[key]}'
            # 5 oct. : plus d'étiquettes d'état ni « Données de test » sur ces cartes (demande de l'utilisateur) ; level et test restent pour mémoire
            f'<span class="v9-body"><span class="v9-top"><h3 class="v9-name">{name}</h3></span>'
            f'<span class="v9-val">{value} <span class="v9-unit">{unit}</span></span>'
            f'<span class="v9-sub">{sub}</span></span></a>')


def _b(x):
    return f'<strong>{x}</strong>'


CARDS9 = [
    card9('enrol', 'Enrôlement', 'Enrolement.dc.html', nf(JF.INS), 'inscriptions',
          f'{_b(pc(JF.NIU / JF.INS * 100))} ont leur NIU, {nf(JF.EC)} en cours', 'Priorité élevée'),
    card9('cartes', 'Impression des cartes', 'Cartes.dc.html', nf(JF.LIV), 'cartes remises',
          f'{_b(nf(JF.REM))} cartes expédiées encore à remettre', 'Priorité élevée'),
    card9('abis', 'ABIS', 'Biometrie.dc.html', nf(BIO.DEDUP), 'recherches de doublons',
          f'{_b(pc(BIO.DEDUP / BIO.INSCRIPTIONS * 100))} des inscriptions dédupliquées', 'À surveiller', test=True),
    card9('idps', 'IDPS', 'Idps.dc.html', '14', 'ordres d’impression', f'{_b("Les 14 en erreur")}, aucune carte imprimée', 'Critique'),
    card9('auth', 'Authentifications', 'Usage.dc.html', nf(510499), 'requêtes',
          f'{_b(pc(215736 / 510499 * 100))} réussies, {pc(294763 / 510499 * 100)} échouées', 'Critique'),
    card9('tech', 'Exploration des données', 'Technique.dc.html', '24', 'indicateurs à croiser',
          f'{_b("5 sources")}, par région, date, profil ou type', 'Info'),
]
MODULES = (f'<section aria-labelledby="modules" class="v7-panel">\n'
           f'<div class="v9-head"><h2 id="modules" style="{H2}; font-size: 20px">Indicateurs clés par module</h2></div>\n'
           '<div class="v9-grid">\n' + '\n'.join(CARDS9) + '\n</div>\n</section>\n')

CSS9 = ('.v9-head{padding:24px 28px 0}'
        '.v9-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px 20px;padding:18px 28px 28px}'
        '.v9-card{display:flex;align-items:center;gap:16px;min-width:0;padding:18px 20px;border:1px solid #F5D77E;border-radius:10px;background:#FFFFFF;'
        'box-shadow:0 2px 6px rgba(7,27,53,.06);color:inherit;text-decoration:none;transition:border-color .15s,box-shadow .15s}'
        '.v9-card:hover{border-color:#FCBA21;box-shadow:0 6px 16px rgba(7,27,53,.10)}'
        '.v9-card:focus-visible{outline:2px solid #013781;outline-offset:2px}'
        '.v9-body{flex-grow:1;min-width:0;display:flex;flex-direction:column;gap:3px}'
        '.v9-top{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:4px 10px}'
        '.v9-name{margin:0;font-size:15px;font-weight:600;color:#013781}'
        '.v9-st{display:inline-flex;flex-wrap:wrap;align-items:center;gap:4px 8px;min-width:0}'
        '.v9-val{display:flex;flex-wrap:wrap;align-items:baseline;column-gap:6px;font-size:24px;font-weight:600;letter-spacing:-0.02em;line-height:1.2;color:#071B35;font-variant-numeric:tabular-nums}'
        '.v9-unit{font-size:13px;font-weight:400;letter-spacing:0;line-height:1.35;color:#4B5A6E}'
        '.v9-sub{font-size:12.5px;line-height:1.4;color:#4B5A6E}.v9-sub strong{font-weight:600;color:#071B35}'
        '@media (max-width:1100px){.v9-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}'
        '@media (max-width:700px){.v9-grid{grid-template-columns:minmax(0,1fr);padding:16px 20px 20px}.v9-head{padding:20px 20px 0}.v9-card{align-items:flex-start;gap:14px;padding:16px}.v9-card>svg{width:42px;height:42px}}')

BODY = TITLE + PARCOURS + MODULES + REGIONS  # 5 oct. : bloc « À traiter » retiré de la Vue d'ensemble à la demande de l'utilisateur
SCRIPT = p_main_v2.SCRIPT

CSS7 = ('.v7-panel{background:#FFFFFF;border-radius:14px;box-shadow:0 1px 2px rgba(7,27,53,.06),0 8px 24px rgba(7,27,53,.06)}'
        '.v7-head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:10px 24px;padding:24px 28px 20px;border-bottom:1px solid #E6EBF0}'
        '.v7-count{margin:0;display:flex;flex-wrap:wrap;gap:6px 20px;font-size:13px;color:#4B5A6E}'
        '.v7-count>span{display:inline-flex;align-items:center;gap:6px;white-space:nowrap}.v7-count strong{font-weight:600;color:#071B35}'
        '.v7-list{list-style:none;margin:0;padding:0}'
        '.v7-row{display:grid;grid-template-columns:150px 116px minmax(0,1fr) auto;column-gap:24px;row-gap:3px;align-items:baseline;padding:16px 28px;border-top:1px solid #EDF1F5}'
        '.v7-row:first-child{border-top:0}.v7-row:hover{background:#F8FAFC}'
        '.v7-st{grid-column:1;grid-row:1/span 2;align-self:start;display:flex;flex-direction:column;align-items:flex-start;gap:4px;padding-top:5px}'
        '.v7-modname{display:inline-flex;flex-wrap:wrap;align-items:center;gap:4px 8px;font-size:12.5px;color:#4B5A6E}'
        '.v7-test{padding:1px 6px;border-radius:4px;border:1px solid #D9A300;color:#6B4A00;font-size:11px;font-weight:600;white-space:nowrap}'
        '.v7-ttl{grid-column:2/span 2;grid-row:1;margin:0;display:grid;grid-template-columns:116px minmax(0,1fr);column-gap:24px;align-items:baseline}'
        '.v7-fig{font-size:22px;font-weight:600;letter-spacing:-0.015em;line-height:1.2;color:#071B35;text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}'
        '.v7-txt{font-size:15px;font-weight:600;line-height:1.35;color:#071B35}'
        '.v7-imp{grid-column:3;grid-row:2;margin:0;font-size:13px;line-height:1.45;color:#4B5A6E}'
        '.v7-act{grid-column:4;grid-row:1/span 2;align-self:center;display:inline-flex;align-items:center;gap:2px;min-height:36px;font-size:13px;font-weight:600;color:#013781;text-decoration:none;white-space:nowrap}'
        '.v7-act:hover{color:#071B35;text-decoration:underline}'
        '.v7-pbody{padding:24px 28px 28px}'
        '.v7-keys{margin:24px 0 0;padding-top:20px;border-top:1px solid #E6EBF0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}'
        '.v7-keys>div{min-width:0;padding:0 20px;border-left:1px solid #E6EBF0}.v7-keys>div:first-child{padding-left:0;border-left:0}'
        '.v7-keys dt{font-size:12px;color:#4B5A6E}'
        '.v7-keys dd{margin:4px 0 0;font-size:13px;line-height:1.45;color:#4B5A6E}'
        '.v7-kv{display:block;margin-bottom:2px;font-size:26px;font-weight:600;letter-spacing:-0.02em;line-height:1.15;color:#071B35}'
        '.v7-reg{display:grid;grid-template-columns:minmax(0,540px) minmax(0,1fr);gap:24px 32px;align-items:start}'
        '.v7-reg-map{min-width:0}.v7-reg-tab{min-width:0;overflow-x:auto}'
        '.v7-table{min-width:400px;font-variant-numeric:tabular-nums}'
        '.v7-tr{display:grid;grid-template-columns:minmax(96px,1.3fr) repeat(4,minmax(68px,1fr));gap:12px;align-items:center;padding:10px 8px;border-top:1px solid #EEF2F5;border-radius:4px}'
        '.v7-th{align-items:end;padding-top:6px;border-top:0;font-size:12px;line-height:1.35;color:#4B5A6E}'
        '@media (max-width:1240px){.v7-reg{grid-template-columns:minmax(0,450px) minmax(0,1fr);gap:24px}.v7-reg .carte-duo{gap:14px}.v7-reg .carte-aside{flex-basis:186px}'
        '.v7-tr{gap:8px;padding-left:6px;padding-right:6px;font-size:13.5px}.v7-th{font-size:11.5px}}'
        '@media (max-width:1000px){.v7-reg{grid-template-columns:minmax(0,1fr)}.v7-reg .carte-aside{flex-basis:200px}.v7-tr{gap:12px;font-size:inherit}}'
        '@media (max-width:860px){.v7-row{grid-template-columns:minmax(0,1fr);row-gap:6px;padding:16px 20px}'
        '.v7-st,.v7-ttl,.v7-imp,.v7-act{grid-column:1;grid-row:auto}.v7-st{flex-direction:row;flex-wrap:wrap;align-items:center;gap:4px 12px;padding:0}'
        '.v7-ttl{display:block}.v7-fig{font-size:20px;text-align:left}.v7-act{justify-self:start}'
        '.v7-head,.v7-pbody{padding-left:20px;padding-right:20px}}'
        '@media (max-width:700px){.v7-keys{grid-template-columns:minmax(0,1fr)}.v7-keys>div{padding:14px 0 0;border-left:0;border-top:1px solid #E6EBF0}'
        '.v7-keys>div:first-child{padding-top:0;border-top:0}.v7-keys>div+div{margin-top:14px}}')

CSS = ('.v5-link{display:inline-flex;align-items:center;gap:6px;min-height:36px;font-size:13px;font-weight:600;color:#013781;text-decoration:none}'
       '.v5-link:hover{text-decoration:underline;color:#071B35}'
       '.v5-fresh{display:inline-flex;align-items:center;gap:6px;margin-left:auto;padding:4px 10px;border-radius:999px;background:#FCBA21;color:#071B35;font-size:12px;font-weight:600;line-height:1.4;text-decoration:none;white-space:nowrap}'
       '.v5-fresh:hover{background:#FFD25E;color:#071B35}'
       '.v5-filter{display:inline-flex;align-items:center;gap:8px;height:40px;padding:0 6px 0 14px;border-radius:999px;background:#1C4C94;border:1px solid rgba(255,255,255,.28);color:rgba(255,255,255,.78);font-size:12.5px;font-weight:500}'
       '.v5-filter select{height:38px;border:0;background:transparent;color:#FFFFFF;font-family:inherit;font-size:14px;font-weight:600;cursor:pointer}'
       '.v5-filter select:focus-visible{outline:2px solid #FCBA21;outline-offset:2px}'
       '.v5-filter option{color:#071B35}')


def build():
    html = page('Vue d’ensemble du parcours citoyen', 'Main.dc.html', p_main.FILTERS, BODY, SCRIPT, 1880, '')
    for blk in (bandeau('Main.dc.html'), filters(p_main.FILTERS)):
        assert html.count(blk) == 1
        html = html.replace(blk, '')
    html = html.replace('\n</style>\n</helmet>', '\n' + p_main_v2.CSS + '\n' + CSS + CSS6 + CSS7 + CSS_FZ + CSS9 + '\n</style>\n</helmet>', 1)
    html = html.replace('<div class="bande-bio" aria-hidden="true" style="height: 230px"></div>\n<main style="position: relative; max-width: 1376px; margin: -230px auto 0; padding: 40px 32px 56px;',
                        '<div class="bande-bio" aria-hidden="true" style="height: 220px"></div>\n<main style="position: relative; max-width: 1376px; margin: -220px auto 0; padding: 30px 32px 56px;', 1)
    return html
