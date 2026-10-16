"""Corrections de la revue UI/UX générale (9 oct. 2026), appliquées aux pages finales.

Couche posée après les constructeurs de pages (build.py) : remplacements vérifiés (chaque motif doit exister)
et une feuille de style commune (CSS_FIX). Constats traités : UX-01 à UX-36 retenus dans claude/revue-uiux.md.
"""
import re
from common import TABS

CHEV_D = ('<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" style="fill: none; stroke: currentColor; stroke-width: 2.4; '
          'stroke-linecap: round; stroke-linejoin: round"><polyline points="6 9 12 15 18 9"></polyline></svg>')
ARROW = ('<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" style="fill: none; stroke: currentColor; stroke-width: 2.2; '
         'stroke-linecap: round; stroke-linejoin: round"><path d="M5 12h14M13 6l6 6-6 6"></path></svg>')
BAND_IMG = '/_blob/41200b4723504e051b5b0bd1b777ba52'


def swap(html, old, new, count=1):
    n = html.count(old)
    assert n == count, (old[:120], n, count)
    return html.replace(old, new)


def scope_tag():
    """Pastille « Ensemble du Togo » : le bloc ne suit pas le filtre Région (UX-03)."""
    return ('<sc-if value="{{natScope}}" hint-placeholder-val="{{false}}"><span title="Ce bloc ne suit pas le filtre Région" class="v8-scope">'
            'Ensemble du Togo</span></sc-if>')


def tag_heads(html, ids):
    for i in ids:
        m = re.search(r'<h2 id="%s"[^>]*>.*?</h2>' % re.escape(i), html, re.S)
        assert m, i
        h = m.group(0)
        html = html.replace(h, h[:-5] + scope_tag() + '</h2>', 1)
    return html


# ------------------------------------------------------------------ feuille commune
CSS_FIX = (
    # lien d'évitement (UX-32)
    '.v8-skip{position:absolute;left:16px;top:-80px;z-index:100;padding:10px 16px;border-radius:8px;background:#FCBA21;color:#071B35;'
    'font-weight:600;text-decoration:none}.v8-skip:focus{top:12px;color:#071B35}'
    'main:focus{outline:none}'
    # pastille de fraîcheur : pas un lien, pas d'effet au survol (UX-25)
    '.v5-fresh:hover{background:#FCBA21}'
    # filtres du bandeau : contour lisible (UX-19), lien vers l'Exploration (UX-03)
    '.v5-filter{border-color:rgba(255,255,255,.5)}'
    '.v8-more{display:inline-flex;align-items:center;gap:6px;min-height:40px;padding:0 2px;color:#FFFFFF;font-size:13px;font-weight:600;'
    'text-decoration:underline;text-decoration-color:rgba(255,255,255,.55);text-underline-offset:4px}'
    '.v8-more:hover{color:#FCBA21;text-decoration-color:#FCBA21}'
    # pastille « Ensemble du Togo » quand une région est choisie (UX-03)
    '.v8-scope{display:inline-flex;align-items:center;margin-left:10px;padding:2px 9px;border:1px solid #8A97A6;border-radius:999px;'
    'font-size:12px;font-weight:500;letter-spacing:0;color:#4B5A6E;vertical-align:3px;white-space:nowrap}'
    # menu mobile (UX-08)
    'header{position:relative}'
    '.v8-menu{display:none;position:relative}'
    '.v8-menu>summary{list-style:none;display:inline-flex;align-items:center;gap:6px;min-height:44px;padding:0 16px;border:1px solid #8A97A6;'
    'border-radius:999px;font-size:14px;font-weight:600;color:#013781;cursor:pointer}'
    '.v8-menu>summary::-webkit-details-marker{display:none}'
    '.v8-menu[open]>summary{background:#EEF4FB;border-color:#013781}.v8-menu[open]>summary svg{transform:rotate(180deg)}'
    '.v8-mnav{position:absolute;right:0;top:calc(100% + 8px);z-index:60;display:flex;flex-direction:column;width:min(280px,calc(100vw - 32px));'
    'padding:6px;border:1px solid #D5DEE8;border-radius:12px;background:#FFFFFF;box-shadow:0 14px 34px rgba(7,27,53,.18)}'
    '.v8-mnav a{display:flex;align-items:center;min-height:44px;padding:0 12px;border-radius:8px;color:#071B35;font-weight:500;text-decoration:none}'
    '.v8-mnav a:hover{background:#F1F5F9}'
    '.v8-mnav a[aria-current=page]{background:#EEF4FB;color:#013781;font-weight:600;box-shadow:inset 3px 0 0 #FCBA21}'
    # graphiques à défilement : la semaine la plus récente est visible d'emblée (UX-10)
    '.v8-scrollr{direction:rtl}.v8-scrollr>*{direction:ltr}'
    # tablette : les paires de panneaux restent côte à côte jusqu'à 900 px (UX-24)
    '@media (min-width:901px) and (max-width:1100px){.en-row2{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}}'
    # téléphone : en-tête compact, bandeau qui suit son contenu, champs à 16 px (UX-08, UX-09)
    '@media (max-width:700px){'
    '.v8-nav{display:none !important}.v8-menu{display:block;margin-left:auto}.v8-prof{margin-left:0 !important}.v8-who{display:none !important}'
    '.v8-hin{min-height:64px !important;padding:8px 16px !important;flex-wrap:nowrap !important;gap:12px !important}'
    '.v8-hin img{height:36px !important}.v8-hin>div:first-child{gap:10px !important}'
    '.v8-hin>div:first-child>span{padding-left:10px !important;font-size:14px !important}'
    '.bande-bio{display:none}'
    'main{margin-top:0 !important;padding:0 16px 40px !important}'
    f'main>:first-child{{margin:0 -16px -32px;padding:24px 16px 56px;background-color:#013781;'
    f'background-image:linear-gradient(rgba(1,55,129,.7),rgba(1,55,129,.7)),url({BAND_IMG});background-repeat:no-repeat;background-size:auto 100%;background-position:right center}}'
    '.v5-filter select{font-size:16px}'
    '}'
)


