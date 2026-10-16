"""Onglet ABIS : déduplication ABIS, adjudication, qualité des captures (chiffres du BI actuel ; détail par centre illustratif)."""
from common import *

FILTERS = PERIODE + REGION + DIVIDER + select('Modalité', ['Toutes les modalités', 'Empreintes digitales', 'Iris', 'Visage'], min_w=190)

NAVY, MUTED = '#071B35', '#4B5A6E'
I_OK = '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; fill: none; stroke: #2A78D6; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round"><circle cx="12" cy="12" r="10"></circle><polyline points="8 12.5 11 15.5 16 9.5"></polyline></svg>'
I_WARN = '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; fill: #FAB219; stroke: none"><path d="M12 2 1 21h22L12 2z"></path></svg>'
I_INFO = '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; fill: none; stroke: #4B5A6E; stroke-width: 2; stroke-linecap: round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="11" x2="12" y2="17"></line><line x1="12" y1="7" x2="12.01" y2="7"></line></svg>'

ICONS = {
    'finger': '<svg width="28" height="28" viewBox="0 0 28 28" aria-hidden="true" style="flex-shrink: 0; fill: none; stroke: #013781; stroke-width: 1.8; stroke-linecap: round">'
              '<path d="M7 20c-1-2-1.5-4-1.5-6.5a8.5 8.5 0 0 1 17 0"></path><path d="M10.5 22c-1-2.2-1.5-4.5-1.5-8.5a5 5 0 0 1 10 0c0 2-.2 3.5-.6 5"></path>'
              '<path d="M14 24c-1.2-3-1.6-6.2-1.6-10.5a1.6 1.6 0 0 1 3.2 0c0 4 .6 6.8 2 9.5"></path><path d="M22.5 17.5c-.2 1.6-.6 3-1.2 4.3"></path></svg>',
    'iris': '<svg width="28" height="28" viewBox="0 0 28 28" aria-hidden="true" style="flex-shrink: 0; fill: none; stroke: #013781; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round">'
            '<path d="M3 14s4-7 11-7 11 7 11 7-4 7-11 7S3 14 3 14z"></path><circle cx="14" cy="14" r="4"></circle><circle cx="14" cy="14" r="1.2" fill="#013781"></circle></svg>',
    'face': '<svg width="28" height="28" viewBox="0 0 28 28" aria-hidden="true" style="flex-shrink: 0; fill: none; stroke: #013781; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round">'
            '<path d="M4 9V5h4M20 5h4v4M24 19v4h-4M8 23H4v-4"></path><circle cx="14" cy="12" r="4"></circle><path d="M8 21c1.2-3 3.4-4.5 6-4.5s4.8 1.5 6 4.5"></path></svg>',
}


def nf(n):
    return f'{n:,}'.replace(',', ' ')


def dec(x):
    return f'{x:.2f}'.replace('.', ',').replace('-', '−')


# ---------- 1. Déduplication ABIS ----------
WEEKS = 39  # semaines 1 à 39 de 2026
spikes = {29: (995, 1236)}  # semaine ISO 29 : du 13 au 19/07/2026
cols = []
for w in range(1, WEEKS + 1):
    ins, ide = spikes.get(w, (0, 0))
    h1, h2 = ins / 1236 * 64, ide / 1236 * 64
    tip = f'Semaine {w} : {nf(ide)} recherches de doublons, {nf(ins)} insertions' if ide else f'Semaine {w} : aucune requête'
    cols.append(f'<div title="{tip}" style="flex: 1 1 0; display: flex; align-items: flex-end; justify-content: center; gap: 1px; height: 64px">'
                f'<span style="width: 40%; height: {max(h2, 1):.1f}px; background: {"#013781" if ide else "#DCE3E9"}; border-radius: 2px 2px 0 0"></span>'
                f'<span style="width: 40%; height: {max(h1, 1):.1f}px; background: {"#6DA7EC" if ins else "#DCE3E9"}; border-radius: 2px 2px 0 0"></span></div>')
months = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.']

