"""Exploration des données (8 oct. 2026) : remplace la page Qualité et technique (même fichier Technique.dc.html).

Tableau croisé libre : une source, un indicateur, une ventilation en lignes et une en colonnes (facultative),
valeurs en nombres, en % du total ou en % de la ligne ; graphique qui suit le tableau ; export CSV.
Données : build/explo_data.py (marges reprises des autres pages, arrondi contrôlé, totaux exacts).
"""
import json
from common import *
import p_tech as OLD, p_main_v3 as V3, p_enrol_v5 as EN, p_bio_v5 as V5, explo_data as XD

CUBE = json.dumps(XD.cube(), ensure_ascii=False, separators=(',', ':'))
PAL = ['#013781', '#2A78D6', '#6DA7EC', '#FCBA21', '#EC835A', '#1BAF7A', '#8A63D2', '#9AA7B5']

# =============== Bandeau ===============
TITLE = ('<div style="display: flex; flex-direction: column; align-items: flex-start; gap: 10px">\n'
         '<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px 18px; align-self: stretch">'
         '<h1 style="margin: 0; font-size: 30px; font-weight: 600; letter-spacing: -0.015em; color: #FFFFFF">Exploration des données</h1>'
         + EN.FRESH.replace('14/01/2026 à 11h42', '14/01/2026 à 11h59') + '</div>\n'
         f'<p class="xp-intro">Croisez les {XD.N_MEASURES} indicateurs des cinq sources du BI : '
         'choisissez une source, un indicateur, puis une ou deux ventilations.</p>\n</div>\n')


def chips(lst, var, label):
    return (f'<div class="xp-step"><span class="xp-k">{label}</span><div role="group" aria-label="{label}" class="xp-chips">'
            f'<sc-for list="{{{{{lst}}}}}" as="{var}" hint-placeholder-count="5">'
            f'<button type="button" onClick="{{{{{var}.pick}}}}" aria-pressed="{{{{{var}.pressed}}}}" class="xp-chip">{{{{{var}.label}}}}</button>'
            '</sc-for></div></div>\n')


BUILDER = ('<section aria-labelledby="construire" class="v7-panel en-dev">\n' + BRACKETS + EN.head('construire', 'Construire l’analyse') +
           '<div class="v7-pbody xp-build">\n'
           + chips('srcBtns', 's', 'Source') + chips('measBtns', 'm', 'Indicateur') + chips('rowBtns', 'r', 'En lignes')
           + chips('colBtns', 'c', 'En colonnes') + chips('modeBtns', 'v', 'Valeurs') +
           '<sc-if value="{{hasNote}}" hint-placeholder-val="{{false}}"><p class="ab-note">{{note}}</p></sc-if>\n'
           '</div>\n</section>\n')

# =============== Résultat ===============
_DL = ('<a href="{{csvHref}}" download="{{csvName}}" class="xp-dl"><svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" '
       'style="fill: none; stroke: currentColor; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"></path></svg>'
       'Exporter en CSV</a>')
SUMMARY = ('<div class="xp-sum"><p class="en-big"><span class="en-bigv">{{totalTxt}}</span><span class="en-bigu">{{totalUnit}}</span></p>'
           '<sc-if value="{{hasLegend}}" hint-placeholder-val="{{true}}"><div class="en-leg">'
           '<sc-for list="{{legend}}" as="l" hint-placeholder-count="2"><span><i style="background: {{l.color}}"></i>{{l.label}}</span></sc-for></div></sc-if></div>\n')