def common_fixes(name, html):
    # en-tête : menu mobile, profil réduit à l'avatar
    html = swap(html, '<nav aria-label="Sections du tableau de bord" style="display: flex;', '<nav aria-label="Sections du tableau de bord" class="v8-nav" style="display: flex;')
    links = ''.join(
        f'<a href="{h}" aria-current="page">{l}</a>' if h == name else f'<a href="{h}">{l}</a>' for h, l in TABS)
    menu = (f'<details class="v8-menu"><summary>Menu{CHEV_D}</summary>'
            f'<nav aria-label="Sections du tableau de bord" class="v8-mnav">{links}</nav></details>\n')
    html = swap(html, '<div style="margin-left: auto; display: flex; align-items: center; gap: 10px; font-size: 13px; color: #4B5A6E">',
                menu + '<div class="v8-prof" style="margin-left: auto; display: flex; align-items: center; gap: 10px; font-size: 13px; color: #4B5A6E">')
    html = swap(html, '<span style="display: flex; flex-direction: column; line-height: 1.3; white-space: nowrap"><span style="font-weight: 600; color: #071B35">Global admin',
                '<span class="v8-who" style="display: flex; flex-direction: column; line-height: 1.3; white-space: nowrap"><span style="font-weight: 600; color: #071B35">Global admin')
    html = swap(html, '<div style="max-width: 1376px; margin: 0 auto; padding: 10px 32px; box-sizing: border-box; display: flex; flex-wrap: wrap; align-items: center; gap: 8px 24px; min-height: 76px">',
                '<div class="v8-hin" style="max-width: 1376px; margin: 0 auto; padding: 10px 32px; box-sizing: border-box; display: flex; flex-wrap: wrap; align-items: center; gap: 8px 24px; min-height: 76px">')
    # lien d'évitement
    html = re.sub(r'(<div class="fond-bio"[^>]*>\n)', r'\1<a class="v8-skip" href="#contenu">Aller au contenu</a>\n', html, count=1)
    html = swap(html, '<main style="position: relative;', '<main id="contenu" tabindex="-1" style="position: relative;')
    # graphiques hebdomadaires
    html = html.replace('<div style="overflow-x: auto; padding-top: 10px">', '<div class="v8-scrollr" style="overflow-x: auto; padding-top: 10px">')
    html = swap(html, '\n</style>\n</helmet>', '\n' + CSS_FIX + '\n</style>\n</helmet>')
    return html


# ------------------------------------------------------------------ filtres du bandeau (UX-03)
_FILTER = re.compile(r'<label class="v5-filter"><span>([^<]*)</span><select([^>]*)>.*?</select></label>', re.S)


