"""Exploration des données (8 oct. 2026, v7.1 « navbar ») : remplace la page Qualité et technique (Technique.dc.html).

Un onglet par source (Enrôlement, Impression des cartes, ABIS, IDPS, Authentifications) ; sous l'onglet, la barre
des filtres propres à la source (période, territoire de la région au centre, sexe, âge, type…), puis les indicateurs
(plusieurs), « Afficher par » (ce qui va en lignes), les valeurs et l'export CSV ; enfin le tableau.
Données : build/explo_data.py (marges reprises des autres pages, arrondi contrôlé, totaux exacts).
Un seul filtre : chiffres exacts (croisement à marges exactes). Plusieurs filtres : estimés par parts conditionnelles.
"""
import json
from common import *
import p_tech as OLD, p_main_v3 as V3, p_enrol_v5 as EN, p_bio_v5 as V5, explo_data as XD

CUBE = json.dumps(XD.cube(), ensure_ascii=False, separators=(',', ':'))

# =============== Bandeau ===============
TITLE = ('<div style="display: flex; flex-direction: column; align-items: flex-start; gap: 10px">\n'
         '<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px 18px; align-self: stretch">'
         '<h1 style="margin: 0; font-size: 30px; font-weight: 600; letter-spacing: -0.015em; color: #FFFFFF">Exploration des données</h1>'
         + EN.FRESH.replace('14/01/2026 à 11h42', '14/01/2026 à 11h59') + '</div>\n'
         f'<p class="xp-intro">Les {XD.N_MEASURES} indicateurs des cinq sources du BI : choisissez une source, filtrez, '
         'puis choisissez les indicateurs et ce qui s’affiche en lignes.</p>\n</div>\n')

# =============== Liste déroulante (filtres et réglages) ===============
_CHEV_D = ('<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" class="xp-chev" '
           'style="fill: none; stroke: currentColor; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round">'
           '<polyline points="6 9 12 15 18 9"></polyline></svg>')
DD = ('<div class="xp-f {{f.cls}}"><span aria-hidden="true" class="xp-fl">{{f.label}}</span>'
      '<button type="button" aria-haspopup="listbox" aria-expanded="{{f.exp}}" aria-label="{{f.aria}}" aria-disabled="{{f.dis}}" title="{{f.tip}}" '
      'onClick="{{f.toggle}}" class="xp-sel"><span>{{f.text}}</span>' + _CHEV_D + '</button>'
      '<sc-if value="{{f.open}}" hint-placeholder-val="{{false}}"><div role="listbox" aria-label="{{f.label}}" aria-multiselectable="{{f.ms}}" class="xp-pop">'
      '<sc-for list="{{f.opts}}" as="o" hint-placeholder-count="4"><button type="button" role="option" aria-selected="{{o.sel}}" '
      'onClick="{{o.pick}}" class="xp-opt"><span aria-hidden="true" class="xp-ck"></span>{{o.l}}</button></sc-for>'
      '<sc-if value="{{f.multi}}" hint-placeholder-val="{{false}}"><div class="xp-popf"><span>{{f.hint}}</span>'
      '<button type="button" onClick="{{f.toggle}}" class="xp-ok">Valider</button></div></sc-if>'
      '</div></sc-if></div>')

_DL = ('<a href="{{csvHref}}" download="{{csvName}}" class="xp-dl"><svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" '
       'style="fill: none; stroke: currentColor; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"></path></svg>'
       'Exporter en CSV</a>')

