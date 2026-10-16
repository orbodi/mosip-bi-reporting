"""Filtre Période des pages (9 oct. 2026).

Une série journalière par indicateur, tirée des totaux mensuels du cube de l'Exploration (explo_data) :
chaque mois est réparti sur ses jours (poids par jour de semaine, creux des fêtes), donc la somme d'un mois
redonne exactement le mois du cube et la somme de tous les jours redonne le total affiché sur les pages.
Les régions (et les types / causes d'authentification) suivent les croisements mois × région du cube.

Côté page : méthode perCore(st) ajoutée au composant ; elle lit l'état (per, d0, d1), calcule la plage de jours
et fournit v(clé) (somme sur la plage), r(clé) (part de la plage dans le total), reg(clé, i) (valeur d'une région),
weeks(...) (12 semaines complètes jusqu'à la fin de la plage) et les valeurs du filtre (liste, dates, libellé).
"""
import datetime as dt
import json
import explo_data as XD

START = dt.date(2024, 1, 1)
END = dt.date(2026, 1, 14)          # dernière donnée (enrôlement, cartes, ABIS, authentifications)
IDPS_DAY = dt.date(2026, 7, 3)      # seul jour d'activité IDPS
N = (END - START).days + 1
MONTHS = XD.months(2024, 1, 2026, 1)
REG_IDS = ['DAGL', 'PLA', 'MAR', 'SAV', 'KAR', 'CEN']   # ordre du cube (XD.REG)
assert [XD.REG[i] for i in range(6)] == ['Grand Lomé', 'Plateaux', 'Maritime', 'Savanes', 'Kara', 'Centrale']

WD = [1, 1, 1, 1, 1, 0.55, 0.12]       # centres : lundi à dimanche
WD_AUTH = [1, 1, 1, 1, 1, 0.8, 0.6]    # authentifications


def _w(d, auth=False):
    w = (WD_AUTH if auth else WD)[d.weekday()]
    if (d.month, d.day) in ((12, 25), (1, 1)):
        w *= 0.1
    elif d.month == 12 and d.day >= 24:
        w *= 0.6
    return w


def _noise(d, seed):
    """Variation journalière déterministe de ±15 % (propre à chaque indicateur)."""
    import math
    x = math.sin(d.toordinal() * 12.9898 + seed * 78.233) * 43758.5453
    return 0.85 + 0.3 * (x - math.floor(x))


def daily(month_vals, month_totals, auth=False, seed=0):
    """Totaux mensuels -> liste de N entiers (un par jour depuis START)."""
    out = [0] * N
    days = [START + dt.timedelta(i) for i in range(N)]
    for (y, m), tot in zip(month_vals, month_totals):
        idx = [i for i, d in enumerate(days) if d.year == y and d.month == m]
        assert idx, (y, m)
        for i, v in zip(idx, XD.lr(tot, [_w(days[i], auth) * _noise(days[i], seed) for i in idx]) if tot else [0] * len(idx)):
            out[i] = v
    return out


def _meas(src, key):
    s = next(s for s in XD.SOURCES if s['key'] == src)
    return next(m for m in s['measures'] if m['key'] == key)


def _mvals(m):
    """Mois du cube ('janv. 2024'…) -> (année, mois)."""
    lab = {XD.mlabel(y, mm): (y, mm) for y, mm in MONTHS}
    return [lab[x] for x in m['vals']['mois']]


def series(src, key, auth=False):
    m = _meas(src, key)
    return daily(_mvals(m), m['marg']['mois'], auth, seed=sum(map(ord, src + key)) % 97)


def pairs(src, key, dim):
    """Croisement mois × dim, aligné sur MONTHS (mois absents = 0)."""
    m = _meas(src, key)
    mv = _mvals(m)
    M = m['pairs'].get(f'mois|{dim}')
    if M is None:
        T = m['pairs'][f'{dim}|mois']
        M = [[T[j][i] for j in range(len(T))] for i in range(len(mv))]
    rows = {ym: M[i] for i, ym in enumerate(mv)}
    ncat = len(M[0])
    return [rows.get(ym, [0] * ncat) for ym in MONTHS]


# ---------------- séries communes ----------------
_S = {}