def band_filters(html, keep_region):
    """Retire les filtres qui ne font rien ; garde Région quand elle pilote la page ; renvoie vers l'Exploration."""
    m = re.search(r'<form aria-label="Filtres appliqués à toute la page"([^>]*)>(.*?)</form>', html, re.S)
    assert m
    kept = [f.group(0) for f in _FILTER.finditer(m.group(2)) if keep_region and f.group(1) == 'Région']
    assert len(kept) == (1 if keep_region else 0), kept
    more = f'<a class="v8-more" href="Technique.dc.html">Filtres détaillés dans l’Exploration{ARROW}</a>'
    if kept:
        new = (f'<form aria-label="Filtre de région"{m.group(1)}>' + kept[0] + more + '</form>')
    else:
        new = f'<div{m.group(1)}>' + more + '</div>'
    return html.replace(m.group(0), new, 1)


def add_return(html, marker, extra):
    """Ajoute des valeurs au retour de renderVals (marker : début exact de l'objet retourné)."""
    return swap(html, marker, marker + extra)


# ------------------------------------------------------------------ Vue d'ensemble
REG_NIU = {'DAGL': 961808, 'PLA': 556639, 'MAR': 479495, 'SAV': 413573, 'KAR': 358514, 'CEN': 288857}  # = page Enrôlement


def fix_main(html):
    # UX-01 : NIU par région identiques à l'Enrôlement (total 3 058 886)
    for old, new in (("['DAGL', 'Grand Lomé', 1020000, 961080,", "['DAGL', 'Grand Lomé', 1020000, 961808,"),
                     ("['PLA', 'Plateaux', 598000, 555858,", "['PLA', 'Plateaux', 598000, 556639,"),
                     ("['MAR', 'Maritime', 512000, 478964,", "['MAR', 'Maritime', 512000, 479495,"),
                     ("['SAV', 'Savanes', 450239, 412740,", "['SAV', 'Savanes', 450239, 413573,"),
                     ("['KAR', 'Kara', 386000, 357964,", "['KAR', 'Kara', 386000, 358514,"),
                     ("['CEN', 'Centrale', 312000, 288370,", "['CEN', 'Centrale', 312000, 288857,")):
        html = swap(html, old, new)
    assert sum(REG_NIU.values()) == 3058886
    # UX-03 : Région pilotée (liste, carte et filtre synchronisés), Période retirée
    html = band_filters(html, keep_region=True)
    html = swap(html, '<span>Région</span><select style="min-width: 150px"><option>Toutes les régions</option><option>Grand Lomé</option><option>Maritime</option>'
                      '<option>Plateaux</option><option>Centrale</option><option>Kara</option><option>Savanes</option></select>',
                '<span>Région</span><select value="{{regionValue}}" onChange="{{onRegion}}" style="min-width: 150px"><option value="">Toutes les régions</option>'
                '<option value="DAGL">Grand Lomé</option><option value="MAR">Maritime</option><option value="PLA">Plateaux</option><option value="CEN">Centrale</option>'
                '<option value="KAR">Kara</option><option value="SAV">Savanes</option></select>')
    html = add_return(html, 'return { steps: steps, actions: actions, watch: watch, tiles: tiles, regions: regions, map: map',
                      ", regionValue: sel || '', natScope: !!sel, onRegion: (e) => this.setState({ region: e && e.target && e.target.value ? e.target.value : null, mapHover: null })")
    html = tag_heads(html, ['parcours', 'modules'])
    # tableau des régions : libellé harmonisé (UX-16), légende du gras (UX-15), colonnes clés visibles sur téléphone (UX-07)
    html = swap(html, '<span role="columnheader" style="text-align: right">Inscriptions</span><span role="columnheader" style="text-align: right">NIU générés</span><span role="columnheader" style="text-align: right">Cartes livrées</span>',
                '<span role="columnheader" class="v8-hm" style="text-align: right">Inscriptions</span><span role="columnheader" class="v8-hm" style="text-align: right">NIU générés</span><span role="columnheader" style="text-align: right">Cartes remises</span>')
    html = swap(html, '<span role="cell" style="text-align: right">{{r.inscr}}</span>\n<span role="cell" style="text-align: right">{{r.niu}}</span>',
                '<span role="cell" class="v8-hm" style="text-align: right">{{r.inscr}}</span>\n<span role="cell" class="v8-hm" style="text-align: right">{{r.niu}}</span>')
    html = swap(html, '<div role="table" aria-label="Parcours par région" class="v7-table">', '<div role="table" aria-label="Parcours par région" class="v7-table v8-t3">')
    html = swap(html, '</sc-for>\n\n</div>\n</div>\n</div>\n</section>',
                '</sc-for>\n\n</div>\n<p class="v8-tnote">En gras : régions où moins de 50 % des inscrits ont reçu leur carte.</p>\n</div>\n</div>\n</section>')
    # UX-29 : le lien du panneau mène au détail des cartes
    html = swap(html, '<a class="v7-act" href="Enrolement.dc.html">Explorer le territoire', '<a class="v7-act" href="Cartes.dc.html">Détail des cartes par région')
    html = swap(html, '\n</style>\n</helmet>', '\n' + CSS_MAIN + '\n</style>\n</helmet>')
    return html


