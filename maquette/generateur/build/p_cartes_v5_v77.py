"""Impression des cartes v5 (7 oct. 2026) : refonte au langage de la Vue d'ensemble et de l'Enrôlement.

- Onglet renommé « Impression des cartes ». Titre, pastille de fraîcheur et filtres en pastilles dans le bandeau bleu.
- Impression et remise : chiffre principal (cartes remises) avec la barre remises / à remettre, et 6 cartes au style v9.
- Parcours de la carte (crochets jaunes) et ancienneté des cartes à remettre côte à côte.
- Territoire : chiffres de la zone dans l'en-tête, carte et tableau des régions côte à côte (une ligne cliquable = la région).
- Remise par centre et réconciliation NIU / cartes, dans des panneaux à en-tête.
Le script reste celui de p_cartes (nettoyé par clean.py), complété ici.
"""
import re
from common import *
import p_cartes, p_main_v3 as V3, p_enrol_v5 as EN, clean
import journey_flow as JF

INS, DEM, IMP, LIV, REM, DATT, DREJ = JF.INS, JF.DEM, JF.IMP, JF.LIV, JF.REM, JF.DATT, JF.DREJ
assert IMP - LIV == REM


def nf(n):
    return f'{n:,}'.replace(',', ' ')


def pc(x):
    return f'{x:.1f}'.replace('.', ',') + ' %'


_old = clean.clean('Cartes.dc.html', p_cartes.build())
SCRIPT = _old[_old.index('<script type="text/x-dc" data-dc-script'):]
SCRIPT = SCRIPT[SCRIPT.index('>') + 1:SCRIPT.index('</script>')].strip('\n')
_old_body = _old[_old.index('</helmet>'):]


def swap(old, new, count=1):
    global SCRIPT
    assert SCRIPT.count(old) == count, (old[:70], SCRIPT.count(old))
    SCRIPT = SCRIPT.replace(old, new)


# =============== Script ===============
swap("{ label: 'Livrées', n: 1770796, color: '#104281', note: '57,1 % des cartes expédiées' }",
     "{ label: 'Remises', n: 1770796, color: '#013781', note: '57,1 % des cartes expédiées' }")
swap("{ label: 'Demandées', n: 3113431, color: '#86B6EF', note: 'Demandes envoyées au partenaire d’impression' }",
     "{ label: 'Demandées', n: 3113431, color: '#86B6EF', note: 'Envoyées au partenaire d’impression' }")
swap("'Absent du classement des cartes livrées'", "'Absent du classement des cartes remises'")
_ret = re.search(r"    return \{ map: map, flow: flow, byRegion: byRegion,", SCRIPT)
assert _ret
SCRIPT = SCRIPT.replace(_ret.group(0), """    // zone choisie et tableau des régions (cliquer une ligne = choisir la région, comme sur la carte)
    const zr = sel ? regs.find((r) => r[0] === sel) : null;
    const zExp = zr ? zr[2] : natExp, zLiv = zr ? zr[3] : regs.reduce((a, r) => a + r[3], 0);
    const regRows = regs.slice().sort((a, b) => b[2] - a[2]).map((r) => {
      const p = (r[2] - r[3]) / r[2] * 100;
      return { name: r[1], exp: nf(r[2]), liv: nf(r[3]), rem: nf(r[2] - r[3]), part: pct(p), high: p >= 50, weight: p >= 50 ? '600' : '400',
        bg: sel === r[0] ? '#EEF5FD' : 'transparent', pressed: sel === r[0] ? 'true' : 'false',
        pick: () => this.setState({ region: sel === r[0] ? null : r[0], mapHover: null }) };
    });
    return { map: map, flow: flow, byRegion: byRegion,
      regionValue: sel || '', onRegion: (e) => this.setState({ region: e && e.target && e.target.value ? e.target.value : null, mapHover: null }),
      zoneLabel: zr ? 'Région ' + zr[1] : 'Ensemble du Togo', zExp: nf(zExp), zLiv: nf(zLiv), zRem: nf(zExp - zLiv),
      zLivPct: pct(zLiv / zExp * 100), zRemPct: pct((zExp - zLiv) / zExp * 100), regRows: regRows,
      remRows: remRows, hasRem: remRows.length > 0, noRem: remRows.length === 0,""", 1)