EXPLORER = ('<sc-if value="{{anyOpen}}" hint-placeholder-val="{{false}}"><button type="button" aria-label="Fermer la liste" onClick="{{closeAll}}" class="xp-scrim"></button></sc-if>\n'
            '<section aria-label="Construire l’analyse" class="v7-panel xp-panel">\n'
            '<div role="tablist" aria-label="Source des données" class="xp-tabs"><sc-for list="{{tabs}}" as="t" hint-placeholder-count="5">'
            '<button type="button" role="tab" aria-selected="{{t.sel}}" onClick="{{t.pick}}" class="xp-tab">{{t.label}}<span class="xp-tn">{{t.n}}</span></button>'
            '</sc-for></div>\n'
            '<div role="tabpanel" aria-label="{{srcLabel}}" class="v7-pbody xp-body">\n'
            '<div class="xp-bar"><h2 class="xp-k">Filtres</h2><sc-if value="{{hasFilt}}" hint-placeholder-val="{{false}}">'
            '<button type="button" onClick="{{clearAll}}" class="xp-clear">Effacer les filtres</button></sc-if></div>\n'
            '<div class="xp-filters"><sc-for list="{{filters}}" as="f" hint-placeholder-count="4">' + DD + '</sc-for></div>\n'
            '<sc-if value="{{hasGeoF}}" hint-placeholder-val="{{true}}"><div role="group" aria-label="Territoire" class="xp-filters xp-geo">'
            '<sc-for list="{{geoF}}" as="f" hint-placeholder-count="6">' + DD + '</sc-for></div></sc-if>\n'
            '<div class="xp-actions"><sc-for list="{{acts}}" as="f" hint-placeholder-count="3">' + DD + '</sc-for>' + _DL + '</div>\n'
            '<sc-if value="{{hasNote}}" hint-placeholder-val="{{false}}"><p class="ab-note xp-note">{{note}}</p></sc-if>\n'
            '</div>\n</section>\n')

# =============== Résultat ===============
TABLE = ('<div class="ab-tw xp-tw"><div role="table" aria-label="{{resTitle}}" class="xp-table" style="min-width: {{tableMin}}px">\n'
         '<div role="row" class="xp-tr xp-th" style="grid-template-columns: {{gridCols}}"><span role="columnheader">{{rowDimLabel}}</span>'
         '<sc-for list="{{headCols}}" as="h" hint-placeholder-count="2"><span role="columnheader">{{h.t}}</span></sc-for></div>\n'
         '<sc-for list="{{rows}}" as="r" hint-placeholder-count="6"><div role="row" class="xp-tr" style="grid-template-columns: {{gridCols}}">'
         '<span role="rowheader"><sc-if value="{{r.drill}}" hint-placeholder-val="{{true}}"><button type="button" onClick="{{r.pick}}" class="en-drill xp-drill">{{r.label}}' + EN._CHEV + '</button></sc-if>'
         '<sc-if value="{{r.plain}}" hint-placeholder-val="{{false}}">{{r.label}}</sc-if></span>'
         '<sc-for list="{{r.cells}}" as="v" hint-placeholder-count="2"><span role="cell">{{v.t}}</span></sc-for></div></sc-for>\n'
         '<sc-if value="{{showTot}}" hint-placeholder-val="{{true}}"><div role="row" class="xp-tr xp-tot" style="grid-template-columns: {{gridCols}}"><span role="rowheader">Total</span>'
         '<sc-for list="{{totCells}}" as="v" hint-placeholder-count="2"><span role="cell">{{v.t}}</span></sc-for></div></sc-if>\n'
         '</div></div>\n')
RESULT = ('<section aria-labelledby="resultat" class="v7-panel">\n'
          '<div class="v7-head"><div><h2 id="resultat" class="en-h2">{{resTitle}}</h2><p class="en-sub">{{resSub}}</p></div></div>\n'
          '<div class="v7-pbody en-hebdo xp-res">\n'
          '<sc-if value="{{showBig}}" hint-placeholder-val="{{true}}"><p class="en-big"><span class="en-bigv">{{totalTxt}}</span><span class="en-bigu">{{totalUnit}}</span></p></sc-if>\n'
          '<sc-if value="{{hasCap}}" hint-placeholder-val="{{false}}"><p class="ab-note xp-cap">{{capNote}}</p></sc-if>\n'
          + TABLE + '</div>\n</section>\n')

BODY = TITLE + EXPLORER + RESULT