def S(name):
    if name not in _S:
        src, key = {
            'ins': ('enrol', 'ins'), 'niu': ('enrol', 'niu'), 'enc': ('enrol', 'enc'), 'ech': ('enrol', 'ech'), 'rej': ('enrol', 'rej'),
            'dem': ('cartes', 'dem'), 'exp': ('cartes', 'exp'), 'rem': ('cartes', 'rem'), 'arem': ('cartes', 'arem'),
            'a_ins': ('abis', 'ins'), 'a_dedup': ('abis', 'dedup'), 'a_adj': ('abis', 'adj'), 'a_trt': ('abis', 'trt'),
            'a_hit': ('abis', 'hit'), 'a_nohit': ('abis', 'nohit'), 'a_eins': ('abis', 'eins'), 'a_eid': ('abis', 'eid'), 'a_eadj': ('abis', 'eadj'),
            'ok': ('auth', 'ok'), 'ko': ('auth', 'ko'), 'req': ('auth', 'req'),
        }.get(name, (None, None))
        if name == 'pre':   # pré-inscriptions : même calendrier que les inscriptions
            _S[name] = daily(MONTHS, XD.lr(606850, XD._enr_w), seed=41)
        else:
            _S[name] = series(src, key, auth=src == 'auth')
    return _S[name]


def month_starts():
    out, prev = [], None
    for i in range(N):
        d = START + dt.timedelta(i)
        if (d.year, d.month) != prev:
            out.append(i)
            prev = (d.year, d.month)
    return out


def data(keys, cats=None, rej_dates=None, max_date=END, min_date=START, end=END, extra=None):
    """Objet JS des données de période. cats : {nom: (clé de série, src, clé cube, dim)} ; extra : séries ajoutées telles quelles."""
    d = {'start': START.isoformat(), 'end': end.isoformat(), 'max': max_date.isoformat(), 'min': min_date.isoformat(), 'ms': month_starts(),
         's': {k: S(k) for k in keys}, 'c': {}}
    d['s'].update(extra or {})
    for name, (base, src, key, dim) in (cats or {}).items():
        if base not in d['s']:
            d['s'][base] = S(base)
        d['c'][name] = {'b': base, 'p': pairs(src, key, dim)}
    if rej_dates:
        d['rj'] = [(dt.date.fromisoformat(x) - START).days for x in rej_dates]
    return json.dumps(d, separators=(',', ':'))


# ---------------- JavaScript (méthode du composant) ----------------
JS_CORE = r'''
  perCore(st) {
    const D = __DATA__;
    const DAY = 864e5, T0 = Date.parse(D.start + 'T00:00:00Z');
    const iso = (i) => new Date(T0 + i * DAY).toISOString().slice(0, 10);
    const idx = (s) => Math.round((Date.parse(s + 'T00:00:00Z') - T0) / DAY);
    const fr = (s) => s.slice(8, 10) + '/' + s.slice(5, 7) + '/' + s.slice(0, 4);
    const MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
    const longd = (i) => { const s = iso(i), j = +s.slice(8, 10); return (j === 1 ? '1er' : String(j)) + ' ' + MOIS[+s.slice(5, 7) - 1]; };
    const E = idx(D.end), MAXI = idx(D.max);
    const per = ['all', '7', '30', '90', 'custom'].indexOf(st.per) >= 0 ? st.per : 'all';
    let a = 0, b = 1e9;
    if (per === '7' || per === '30' || per === '90') { b = E; a = E - (+per) + 1; }
    const MINI = idx(D.min);
    const clampI = (i) => Math.max(MINI, Math.min(MAXI, i));
    const dd0 = st.d0 || iso(Math.max(MINI, E - 29)), dd1 = st.d1 || D.end;
    if (per === 'custom') { a = clampI(idx(dd0)); b = clampI(idx(dd1)); if (b < a) { const t = a; a = b; b = t; } }
    // sommes cumulées
    const cum = {};
    const C = (k) => { if (!cum[k]) { const s = D.s[k], c = [0]; for (let i = 0; i < s.length; i++) c.push(c[i] + s[i]); cum[k] = c; } return cum[k]; };
    const sumK = (k, x, y) => { const c = C(k), n = c.length - 1; x = Math.max(0, x); y = Math.min(n - 1, y); return y < x ? 0 : c[y + 1] - c[x]; };
    const v = (k) => sumK(k, a, b);
    const tot = (k) => C(k)[C(k).length - 1];
    const r = (k) => tot(k) ? v(k) / tot(k) : 0;
    // croisements mois × catégorie (régions, types…)
    const ms = D.ms.concat([1e9]);
    const cat = (name) => {
      const c = D.c[name], out = c.p[0].map(() => 0), all = c.p[0].map(() => 0);
      c.p.forEach((row, m) => {
        const x = ms[m], y = ms[m + 1] - 1, mt = sumK(c.b, x, y), f = mt ? sumK(c.b, Math.max(x, a), Math.min(y, b)) / mt : 0;
        row.forEach((n, j) => { out[j] += n * f; all[j] += n; });
      });
      return { v: out, all: all, r: out.map((x, j) => all[j] ? x / all[j] : 0) };
    };
    // 12 semaines complètes (lundi-dimanche) jusqu'à la fin de la plage
    const weeks = (keys) => {
      const end = Math.min(b, E);
      const wd = (new Date(T0 + end * DAY).getUTCDay() + 6) % 7;   // 0 = lundi
      const lastMon = wd === 6 ? end - 6 : end - wd - 7;
      const out = [];
      for (let k = 11; k >= 0; k--) {
        const m0 = lastMon - 7 * k, s = iso(m0);
        out.push({ lab: s.slice(8, 10) + '/' + s.slice(5, 7), long: longd(m0), x: m0, y: m0 + 6,
          inR: m0 + 6 >= a && m0 <= b, v: keys.map((key) => sumK(key, m0, m0 + 6)) });
      }
      return out;
    };
    const rej = (D.rj || []).filter((i) => i >= a && i <= b);
    const set = (o) => this.setState(o);
    const label = per === 'all' ? 'Depuis le début' : per === 'custom' ? 'Du ' + fr(iso(a)) + ' au ' + fr(iso(b))
      : 'Du ' + fr(iso(a)) + ' au ' + fr(iso(b));
    return {
      per: per, all: per === 'all', a: a, b: b, E: E, v: v, r: r, tot: tot, sum: sumK, cat: cat, weeks: weeks, rej: rej, rjAll: D.rj || [], iso: iso, fr: fr, longd: longd,
      endTxt: fr(D.end),
      ui: {
        perValue: per, perCustom: per === 'custom', perOn: per !== 'all', perShowRange: per !== 'all' && per !== 'custom', perRange: per === 'all' ? '' : label,
        d0: per === 'custom' ? iso(a) : dd0, d1: per === 'custom' ? iso(b) : dd1, dMin: D.min, dMax: D.max,
        onPer: (e) => { const x = e && e.target ? e.target.value : 'all'; set(x === 'custom' ? { per: x, d0: dd0, d1: dd1 } : { per: x }); },
        onD0: (e) => { if (e && e.target && e.target.value) set({ per: 'custom', d0: e.target.value }); },
        onD1: (e) => { if (e && e.target && e.target.value) set({ per: 'custom', d1: e.target.value }); },
        perTag: 'Au ' + fr(D.end) + ', hors filtre Période'
      }
    };
  }
'''