# impressions par semaine (7 oct.) : barres = cartes imprimées, courbe = demandes d'impression ; même graphique que l'Enrôlement
swap("    // zone choisie et tableau des régions (cliquer",
     "    const wk = [\n"
     "      ['20/10', 28900, 28400, '20 octobre'], ['27/10', 29300, 29000, '27 octobre'], ['03/11', 31200, 30600, '3 novembre'],\n"
     "      ['10/11', 33800, 33100, '10 novembre'], ['17/11', 32600, 32900, '17 novembre'], ['24/11', 34500, 33800, '24 novembre'],\n"
     "      ['01/12', 36100, 35600, '1er décembre'], ['08/12', 35300, 35400, '8 décembre'], ['15/12', 33200, 33500, '15 décembre'],\n"
     "      ['22/12', 22600, 23900, '22 décembre'], ['29/12', 17500, 16800, '29 décembre'], ['05/01', 20100, 19400, '5 janvier']\n"
     "    ];\n"
     "    const hovW = typeof st.hoverW === 'number' ? st.hoverW : wk.length - 1;\n"
     "    const HH = 220, MX = 40000;\n"
     "    const trend = wk.map((w, i) => ({ label: i % 2 === 0 ? w[0] : '', h: (w[2] / MX * HH).toFixed(1), bg: i === hovW ? '#1C5CAB' : '#2A78D6',\n"
     "      band: i === hovW ? 'rgba(42,120,214,0.07)' : 'transparent',\n"
     "      aria: 'Semaine du ' + w[3] + ' : ' + nf(w[2]) + ' cartes imprimées, ' + nf(w[1]) + ' demandes d’impression',\n"
     "      enter: () => this.setState({ hoverW: i }) }));\n"
     "    const hw = wk[hovW];\n"
     "    const readout = 'Semaine du ' + hw[3] + ' : ' + nf(hw[2]) + ' cartes imprimées, ' + nf(hw[1]) + ' demandes d’impression reçues.';\n"
     "    const linePoints = wk.map((w, i) => ((i + 0.5) * 100).toFixed(1) + ',' + (HH - w[1] / MX * HH).toFixed(1)).join(' ');\n"
     "    const lw = wk[wk.length - 1];\n"
     "    const endDot = { left: ((wk.length - 0.5) / wk.length * 100).toFixed(2), bottom: (lw[1] / MX * HH).toFixed(1) };\n"
     "    // zone choisie et tableau des régions (cliquer")
swap("      remRows: remRows, hasRem: remRows.length > 0, noRem: remRows.length === 0,",
     "      remRows: remRows, hasRem: remRows.length > 0, noRem: remRows.length === 0,\n      trend: trend, readout: readout, linePoints: linePoints, endDot: endDot,\n      rejTrend: rejTrend, rejRead: rejRead,")
# rejets par semaine (7 oct.) : 5 des 6 demandes rejetées tombent dans la fenêtre de 12 semaines (la 6e, le 13/03/2026, est après)
swap("    const lw = wk[wk.length - 1];\n",
     "    const lw = wk[wk.length - 1];\n"
     "    const rj = [0, 1, 0, 0, 2, 0, 0, 1, 0, 0, 0, 1];\n"
     "    const hovR = typeof st.hoverR === 'number' ? st.hoverR : rj.length - 1;\n"
     "    const rejTrend = wk.map((w, i) => ({ label: w[0], lab: i % 2 === 0 ? w[0] : '', h: (rj[i] / 3 * 220).toFixed(1), n: rj[i] ? String(rj[i]) : '',\n"
     "      bg: i === hovR ? '#A32C2C' : '#D03B3B', band: i === hovR ? 'rgba(208,59,59,0.07)' : 'transparent',\n"
     "      aria: 'Semaine du ' + w[3] + ' : ' + rj[i] + (rj[i] > 1 ? ' demandes rejetées' : ' demande rejetée'),\n"
     "      enter: () => this.setState({ hoverR: i }) }));\n"
     "    const rjN = rj[hovR];\n"
     "    const rejRead = 'Semaine du ' + wk[hovR][3] + ' : ' + (rjN === 0 ? 'aucune demande rejetée' : rjN + (rjN > 1 ? ' demandes rejetées' : ' demande rejetée')) + '.';\n")