SCRIPT = '''class Component extends DCLogic {
  renderVals() {
    const st = this.state || {};
    const D = ''' + CUBE + ''';
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
    const regionNode = (ri) => ({ lvl: 'region', name: GEO[ri].name, key: 'R' + ri, path: [ri], ri: ri });
    const nodeAt = (path) => { let nd = regionNode(path[0]); for (let i = 1; i < path.length && nd; i++) nd = kids(nd)[path[i]]; return nd || null; };
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
    const regions = (m, c) => { const M = c ? pairM(m, 'region', c) : null; return GEO.map((g, ri) => ({ node: regionNode(ri), tot: m.marg.region[ri], vec: M ? M[ri] : null })); };
    const geoRows = (m, lvl, zone, c) => {
      let items = regions(m, c);
      for (const k of zone) { const it = items[k]; if (!it) return []; items = split(m, it, c); }
      while (items.length && LEV.indexOf(items[0].node.lvl) < LEV.indexOf(lvl)) items = [].concat(...items.map((it) => split(m, it, c)));
      return items;
    };
    const nodeItem = (m, path, c) => {
      let items = regions(m, c), it = null;
      path.forEach((k, i) => { it = items[k]; if (i < path.length - 1) items = split(m, it, c); });
      return it;
    };
    // ---------- source et indicateurs (onglet) ----------
    const src = D.sources.find((s) => s.key === st.src) || D.sources[0];
    let keys = (st.ms || []).filter((k) => src.measures.some((m) => m.key === k));
    if (!keys.length) keys = [src.measures[0].key];
    const ms = keys.map((k) => src.measures.find((m) => m.key === k));
    const m0 = ms[0], multi = ms.length > 1;
    const sDims = [];
    src.measures.forEach((m) => m.dims.forEach((d) => { if (!sDims.includes(d)) sDims.push(d); }));
    const valsOf = (d) => src.measures.find((m) => m.dims.includes(d)).vals[d];
    const hasGeo = sDims.includes('region'), hasPer = sDims.includes('mois');
    const fdims = Object.keys(D.dims).filter((d) => sDims.includes(d) && !['region', 'annee', 'mois'].includes(d));
    // ---------- filtres de l'onglet ----------
    let g = hasGeo ? (st.g || []).slice(0, LEV.length) : [];
    while (g.length && !nodeAt(g)) g = g.slice(0, -1);
    const pv = (st.per || '').slice(2);
    const per = hasPer && st.per && (st.per[0] === 'Y' ? valsOf('annee') : valsOf('mois')).includes(pv) ? st.per : '';
    const yOf = per[0] === 'Y' ? pv : '', mOf = per[0] === 'M' ? pv : '';
    const f = {};
    const appl = (d) => ms.some((m) => m.dims.includes(d));
    fdims.forEach((d) => { const v = (st.f || {})[d]; if (appl(d) && v !== undefined && v !== null && v !== '' && valsOf(d)[+v] !== undefined) f[d] = +v; });
    const fset = (d, v) => { const o = Object.assign({}, f); if (v === null) delete o[d]; else o[d] = v; return o; };
    // ---------- « Afficher par » : ce qui va en lignes ----------
    const common = m0.dims.filter((d) => ms.every((m) => m.dims.includes(d)));
    const rowOpts = [];
    if (common.includes('region')) for (let L = g.length; L < LEV.length; L++) rowOpts.push({ k: 'g' + L, l: LEVL[LEV[L]] });
    if (common.includes('mois')) { if (!per) rowOpts.push({ k: 'annee', l: 'Année' }); if (!mOf) rowOpts.push({ k: 'mois', l: 'Mois' }); }
    common.filter((d) => fdims.includes(d) && f[d] === undefined).forEach((d) => rowOpts.push({ k: d, l: D.dims[d].label }));
    if (!rowOpts.length) rowOpts.push({ k: 'none', l: 'Total seul' });
    const defBy = { enrol: 'g', cartes: 'g', idps: 'g', abis: 'mois', auth: 'taut' }[src.key];
    let by = rowOpts.some((o) => o.k === st.by) ? st.by : '';
    if (!by) by = (defBy === 'g' ? (rowOpts.find((o) => o.k[0] === 'g') || {}).k : rowOpts.some((o) => o.k === defBy) ? defBy : '') || rowOpts[0].k;
    let mode = st.mode || 'n';
    if (mode === 'pf' && !multi) mode = 'n';
    // ---------- calcul : un filtre = exact (croisement), les suivants = parts conditionnelles ----------
    const isG = by[0] === 'g', Lr = isG ? +by.slice(1) : -1, R = isG ? '' : by;
    let est = false;
    const calc = (m) => {
      const na = Object.keys(f).filter((d) => !m.dims.includes(d));
      if (na.length) return { na: na };
      const fl = [];
      if (yOf && R !== 'mois') fl.push({ d: 'annee', v: m.vals.annee.indexOf(yOf) });
      if (mOf) fl.push({ d: 'mois', v: m.vals.mois.indexOf(mOf) });
      Object.keys(f).forEach((d) => fl.push({ d: d, v: f[d] }));
      if (isG) {
        const c1 = fl[0], rest = fl.slice(1), PR = rest.map((k) => pairM(m, 'region', k.d));
        if (rest.length) est = true;
        const items = geoRows(m, LEV[Lr], g, c1 ? c1.d : null);
        return { items: items, v: items.map((it) => {
          const ri = it.node.ri, den = m.marg.region[ri];
          let x = c1 ? it.vec[c1.v] : it.tot;
          rest.forEach((k, j) => { x = den ? x * PR[j][ri][k.v] / den : 0; });
          return x;
        }) };
      }
      const margR = R === 'none' ? [m.total] : m.marg[R];
      const pairR = (d) => R === 'none' ? [m.marg[d]] : pairM(m, R, d);
      let base, rest = fl;
      if (g.length) { const it = nodeItem(m, g, R === 'none' ? null : R); base = R === 'none' ? [it.tot] : it.vec.slice(); }
      else if (fl.length) { base = pairR(fl[0].d).map((row) => row[fl[0].v]); rest = fl.slice(1); }
      else base = margR.slice();
      if (rest.length) est = true;
      const PR = rest.map((k) => pairR(k.d));
      return { v: base.map((x, i) => { rest.forEach((k, j) => { x = margR[i] ? x * PR[j][i][k.v] / margR[i] : 0; }); return x; }) };
    };
    const res = ms.map(calc);
    const ok = res.find((r) => !r.na);
    let labels, nodes = null;
    if (isG) {
      const items = ok ? ok.items : geoRows(m0, LEV[Lr], g, null);
      nodes = items.map((it) => it.node);
      const direct = Lr === g.length;
      const lab = (nd) => {
        if (direct || LEV.indexOf(nd.lvl) <= 2) return nd.name;
        const up = [];
        for (let p = nd.parent; p && LEV.indexOf(p.lvl) >= 2 && p.path.length > g.length; p = p.parent) up.push(p.name);
        return [nd.name].concat(up).join(' · ');
      };
      labels = nodes.map(lab);
    } else labels = R === 'none' ? [[mOf || (yOf ? 'Année ' + yOf : '')].concat(g.length ? [nodeAt(g).name] : []).concat(Object.keys(f).map((d) => valsOf(d)[f[d]])).filter((x) => x).join(', ') || 'Total'] : m0.vals[R];
    const cols = res.map((r) => r.na ? null : r.v.map((x) => Math.round(x)));
    let all = labels.map((_, i) => i);
    if (R === 'mois' && yOf) all = all.filter((i) => labels[i].endsWith(' ' + yOf));
    const key0 = cols.find((c) => c);
    if (key0 && (isG || (R !== 'none' && D.dims[R].sort === 'value'))) all.sort((a, b) => key0[b] - key0[a]);
    const CAP = 150, idx = all.slice(0, CAP);
    const tots = cols.map((c) => c ? sum(all.map((i) => c[i])) : null);
    const b0 = cols[0];
    const cell = (j, i) => {
      const c = cols[j]; if (!c) return '–';
      if (mode === 'n') return nf(c[i]);
      if (mode === 'pt') return tots[j] ? pc(c[i] / tots[j] * 100) : '–';
      return b0 && b0[i] ? pc(c[i] / b0[i] * 100) : '–';
    };
    const totCell = (j) => {
      if (!cols[j]) return '–';
      if (mode === 'n') return nf(tots[j]);
      if (mode === 'pt') return tots[j] ? '100,0 %' : '–';
      return b0 && tots[0] ? pc(tots[j] / tots[0] * 100) : '–';
    };
    const set = (o) => () => this.setState(o);
    const canDrill = isG && Lr < LEV.length - 1;
    const rows = idx.map((i) => ({ label: labels[i], drill: canDrill, plain: !canDrill,
      pick: canDrill ? set({ g: nodes[i].path, by: 'g' + (Lr + 1), open: '' }) : null,
      cells: cols.map((_, j) => ({ t: cell(j, i) })) }));
    const nCols = ms.length, deep = isG && Lr >= 3 && Lr > g.length;
    // ---------- titres, notes ----------
    const rowLab = isG ? LEVL[LEV[Lr]] : R === 'none' ? 'Sélection' : D.dims[R].label;
    const gNames = g.map((_, i) => nodeAt(g.slice(0, i + 1)).name);
    const MV = m0.vals.mois || [];
    const span = MV.length > 1 ? 'de ' + MV[0] + ' à ' + MV[MV.length - 1] : MV.length ? MV[0] : '';
    const perTxt = yOf ? 'année ' + yOf : mOf || span;
    const fparts = (gNames.length ? [gNames.join(' › ')] : []).concat(Object.keys(f).map((d) => valsOf(d)[f[d]]));
    const names = ms.map((m, k) => k ? low(m.label) : m.label);
    const what = names.length > 1 ? names.slice(0, -1).join(', ') + ' et ' + names[names.length - 1] : names[0];
    const zname = gNames.length ? gNames[gNames.length - 1] : '';
    const title = what + (R === 'none' ? '' : ' par ' + low(rowLab)) + (zname ? ' : ' + zname : '');
    const sub = [src.label, perTxt, fparts.length ? 'filtres : ' + fparts.join(', ') : 'sans filtre'].filter((x) => x).join(' · ');
    const naNotes = Object.keys(f).map((d) => {
      const who = ms.filter((m) => !m.dims.includes(d)).map((m) => low(m.label));
      return who.length ? 'Le filtre « ' + D.dims[d].label + ' » ne s’applique pas à : ' + who.join(', ') + ' (« – » dans le tableau).' : '';
    });
    const note = [src.note].concat(naNotes)
      .concat(est ? ['Avec plusieurs filtres, les valeurs sont estimées à partir des croisements deux à deux.'] : []).filter((x) => x).join(' ');
    // ---------- export CSV (point-virgule, pour Excel en français) ----------
    const esc = (s) => /[;"\\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
    const lines = [['Source', src.label], ['Période', perTxt], ['Filtres', fparts.length ? fparts.join(', ') : 'aucun'], [], [rowLab].concat(ms.map((m) => m.label))];
    all.forEach((i) => lines.push([labels[i]].concat(cols.map((c) => c ? String(c[i]) : ''))));
    if (R !== 'none') lines.push(['Total'].concat(tots.map((t) => t === null ? '' : String(t))));
    const csv = lines.map((l) => l.map(esc).join(';')).join('\\r\\n');
    // ---------- listes déroulantes ----------
    const open = st.open || '';
    const opt = (l, on, pick) => ({ l: l, sel: on ? 'true' : 'false', pick: pick });
    const dd = (id, label, text, on, opts, x) => Object.assign({ id: id, label: label, text: text,
      cls: (on ? 'xp-on' : '') + (open === id ? ' xp-open' : ''), exp: open === id ? 'true' : 'false', open: open === id,
      aria: label + ' : ' + text, tip: '', dis: 'false', ms: 'false', multi: false, hint: '',
      toggle: set({ open: open === id ? '' : id }), opts: opts }, x || {});
    const pick = (o) => set(Object.assign({ open: '' }, o));
    const filters = [], geoF = [];
    if (hasPer) {
      const yv = valsOf('annee'), mv = valsOf('mois');
      filters.push(dd('per', 'Période', yOf ? 'Année ' + yOf : mOf || 'Toute la période', !!per,
        [opt('Toute la période', !per, pick({ per: '' }))]
          .concat(yv.map((y) => opt('Année ' + y, yOf === y, pick({ per: 'Y:' + y }))))
          .concat(mv.map((x) => opt(x, mOf === x, pick({ per: 'M:' + x }))))));
    }
    if (hasGeo) {
      const ALLW = { region: 'Toutes', pref: 'Toutes', commune: 'Toutes', canton: 'Tous', localite: 'Toutes', centre: 'Tous' };
      LEV.forEach((lv, L) => {
        if (L > g.length) {
          geoF.push(dd('g' + L, LEVL[lv], '—', false, [], { cls: 'xp-off', dis: 'true', open: false, exp: 'false',
            aria: LEVL[lv] + ' : choisissez d’abord ' + (L - 1 === 1 || L - 1 === 4 || L - 1 === 0 || L - 1 === 2 ? 'la ' : 'le ') + low(LEVL[LEV[L - 1]]), toggle: () => {} }));
          return;
        }
        const ch = L === 0 ? GEO.map((x) => x.name) : kids(nodeAt(g.slice(0, L))).map((x) => x.name);
        const cur = g[L];
        geoF.push(dd('g' + L, LEVL[lv], cur === undefined ? ALLW[lv] : ch[cur], cur !== undefined,
          [opt(ALLW[lv], cur === undefined, pick({ g: g.slice(0, L) }))]
            .concat(ch.map((n, k) => opt(n, cur === k, pick({ g: g.slice(0, L).concat([k]) }))))));
      });
    }
    const ALLD = { sexe: 'Tous', age: 'Toutes', type: 'Tous', taut: 'Tous', part: 'Tous', cause: 'Toutes', terr: 'Tous' };
    fdims.forEach((d) => {
      const vv = valsOf(d), cur = f[d];
      if (!appl(d)) {
        const who = src.measures.filter((m) => m.dims.includes(d)).map((m) => m.label).join(', ');
        filters.push(dd('f' + d, D.dims[d].label, 'Sans objet', false, [], { cls: 'xp-off', dis: 'true', open: false, exp: 'false',
          aria: D.dims[d].label + ' : sans objet pour les indicateurs choisis (concerne : ' + who + ')', tip: 'Concerne : ' + who, toggle: () => {} }));
        return;
      }
      filters.push(dd('f' + d, D.dims[d].label, cur === undefined ? ALLD[d] : vv[cur], cur !== undefined,
        [opt(ALLD[d], cur === undefined, pick({ f: fset(d, null) }))].concat(vv.map((v, k) => opt(v, cur === k, pick({ f: fset(d, k) }))))));
    });
    const toggle = (k) => keys.includes(k) ? (keys.length > 1 ? keys.filter((x) => x !== k) : keys) : (keys.length >= 5 ? keys : keys.concat([k]));
    const modes = [['n', 'Nombres'], ['pt', 'Part du total (%)']].concat(multi ? [['pf', 'En % de « ' + m0.label + ' »']] : []);
    const acts = [
      dd('ind', 'Indicateurs', m0.label + (multi ? ' + ' + (ms.length - 1) : ''), false,
        src.measures.map((m) => opt(m.label, keys.includes(m.key), set({ ms: toggle(m.key) }))),
        { ms: 'true', multi: true, hint: keys.length + (multi ? ' choisis' : ' choisi') + ', 5 au plus', cls: 'xp-ind xp-multi' + (open === 'ind' ? ' xp-open' : '') }),
      dd('by', 'Afficher par', rowOpts.find((o) => o.k === by).l, false, rowOpts.map((o) => opt(o.l, o.k === by, pick({ by: o.k })))),
      dd('mode', 'Valeurs', modes.find((x) => x[0] === mode)[1], false, modes.map((x) => opt(x[1], x[0] === mode, pick({ mode: x[0] }))))
    ];
    return {
      anyOpen: !!open, closeAll: set({ open: '' }),
      tabs: D.sources.map((s) => ({ label: s.label, n: s.measures.length, sel: s.key === src.key ? 'true' : 'false',
        pick: set({ src: s.key, ms: null, g: [], per: '', f: {}, by: '', mode: 'n', open: '' }) })),
      srcLabel: src.label, hasFilt: !!(g.length || per || Object.keys(f).length), clearAll: set({ g: [], per: '', f: {}, open: '' }),
      filters: filters, geoF: geoF, hasGeoF: geoF.length > 0, acts: acts, hasNote: !!note, note: note,
      resTitle: title, resSub: sub.charAt(0).toUpperCase() + sub.slice(1) + '.',
      showBig: !multi && !!b0, totalTxt: nf(tots[0] || 0), totalUnit: low(m0.label) + (fparts.length || per ? ' dans la sélection' : ' au total'),
      hasCap: all.length > CAP, capNote: 'Les ' + CAP + ' premières lignes sont affichées, sur ' + nf(all.length) + ' : filtrez une zone ou cliquez une ligne pour voir le détail. L’export contient toutes les lignes.',
      rowDimLabel: rowLab, headCols: ms.map((m) => ({ t: m.label })), rows: rows, showTot: R !== 'none', totCells: cols.map((_, j) => ({ t: totCell(j) })),
      gridCols: 'minmax(' + (deep ? 230 : 150) + 'px, 1.6fr) repeat(' + nCols + ', minmax(' + (multi ? 110 : 84) + 'px, 1fr))',
      tableMin: (deep ? 250 : 170) + nCols * (multi ? 118 : 92),
      csvHref: 'data:text/csv;charset=utf-8,' + encodeURIComponent('\\ufeff' + csv),
      csvName: 'exploration-' + src.key + '-' + keys.join('-') + '-par-' + (isG ? LEV[Lr] : R) + '.csv'
    };
  }
}'''

