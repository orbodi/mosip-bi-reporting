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


def chips(lst, var, label, hint=''):
    h = f'<span class="xp-kh">{hint}</span>' if hint else ''
    return (f'<div class="xp-step"><span class="xp-k">{label}{h}</span><div role="group" aria-label="{label}" class="xp-chips">'
            f'<sc-for list="{{{{{lst}}}}}" as="{var}" hint-placeholder-count="5">'
            f'<button type="button" onClick="{{{{{var}.pick}}}}" aria-pressed="{{{{{var}.pressed}}}}" class="xp-chip">{{{{{var}.label}}}}</button>'
            '</sc-for></div></div>\n')


BUILDER = ('<section aria-labelledby="construire" class="v7-panel en-dev">\n' + BRACKETS + EN.head('construire', 'Construire l’analyse') +
           '<div class="v7-pbody xp-build">\n'
           + chips('srcBtns', 's', 'Source') + chips('measBtns', 'm', 'Indicateurs', 'un ou plusieurs') + chips('rowBtns', 'r', 'En lignes')
           + '<sc-if value="{{isGeo}}" hint-placeholder-val="{{true}}">' + chips('lvBtns', 'l', 'Niveau', 'de région à centre')
           + chips('zoneBtns', 'z', 'Zone', 'cliquez une ligne pour descendre') + '</sc-if>\n'
           + chips('colBtns', 'c', 'En colonnes') + chips('modeBtns', 'v', 'Valeurs') +
           '<sc-if value="{{hasNote}}" hint-placeholder-val="{{false}}"><p class="ab-note">{{note}}</p></sc-if>\n'
           '</div>\n</section>\n')

# =============== Résultat ===============
_DL = ('<a href="{{csvHref}}" download="{{csvName}}" class="xp-dl"><svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" '
       'style="fill: none; stroke: currentColor; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"></path></svg>'
       'Exporter en CSV</a>')
SUMMARY = ('<div class="xp-sum"><sc-if value="{{showBig}}" hint-placeholder-val="{{true}}"><p class="en-big"><span class="en-bigv">{{totalTxt}}</span><span class="en-bigu">{{totalUnit}}</span></p></sc-if>'
           '<sc-if value="{{hasLegend}}" hint-placeholder-val="{{true}}"><div class="en-leg xp-leg">'
           '<sc-for list="{{legend}}" as="l" hint-placeholder-count="2"><span><i style="background: {{l.color}}"></i>{{l.label}} <strong>{{l.val}}</strong></span></sc-for></div></sc-if></div>\n')
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
HMULTI = ('<sc-if value="{{hMulti}}" hint-placeholder-val="{{false}}"><div role="img" aria-label="{{chartAria}}" class="xp-hb">\n'
          '<sc-for list="{{bars}}" as="b" hint-placeholder-count="6">'
          '<div class="xp-hr xp-hrm"><span class="xp-hl" title="{{b.label}}">{{b.label}}</span><span class="xp-mb">'
          '<sc-for list="{{b.items}}" as="it" hint-placeholder-count="2"><span class="xp-mi" title="{{it.tip}}"><span class="xp-mt">'
          '<span style="width: {{it.w}}%; background: {{it.bg}}"></span></span><strong>{{it.v}}</strong></span></sc-for></span></div>\n'
          '</sc-for>\n</div></sc-if>\n')
VMULTI = ('<sc-if value="{{vMulti}}" hint-placeholder-val="{{false}}"><div role="img" aria-label="{{chartAria}}" class="xp-vw"><div class="xp-vb">\n'
          '<sc-for list="{{bars}}" as="b" hint-placeholder-count="12">'
          '<div class="xp-vc xp-vg" title="{{b.tip}}"><sc-for list="{{b.items}}" as="it" hint-placeholder-count="2">'
          '<span style="height: {{it.h}}%; background: {{it.bg}}"></span></sc-for></div>\n'
          '</sc-for>\n</div>\n<div aria-hidden="true" class="xp-vx"><sc-for list="{{bars}}" as="b" hint-placeholder-count="12"><span>{{b.short}}</span></sc-for></div></div></sc-if>\n')