# top des centres (7 oct.) : centres classés par nombre de cartes remises, suivant la région choisie
swap("    // zone choisie et tableau des régions",
     "    const regOf = (place) => place.endsWith('Grand Lomé') ? 'DAGL' : place.endsWith('Savanes') ? 'SAV' : '';\n"
     "    const remRows = c.filter((x) => x[3] !== null && (!sel || regOf(x[1]) === sel)).sort((a, b) => b[3] - a[3]).slice(0, 5)\n"
     "      .map((x, i) => ({ rank: String(i + 1), name: x[0], place: x[1], metric: nf(x[3]),\n"
     "        sub: x[2] !== null ? pct(x[3] / x[2] * 100) + ' des ' + nf(x[2]) + ' cartes expédiées' : 'nombre de cartes expédiées non connu' }));\n"
     "    // zone choisie et tableau des régions")

# =============== Bandeau ===============
TITLE = EN.TITLE.replace('>Enrôlement</h1>', '>Impression des cartes</h1>', 1)
_pills = re.search(r'<form aria-label="Filtres appliqués à toute la page".*?</form>', TITLE, re.S).group(0)
_keep = re.findall(r'<label class="v5-filter"><span>(?:Période|Région)</span>.*?</label>', _pills, re.S)
assert len(_keep) == 2
TITLE = TITLE.replace(_pills, '<form aria-label="Filtres appliqués à toute la page" style="display: flex; flex-wrap: wrap; gap: 10px">' + ''.join(_keep) + '</form>')
assert 'Impression des cartes</h1>' in TITLE and '{{onRegion}}' in TITLE

# =============== Icônes en plus (même style bicolore) ===============
_N, _G1, _G2, _IA = EN._N, EN._G1, EN._G2, EN._IA
IC = dict(EN.IC)
IC['doc'] = (f'<svg {_IA}><path d="M11 5h18l9 9v29H11z" fill="{_G1}"></path><path d="M29 5v9h9" fill="{_G2}"></path>'
             '<path d="M17 22h15M17 28h15M17 34h9"></path></svg>')
IC['print'] = V3.ICONS9['idps'].replace('width="52" height="52"', 'width="44" height="44"')
IC['idcard'] = V3.ICONS9['cartes'].replace('width="52" height="52"', 'width="44" height="44"')
IC['card_wait'] = (f'<svg {_IA}><rect x="3" y="9" width="34" height="24" rx="3.5" fill="{_G1}"></rect><rect x="8" y="15" width="9" height="11" rx="1.5" fill="{_G2}"></rect>'
                   f'<path d="M21 17h11M21 22h11M21 27h6"></path><circle cx="36" cy="35" r="8.5" fill="#FFFFFF"></circle><path d="M36 30.5V35l3 2"></path></svg>')


def scard(icon, label, value, detail):
    """Carte v9 à valeurs fixes (les totaux nationaux ne dépendent pas du filtre)."""
    return (f'<div class="v9-card en-card">{IC[icon]}<span class="v9-body"><span class="v9-name">{label}</span>'
            f'<span class="v9-val">{value}</span><span class="v9-sub">{detail}</span></span></div>')


# =============== 1. Impression et remise ===============
P1 = ('<section aria-labelledby="impr" class="v7-panel en-dev">\n' + BRACKETS + EN.head('impr', 'Impression et remise') +
      '<div class="en-pre">\n<div class="en-pre-main">'
      f'<p class="en-big"><span class="en-bigv">{nf(LIV)}</span><span class="en-bigu">cartes remises, soit {pc(LIV / IMP * 100)} des {nf(IMP)} cartes expédiées</span></p>'
      f'<div role="img" aria-label="Cartes expédiées : remises {pc(LIV / IMP * 100)}, à remettre {pc(REM / IMP * 100)}" class="en-split">'
      f'<span style="flex: {LIV} 1 0; background: #013781"></span><span style="flex: {REM} 1 0; background: #FAB219"></span></div>'
      '<div class="en-leg">'
      f'<span><i style="background: #013781"></i>Remises <strong>{pc(LIV / IMP * 100)}</strong></span>'
      f'<span><i style="background: #FAB219"></i>À remettre <strong>{pc(REM / IMP * 100)}</strong></span></div>'
      '</div>\n<div class="en-cards en-c3 en-pre-cards ca-p1cards">'
      + scard('doc', 'Demandes d’impression', nf(DEM), f'{pc(DEM / INS * 100)} des inscriptions')
      + scard('wait', 'En attente d’impression', nf(DATT), 'Pas encore lancées en production')
      + scard('rejet', 'Demandes rejetées', nf(DREJ), 'La dernière le 13/03/2026')
      + scard('print', 'Imprimées et expédiées', nf(IMP), f'{pc(IMP / DEM * 100)} des demandes')
      + scard('card_wait', 'Cartes à remettre', nf(REM), f'{pc(REM / IMP * 100)} des cartes expédiées')
      + scard('delai', 'Délai du NIU à la carte', '34 jours', 'Médiane, sur les cartes remises')
      + '</div>\n</div>\n</section>\n')