_CHECK = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M5 12.5l4.5 4.5L19 7.5' "
          "fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")
CSS_XP = (
    '.xp-intro{margin:0;max-width:760px;font-size:14px;color:rgba(255,255,255,.82)}'
    # onglets
    '.xp-tabs{display:flex;gap:2px;padding:0 18px;border-bottom:1px solid #E6EBF0;overflow-x:auto;scrollbar-width:none}'
    '.xp-tabs::-webkit-scrollbar{display:none}'
    '.xp-tab{position:relative;display:inline-flex;align-items:center;gap:8px;min-height:58px;padding:0 14px;border:0;background:none;'
    'font-family:inherit;font-size:14.5px;font-weight:500;color:#4B5A6E;cursor:pointer;white-space:nowrap}'
    '.xp-tab::after{content:"";position:absolute;left:10px;right:10px;bottom:-1px;height:3px;border-radius:3px 3px 0 0;background:transparent}'
    '.xp-tab:hover{color:#071B35}'
    '.xp-tab[aria-selected=true]{color:#013781;font-weight:600}.xp-tab[aria-selected=true]::after{background:#FCBA21}'
    '.xp-tn{min-width:22px;padding:1px 7px;border-radius:999px;background:#EEF2F6;font-size:11.5px;font-weight:600;line-height:18px;color:#4B5A6E;text-align:center}'
    '.xp-tab[aria-selected=true] .xp-tn{background:#013781;color:#FFFFFF}'
    # corps de l'onglet
    '.xp-body{display:flex;flex-direction:column;gap:14px}'
    '.xp-bar{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:24px}'
    '.xp-k{margin:0;font-size:12px;font-weight:600;color:#4B5A6E;text-transform:uppercase;letter-spacing:.06em}'
    '.xp-clear{padding:0;border:0;background:none;font-family:inherit;font-size:13px;font-weight:600;color:#013781;cursor:pointer;text-decoration:underline;text-underline-offset:3px}'
    '.xp-clear:hover{color:#071B35}'
    '.xp-filters{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px 14px}@media (max-width:1100px){.xp-filters{grid-template-columns:repeat(3,minmax(0,1fr))}}'
    '.xp-f{position:relative;display:flex;flex-direction:column;gap:5px;min-width:0}'
    '.xp-fl{font-size:12px;font-weight:500;color:#4B5A6E;white-space:nowrap}'
    '.xp-sel{display:flex;align-items:center;justify-content:space-between;gap:8px;width:100%;min-height:40px;padding:0 10px 0 12px;'
    'border:1px solid #D5DEE8;border-radius:8px;background:#FFFFFF;font-family:inherit;font-size:13.5px;font-weight:500;color:#071B35;cursor:pointer;text-align:left}'
    '.xp-sel>span{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}'
    '.xp-sel:hover{border-color:#013781}'
    '.xp-chev{flex:none;color:#4B5A6E;transition:transform .15s}'
    '.xp-sel[aria-expanded=true]{border-color:#013781;box-shadow:0 0 0 3px rgba(1,55,129,.12)}.xp-sel[aria-expanded=true] .xp-chev{transform:rotate(180deg)}'
    '.xp-on .xp-sel{border-color:#013781;background:#EEF4FB;font-weight:600;color:#013781}.xp-on .xp-chev{color:#013781}'
    '.xp-off .xp-sel{background:#F5F7F9;border-color:#E3E9EF;color:#9AA7B5;cursor:default}.xp-off .xp-chev{color:#C5CFDA}'
    '.xp-off .xp-fl{color:#8A97A6}'
    '.xp-open{z-index:25}'
    '.xp-pop{position:absolute;top:calc(100% + 4px);left:0;right:0;z-index:30;min-width:210px;max-height:300px;overflow:auto;padding:6px;'
    'border:1px solid #D5DEE8;border-radius:10px;background:#FFFFFF;box-shadow:0 14px 34px rgba(7,27,53,.18)}'
    '.xp-opt{display:flex;align-items:center;gap:10px;width:100%;min-height:36px;padding:6px 10px;border:0;border-radius:6px;background:none;'
    'font-family:inherit;font-size:13.5px;line-height:1.35;color:#071B35;text-align:left;cursor:pointer}'
    '.xp-opt:hover{background:#F1F5F9}'
    '.xp-opt[aria-selected=true]{font-weight:600;color:#013781;background:#EEF4FB}'
    '.xp-ck{display:none;flex:none;width:16px;height:16px;border:1.5px solid #9AA7B5;border-radius:4px;background:#FFFFFF}'
    '.xp-multi .xp-ck{display:inline-block}'
    f'.xp-multi .xp-opt[aria-selected=true] .xp-ck{{border-color:#013781;background:#013781 url("{_CHECK}") center/12px no-repeat}}'
    '.xp-multi .xp-opt[aria-selected=true]{background:none}.xp-multi .xp-opt:hover{background:#F1F5F9}'
    '.xp-popf{position:sticky;bottom:-6px;display:flex;align-items:center;justify-content:space-between;gap:12px;margin:6px -6px -6px;'
    'padding:8px 8px 8px 14px;border-top:1px solid #E6EBF0;background:#FFFFFF;font-size:12px;color:#4B5A6E}'
    '.xp-ok{min-height:32px;padding:0 14px;border:0;border-radius:999px;background:#013781;font-family:inherit;font-size:13px;font-weight:600;color:#FFFFFF;cursor:pointer}'
    '.xp-ok:hover{background:#071B35}'
    '.xp-scrim{position:fixed;inset:0;z-index:20;width:100%;height:100%;padding:0;border:0;background:transparent;cursor:default}'
    # réglages
    '.xp-actions{display:flex;flex-wrap:wrap;align-items:flex-end;gap:12px 14px;margin-top:4px;padding-top:16px;border-top:1px solid #E6EBF0}'
    '.xp-actions .xp-f{flex:1 1 190px;max-width:250px}.xp-actions .xp-ind{flex:2 1 300px;max-width:400px}'
    '.xp-ind .xp-pop{min-width:300px}'
    '.xp-dl{display:inline-flex;align-items:center;gap:8px;min-height:40px;margin-left:auto;padding:0 16px;border-radius:999px;background:#FCBA21;'
    'color:#071B35;font-size:13.5px;font-weight:600;text-decoration:none;white-space:nowrap}'
    '.xp-dl:hover{background:#FFD25E;color:#071B35}'
    '.xp-note{margin-top:2px}'
    # tableau
    '.xp-res{gap:16px}.xp-tw{max-height:560px;overflow:auto}'
    '.xp-th{position:sticky;top:0;z-index:1;background:#FFFFFF}.xp-tot{position:sticky;bottom:0;z-index:1;background:#FFFFFF}'
    '.xp-table{font-variant-numeric:tabular-nums}'
    '.xp-tr{display:grid;gap:10px;align-items:center;padding:10px 8px;border-top:1px solid #EEF2F5}.xp-tr>span:not(:first-child){text-align:right}'
    '.xp-tr>span:first-child{font-weight:500;color:#071B35}'
    '.xp-th{align-items:end;padding-top:4px;padding-bottom:8px;border-top:0;font-size:12px;line-height:1.35;color:#4B5A6E}.xp-th>span:first-child{font-weight:400;color:#4B5A6E}'
    '.xp-tot{border-top:1px solid #C5CFDA;font-weight:600}.xp-tot>span{color:#071B35}'
    '.xp-drill{min-height:0;font-size:13.5px;text-align:left;white-space:normal}.xp-cap{margin-top:-4px}'
    '@media (max-width:860px){.xp-tabs{padding:0 8px}}'
    '@media (max-width:700px){.xp-intro{display:none}.xp-tab{min-height:50px;padding:0 10px;font-size:14px}'
    '.xp-filters{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.xp-open{grid-column:1/-1}'
    '.xp-pop{position:static;min-width:0;margin-top:2px;max-height:260px;box-shadow:0 6px 18px rgba(7,27,53,.12)}.xp-ind .xp-pop{min-width:0}'
    '.xp-actions .xp-f,.xp-actions .xp-ind{flex:1 1 100%;max-width:none}.xp-dl{margin-left:0}}'
)


def build():
    html = page('Exploration des données', 'Technique.dc.html', OLD.FILTERS, BODY, SCRIPT, 1375, '')
    for blk in (bandeau('Technique.dc.html'), filters(OLD.FILTERS)):
        assert html.count(blk) == 1
        html = html.replace(blk, '')
    html = html.replace('\n</style>\n</helmet>', '\n' + V3.CSS + V3.CSS7 + V3.CSS9 + EN.CSS_EN + V5.CSS_AB + CSS_XP + '\n</style>\n</helmet>', 1)
    old = ('<div class="bande-bio" aria-hidden="true" style="height: 230px"></div>\n<main style="position: relative; max-width: 1376px; '
           'margin: -230px auto 0; padding: 40px 32px 56px;')
    assert html.count(old) == 1
    html = html.replace(old, old.replace('230px', '220px').replace('padding: 40px', 'padding: 30px'))
    return html