ABIS = '''<section aria-labelledby="abis" style="position: relative; background: #FFFFFF; border-radius: 8px; padding: 36px 40px; box-sizing: border-box; display: flex; flex-direction: column; gap: 28px">
''' + BRACKETS + '''<div style="display: flex; flex-wrap: wrap; gap: 24px 56px; align-items: flex-start">
<div style="flex: 1 1 340px; display: flex; flex-direction: column; gap: 6px">
<h2 id="abis" style="margin: 0; font-size: 15px; font-weight: 500; color: #4B5A6E">Recherches de doublons dans l’ABIS</h2>
<span style="font-size: clamp(40px, 9vw, 56px); font-weight: 600; letter-spacing: -0.02em; line-height: 1.05">1 236</span>
<p style="margin: 4px 0 0; font-size: 15px">995 dossiers insérés dans la base biométrique.</p>
<div style="display: flex; flex-wrap: wrap; gap: 8px 20px; margin-top: 8px; font-size: 13px; color: #4B5A6E">
<span style="display: inline-flex; align-items: center; gap: 6px">''' + I_OK + '''0 erreur d’identification</span>
<span style="display: inline-flex; align-items: center; gap: 6px">''' + I_OK + '''0 erreur d’insertion</span>
</div>
</div>
<div style="flex: 2 1 520px; min-width: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 1px; background: #E6EBEF; border: 1px solid #E6EBEF; border-radius: 6px; overflow: hidden">
<div style="background: #FFFFFF; padding: 16px 18px; display: flex; flex-direction: column; gap: 4px">
<span style="font-size: 13px; color: #4B5A6E">Recherches sans insertion</span>
<span style="font-size: 24px; font-weight: 600">241</span>
<span style="font-size: 12px; color: #4B5A6E">1 236 recherches, 995 insertions</span>
</div>
<div style="background: #FFFFFF; padding: 16px 18px; display: flex; flex-direction: column; gap: 6px">
<span style="font-size: 13px; color: #4B5A6E">Inscriptions passées par l’ABIS</span>
<span style="font-size: 24px; font-weight: 600">0,03 %</span>
<span aria-hidden="true" style="height: 6px; background: #EEF2F5; border-radius: 3px"><span style="display: block; width: 2px; height: 6px; background: #013781; border-radius: 3px"></span></span>
<span style="font-size: 12px; color: #4B5A6E">995 sur 3 278 239 inscriptions</span>
</div>
<div style="background: #FFFFFF; padding: 16px 18px; display: flex; flex-direction: column; gap: 4px">
<span style="font-size: 13px; color: #4B5A6E">Jours avec activité</span>
<span style="font-size: 24px; font-weight: 600">1</span>
<span style="font-size: 12px; color: #4B5A6E">Dernière requête le 13/07/2026 à 11h59</span>
</div>
</div>
</div>
<div style="display: flex; flex-direction: column; gap: 8px">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 6px 24px; font-size: 13px; color: #4B5A6E">
<span style="font-weight: 500; color: #071B35">Requêtes ABIS par semaine, 2026</span>
<span style="display: flex; gap: 18px"><span style="display: inline-flex; align-items: center; gap: 6px"><span style="width: 10px; height: 10px; border-radius: 2px; background: #013781"></span>Recherches de doublons</span><span style="display: inline-flex; align-items: center; gap: 6px"><span style="width: 10px; height: 10px; border-radius: 2px; background: #6DA7EC"></span>Insertions</span></span>
</div>
<div style="overflow-x: auto"><div style="min-width: 640px">
<div role="img" aria-label="Requêtes ABIS par semaine en 2026 : une seule semaine active, celle du 13 juillet, avec 1 236 recherches et 995 insertions" style="display: flex; gap: 3px; border-bottom: 1px solid #9AA7B5">''' + ''.join(cols) + '''</div>
<div aria-hidden="true" style="display: grid; grid-template-columns: repeat(9, minmax(0, 1fr)); font-size: 12px; color: #4B5A6E; padding-top: 4px">''' + ''.join(f'<span>{m}</span>' for m in months) + '''</div>
</div></div>
</div>
</section>
'''

# ---------- 2. Adjudication ----------
def step(label, value, sub='', strong=False, stacked=False):
    return (f'<div style="flex: {"0 0 auto" if stacked else "1 1 150px"}; min-width: 0; border: 1px solid #DCE3E9; border-radius: 6px; padding: 12px 14px; display: flex; flex-direction: column; gap: 2px; background: {"#F7F9FB" if not strong else "#FFFFFF"}">'
            f'<span style="font-size: 12.5px; color: #4B5A6E">{label}</span><span style="font-size: 22px; font-weight: 600">{value}</span>'
            + (f'<span style="font-size: 12px; color: #4B5A6E">{sub}</span>' if sub else '') + '</div>')