TABLE = ('<div class="ab-tw xp-tw"><div role="table" aria-label="{{resTitle}}" class="xp-table {{tblCls}}" style="min-width: {{tableMin}}px">\n'
         '<div role="row" class="xp-tr xp-th" style="grid-template-columns: {{gridCols}}"><span role="columnheader">{{rowDimLabel}}</span>'
         '<sc-for list="{{headCols}}" as="h" hint-placeholder-count="3"><span role="columnheader">{{h.t}}</span></sc-for></div>\n'
         '<sc-for list="{{rows}}" as="r" hint-placeholder-count="6"><div role="row" class="xp-tr" style="grid-template-columns: {{gridCols}}">'
         '<span role="rowheader"><sc-if value="{{r.drill}}" hint-placeholder-val="{{false}}"><button type="button" onClick="{{r.pick}}" class="en-drill xp-drill">{{r.label}}' + EN._CHEV + '</button></sc-if><sc-if value="{{r.plain}}" hint-placeholder-val="{{true}}">{{r.label}}</sc-if></span><sc-for list="{{r.cells}}" as="v" hint-placeholder-count="3"><span role="cell">{{v.t}}</span></sc-for></div></sc-for>\n'
         '<div role="row" class="xp-tr xp-tot" style="grid-template-columns: {{gridCols}}"><span role="rowheader">Total</span>'
         '<sc-for list="{{totCells}}" as="v" hint-placeholder-count="3"><span role="cell">{{v.t}}</span></sc-for></div>\n'
         '</div></div>\n')
RESULT = ('<section aria-labelledby="resultat" class="v7-panel">\n'
          '<div class="v7-head"><div><h2 id="resultat" class="en-h2">{{resTitle}}</h2><p class="en-sub">{{resSub}}</p></div>' + _DL + '</div>\n'
          '<div class="v7-pbody en-hebdo xp-res">\n'
          '<sc-if value="{{showBig}}" hint-placeholder-val="{{true}}"><p class="en-big"><span class="en-bigv">{{totalTxt}}</span><span class="en-bigu">{{totalUnit}}</span></p></sc-if>\n'
          '<sc-if value="{{hasCap}}" hint-placeholder-val="{{false}}"><p class="ab-note xp-cap">{{capNote}}</p></sc-if>\n'
          + TABLE + '</div>\n</section>\n')  # 8 oct. : graphique retiré à la demande (HCHART, VCHART, HMULTI, VMULTI gardés pour mémoire)

BODY = TITLE + BUILDER + RESULT