HCHART = ('<sc-if value="{{hBars}}" hint-placeholder-val="{{true}}"><div role="img" aria-label="{{chartAria}}" class="xp-hb">\n'
          '<sc-for list="{{bars}}" as="b" hint-placeholder-count="6">'
          '<div class="xp-hr"><span class="xp-hl" title="{{b.label}}">{{b.label}}</span><span class="xp-ht">'
          '<span class="xp-hs" style="width: {{b.w}}%"><sc-for list="{{b.segs}}" as="g" hint-placeholder-count="2">'
          '<span title="{{g.tip}}" style="flex: {{g.f}} 1 0; background: {{g.bg}}"></span></sc-for></span></span>'
          '<strong class="xp-hv">{{b.value}}</strong></div>\n'
          '</sc-for>\n</div></sc-if>\n')
VCHART = ('<sc-if value="{{vBars}}" hint-placeholder-val="{{false}}"><div role="img" aria-label="{{chartAria}}" class="xp-vw"><div class="xp-vb">\n'
          '<sc-for list="{{bars}}" as="b" hint-placeholder-count="12">'
          '<div class="xp-vc" title="{{b.tip}}"><span class="xp-vs" style="height: {{b.h}}%">'
          '<sc-for list="{{b.segs}}" as="g" hint-placeholder-count="2"><span style="flex: {{g.f}} 1 0; background: {{g.bg}}"></span></sc-for></span></div>\n'
          '</sc-for>\n</div>\n<div aria-hidden="true" class="xp-vx"><sc-for list="{{bars}}" as="b" hint-placeholder-count="12"><span>{{b.short}}</span></sc-for></div></div></sc-if>\n')
TABLE = ('<div class="ab-tw xp-tw"><div role="table" aria-label="{{resTitle}}" class="xp-table" style="min-width: {{tableMin}}px">\n'
         '<div role="row" class="xp-tr xp-th" style="grid-template-columns: {{gridCols}}"><span role="columnheader">{{rowDimLabel}}</span>'
         '<sc-for list="{{headCols}}" as="h" hint-placeholder-count="3"><span role="columnheader">{{h.t}}</span></sc-for></div>\n'
         '<sc-for list="{{rows}}" as="r" hint-placeholder-count="6"><div role="row" class="xp-tr" style="grid-template-columns: {{gridCols}}">'
         '<span role="rowheader">{{r.label}}</span><sc-for list="{{r.cells}}" as="v" hint-placeholder-count="3"><span role="cell">{{v.t}}</span></sc-for></div></sc-for>\n'
         '<div role="row" class="xp-tr xp-tot" style="grid-template-columns: {{gridCols}}"><span role="rowheader">Total</span>'
         '<sc-for list="{{totCells}}" as="v" hint-placeholder-count="3"><span role="cell">{{v.t}}</span></sc-for></div>\n'
         '</div></div>\n')
RESULT = ('<section aria-labelledby="resultat" class="v7-panel">\n'
          '<div class="v7-head"><div><h2 id="resultat" class="en-h2">{{resTitle}}</h2><p class="en-sub">{{resSub}}</p></div>' + _DL + '</div>\n'
          '<div class="v7-pbody en-hebdo xp-res">\n' + SUMMARY + '<div class="xp-chart">' + HCHART + VCHART + '</div>\n<div class="xp-tsep">' + TABLE + '</div>\n</div>\n</section>\n')

BODY = TITLE + BUILDER + RESULT