def js_core(data_json):
    return JS_CORE.replace('__DATA__', data_json)


BAND = ('<label class="v5-filter"><span>Période</span><select value="{{perValue}}" onChange="{{onPer}}" style="min-width: 168px">'
        '<option value="all">Depuis le début</option><option value="7">7 derniers jours</option><option value="30">30 derniers jours</option>'
        '<option value="90">90 derniers jours</option><option value="custom">Période personnalisée</option></select></label>'
        '<sc-if value="{{perCustom}}" hint-placeholder-val="{{false}}"><span class="v8-dates">'
        '<label><span>Du</span><input type="date" value="{{d0}}" min="{{dMin}}" max="{{dMax}}" onChange="{{onD0}}"></label>'
        '<label><span>au</span><input type="date" value="{{d1}}" min="{{dMin}}" max="{{dMax}}" onChange="{{onD1}}"></label></span></sc-if>'
        '<sc-if value="{{perShowRange}}" hint-placeholder-val="{{false}}"><span class="v8-range">{{perRange}}</span></sc-if>')

TAG = ('<sc-if value="{{perOn}}" hint-placeholder-val="{{false}}"><span title="Ce bloc montre la situation à la date de mise à jour" class="v8-scope">'
       '{{perTag}}</span></sc-if>')

CSS = ('.v8-dates{display:inline-flex;flex-wrap:wrap;align-items:center;gap:8px}'
       '.v8-dates label{display:inline-flex;align-items:center;gap:8px;height:40px;padding:0 10px 0 14px;border-radius:999px;background:#1C4C94;'
       'border:1px solid rgba(255,255,255,.5);color:rgba(255,255,255,.85);font-size:12.5px;font-weight:500}'
       '.v8-dates input{height:36px;border:0;background:transparent;color:#FFFFFF;font-family:inherit;font-size:14px;font-weight:600;color-scheme:dark}'
       '.v8-dates input:focus-visible{outline:2px solid #FCBA21;outline-offset:2px}'
       '.v8-range{display:inline-flex;align-items:center;min-height:40px;font-size:13px;font-weight:500;color:rgba(255,255,255,.9)}'
       '.v8-dim{opacity:.38}'
       '@media (max-width:700px){.v8-dates input{font-size:16px}}')