CSS_MAIN = ('.v8-tnote{margin:14px 0 0;font-size:12.5px;color:#4B5A6E}'
            '@media (max-width:700px){.fz-hero{font-size:30px !important}}'
            '@media (max-width:600px){.v8-t3{min-width:0 !important}.v8-t3 .v8-hm{display:none}'
            '.v8-t3 .v7-tr{grid-template-columns:minmax(0,1.2fr) minmax(84px,1fr) minmax(84px,1fr)}}')


TRI_OK = '#B07D00'  # triangle d'alerte : 3,6:1 sur blanc (au lieu de #FAB219, 1,8:1) (UX-15)
CSS_TABLES = (
    '.v8-tnote{margin:12px 0 0;font-size:12.5px;line-height:1.45;color:#4B5A6E}'
    '.v8-tnote svg{vertical-align:-1px;margin-right:3px}'
    '.v8-rate{display:block;font-size:12px;font-weight:400;line-height:1.2;color:#4B5A6E;white-space:nowrap}'
    '.v8-mu{display:none;font-weight:400;color:#4B5A6E}'
    '.v8-wl:last-child{text-align:right}@media (max-width:1240px){.v8-wl:nth-child(odd){visibility:hidden}}'
    '@media (max-width:600px){'
    '.v8-t4{min-width:0 !important}.v8-t4 .v8-hm{display:none}'
    '.v8-t4 .en-tr{grid-template-columns:minmax(0,1.3fr) repeat(2,minmax(76px,1fr)) !important;gap:8px !important}'
    '.v8-t4 .ca-tr{grid-template-columns:minmax(0,1.2fr) repeat(2,minmax(78px,1fr)) !important;gap:8px !important}'
    
    '.v8-csc{grid-template-columns:28px minmax(0,1fr) !important;align-items:start !important}'
    '.v8-csc>span:last-child{grid-column:2;align-items:flex-start !important;text-align:left}'
    '.v8-csch{display:none !important}'
    '.ca-rk{grid-template-columns:28px minmax(0,1fr);align-items:start}.ca-rkm{grid-column:2;align-items:flex-start;text-align:left}'
    '.ca-rkh{display:none}.v8-mu{display:inline}'
    '}'
)
_TRI_SVG = (f'<svg width="11" height="11" viewBox="0 0 24 24" aria-hidden="true" style="fill: {TRI_OK}"><path d="M12 2 1 21h22L12 2z"></path></svg>')