# =============== 2. Parcours de la carte + ancienneté ===============
FLOW = ('<div class="ca-flow">\n<sc-for list="{{flow}}" as="f" hint-placeholder-count="3">\n'
        '<div title="{{f.tip}}" class="ca-frow"><span class="ca-fl">{{f.label}}</span>'
        '<span class="ca-fb"><span style="width: {{f.w}}%; background: {{f.color}}"></span><strong>{{f.value}}</strong></span>'
        '<span></span><span class="ca-fn">{{f.note}}</span></div>\n</sc-for>\n</div>\n'
        f'<p class="ca-note">{nf(DATT)} demandes attendent encore l’impression. {nf(DREJ)} demandes ont été rejetées, la dernière le 13/03/2026.</p>\n')
P2 = ('<section aria-labelledby="parcours" class="v7-panel en-dev">\n' + BRACKETS + EN.head('parcours', 'Parcours de la carte', 'De la demande d’impression à la remise au citoyen.') +
      '<div class="v7-pbody en-devb">\n' + FLOW + '</div>\n</section>\n')
AGES = ('<div class="ca-flow">\n<sc-for list="{{ages}}" as="a" hint-placeholder-count="4">\n'
        '<div title="{{a.tip}}" class="ca-frow ca-arow"><span class="ca-fl">{{a.label}}</span>'
        '<span class="ca-fb"><span style="width: {{a.w}}%; background: {{a.color}}"></span><strong>{{a.value}}</strong></span></div>\n</sc-for>\n</div>\n'
        '<p class="ca-note">42 % des cartes à remettre attendent depuis plus de six mois.</p>\n')
P3 = ('<section aria-labelledby="anciennete" class="v7-panel">\n' + EN.head('anciennete', 'Depuis quand ces cartes attendent', 'Cartes à remettre, selon le temps écoulé depuis l’expédition.') +
      '<div class="v7-pbody en-hebdo">\n' + AGES + '</div>\n</section>\n')
ROW2 = '<div class="en-row2 ca-row2">\n' + P2 + P3 + '</div>\n'

# =============== 3. Territoire : carte et tableau ===============
_mapblk = _old_body[_old_body.index('<div class="carte-duo">'):]
_mapblk = _mapblk[:_mapblk.index('</section>')]
assert '{{map.items}}' in _mapblk
_CHEV = EN._CHEV
TABLE = ('<div class="v7-reg-tab">\n<p class="en-tt" id="tabreg">Régions</p>\n'
         '<div role="table" aria-labelledby="tabreg" class="ca-table">\n'
         '<div role="row" class="ca-tr en-th"><span role="columnheader">Région</span><span role="columnheader">Expédiées</span>'
         '<span role="columnheader">Remises</span><span role="columnheader">À remettre</span><span role="columnheader">Part à remettre</span></div>\n'
         '<sc-for list="{{regRows}}" as="r" hint-placeholder-count="6">\n<div role="row" class="ca-tr" style="background: {{r.bg}}">'
         '<span role="rowheader"><button type="button" onClick="{{r.pick}}" aria-pressed="{{r.pressed}}" class="en-drill">{{r.name}}' + _CHEV + '</button></span>'
         '<span role="cell">{{r.exp}}</span><span role="cell">{{r.liv}}</span><span role="cell">{{r.rem}}</span>'
         '<span role="cell" style="font-weight: {{r.weight}}"><sc-if value="{{r.high}}" hint-placeholder-val="{{false}}">'
         '<svg width="11" height="11" viewBox="0 0 24 24" aria-label="Plus de la moitié à remettre" style="margin-right: 4px; fill: #FAB219"><path d="M12 2 1 21h22L12 2z"></path></svg>'
         '</sc-if>{{r.part}}</span></div>\n</sc-for>\n</div>\n</div>\n')