ARROW = '<svg width="22" height="14" viewBox="0 0 22 14" aria-hidden="true" style="flex-shrink: 0; align-self: center"><path d="M1 7 H19 M14 2 L20 7 L14 12" fill="none" stroke="#9AA7B5" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path></svg>'

ADJ = '''<section aria-labelledby="adjudication" style="''' + CARD + '''; display: flex; flex-direction: column; gap: 18px">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: 8px 24px">
<div>
<h2 id="adjudication" style="''' + H2 + '''">Adjudication des doublons</h2>
<p style="''' + SUB + '''">Un agent tranche quand l’ABIS signale une ressemblance.</p>
</div>
<span role="status" style="display: inline-flex; align-items: center; gap: 8px; min-height: 36px; padding: 4px 12px; border-radius: 6px; background: #FFF5DA; font-size: 13px; color: #6B4A00">''' + I_WARN + '''<strong style="font-weight: 600">Aucun dossier reçu</strong></span>
</div>
<div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: stretch">
''' + step('Ressemblances signalées', '0') + ARROW + step('En attente d’un agent', '0') + ARROW + step('Dossiers traités', '0') + ARROW + '''
<div style="flex: 1 1 200px; min-width: 0; display: flex; flex-direction: column; gap: 6px">
''' + step('HIT : doublon confirmé', '0', stacked=True) + step('NO HIT : pas de doublon', '0', stacked=True) + '''
</div>
</div>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px 24px; padding-top: 14px; border-top: 1px solid #EEF2F5">
<div style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 13px; color: #4B5A6E">Taux de traitement</span><span style="font-size: 20px; font-weight: 600">—</span><span style="font-size: 12px; color: #4B5A6E">aucun dossier</span></div>
<div style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 13px; color: #4B5A6E">Erreurs d’adjudication</span><span style="font-size: 20px; font-weight: 600">0</span><span style="font-size: 12px; color: #4B5A6E">taux : —</span></div>
<div style="display: flex; gap: 10px; align-items: flex-start; padding: 12px 14px; border-radius: 6px; background: #FFF5DA">''' + I_WARN + '''
<div style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 13px; color: #6B4A00">Rejets pour doublon à l’enrôlement</span><span style="font-size: 20px; font-weight: 600">16 002</span><span style="font-size: 12px; color: #6B4A00">contre 0 doublon confirmé ici</span></div>
</div>
</div>
</section>
'''

# ---------- 3. Qualité des captures ----------
LEVELS = [('Faible', '#B7D3F6'), ('Moyen', '#6DA7EC'), ('Excellent', '#184F95'), ('Non classé', '#C5CFDA')]