SCRIPT = '''class Component extends DCLogic {
  renderVals() {
    const st = this.state || {};
    const D = ''' + CUBE + ''';
    const PAL = ''' + json.dumps(PAL) + ''';
    const nf = (n) => Math.round(n).toLocaleString('fr-FR').replace(/[\\u202f\\u00a0]/g, ' ');
    const pc = (x) => x.toFixed(1).replace('.', ',') + ' %';
    const low = (s) => /^[A-ZÉ]{2}/.test(s) ? s : s.charAt(0).toLowerCase() + s.slice(1);
    const sum = (a) => a.reduce((x, y) => x + y, 0);
    // ---------- outils : tirage déterministe, répartition et croisement à marges exactes ----------
    const hash = (s) => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; };
    const rnd = (s) => { let t = (hash(s) + 0x6D2B79F5) >>> 0; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
    const lr = (total, w) => {
      const s = sum(w) || 1, raw = w.map((x) => total * x / s), out = raw.map((x) => Math.floor(x));
      const ord = raw.map((_, i) => i).sort((a, b) => (raw[b] - out[b]) - (raw[a] - out[a]));
      for (let k = 0, rest = total - sum(out); k < rest; k++) out[ord[k % ord.length]]++;
      return out;
    };
    const cross = (R, C) => {
      const T = sum(R);
      if (!T) return R.map(() => C.map(() => 0));
      const raw = R.map((r) => C.map((c) => r * c / T)), x = R.map((r, i) => r ? lr(r, raw[i]) : C.map(() => 0));
      for (let it = 0; it < 20000; it++) {
        const d = C.map((c, j) => c - sum(x.map((row) => row[j])));
        const up = d.findIndex((v) => v > 0);
        if (up < 0) break;
        const dn = d.findIndex((v) => v < 0);
        let best = -1, bv = -Infinity;
        x.forEach((row, i) => { if (row[dn] > 0) { const v = (raw[i][up] - row[up]) - (raw[i][dn] - row[dn]); if (v > bv) { bv = v; best = i; } } });
        if (best < 0) break;
        x[best][dn]--; x[best][up]++;
      }
      return x;
    };
    // ---------- territoire : région > préfecture > commune > canton > localité > centre ----------
    const LEV = ['region', 'pref', 'commune', 'canton', 'localite', 'centre'];
    const LEVL = { region: 'Région', pref: 'Préfecture', commune: 'Commune', canton: 'Canton', localite: 'Localité', centre: 'Centre' };
    const GEO = D.geo;
    const kids = (nd) => {
      const L = LEV.indexOf(nd.lvl);
      let n = 0, mk = null;
      if (L === 0) { n = GEO[nd.ri].prefs.length; mk = (k) => GEO[nd.ri].prefs[k][0]; }
      else if (L === 1) { n = GEO[nd.ri].prefs[nd.pi][1]; mk = (k) => nd.name + ' ' + (k + 1); }
      else if (L === 2) { n = 2 + Math.floor(rnd(nd.key + 'n') * 4); mk = (k) => 'Canton ' + (k + 1); }
      else if (L === 3) { n = 3 + Math.floor(rnd(nd.key + 'n') * 4); mk = (k) => 'Localité ' + (k + 1); }
      else if (L === 4) { n = rnd(nd.key + 'n') < 0.35 ? 2 : 1; mk = (k) => 'Centre n° ' + ((nd.ri + 1) * 10000 + 500 + Math.floor(rnd(nd.key + 'c' + k) * 9000)); }
      return Array.from({ length: n }, (_, k) => ({ lvl: LEV[L + 1], name: mk(k), key: nd.key + '/' + k, path: nd.path.concat([k]),
        ri: nd.ri, pi: L === 0 ? k : nd.pi, parent: nd }));
    };
    const pairM = (m, a, b) => {
      if (m.pairs[a + '|' + b]) return m.pairs[a + '|' + b];
      const t = m.pairs[b + '|' + a]; return m.vals[a].map((_, i) => t.map((row) => row[i]));
    };
    const split = (m, it, c) => {
      const ch = kids(it.node);
      const tots = it.node.lvl === 'region' ? m.pref[it.node.ri].slice()
        : lr(it.tot, ch.map((x) => 0.45 + rnd(x.key + 'w')));  // mêmes poids pour tous les indicateurs : les taux d'une préfecture se retrouvent dans ses communes
      const mat = c ? cross(tots, it.vec) : null;
      return ch.map((x, k) => ({ node: x, tot: tots[k], vec: mat ? mat[k] : null }));
    };
    const geoRows = (m, lvl, zone, c) => {
      const M = c ? pairM(m, 'region', c) : null;
      let items = GEO.map((g, ri) => ({ node: { lvl: 'region', name: g.name, key: 'R' + ri, path: [ri], ri: ri }, tot: m.marg.region[ri], vec: M ? M[ri] : null }));
      for (const k of zone) { const it = items[k]; if (!it) break; items = split(m, it, c); }
      while (items.length && LEV.indexOf(items[0].node.lvl) < LEV.indexOf(lvl)) items = [].concat(...items.map((it) => split(m, it, c)));
      return items;
    };
    // ---------- choix ----------
    const src = D.sources.find((s) => s.key === st.src) || D.sources[0];
    let keys = (st.ms || []).filter((k) => src.measures.some((m) => m.key === k));
    if (!keys.length) keys = [src.measures[0].key];
    const ms = keys.map((k) => src.measures.find((m) => m.key === k));
    const multi = ms.length > 1, m0 = ms[0];
    const dims0 = m0.dims.filter((d) => ms.every((m) => m.dims.includes(d)));
    const hasGeo = dims0.includes('region');
    const rowKeys = dims0.map((d) => d === 'region' ? 'geo' : d);
    const r = rowKeys.includes(st.r) ? st.r : (hasGeo ? 'geo' : dims0.includes('mois') && dims0.length === 2 ? 'mois' : rowKeys[0]);
    const isGeo = r === 'geo';
    const lvl = isGeo && LEV.includes(st.lv) ? st.lv : 'region';
    let zone = isGeo ? (st.zone || []).slice(0, LEV.indexOf(lvl)) : [];
    const rd = isGeo ? 'region' : r;
    const colOk = (d) => d !== rd && !D.dims[d].rowsOnly && !(r === 'mois' && d === 'annee');
    const auto = { enrol: 'sexe', cartes: 'sexe', auth: 'taut', idps: 'terr' }[src.key];
    let c = (st.c === undefined || st.c === 'auto') ? auto : st.c;
    if (multi || !c || c === 'none' || !dims0.includes(c) || !colOk(c)) c = null;
    let mode = st.mode || 'n';
    if ((mode === 'pr' && (multi || !c)) || (mode === 'pf' && !multi)) mode = 'n';
    // ---------- lignes ----------
    let rv, rm, rk, rnode, zoneNames = [];
    const perM = {};
    if (isGeo) {
      ms.forEach((m) => { perM[m.key] = geoRows(m, lvl, zone, c && m === m0 ? c : null); });
      const g0 = perM[m0.key];
      // noms de la zone (fil d'Ariane)
      let items = GEO.map((g, ri) => ({ node: { lvl: 'region', name: g.name, key: 'R' + ri, path: [ri], ri: ri } }));
      for (const k of zone) { const it = items[k]; if (!it) break; zoneNames.push(it.node.name); items = kids(it.node).map((x) => ({ node: x })); }
      const direct = LEV.indexOf(lvl) === zone.length;
      const lab = (nd) => {
        if (direct || nd.lvl === 'region' || nd.lvl === 'pref' || nd.lvl === 'commune') return nd.name;
        const up = [];
        for (let p = nd.parent; p && LEV.indexOf(p.lvl) >= 2 && p.path.length > zone.length; p = p.parent) up.push(p.name);
        return [nd.name].concat(up).join(' · ');
      };
      rv = g0.map((it) => lab(it.node)); rm = g0.map((it) => it.tot); rnode = g0.map((it) => it.node);
    } else {
      rv = m0.vals[r]; rm = m0.marg[r];
    }
    const T = sum(rm);
    let series;
    if (multi) series = ms.map((m, k) => { const v = isGeo ? perM[m.key].map((it) => it.tot) : m.marg[r]; return { label: m.label, vals: v, total: sum(v) }; });
    else if (c) {
      const cv = m0.vals[c];
      const M = isGeo ? perM[m0.key].map((it) => it.vec) : pairM(m0, r, c);
      const cm = cv.map((_, j) => sum(M.map((row) => row[j])));
      const cidx = cv.map((_, j) => j);
      if (D.dims[c].sort === 'value') cidx.sort((a, b) => cm[b] - cm[a]);
      series = cidx.map((j) => ({ label: cv[j], vals: M.map((row) => row[j]), total: cm[j] }));
    } else series = [{ label: m0.label, vals: rm, total: T }];
    let idx = rv.map((_, i) => i);
    if (isGeo || D.dims[r].sort === 'value') idx.sort((a, b) => rm[b] - rm[a]);
    const CAP = 150, nAll = idx.length;
    if (nAll > CAP) idx = idx.slice(0, CAP);
    const base = series[0];
    const num = (s, i) => {
      const v = s.vals[i];
      if (mode === 'n') return v;
      if (mode === 'pt') return (multi ? s.total : T) ? v / (multi ? s.total : T) * 100 : 0;
      if (mode === 'pr') return rm[i] ? v / rm[i] * 100 : 0;
      return base.vals[i] ? v / base.vals[i] * 100 : null;
    };
    const txt = (x) => x === null ? '–' : mode === 'n' ? nf(x) : pc(x);
    const showTot = !multi && !!c;
    const T_ = (t) => ({ t: t });
    const set = (o) => () => this.setState(o);
    const nextLv = LEV[LEV.indexOf(lvl) + 1];
    const headCols = series.map((s) => s.label).concat(showTot ? ['Total'] : []).map(T_);
    const rows = idx.map((i) => {
      const drill = isGeo && !!nextLv;
      return { label: rv[i], drill: drill, plain: !drill, pick: drill ? set({ zone: rnode[i].path, lv: nextLv }) : null,
        cells: series.map((s) => txt(num(s, i))).concat(showTot ? [mode === 'n' ? nf(rm[i]) : mode === 'pr' ? (rm[i] ? '100,0 %' : '–') : pc(T ? rm[i] / T * 100 : 0)] : []).map(T_) };
    });
    const totCells = series.map((s) => mode === 'n' ? nf(s.total) : mode === 'pf' ? (base.total ? pc(s.total / base.total * 100) : '–')
      : multi ? '100,0 %' : pc(T ? s.total / T * 100 : 0)).concat(showTot ? [mode === 'n' ? nf(T) : '100,0 %'] : []).map(T_);
    const nCols = headCols.length;
    const gridCols = 'minmax(' + (isGeo && LEV.indexOf(lvl) >= 3 ? 230 : 150) + 'px, 1.6fr) repeat(' + nCols + ', minmax(' + (multi ? 110 : 84) + 'px, 1fr))';
    const tableMin = (isGeo && LEV.indexOf(lvl) >= 3 ? 250 : 170) + nCols * (multi ? 118 : 92);
    // ---------- titres, notes ----------
    const names = ms.map((m, k) => k ? low(m.label) : m.label);
    const what = names.length > 1 ? names.slice(0, -1).join(', ') + ' et ' + names[names.length - 1] : names[0];
    const rowLab = isGeo ? LEVL[lvl] : D.dims[r].label;
    const zname = zoneNames.length ? zoneNames[zoneNames.length - 1] : '';
    const title = what + ' par ' + low(rowLab) + (c ? ' et par ' + low(D.dims[c].label) : '') + (zname ? ' : ' + zname : '');
    const span = m0.vals.mois ? ', de ' + m0.vals.mois[0] + ' à ' + m0.vals.mois[m0.vals.mois.length - 1] : '';
    const lost = multi && dims0.length < Math.max(...ms.map((m) => m.dims.length));
    const note = [src.note, lost ? 'Seules les ventilations communes aux indicateurs choisis sont proposées.' : ''].filter((x) => x).join(' ');
    // ---------- export CSV (point-virgule, pour Excel en français) ----------
    const esc = (s) => /[;"\\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
    const all = rv.map((_, i) => i).sort((a, b) => isGeo || D.dims[r].sort === 'value' ? rm[b] - rm[a] : a - b);
    const lines = [[rowLab].concat(series.map((s) => s.label)).concat(showTot ? ['Total'] : [])];
    all.forEach((i) => lines.push([rv[i]].concat(series.map((s) => String(s.vals[i]))).concat(showTot ? [String(rm[i])] : [])));
    lines.push(['Total'].concat(series.map((s) => String(s.total))).concat(showTot ? [String(T)] : []));
    const csv = lines.map((l) => l.map(esc).join(';')).join('\\r\\n');
    const btn = (label, on, pick) => ({ label: label, pressed: on ? 'true' : 'false', pick: pick });
    const toggle = (k) => {
      if (keys.includes(k)) return keys.length > 1 ? keys.filter((x) => x !== k) : keys;
      return keys.length >= 5 ? keys.slice(0, 4).concat([k]) : keys.concat([k]);
    };
    const rowLabel = (d) => d === 'geo' ? 'Territoire' : D.dims[d].label;
    return {
      srcBtns: D.sources.map((s) => btn(s.label, s.key === src.key, set({ src: s.key, ms: null, r: null, c: 'auto', mode: 'n', zone: [], lv: 'region' }))),
      measBtns: src.measures.map((m) => btn(m.label, keys.includes(m.key), set({ ms: toggle(m.key) }))),
      rowBtns: rowKeys.map((d) => btn(rowLabel(d), d === r, set({ r: d, c: (d === 'geo' ? 'region' : d) === c ? 'none' : (c || st.c || 'none') }))),
      isGeo: isGeo,
      lvBtns: LEV.map((l) => btn(LEVL[l], l === lvl, set({ lv: l, zone: zone.slice(0, LEV.indexOf(l)) }))),
      zoneBtns: [btn('Togo', !zone.length, set({ zone: [], lv: lvl }))].concat(zoneNames.map((n, i) => btn(n, i === zoneNames.length - 1, set({ zone: zone.slice(0, i + 1) })))),
      colBtns: multi ? [btn('Les indicateurs choisis', true, () => {})]
        : [btn('Aucune', !c, set({ c: 'none' }))].concat(dims0.filter(colOk).map((d) => btn(D.dims[d].label, d === c, set({ c: d })))),
      modeBtns: [btn('Nombres', mode === 'n', set({ mode: 'n' })), btn('% du total', mode === 'pt', set({ mode: 'pt' }))]
        .concat(c ? [btn('% de la ligne', mode === 'pr', set({ mode: 'pr' }))] : [])
        .concat(multi ? [btn('% de « ' + m0.label + ' »', mode === 'pf', set({ mode: 'pf' }))] : []),
      hasNote: !!note, note: note,
      resTitle: title, resSub: src.label + span + '.',
      showBig: !multi, totalTxt: nf(T), totalUnit: low(m0.label) + ' au total' + (zname ? ', ' + zname : ''),
      hasCap: nAll > CAP, capNote: 'Les ' + CAP + ' plus grandes zones sont affichées, sur ' + nf(nAll) + ' : choisissez une zone pour voir le détail. L’export contient toutes les lignes.',
      rowDimLabel: rowLab, tblCls: showTot ? 'xp-hastot' : '', headCols: headCols, rows: rows, totCells: totCells, gridCols: gridCols, tableMin: tableMin,
      csvHref: 'data:text/csv;charset=utf-8,' + encodeURIComponent('\\ufeff' + csv), csvName: 'exploration-' + src.key + '-' + keys.join('-') + (isGeo ? '-' + lvl : '') + '.csv'
    };
  }
}'''