ZONE = ('<dl class="en-zone" aria-label="Chiffres de la zone">'
        '<div><dt>Cartes expédiées</dt><dd class="en-zv">{{zExp}}</dd><dd class="en-zd">{{zoneLabel}}</dd></div>'
        '<div><dt>Remises</dt><dd class="en-zv">{{zLiv}}</dd><dd class="en-zd">{{zLivPct}} des expédiées</dd></div>'
        '<div><dt>À remettre</dt><dd class="en-zv">{{zRem}}</dd><dd class="en-zd">{{zRemPct}} des expédiées</dd></div></dl>')
TERR = ('<section aria-labelledby="parregion" class="v7-panel">\n'
        '<div class="v7-head"><div><h2 id="parregion" class="en-h2">Cartes à remettre par région</h2>'
        '<p class="en-sub">Carte colorée selon la part des cartes expédiées qui restent à remettre. Cliquez sur une région pour voir ses préfectures.</p></div>'
        + ZONE + '</div>\n<div class="v7-pbody v7-reg">\n<div class="v7-reg-map">\n' + _mapblk + '</div>\n' + TABLE + '</div>\n</section>\n')

# =============== 4. Remise par centre ===============
# 4. Top des centres (7 oct.) : remplace le tableau « Remise des cartes par centre » ; classement par nombre de cartes remises
CENTRES = ('<section aria-labelledby="centres" class="v7-panel">\n' + EN.head('centres', 'Top des centres', '{{zoneLabel}}, classés par nombre de cartes remises') +
           '<div class="v7-pbody ca-cent">\n<sc-if value="{{hasRem}}" hint-placeholder-val="{{true}}">\n'
           '<div role="table" aria-label="Centres qui remettent le plus de cartes" style="font-variant-numeric: tabular-nums">\n'
           '<div role="row" class="ca-rk ca-rkh"><span role="columnheader">Rang</span><span role="columnheader">Centre</span>'
           '<span role="columnheader" style="text-align: right">Cartes remises</span></div>\n'
           '<sc-for list="{{remRows}}" as="c" hint-placeholder-count="5">\n'
           '<div role="row" class="ca-rk"><span role="cell" class="ca-rkn">{{c.rank}}</span>'
           '<span role="rowheader" class="ca-rkc"><span>{{c.name}}</span><span>{{c.place}}</span></span>'
           '<span role="cell" class="ca-rkm"><strong>{{c.metric}}</strong><span>{{c.sub}}</span></span></div>\n'
           '</sc-for>\n</div>\n</sc-if>\n'
           '<sc-if value="{{noRem}}" hint-placeholder-val="{{false}}"><p class="ca-empty">Aucun des centres du classement ne se trouve dans cette région.</p></sc-if>\n'
           '</div>\n</section>\n')

# =============== 5. Plus de cartes que de NIU ===============
_rec = re.search(r'<section aria-labelledby="reconcil".*?</section>', _old_body, re.S).group(0)
_rtab = _rec[_rec.index('<div role="table" aria-label="Réconciliation'):_rec.rindex('</section>')]
_rtab = _rtab.replace('style="flex: 2 1 520px; min-width: 0; display: flex;', 'style="display: flex;', 1)
RECON = ('<section aria-labelledby="reconcil" class="v7-panel">\n' + EN.head('reconcil', 'Plus de cartes que de NIU',
         f'Le BI compte {nf(IMP - JF.NIU)} cartes imprimées de plus que de NIU générés, et {nf(DEM - JF.NIU)} demandes d’impression de plus.') +
         '<div class="v7-pbody ca-rec">\n' + _rtab + '</div>\n</section>\n')

# 7 oct. : bloc « Plus de cartes que de NIU » (RECON) retiré de la page à la demande
# 7 oct. : graphique des impressions par semaine, à la place du parcours (pleine largeur, barres élargies)
_LEGW = ('<div class="en-leg" style="margin-top: 0">'
         '<span><i style="background: #2A78D6"></i>Cartes imprimées</span>'
         '<span><i style="width: 16px; height: 2px; border-radius: 0; background: #1BAF7A"></i>Demandes d’impression</span></div>')