def modality(icon, name, excellent, parts, score, smin, smax, extra='', warn=''):
    seg = ''.join(f'<div title="{lab} : {v} %" style="width: {v}%; background: {col}"></div>' for (lab, col), v in zip(LEVELS, parts) if v > 0)
    leg = ''.join(f'<span style="display: inline-flex; align-items: center; gap: 5px"><span style="width: 9px; height: 9px; border-radius: 2px; background: {col}"></span>{lab}&nbsp;{v}&nbsp;%</span>'
                  for (lab, col), v in zip(LEVELS, parts) if v > 0)
    pos = (score - smin) / (smax - smin) * 100
    return f'''<div style="flex: 1 1 300px; min-width: 0; border: 1px solid #DCE3E9; border-radius: 8px; padding: 20px 22px; display: flex; flex-direction: column; gap: 12px">
<div style="display: flex; align-items: center; gap: 10px">{ICONS[icon]}<h3 style="margin: 0; font-size: 16px; font-weight: 600">{name}</h3></div>
<div style="display: flex; align-items: baseline; gap: 8px"><span style="font-size: 32px; font-weight: 600; letter-spacing: -0.01em">{excellent}&nbsp;%</span><span style="font-size: 13px; color: #4B5A6E">de captures excellentes</span></div>
<div role="img" aria-label="{name} : {', '.join(f'{lab} {v} %' for (lab, _), v in zip(LEVELS, parts) if v > 0)}" style="display: flex; gap: 2px; height: 12px; border-radius: 3px; overflow: hidden">{seg}</div>
<div style="display: flex; flex-wrap: wrap; gap: 4px 14px; font-size: 12px; color: #4B5A6E">{leg}</div>
<div style="padding-top: 12px; border-top: 1px solid #EEF2F5; display: flex; flex-direction: column; gap: 6px">
<div style="display: flex; justify-content: space-between; align-items: baseline; gap: 12px"><span style="font-size: 13px; color: #4B5A6E">Score moyen</span><strong style="font-size: 16px; font-weight: 600">{dec(score)}</strong></div>
<div role="img" aria-label="Scores de {dec(smin)} à {dec(smax)}, moyenne {dec(score)}" style="position: relative; height: 14px">
<span style="position: absolute; left: 0; right: 0; top: 6px; height: 2px; background: #C5CFDA"></span>
<span style="position: absolute; left: 0; top: 2px; width: 2px; height: 10px; background: #9AA7B5"></span>
<span style="position: absolute; right: 0; top: 2px; width: 2px; height: 10px; background: #9AA7B5"></span>
<span style="position: absolute; left: calc({pos:.1f}% - 5px); top: 2px; width: 10px; height: 10px; border-radius: 5px; background: #013781"></span>
</div>
<div style="display: flex; justify-content: space-between; font-size: 12px; color: #4B5A6E; font-variant-numeric: tabular-nums"><span>min {dec(smin)}</span><span>max {dec(smax)}</span></div>
{extra}{warn}
</div>
</div>'''


FINGER_EXTRA = '<div style="display: flex; justify-content: space-between; align-items: baseline; gap: 12px"><span style="font-size: 13px; color: #4B5A6E">Indice de fiabilité (NBPK)</span><strong style="font-size: 16px; font-weight: 600">44,36</strong></div><span style="font-size: 12px; color: #4B5A6E">de 11 à 80</span>'
FACE_WARN = '<span style="display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px; color: #6B4A00">' + I_WARN + 'Scores hors de l’échelle 0–255</span>'

QUALITY = '''<section aria-labelledby="qualite" style="''' + CARD + '''; display: flex; flex-direction: column; gap: 16px">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 4px 24px">
<div>
<h2 id="qualite" style="''' + H2 + '''">Qualité des captures biométriques</h2>
<p style="''' + SUB + '''">Part des captures par niveau de qualité, et score moyen par modalité.</p>
</div>
<span style="font-size: 13px; color: #4B5A6E">Dernière capture le 29/06/2026 à 15h15</span>
</div>
<div style="display: flex; flex-wrap: wrap; gap: 16px">
''' + modality('finger', 'Empreintes digitales', 88, [0, 10, 88, 2], 106.69, 38, 196, FINGER_EXTRA) \
    + modality('iris', 'Iris', 100, [0, 0, 100, 0], 82.83, 80, 86) \
    + modality('face', 'Visage', 98, [1, 0, 98, 1], 196.66, -274, 452, '', FACE_WARN) + '''
</div>
</section>
'''