SCRIPT = '''class Component extends DCLogic {
  renderVals() {
    const st = this.state || {};
    const D = ''' + CUBE + ''';
    const PAL = ''' + json.dumps(PAL) + ''';
    const nf = (n) => Math.round(n).toLocaleString('fr-FR').replace(/[\\u202f\\u00a0]/g, ' ');
    const pc = (x) => x.toFixed(1).replace('.', ',') + ' %';
    const low = (s) => s.charAt(0).toLowerCase() + s.slice(1);
    const src = D.sources.find((s) => s.key === st.src) || D.sources[0];
    const meas = src.measures.find((m) => m.key === st.m) || src.measures[0];
    const dims = meas.dims;
    const r = dims.includes(st.r) ? st.r : (dims.includes('region') ? 'region' : dims.includes('mois') && dims.length === 2 ? 'mois' : dims[0]);
    const colOk = (d) => d !== r && !D.dims[d].rowsOnly && !(r === 'mois' && d === 'annee');
    const auto = { enrol: 'sexe', cartes: 'sexe', auth: 'taut', idps: 'terr' }[src.key];
    let c = (st.c === undefined || st.c === 'auto') ? auto : st.c;
    if (!c || c === 'none' || !dims.includes(c) || !colOk(c)) c = null;
    const mode = (st.mode === 'pr' && !c) ? 'n' : (st.mode || 'n');
    const T = meas.total, rv = meas.vals[r], rm = meas.marg[r];
    let M;
    if (c) {
      const k1 = r + '|' + c, k2 = c + '|' + r;
      if (meas.pairs[k1]) M = meas.pairs[k1];
      else { const t = meas.pairs[k2]; M = rv.map((_, i) => t.map((row) => row[i])); }
    } else M = rm.map((v) => [v]);
    const idx = rv.map((_, i) => i);
    if (D.dims[r].sort === 'value') idx.sort((a, b) => rm[b] - rm[a]);
    const cv = c ? meas.vals[c] : [meas.label];
    const cm = c ? meas.marg[c] : [T];
    const cidx = cv.map((_, j) => j);
    if (c && D.dims[c].sort === 'value') cidx.sort((a, b) => cm[b] - cm[a]);
    const color = (k) => c ? PAL[k % PAL.length] : '#2A78D6';
    const fmt = (v, rt) => mode === 'n' ? nf(v) : mode === 'pt' ? pc(T ? v / T * 100 : 0) : pc(rt ? v / rt * 100 : 0);
    const T_ = (t) => ({ t: t });
    const headCols = cidx.map((j) => cv[j]).concat(c ? ['Total'] : []).map(T_);
    const rows = idx.map((i) => ({ label: rv[i],
      cells: cidx.map((j) => fmt(M[i][j], rm[i])).concat(c ? [mode === 'pr' ? (rm[i] ? '100,0 %' : '–') : fmt(rm[i], rm[i])] : []).map(T_) }));
    const totCells = cidx.map((j) => mode === 'n' ? nf(cm[j]) : pc(T ? cm[j] / T * 100 : 0)).concat(c ? [mode === 'n' ? nf(T) : '100,0 %'] : []).map(T_);
    const nCols = headCols.length;
    const gridCols = 'minmax(150px, 1.6fr) repeat(' + nCols + ', minmax(84px, 1fr))';
    const tableMin = 170 + nCols * 92;
    // graphique
    const vBars = r === 'mois';
    const maxRow = Math.max(1, ...rm);
    const bars = idx.map((i) => {
      const rt = rm[i];
      return { label: rv[i], tip: rv[i] + ' : ' + nf(rt), short: rv[i].startsWith('janv.') ? rv[i] : rv[i].split(' ')[0],
        value: mode === 'pr' ? nf(rt) : fmt(rt, rt),
        w: (mode === 'pr' ? (rt ? 100 : 0) : rt / maxRow * 100).toFixed(2),
        h: (rt / maxRow * 100).toFixed(2),
        segs: cidx.map((j, k) => ({ f: M[i][j], bg: color(k), tip: (c ? cv[j] + ' : ' : '') + nf(M[i][j]) })).filter((g) => g.f > 0) };
    });
    const legend = c ? cidx.map((j, k) => ({ label: cv[j], color: color(k) })) : [];
    const title = meas.label + ' par ' + low(D.dims[r].label) + (c ? ' et par ' + low(D.dims[c].label) : '');
    const span = meas.vals.mois ? ', de ' + meas.vals.mois[0] + ' à ' + meas.vals.mois[meas.vals.mois.length - 1] : '';
    // export CSV (séparateur point-virgule, pour Excel en français)
    const esc = (s) => /[;"\\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
    const lines = [[D.dims[r].label].concat(cidx.map((j) => cv[j])).concat(c ? ['Total'] : [])];
    idx.forEach((i) => lines.push([rv[i]].concat(cidx.map((j) => String(M[i][j]))).concat(c ? [String(rm[i])] : [])));
    lines.push(['Total'].concat(cidx.map((j) => String(cm[j]))).concat(c ? [String(T)] : []));
    const csv = lines.map((l) => l.map(esc).join(';')).join('\\r\\n');
    const set = (o) => () => this.setState(o);
    const btn = (label, on, pick) => ({ label: label, pressed: on ? 'true' : 'false', pick: pick });
    return {
      srcBtns: D.sources.map((s) => btn(s.label, s.key === src.key, set({ src: s.key, m: null, r: null, c: 'auto', mode: st.mode === 'pr' ? 'n' : st.mode }))),
      measBtns: src.measures.map((m) => btn(m.label, m.key === meas.key, set({ m: m.key }))),
      rowBtns: dims.map((d) => btn(D.dims[d].label, d === r, set({ r: d, c: d === c ? 'none' : (c || 'none') }))),
      colBtns: [btn('Aucune', !c, set({ c: 'none' }))].concat(dims.filter(colOk).map((d) => btn(D.dims[d].label, d === c, set({ c: d })))),
      modeBtns: [btn('Nombres', mode === 'n', set({ mode: 'n' })), btn('% du total', mode === 'pt', set({ mode: 'pt' }))]
        .concat(c ? [btn('% de la ligne', mode === 'pr', set({ mode: 'pr' }))] : []),
      hasNote: !!src.note, note: src.note,
      resTitle: title, resSub: src.label + span + '.',
      totalTxt: nf(T), totalUnit: low(meas.label) + ' au total',
      hasLegend: legend.length > 0, legend: legend,
      hBars: !vBars, vBars: vBars, bars: bars, chartAria: title,
      rowDimLabel: D.dims[r].label, headCols: headCols, rows: rows, totCells: totCells, gridCols: gridCols, tableMin: tableMin,
      csvHref: 'data:text/csv;charset=utf-8,' + encodeURIComponent('\\ufeff' + csv), csvName: 'exploration-' + src.key + '-' + meas.key + '.csv'
    };
  }
}'''