_CHART = EN.HEBDO_CHART.replace('width: 22px; height: {{w.h}}px', 'width: min(30px, 64%); height: {{w.h}}px', 1).replace('min-width: 560px;', 'min-width: 340px;', 1)
assert 'min(30px, 64%)' in _CHART and 'min-width: 340px' in _CHART
_YR = ''.join(f'<span style="position: absolute; right: 0; top: {t}px">{v}</span>' for v, t in ((3, -9), (2, 64), (1, 138), (0, 211)))
REJ_CHART = ('<p aria-live="polite" class="en-read" style="border-left-color: #D03B3B">{{rejRead}}</p>\n'
             '<div style="overflow-x: auto; padding-top: 10px">\n<div style="min-width: 220px; display: flex; gap: 10px">\n'
             '<div aria-hidden="true" style="position: relative; width: 20px; height: 220px; font-size: 12px; color: #4B5A6E; font-variant-numeric: tabular-nums; flex-shrink: 0">' + _YR + '</div>\n'
             '<div style="flex-grow: 1; min-width: 0">\n'
             '<div style="position: relative; height: 220px; border-bottom: 1px solid #9AA7B5; background-image: linear-gradient(#E6EBEF 1px, transparent 1px); background-size: 100% 73.33px">\n'
             '<div style="position: absolute; top: 0; right: 0; bottom: 0; left: 0; display: flex; align-items: flex-end">\n'
             '<sc-for list="{{rejTrend}}" as="r" hint-placeholder-count="12">\n'
             '<button type="button" onMouseEnter="{{r.enter}}" onFocus="{{r.enter}}" aria-label="{{r.aria}}" class="ca-rb" style="background: {{r.band}}">'
             '<span class="ca-rbn">{{r.n}}</span><span class="ca-rbb" style="height: {{r.h}}px; background: {{r.bg}}"></span></button>\n'
             '</sc-for>\n</div>\n</div>\n'
             '<div aria-hidden="true" style="display: flex; margin-top: 6px; font-size: 12px; color: #4B5A6E; font-variant-numeric: tabular-nums">\n'
             '<sc-for list="{{rejTrend}}" as="r" hint-placeholder-count="12"><span style="flex: 1 1 0; text-align: center; white-space: nowrap">{{r.lab}}</span></sc-for>\n'
             '</div>\n</div>\n</div>\n</div>\n'
             '<p class="ca-note">6 demandes rejetées depuis le début, la dernière le 13/03/2026.</p>\n')
REJETS = ('<section aria-labelledby="rejets" class="v7-panel">\n' + EN.head('rejets', 'Demandes rejetées par semaine', 'Mêmes 12 semaines.') +
          '<div class="v7-pbody en-hebdo">\n' + REJ_CHART + '</div>\n</section>\n')
HEBDO = ('<section aria-labelledby="hebdo" class="v7-panel">\n' + EN.head('hebdo', 'Impressions par semaine', '12 dernières semaines complètes.', _LEGW) +
         '<div class="v7-pbody en-hebdo">\n' + _CHART + '</div>\n</section>\n')
# 7 oct. : « Parcours de la carte » (P2) retiré à la demande ; l'ancienneté et le top des centres passent côte à côte
# 7 oct. : impressions et rejets par semaine sur la même ligne
BODY = TITLE + P1 + '<div class="en-row2 ca-row3">\n' + HEBDO + REJETS + '</div>\n' + TERR + '<div class="en-row2 ca-row2">\n' + P3 + CENTRES + '</div>\n'  # 7 oct. : ancienneté et top des centres après le territoire
for h in ('{{rejTrend}}', '{{rejRead}}', '{{trend}}', '{{linePoints}}', '{{ages}}', '{{map.items}}', '{{regRows}}', '{{remRows}}', '{{zExp}}', '{{onRegion}}'):
    assert h in BODY, h