CENTRES = '''<section aria-labelledby="centres-qualite" style="''' + CARD + '''; display: flex; flex-direction: column; gap: 12px">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-end; gap: 12px 24px">
<div>
<h2 id="centres-qualite" style="''' + H2 + '''">Centres où la qualité est la plus basse</h2>
<p style="''' + SUB + '''">{{modLabel}}, classés de la plus faible part de captures excellentes à la plus forte.</p>
</div>
<div role="group" aria-label="Choisir une modalité" style="display: flex; gap: 4px; padding: 3px; border-radius: 8px; background: #F1F4F6">
<sc-for list="{{modTabs}}" as="m" hint-placeholder-count="3">
<button type="button" onClick="{{m.pick}}" aria-pressed="{{m.pressed}}" style="min-height: 40px; padding: 0 14px; border: 0; border-radius: 6px; background: {{m.bg}}; box-shadow: {{m.shadow}}; font-family: inherit; font-size: 13px; font-weight: 600; color: #071B35; cursor: pointer">{{m.label}}</button>
</sc-for>
</div>
</div>
<div style="overflow-x: auto">
<div role="table" aria-label="Qualité des captures par centre" style="min-width: 760px; font-variant-numeric: tabular-nums">
<div role="row" style="display: grid; grid-template-columns: minmax(220px, 1.4fr) minmax(170px, 1fr) 110px minmax(220px, 1.6fr) 90px; gap: 16px; padding: 6px 0; font-size: 12px; color: #4B5A6E">
<span role="columnheader">Centre</span><span role="columnheader">Préfecture, région</span><span role="columnheader" style="text-align: right">Captures</span><span role="columnheader">Captures excellentes</span><span role="columnheader" style="text-align: right">Faibles</span>
</div>
<sc-for list="{{centres}}" as="c" hint-placeholder-count="6">
<div role="row" style="display: grid; grid-template-columns: minmax(220px, 1.4fr) minmax(170px, 1fr) 110px minmax(220px, 1.6fr) 90px; gap: 16px; align-items: center; padding: 10px 0; border-top: 1px solid #EEF2F5">
<span role="rowheader" style="font-weight: 500">{{c.name}}</span>
<span role="cell" style="color: #4B5A6E">{{c.place}}</span>
<span role="cell" style="text-align: right">{{c.n}}</span>
<span role="cell" style="display: flex; align-items: center; gap: 10px"><span style="flex-grow: 1; height: 10px; background: #E3EAF3; border-radius: 0 4px 4px 0"><span style="display: block; height: 10px; width: {{c.w}}%; background: #184F95; border-radius: 0 4px 4px 0"></span></span><span style="width: 56px; text-align: right; font-weight: {{c.weight}}">{{c.exc}}</span></span>
<span role="cell" style="text-align: right">{{c.low}}</span>
</div>
</sc-for>
</div>
</div>
</section>
'''

BODY = title('ABIS : déduplication et qualité des captures') + ABIS + ADJ + QUALITY + CENTRES

SCRIPT = r'''class Component extends DCLogic {
  renderVals() {
    const st = this.state || {};
    const mod = st.mod || 'finger';
    const nf = (n) => Math.round(n).toLocaleString('fr-FR').replace(/[  ]/g, ' ');
    const pct = (x) => x.toFixed(1).replace('.', ',') + ' %';
    const C = [
      ['Centre n° 60412', 'Kpendjal, Savanes', 4210, [71.4, 3.8], [97.8, 0.4], [92.3, 2.6]],
      ['Centre n° 60227', 'Oti, Savanes', 3480, [76.9, 2.9], [98.6, 0.2], [94.8, 1.9]],
      ['Centre n° 50318', 'Dankpen, Kara', 2960, [79.2, 2.1], [99.1, 0.1], [95.6, 1.4]],
      ['EPP Worgou G/A', 'Tône, Savanes', 12404, [82.5, 1.4], [99.4, 0], [96.9, 1.1]],
      ['Lycée Nassable', 'Tône, Savanes', 10109, [84.1, 0.9], [99.7, 0], [97.4, 0.8]],
      ['CEG Baguida Centre', 'Golfe, Grand Lomé', 15971, [86.3, 0.6], [99.9, 0], [98.1, 0.5]]
    ];
    const idx = { finger: 3, iris: 4, face: 5 }[mod];
    const centres = C.map((c) => ({ name: c[0], place: c[1], n: nf(c[2]), exc: pct(c[idx][0]), w: c[idx][0].toFixed(1),
      weight: c[idx][0] < 80 ? '600' : '400', low: pct(c[idx][1]) })).sort((a, b) => parseFloat(a.w) - parseFloat(b.w));
    const labels = { finger: 'Empreintes digitales', iris: 'Iris', face: 'Visage' };
    const modTabs = ['finger', 'iris', 'face'].map((k) => ({ label: labels[k], pressed: k === mod ? 'true' : 'false',
      bg: k === mod ? '#FFFFFF' : 'transparent', shadow: k === mod ? '0 1px 2px rgba(7, 27, 53, 0.15)' : 'none',
      pick: () => this.setState({ mod: k }) }));
    return { centres: centres, modTabs: modTabs, modLabel: labels[mod] };
  }
}'''

FOOTER = ''


def build():
    return page('ABIS', 'Biometrie.dc.html', FILTERS, BODY, SCRIPT, 2140, FOOTER)