# ------------------------------------------------------------------ Enrôlement
def fix_enrol(html):
    html = band_filters(html, keep_region=True)
    html = add_return(html, "regionValue: sel || '',", " natScope: !!sel,")
    html = tag_heads(html, ['prereg', 'devenir', 'hebdo'])
    # pré-inscription : pas de chiffre « Non mesuré » en vedette ; le nombre d'abord ; ordre femmes / hommes (UX-12, UX-11, UX-36)
    html = swap(html, "{ label: 'Honorées à l’inscription', value: 'Non mesuré', detail: '', warn: false, valueColor: '#4B5A6E' }",
                "{ label: 'Honorées à l’inscription', value: '—', detail: 'Non mesuré : rendez-vous et inscriptions non reliés', warn: false, valueColor: '#4B5A6E' }")
    html = swap(html, "{ label: 'Pré-inscrits par sexe', value: '53 % / 47 %', detail: 'Hommes / femmes, l’inverse des NIU générés', warn: false, valueColor: '#071B35' }",
                "{ label: 'Femmes pré-inscrites', value: '285 220', detail: '47 %, contre 321 630 hommes : l’inverse des NIU', warn: false, valueColor: '#071B35' }")
    # tableau des zones : taux affiché à côté des rejets signalés, légende du triangle, colonnes clés sur téléphone (UX-15, UX-07)
    html = swap(html, '<div role="table" aria-labelledby="souszones" class="en-table">', '<div role="table" aria-labelledby="souszones" class="en-table v8-t4">')
    html = swap(html, '<span role="columnheader">Zone</span><span role="columnheader">Inscriptions</span>', '<span role="columnheader">Zone</span><span role="columnheader" class="v8-hm">Inscriptions</span>')
    html = swap(html, '<span role="cell" title="{{r.tip}}">{{r.value}}</span>', '<span role="cell" class="v8-hm" title="{{r.tip}}">{{r.value}}</span>')
    html = swap(html, '<span role="columnheader">Échoués</span><span role="columnheader">En cours</span><span role="columnheader">Délai médian</span>',
                '<span role="columnheader" class="v8-hm">Échoués</span><span role="columnheader" class="v8-hm">En cours</span><span role="columnheader" class="v8-hm">Délai médian</span>')
    html = swap(html, '<span role="cell">{{r.ech}}</span><span role="cell">{{r.cours}}</span><span role="cell">{{r.delai}}</span>',
                '<span role="cell" class="v8-hm">{{r.ech}}</span><span role="cell" class="v8-hm">{{r.cours}}</span><span role="cell" class="v8-hm">{{r.delai}}</span>')
    html = swap(html, '<svg width="11" height="11" viewBox="0 0 24 24" aria-label="Taux élevé" style="margin-right: 4px; fill: #FAB219"><path d="M12 2 1 21h22L12 2z"></path></svg></sc-if>{{r.rej}}</span>',
                f'<svg width="11" height="11" viewBox="0 0 24 24" role="img" aria-label="Taux de rejet de 3,5 % ou plus" style="margin-right: 4px; fill: {TRI_OK}"><path d="M12 2 1 21h22L12 2z"></path></svg></sc-if>{{{{r.rej}}}}'
                '<sc-if value="{{r.high}}" hint-placeholder-val="{{false}}"><span class="v8-rate">{{r.rejRate}}</span></sc-if></span>')
    html = swap(html, "rejTip: 'Taux de rejet : ' + pct(s.rej),", "rejTip: 'Taux de rejet : ' + pct(s.rej), rejRate: pct(s.rej),")
    i = html.index('aria-labelledby="souszones" class="en-table v8-t4"')
    j = html.index('</sc-for>\n</div>', i) + len('</sc-for>\n</div>')
    html = html[:j] + f'\n<p class="v8-tnote">{_TRI_SVG}Taux de rejet de 3,5 % ou plus (rejets rapportés aux inscriptions de la zone).</p>' + html[j:]
    # NIU : même couleur que dans « Devenir des inscriptions » (marine), liseré blanc sur les barres ; hommes en vert plus soutenu (UX-22)
    html = swap(html, '<i style="width: 16px; height: 2px; border-radius: 0; background: #1BAF7A"></i>NIU générés', '<i style="width: 16px; height: 3px; border-radius: 0; background: #013781"></i>NIU générés')
    html = swap(html, '<polyline points="{{linePoints}}" style="fill: none; stroke: #1BAF7A; stroke-width: 2px;',
                '<polyline points="{{linePoints}}" style="fill: none; stroke: #FFFFFF; stroke-width: 6px; stroke-linejoin: round; stroke-linecap: round; vector-effect: non-scaling-stroke"></polyline>'
                '<polyline points="{{linePoints}}" style="fill: none; stroke: #013781; stroke-width: 2.5px;')
    html = swap(html, 'border-radius: 7px; background: #1BAF7A; border: 2px solid #FFFFFF', 'border-radius: 7px; background: #013781; border: 2px solid #FFFFFF')
    html = html.replace('#1BAF7A', '#0E8A62')  # pyramide : hommes
    # graphique hebdomadaire fluide (tablette en deux colonnes) : barres élastiques, largeur minimale réduite (UX-24)
    html = swap(html, 'width: 22px; height: {{w.h}}px', 'width: min(22px, 64%); height: {{w.h}}px')
    html = swap(html, 'min-width: 560px;', 'min-width: 380px;')
    html = swap(html, '<span style="flex: 1 1 0; text-align: center">{{w.label}}</span>', '<span class="v8-wl" style="flex: 1 1 0; text-align: center; white-space: nowrap">{{w.label}}</span>')
    # top des centres : unité non répétée ; classement lisible sur téléphone
    html = swap(html, "metric: nf(c[3]), sub: 'inscriptions' }));", "metric: nf(c[3]), sub: '' }));")
    html = swap(html, '<div role="row" style="display: grid; grid-template-columns: 36px minmax(0, 1fr) minmax(120px, auto); gap: 12px; padding: 6px 0;',
                '<div role="row" class="v8-csch" style="display: grid; grid-template-columns: 36px minmax(0, 1fr) minmax(120px, auto); gap: 12px; padding: 6px 0;')
    html = swap(html, '<div role="row" style="display: grid; grid-template-columns: 36px minmax(0, 1fr) minmax(120px, auto); gap: 12px; align-items: center;',
                '<div role="row" class="v8-csc" style="display: grid; grid-template-columns: 36px minmax(0, 1fr) minmax(120px, auto); gap: 12px; align-items: center;')
    html = swap(html, '<span style="font-weight: 600">{{c.metric}}</span>', '<span style="font-weight: 600">{{c.metric}}<span class="v8-mu"> {{metricUnit}}</span></span>')
    html = add_return(html, "regionValue: sel || '',", " metricUnit: tab === 'ech' ? 'échecs' : tab === 'rej' ? 'rejets' : 'inscriptions',")
    html = swap(html, '\n</style>\n</helmet>', '\n' + CSS_TABLES + '\n</style>\n</helmet>')
    return html