CSS_CA = (
    '.ca-flow{display:flex;flex-direction:column;gap:14px}'
    '.ca-frow{display:grid;grid-template-columns:170px minmax(0,1fr);gap:3px 16px;align-items:center}.ca-arow{grid-template-columns:140px minmax(0,1fr)}'
    '.ca-fl{font-size:13px;font-weight:500;color:#071B35}'
    '.ca-fb{display:flex;align-items:center;gap:10px;min-width:0}.ca-fb>span{height:14px;border-radius:0 4px 4px 0;min-width:3px}'
    '.ca-fb strong{font-size:14px;font-weight:600;color:#071B35;white-space:nowrap;font-variant-numeric:tabular-nums}'
    '.ca-fn{font-size:12px;color:#4B5A6E}'
    '.ca-note{margin:4px 0 0;padding-top:12px;border-top:1px solid #E6EBF0;font-size:13px;color:#4B5A6E}'
    '.ca-row2{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}.ca-p1cards{padding-bottom:40px}'
    '.ca-row3{grid-template-columns:minmax(0,1.7fr) minmax(0,1fr)}'
    '.ca-rb{flex:1 1 0;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:4px;padding:0;border:0;cursor:default}'
    '.ca-rbb{display:block;width:min(16px,60%);border-radius:3px 3px 0 0}.ca-rbn{font-size:12px;font-weight:600;color:#8A1F1F;line-height:1}'
    '.ca-table{min-width:420px;font-variant-numeric:tabular-nums}'
    '.ca-tr{display:grid;grid-template-columns:minmax(116px,1.3fr) repeat(4,minmax(70px,1fr));gap:12px;align-items:center;padding:0 8px;border-top:1px solid #EEF2F5;border-radius:4px}'
    '.ca-tr>span:not(:first-child){text-align:right}.ca-tr.en-th{border-top:0}'
    '.ca-cent{padding-top:12px}'
    '.ca-rk{display:grid;grid-template-columns:36px minmax(0,1fr) minmax(150px,auto);gap:12px;align-items:center;padding:10px 0;border-top:1px solid #EEF2F5}'
    '.ca-rkh{padding:6px 0;border-top:0;font-size:12px;color:#4B5A6E}.ca-rkn{color:#4B5A6E}'
    '.ca-rkc{display:flex;flex-direction:column;min-width:0}.ca-rkc>span:first-child{font-weight:500;color:#071B35}.ca-rkc>span:last-child{font-size:12px;color:#4B5A6E}'
    '.ca-rkm{display:flex;flex-direction:column;align-items:flex-end;text-align:right}.ca-rkm strong{font-weight:600;color:#071B35}.ca-rkm span{font-size:12px;color:#4B5A6E}'
    '.ca-empty{margin:0;padding:20px;border-radius:6px;background:#F1F4F6;font-size:13px;color:#4B5A6E}'
    '@media (max-width:1240px){.ca-tr{gap:8px;padding:0 4px;font-size:13.5px;grid-template-columns:minmax(100px,1.2fr) repeat(4,minmax(62px,1fr))}}'
    '@media (max-width:1100px){.ca-row2{grid-template-columns:minmax(0,1fr)}}'
    '@media (max-width:760px){.ca-row3{grid-template-columns:minmax(0,1fr)}}'
    '@media (max-width:600px){.ca-rec [role=row]{grid-template-columns:minmax(0,1fr) auto !important;row-gap:4px !important}'
    '.ca-rec [role=row]>[role=cell]:nth-child(2){grid-column:1/-1;grid-row:2}.ca-rec [role=row]>[role=cell]:nth-child(3){grid-column:2;grid-row:1}'
    '.ca-frow,.ca-arow{grid-template-columns:minmax(0,1fr)}.ca-frow>span:nth-child(3){display:none}.en-zone{flex-wrap:wrap;row-gap:12px}}'
)


def build():
    html = page('Impression des cartes', 'Cartes.dc.html', p_cartes.FILTERS, BODY, SCRIPT, 2400, '')
    for blk in (bandeau('Cartes.dc.html'), filters(p_cartes.FILTERS)):
        assert html.count(blk) == 1
        html = html.replace(blk, '')
    html = html.replace('\n</style>\n</helmet>', '\n' + V3.CSS + V3.CSS7 + V3.CSS9 + EN.CSS_EN + CSS_CA + '\n</style>\n</helmet>', 1)
    old = ('<div class="bande-bio" aria-hidden="true" style="height: 230px"></div>\n<main style="position: relative; max-width: 1376px; '
           'margin: -230px auto 0; padding: 40px 32px 56px;')
    assert html.count(old) == 1
    html = html.replace(old, old.replace('230px', '220px').replace('padding: 40px', 'padding: 30px'))
    return html