CSS_XP = (
    '.xp-intro{margin:0;max-width:720px;font-size:14px;color:rgba(255,255,255,.82)}.xp-chart{min-height:250px}'
    '.xp-tw{max-height:560px;overflow:auto}.xp-th{position:sticky;top:0;z-index:1;background:#FFFFFF}.xp-tot{position:sticky;bottom:0;z-index:1;background:#FFFFFF}'
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
    '.xp-drill{min-height:0;font-size:13.5px;text-align:left;white-space:normal}.xp-cap{margin-top:-6px}'
    '.xp-kh{display:block;margin-top:2px;font-size:11.5px;font-weight:400;text-transform:none;letter-spacing:0;color:#4B5A6E}'
    '.xp-leg strong{margin-left:2px}'
    '.xp-hrm{grid-template-columns:minmax(120px,220px) minmax(0,1fr);align-items:start}.xp-hrm .xp-hl{padding-top:1px}'
    '.xp-mb{display:flex;flex-direction:column;gap:3px}.xp-mi{display:grid;grid-template-columns:minmax(0,1fr) minmax(84px,auto);gap:12px;align-items:center}'
    '.xp-mt{display:block;height:11px;background:#F1F4F6;border-radius:0 3px 3px 0}.xp-mt>span{display:block;height:11px;min-width:2px;border-radius:0 3px 3px 0}'
    '.xp-mi strong{text-align:right;font-size:12.5px;font-weight:600;color:#071B35;font-variant-numeric:tabular-nums;white-space:nowrap}'
    '.xp-vg{gap:1px;align-items:flex-end}.xp-vg>span{display:block;width:min(9px,30%);border-radius:2px 2px 0 0}'
    '.xp-table{font-variant-numeric:tabular-nums}'
    '.xp-tr{display:grid;gap:10px;align-items:center;padding:10px 8px;border-top:1px solid #EEF2F5}.xp-tr>span:not(:first-child){text-align:right}'
    '.xp-tr>span:first-child{font-weight:500;color:#071B35}'
    '.xp-th{align-items:end;padding-top:4px;padding-bottom:8px;border-top:0;font-size:12px;line-height:1.35;color:#4B5A6E}.xp-th>span:first-child{font-weight:400;color:#4B5A6E}'
    '.xp-tot{border-top:1px solid #C5CFDA;font-weight:600}.xp-tot>span{color:#071B35}'
    '.xp-hastot .xp-tr>span:last-child{font-weight:600}'
    '@media (max-width:700px){.xp-intro{display:none}.xp-chart{min-height:0}.xp-step{grid-template-columns:minmax(0,1fr);gap:6px}.xp-k{padding-top:0}'
    '.xp-hr{grid-template-columns:minmax(90px,120px) minmax(0,1fr) auto;gap:8px}.xp-chip{min-height:34px;padding:0 12px;font-size:13px}}'
)


def build():
    html = page('Exploration des données', 'Technique.dc.html', OLD.FILTERS, BODY, SCRIPT, 1522, '')
    for blk in (bandeau('Technique.dc.html'), filters(OLD.FILTERS)):
        assert html.count(blk) == 1
        html = html.replace(blk, '')
    html = html.replace('\n</style>\n</helmet>', '\n' + V3.CSS + V3.CSS7 + V3.CSS9 + EN.CSS_EN + V5.CSS_AB + CSS_XP + '\n</style>\n</helmet>', 1)
    old = ('<div class="bande-bio" aria-hidden="true" style="height: 230px"></div>\n<main style="position: relative; max-width: 1376px; '
           'margin: -230px auto 0; padding: 40px 32px 56px;')
    assert html.count(old) == 1
    html = html.replace(old, old.replace('230px', '220px').replace('padding: 40px', 'padding: 30px'))
    return html