CSS_XP = (
    '.xp-intro{margin:0;max-width:720px;font-size:14px;color:rgba(255,255,255,.82)}.xp-chart{min-height:250px}'
    '.xp-tw{max-height:452px;overflow:auto}.xp-th{position:sticky;top:0;z-index:1;background:#FFFFFF}.xp-tot{position:sticky;bottom:0;z-index:1;background:#FFFFFF}'
    '.xp-build{display:flex;flex-direction:column;gap:14px;padding-bottom:44px}'
    '.xp-step{display:grid;grid-template-columns:120px minmax(0,1fr);gap:8px 16px;align-items:start}'
    '.xp-k{padding-top:8px;font-size:12.5px;font-weight:600;color:#4B5A6E;text-transform:uppercase;letter-spacing:.04em}'
    '.xp-chips{display:flex;flex-wrap:wrap;gap:8px}'
    '.xp-chip{min-height:36px;padding:0 14px;border:1px solid #D5DEE8;border-radius:999px;background:#FFFFFF;font-family:inherit;font-size:13.5px;font-weight:500;color:#071B35;cursor:pointer}'
    '.xp-chip:hover{border-color:#013781}'
    '.xp-chip[aria-pressed=true]{background:#013781;border-color:#013781;color:#FFFFFF;font-weight:600}'
    '.xp-dl{display:inline-flex;align-items:center;gap:8px;min-height:38px;padding:0 16px;border-radius:999px;background:#FCBA21;color:#071B35;font-size:13.5px;font-weight:600;text-decoration:none;white-space:nowrap}'
    '.xp-dl:hover{background:#FFD25E;color:#071B35}'
    '.xp-res{gap:20px}.xp-sum{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:10px 24px}'
    '.xp-hb{display:flex;flex-direction:column;gap:8px}'
    '.xp-hr{display:grid;grid-template-columns:minmax(120px,220px) minmax(0,1fr) minmax(76px,auto);gap:14px;align-items:center}'
    '.xp-hl{font-size:13px;font-weight:500;color:#071B35;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'
    '.xp-ht{display:block;height:18px;background:#F1F4F6;border-radius:0 4px 4px 0}'
    '.xp-hs{display:flex;gap:1px;height:18px;min-width:2px;border-radius:0 4px 4px 0;overflow:hidden}.xp-hs>span{min-width:0}'
    '.xp-hv{text-align:right;font-weight:600;color:#071B35;font-variant-numeric:tabular-nums;white-space:nowrap}'
    '.xp-vw{overflow-x:auto}.xp-vb{display:flex;align-items:flex-end;gap:4px;height:220px;min-width:520px;border-bottom:1px solid #9AA7B5;'
    'background-image:linear-gradient(#E6EBEF 1px,transparent 1px);background-size:100% 55px}'
    '.xp-vc{flex:1 1 0;height:100%;display:flex;align-items:flex-end;justify-content:center}'
    '.xp-vs{display:flex;flex-direction:column-reverse;gap:1px;width:min(26px,70%);border-radius:3px 3px 0 0;overflow:hidden}.xp-vs>span{min-height:0}'
    '.xp-vx{display:flex;gap:4px;min-width:520px;margin-top:6px;font-size:11.5px;color:#4B5A6E}.xp-vx>span{flex:1 1 0;text-align:center;white-space:nowrap;overflow:visible}'
    '.xp-tsep{padding-top:18px;border-top:1px solid #E6EBF0}'
    '.xp-table{font-variant-numeric:tabular-nums}'
    '.xp-tr{display:grid;gap:10px;align-items:center;padding:10px 8px;border-top:1px solid #EEF2F5}.xp-tr>span:not(:first-child){text-align:right}'
    '.xp-tr>span:first-child{font-weight:500;color:#071B35}'
    '.xp-th{align-items:end;padding-top:4px;padding-bottom:8px;border-top:0;font-size:12px;line-height:1.35;color:#4B5A6E}.xp-th>span:first-child{font-weight:400;color:#4B5A6E}'
    '.xp-tot{border-top:1px solid #C5CFDA;font-weight:600}.xp-tot>span{color:#071B35}'
    '.xp-tr>span:last-child{font-weight:600}'
    '@media (max-width:700px){.xp-intro{display:none}.xp-chart{min-height:0}.xp-step{grid-template-columns:minmax(0,1fr);gap:6px}.xp-k{padding-top:0}'
    '.xp-hr{grid-template-columns:minmax(90px,120px) minmax(0,1fr) auto;gap:8px}.xp-chip{min-height:34px;padding:0 12px;font-size:13px}}'
)


def build():
    html = page('Exploration des données', 'Technique.dc.html', OLD.FILTERS, BODY, SCRIPT, 1663, '')
    for blk in (bandeau('Technique.dc.html'), filters(OLD.FILTERS)):
        assert html.count(blk) == 1
        html = html.replace(blk, '')
    html = html.replace('\n</style>\n</helmet>', '\n' + V3.CSS + V3.CSS7 + V3.CSS9 + EN.CSS_EN + V5.CSS_AB + CSS_XP + '\n</style>\n</helmet>', 1)
    old = ('<div class="bande-bio" aria-hidden="true" style="height: 230px"></div>\n<main style="position: relative; max-width: 1376px; '
           'margin: -230px auto 0; padding: 40px 32px 56px;')
    assert html.count(old) == 1
    html = html.replace(old, old.replace('230px', '220px').replace('padding: 40px', 'padding: 30px'))
    return html