# ------------------------------------------------------------------ Impression des cartes
def fix_cartes(html):
    html = band_filters(html, keep_region=True)
    html = add_return(html, "regionValue: sel || '',", " natScope: !!sel, allTogo: !sel,")
    html = tag_heads(html, ['impr', 'hebdo', 'rejets', 'anciennete'])
    html = swap(html, '<div role="table" aria-labelledby="tabreg" class="ca-table">', '<div role="table" aria-labelledby="tabreg" class="ca-table v8-t4">')
    html = swap(html, '<span role="columnheader">Expédiées</span><span role="columnheader">Remises</span>',
                '<span role="columnheader" class="v8-hm">Expédiées</span><span role="columnheader" class="v8-hm">Remises</span>')
    html = swap(html, '<span role="cell">{{r.exp}}</span><span role="cell">{{r.liv}}</span>', '<span role="cell" class="v8-hm">{{r.exp}}</span><span role="cell" class="v8-hm">{{r.liv}}</span>')
    html = swap(html, '<svg width="11" height="11" viewBox="0 0 24 24" aria-label="Plus de la moitié à remettre" style="margin-right: 4px; fill: #FAB219">',
                f'<svg width="11" height="11" viewBox="0 0 24 24" role="img" aria-label="Plus de la moitié des cartes à remettre" style="margin-right: 4px; fill: {TRI_OK}">')
    i = html.index('aria-labelledby="tabreg" class="ca-table v8-t4"')
    j = html.index('</sc-for>\n</div>', i) + len('</sc-for>\n</div>')
    html = html[:j] + f'\n<p class="v8-tnote">{_TRI_SVG}Plus de la moitié des cartes expédiées reste à remettre.</p>' + html[j:]
    html = swap(html, '\n</style>\n</helmet>', '\n' + CSS_TABLES + '\n</style>\n</helmet>')
    return html


CSS_SRC = ('.v8-src{margin:0;padding-top:12px;border-top:1px solid #E6EBF0;font-size:12px;color:#4B5A6E}'
           '.ab-srct{margin:-30px 28px 0;padding-bottom:46px}')


# ------------------------------------------------------------------ ABIS, IDPS, Authentifications, Exploration
def fix_bio(html):
    html = band_filters(html, keep_region=False)
    return swap(html, '\n</style>\n</helmet>', '\n' + CSS_SRC + '\n</style>\n</helmet>')


def fix_idps(html):
    html = band_filters(html, keep_region=False)
    return swap(html, '\n</style>\n</helmet>', '\n' + CSS_TABLES + 'section[aria-labelledby=ordres] .en-pre-main{padding-bottom:48px}' + '\n</style>\n</helmet>')


def fix_usage(html):
    html = band_filters(html, keep_region=False)
    return swap(html, '\n</style>\n</helmet>', '\n' + CSS_TABLES + '\n</style>\n</helmet>')


FIXERS = {'Main.dc.html': fix_main, 'Enrolement.dc.html': fix_enrol, 'Cartes.dc.html': fix_cartes,
          'Biometrie.dc.html': fix_bio, 'Idps.dc.html': fix_idps, 'Usage.dc.html': fix_usage}


def fix(name, html):
    html = common_fixes(name, html)
    if name in FIXERS:
        html = FIXERS[name](html)
    return html
