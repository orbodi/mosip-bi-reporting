"""Filtre Période branché sur les pages (9 oct. 2026), appliqué après p_fix.

Chaque page reçoit la méthode perCore (period.py), une liste Période dans le bandeau (Depuis le début, 7, 30 et
90 derniers jours comptés jusqu'à la dernière mise à jour, période personnalisée avec dates de début et de fin),
et ses chiffres de flux (inscriptions, NIU, cartes, requêtes…) deviennent des valeurs calculées sur la plage.
Les stocks (en attente, ancienneté des cartes à remettre, scores de qualité) restent à la date de mise à jour,
avec une pastille qui le dit.
"""
import datetime as dt
import re
import period as P
from p_fix import swap as _swap_exact


def _rx(old):
    """Motif tolérant aux espaces : espace simple, insécable ou fine insécable."""
    return re.escape(old).replace('\\ ', '[ \u00a0\u202f]')


def swap(html, old, new, count=1):
    pat = re.compile(_rx(old))
    n = len(pat.findall(html))
    assert n == count, (old[:120], n, count)
    return pat.sub(lambda m: new, html)

RIX = "{ DAGL: 0, PLA: 1, MAR: 2, SAV: 3, KAR: 4, CEN: 5 }"
UI_KEYS = ['perValue', 'onPer', 'perCustom', 'd0', 'd1', 'dMin', 'dMax', 'onD0', 'onD1', 'perShowRange', 'perRange', 'perOn', 'perTag']
UI_RET = ' ' + ', '.join(f'{k}: PER.ui.{k}' for k in UI_KEYS) + ','
JS_UTIL = ("\n    const nf_ = (n) => Math.round(n).toLocaleString('fr-FR').replace(/[\\u202f\\u00a0]/g, ' ');"
           "\n    const pc_ = (x, d) => (isFinite(x) ? x : 0).toFixed(d === undefined ? 1 : d).replace('.', ',') + ' %';")


def core(html, data_json):
    html = swap(html, 'class Component extends DCLogic {', 'class Component extends DCLogic {' + P.js_core(data_json))
    html = swap(html, 'renderVals() {', 'renderVals() {\n    const PER = this.perCore(this.state || {});' + JS_UTIL)
    html = swap(html, '\n</style>\n</helmet>', '\n' + P.CSS + '\n</style>\n</helmet>')
    return html


def band(html):
    """Liste Période en tête du bandeau (avant Région ou avant le lien vers l'Exploration)."""
    m = re.search(r'<label class="v5-filter"><span>Région</span>|<a class="v8-more"', html)
    assert m
    html = html[:m.start()] + P.BAND + html[m.start():]
    return html.replace('<form aria-label="Filtre de région"', '<form aria-label="Filtres"', 1)


def ret(html, marker, extra):
    return swap(html, marker, marker + extra)


def card(html, name, vkey=None, skey=None):
    pat = re.compile(r'(<span class="v9-name">' + re.escape(name) + r'</span><span class="v9-val">)([^<]*)(</span><span class="v9-sub">)([^<]*)(</span>)')
    assert len(pat.findall(html)) == 1, name
    return pat.sub(lambda m: m.group(1) + (('{{%s}}' % vkey) if vkey else m.group(2)) + m.group(3) + (('{{%s}}' % skey) if skey else m.group(4)) + m.group(5), html)


def big(html, value, vkey, unit=None, ukey=None):
    old = f'<span class="en-bigv">{value}</span>'
    new = '<span class="en-bigv">{{%s}}</span>' % vkey
    if unit is not None:
        old += f'<span class="en-bigu">{unit}</span>'
        new += '<span class="en-bigu">{{%s}}</span>' % ukey
    return swap(html, old, new)


def split(html, aria, key, n):
    m = re.search(_rx(f'<div role="img" aria-label="{aria}" class="en-split">'), html)
    assert m, aria
    start = m.start()
    end = html.index('</div>', start)
    seg = html[start:end]
    assert seg.count('style="flex: ') == n, (aria, seg.count('style="flex: '))
    i = [0]

    def f(m):
        i[0] += 1
        return 'style="flex: {{%s.f%d}} 1 0;' % (key, i[0])
    new = re.sub(r'style="flex: [\d.]+ 1 0;', f, seg)
    new = re.sub(r'aria-label="[^"]*"', 'aria-label="{{%s.aria}}"' % key, new, count=1)
    return html[:start] + new + html[end:]


def tag(html, hid, key='perTag', show='perOn'):
    m = re.search(r'<h2 id="%s"[^>]*>.*?</h2>' % re.escape(hid), html, re.S)
    assert m, hid
    t = ('<sc-if value="{{%s}}" hint-placeholder-val="{{false}}"><span title="Ce bloc montre la situation à la date de mise à jour" class="v8-scope">'
         '{{%s}}</span></sc-if>') % (show, key)
    return html.replace(m.group(0), m.group(0)[:-5] + t + '</h2>', 1)


def sub_once(html, pattern, repl):
    n = len(re.findall(pattern, html, re.S))
    assert n == 1, (pattern[:60], n)
    return re.sub(pattern, repl, html, count=1, flags=re.S)


WEEK_SUB = ("PER.all ? '12 dernières semaines complètes.' : '12 semaines complètes jusqu’à la fin de la période ; "
            "en clair, les semaines hors période.'")


# ------------------------------------------------------------------ Enrôlement
def enrol(html):
    html = core(html, P.data(['ins', 'niu', 'enc', 'ech', 'rej', 'pre'], cats={'reg': ('ins', 'enrol', 'ins', 'region')}))
    html = band(html)
    html = swap(html, 'const NAT = 3278239;',
                "const NAT = PER.v('ins');\n    const ENC = PER.v('enc'), ECH = PER.v('ech'), REJ = PER.v('rej'), NIUP = NAT - ENC - ECH - REJ, RP = PER.r('pre');"
                "\n    const BLOQ = Math.round(PER.sum('enc', PER.a, Math.min(PER.b, PER.E - 30)) * 118402 / Math.max(1, PER.sum('enc', 0, PER.E - 30)));")
    html = swap(html, 'const ECHP = 9218 / NAT * 100;', 'const ECHP = 9218 / 3278239 * 100;')
    html = swap(html, "value: '≈ ' + nf(546964)", "value: '≈ ' + nf(546964 * RP)")
    html = swap(html, "value: nf(59886)", "value: nf(59886 * RP)")
    html = swap(html, "value: '285 220', detail: '47 %, contre 321 630 hommes : l’inverse des NIU'",
                "value: nf(285220 * RP), detail: '47 %, contre ' + nf(321630 * RP) + ' hommes : l’inverse des NIU'")
    html = swap(html, "{ label: 'NIU générés', n: 3058886,", "{ label: 'NIU générés', n: NIUP,")
    html = swap(html, "n: 123639, color: '#FAB219', note: ', dont 118 402 bloqués depuis plus de 30 jours' }",
                "n: ENC, color: '#FAB219', note: ', dont ' + nf(BLOQ) + ' bloqués depuis plus de 30 jours' }")
    html = swap(html, "{ label: 'Échoués', n: 9218,", "{ label: 'Échoués', n: ECH,")
    html = swap(html, "{ label: 'Rejetés', n: 86496,", "{ label: 'Rejetés', n: REJ,")
    # semaines : 12 semaines complètes jusqu'à la fin de la plage, hors période en clair
    html = sub_once(html, r'const weeks = \[.*?\n\s*\];', "const weeks = PER.weeks(['ins', 'niu']).map((w) => [w.lab, w.v[0], w.v[1], w.long, w.inR]);")
    html = swap(html, "bg: i === hov ? '#1C5CAB' : '#2A78D6',", "bg: i === hov ? '#1C5CAB' : (w[4] ? '#2A78D6' : '#B7D3F6'),")
    html = swap(html, "pct(hw[2] / hw[1] * 100)", "pct(hw[1] ? hw[2] / hw[1] * 100 : 0)")
    # territoire : inscriptions des préfectures au prorata de leur région sur la plage
    html = sub_once(html, r'(const R = \[.*?\n\s*\];)',
                    r"\1\n    const RR_ = PER.cat('reg').r, RIX_ = " + RIX + ";\n"
                    r"    R.forEach((g) => { const k = RR_[RIX_[g.id]]; g.prefs = g.prefs.map((p) => [p[0], Math.round(p[1] * k)].concat(p.slice(2))); });")
    n = html.count(': 3058886;')
    assert n == 1, n
    html = html.replace(': 3058886;', ': NIUP;')
    html = html.replace('nf(3058886)', 'nf(NIUP)').replace('nf(86496)', 'nf(REJ)').replace('nf(123639)', 'nf(ENC)')
    # top des centres : au prorata des inscriptions de la plage
    html = swap(html, 'const inZone = (c) => !sel || c[2] === sel;',
                "const RI_ = PER.r('ins');\n    [top, ech, rej].forEach((L) => L.forEach((c) => { c[3] = Math.round(c[3] * RI_); if (c.length > 4) c[4] = Math.round(c[4] * RI_); }));"
                "\n    const inZone = (c) => c[3] > 0 && (!sel || c[2] === sel);")
    # valeurs fixes de la page
    html = big(html, '606 850', 'preTotal')
    html = big(html, '3 058 886', 'dvNiu', 'NIU générés, soit 93,3 % des 3 278 239 inscriptions', 'dvSub')
    html = swap(html, '<p class="en-sub">12 dernières semaines complètes.</p>', '<p class="en-sub">{{wkSub}}</p>')
    html = ret(html, "regionValue: sel || '',", UI_RET +
               " preTotal: nf(606850 * RP), dvNiu: nf(NIUP), dvSub: 'NIU générés, soit ' + pct(NAT ? NIUP / NAT * 100 : 0) + ' des ' + nf(NAT) + ' inscriptions',"
               " wkSub: " + WEEK_SUB + ",")
    return html


# ------------------------------------------------------------------ Impression des cartes
REJ_DATES = ['2025-10-27', '2025-11-17', '2025-11-17', '2025-12-08', '2026-01-05', '2026-03-13']


def cartes(html):
    html = core(html, P.data(['dem', 'exp', 'rem'], cats={'rExp': ('exp', 'cartes', 'exp', 'region'), 'rRem': ('rem', 'cartes', 'rem', 'region')},
                             rej_dates=REJ_DATES, min_date=dt.date(2024, 2, 1)))
    html = band(html)
    html = sub_once(html, r"(const regs = \[\n\s*\['DAGL', 'Grand Lomé', 975000, 690000\].*?\n\s*\];)",
                    r"\1\n    const RE_ = PER.cat('rExp').r, RL_ = PER.cat('rRem').r, RIX_ = " + RIX + ";\n"
                    r"    regs.forEach((r) => { r[2] = Math.round(r[2] * RE_[RIX_[r[0]]]); r[3] = Math.round(r[3] * RL_[RIX_[r[0]]]); });")
    html = sub_once(html, r"(const c = \[\n\s*\['EPP Doumassesse I G/B'.*?\n\s*\];)",
                    r"\1\n    c.forEach((x) => { if (x[2] !== null) x[2] = Math.round(x[2] * PER.r('exp')); if (x[3] !== null) x[3] = Math.round(x[3] * PER.r('rem')); });")
    html = swap(html, 'const remRows = c.filter((x) => x[3] !== null && ', 'const remRows = c.filter((x) => x[3] !== null && x[3] > 0 && ')
    # semaines : demandes (courbe) et cartes imprimées (barres) ; rejets aux dates connues
    html = sub_once(html, r'const wk = \[.*?\n\s*\];', "const wk = PER.weeks(['dem', 'exp']).map((w) => [w.lab, w.v[0], w.v[1], w.long, w.inR, w.x, w.y]);")
    html = swap(html, "bg: i === hovW ? '#1C5CAB' : '#2A78D6',", "bg: i === hovW ? '#1C5CAB' : (w[4] ? '#2A78D6' : '#B7D3F6'),")
    html = swap(html, 'const rj = [0, 1, 0, 0, 2, 0, 0, 1, 0, 0, 0, 1];', 'const rj = wk.map((w) => PER.rjAll.filter((d) => d >= w[5] && d <= w[6]).length);')
    # bloc « Impression et remise »
    html = big(html, '1 770 796', 'caBig', 'cartes remises, soit 57,1 % des 3 101 590 cartes expédiées', 'caBigSub')
    html = split(html, 'Cartes expédiées : remises 57,1 %, à remettre 42,9 %', 'caSp', 2)
    html = swap(html, 'Remises <strong>57,1 %</strong>', 'Remises <strong>{{caLiv}}</strong>')
    html = swap(html, 'À remettre <strong>42,9 %</strong>', 'À remettre <strong>{{caRem}}</strong>')
    html = card(html, 'Demandes d’impression', 'caDem', 'caDemS')
    html = card(html, 'En attente d’impression', None, 'caAttS')
    html = card(html, 'Demandes rejetées', 'caRej', 'caRejS')
    html = card(html, 'Imprimées et expédiées', 'caExp', 'caExpS')
    html = card(html, 'Cartes à remettre', 'caAr', 'caArS')
    html = swap(html, '<p class="en-sub">12 dernières semaines complètes.</p>', '<p class="en-sub">{{wkSub}}</p>')
    html = tag(html, 'anciennete')
    js = ("\n    const DEM_ = PER.v('dem'), EXP_ = PER.v('exp'), REM_ = PER.v('rem'), AR_ = EXP_ - REM_, RJ_ = PER.rej;"
          "\n    const caLast_ = RJ_.length ? PER.fr(PER.iso(Math.max.apply(null, RJ_))) : '';")
    html = _swap_exact(html, JS_UTIL, JS_UTIL + js)
    html = ret(html, "regionValue: sel || '',", UI_RET +
               " caBig: nf_(REM_), caBigSub: 'cartes remises, soit ' + pc_(REM_ / EXP_ * 100) + ' des ' + nf_(EXP_) + ' cartes expédiées',"
               " caSp: { f1: REM_, f2: AR_, aria: 'Cartes expédiées : remises ' + pc_(REM_ / EXP_ * 100) + ', à remettre ' + pc_(AR_ / EXP_ * 100) },"
               " caLiv: pc_(REM_ / EXP_ * 100), caRem: pc_(AR_ / EXP_ * 100),"
               " caDem: nf_(DEM_), caDemS: PER.all ? '54 545 de plus que les NIU : à réconcilier' : 'Reçues sur la période',"
               " caAttS: PER.all ? 'Pas encore lancées en production' : 'Au ' + PER.endTxt + ', hors filtre Période',"
               " caRej: String(RJ_.length), caRejS: PER.all ? 'Dernière datée du 13/03/2026 : à vérifier' : (RJ_.length ? 'Dernière le ' + caLast_ : 'Aucune sur la période'),"
               " caExp: nf_(EXP_), caExpS: pc_(EXP_ / DEM_ * 100) + ' des demandes',"
               " caAr: nf_(AR_), caArS: pc_(AR_ / EXP_ * 100) + ' des cartes expédiées',"
               " wkSub: " + WEEK_SUB + ",")
    return html


# ------------------------------------------------------------------ Vue d'ensemble
def main(html):
    idps = (P.IDPS_DAY - P.START).days
    html = core(html, P.data(['pre', 'ins', 'enc', 'ech', 'rej', 'dem', 'exp', 'rem', 'a_dedup', 'ok', 'ko'],
                             cats={'rIns': ('ins', 'enrol', 'ins', 'region'), 'rRem': ('rem', 'cartes', 'rem', 'region')}))
    html = band(html)
    js = ("\n    const M_ = (() => {"
          "\n      const ins = PER.v('ins'), enc = PER.v('enc'), ech = PER.v('ech'), rej = PER.v('rej'), niu = ins - enc - ech - rej;"
          "\n      const pre = PER.v('pre'), dem = PER.v('dem'), exp = PER.v('exp'), rem = PER.v('rem'), dd = PER.v('a_dedup'), ok = PER.v('ok'), ko = PER.v('ko');"
          f"\n      const idOn = PER.a <= {idps} && PER.b >= {idps};"
          "\n      const steps = [['pré-inscription', 'Pré-inscriptions', pre], ['inscription', 'Inscriptions', ins], ['traitement', 'Paquets traités', niu + ech + rej],"
          " ['niu', 'NIU générés', niu], ['demande', 'Demandes d’impression', dem], ['impression', 'Cartes imprimées et expédiées', exp], ['remise', 'Cartes remises', rem]];"
          "\n      const fz = {}; steps.forEach((s, i) => { const w = ins ? s[2] / ins * 100 : 0; fz['v' + (i + 1)] = nf_(s[2]); fz['w' + (i + 1)] = Math.min(w, 100).toFixed(1);"
          " fz['p' + (i + 1)] = pc_(w); fz['a' + (i + 1)] = 'Étape ' + (i + 1) + ', ' + s[0] + ' : ' + s[1] + ' ' + nf_(s[2]); });"
          "\n      fz.ec = nf_(enc); fz.ech = nf_(ech); fz.rej = nf_(rej);"
          "\n      return { fz: fz, hero: nf_(rem), heroSub: PER.all ? 'cartes en main, soit ' + pc_(ins ? rem / ins * 100 : 0) + ' des inscrits' : 'cartes remises sur la période',"
          " mEnr: nf_(ins), mEnrP: pc_(ins ? niu / ins * 100 : 0), mEnrC: nf_(enc), mCar: nf_(rem), mCarR: nf_(Math.max(0, exp - rem)),"
          " mAb: nf_(dd), mAbP: pc_(ins ? dd / ins * 100 : 0), mId: idOn ? '14' : '0', mIdS1: idOn ? 'Les 14 en erreur' : 'Aucun ordre', mIdS2: idOn ? ', aucune carte imprimée' : ' sur la période',"
          " mAu: nf_(ok + ko), mAuOk: ok + ko ? pc_(ok / (ok + ko) * 100) : '–', mAuKo: ok + ko ? pc_(ko / (ok + ko) * 100) : '–' };"
          "\n    })();")
    html = _swap_exact(html, JS_UTIL, JS_UTIL + js)
    # frise : chaque étape devient calculée
    steps = re.findall(r'<div role="listitem" aria-label="Étape \d.*?(?=<div role="listitem" aria-label="Étape |</div></div>\n)', html, re.S)
    assert len(steps) == 7, len(steps)
    for i, s in enumerate(steps, 1):
        t = re.sub(r'aria-label="Étape [^"]*"', 'aria-label="{{fz.a%d}}"' % i, s, count=1)
        t = re.sub(r'<span class="fz-val">[^<]*</span>', '<span class="fz-val">{{fz.v%d}}</span>' % i, t, count=1)
        t = re.sub(r'<span style="width: [\d.]+%; background: ([^"]*)"></span></span>[^<]*</span>',
                   lambda m: '<span style="width: {{fz.w%d}}%%; background: %s"></span></span>{{fz.p%d}}</span>' % (i, m.group(1), i), t, count=1)
        if i == 3:
            for lab, k in (('En cours', 'ec'), ('Échoués', 'ech'), ('Rejetés', 'rej')):
                t = re.sub(r'(<span style="flex-grow: 1; text-align: left">%s</span><strong style="font-weight: 600; color: #071B35">)[^<]*(</strong>)' % lab,
                           r'\g<1>{{fz.%s}}\g<2>' % k, t, count=1)
        assert '{{fz.v%d}}' % i in t and '{{fz.p%d}}' % i in t, i
        html = html.replace(s, t, 1)
    html = swap(html, 'font-variant-numeric: tabular-nums">1 770 796</span><span style="font-size: 13px; line-height: 1.35; color: #664700; max-width: 170px">cartes en main, soit 54,0 % des inscrits</span>',
                'font-variant-numeric: tabular-nums">{{hero}}</span><span style="font-size: 13px; line-height: 1.35; color: #664700; max-width: 170px">{{heroSub}}</span>')
    for old, new in (('<span class="v9-val">3 278 239 <span class="v9-unit">inscriptions</span></span><span class="v9-sub"><strong>93,3 %</strong> ont leur NIU, 123 639 en cours</span>',
                      '<span class="v9-val">{{mEnr}} <span class="v9-unit">inscriptions</span></span><span class="v9-sub"><strong>{{mEnrP}}</strong> ont leur NIU, {{mEnrC}} en cours</span>'),
                     ('<span class="v9-val">1 770 796 <span class="v9-unit">cartes remises</span></span><span class="v9-sub"><strong>1 330 794</strong> cartes expédiées encore à remettre</span>',
                      '<span class="v9-val">{{mCar}} <span class="v9-unit">cartes remises</span></span><span class="v9-sub"><strong>{{mCarR}}</strong> cartes expédiées encore à remettre</span>'),
                     ('<span class="v9-val">3 158 734 <span class="v9-unit">recherches de doublons</span></span><span class="v9-sub"><strong>96,4 %</strong> des inscriptions dédupliquées</span>',
                      '<span class="v9-val">{{mAb}} <span class="v9-unit">recherches de doublons</span></span><span class="v9-sub"><strong>{{mAbP}}</strong> des inscriptions dédupliquées</span>'),
                     ('<span class="v9-val">14 <span class="v9-unit">ordres d’impression</span></span><span class="v9-sub"><strong>Les 14 en erreur</strong>, aucune carte imprimée</span>',
                      '<span class="v9-val">{{mId}} <span class="v9-unit">ordres d’impression</span></span><span class="v9-sub"><strong>{{mIdS1}}</strong>{{mIdS2}}</span>'),
                     ('<span class="v9-val">510 499 <span class="v9-unit">requêtes</span></span><span class="v9-sub"><strong>42,3 %</strong> réussies, 57,7 % échouées</span>',
                      '<span class="v9-val">{{mAu}} <span class="v9-unit">requêtes</span></span><span class="v9-sub"><strong>{{mAuOk}}</strong> réussies, {{mAuKo}} échouées</span>')):
        html = swap(html, old, new)
    # régions : inscriptions et NIU au prorata des inscriptions de la région, cartes remises au prorata des remises
    html = sub_once(html, r"(const regs = \[\n\s*\['DAGL', 'Grand Lomé', 1020000, 961808,.*?\n\s*\];)",
                    r"\1\n    const RI_ = PER.cat('rIns').r, RL_ = PER.cat('rRem').r, RIX_ = " + RIX + ";\n"
                    r"    regs.forEach((r) => { const j = RIX_[r[0]]; r[2] = Math.round(r[2] * RI_[j]); r[3] = Math.round(r[3] * RI_[j]); r[4] = Math.round(r[4] * RL_[j]); });")
    html = swap(html, 'par région (moyenne nationale : 54,0 %).', 'par région (moyenne nationale : {{regAvg}}).')
    i = html.index('<section aria-labelledby="parcours"')
    j = html.index('</section>', i)
    html = html[:j] + ('<sc-if value="{{perOn}}" hint-placeholder-val="{{false}}"><p class="v8-tnote">Sur une période, chaque étape compte ce qui s’y est passé '
                       'pendant la période : les cartes demandées, imprimées ou remises peuvent concerner des inscriptions plus anciennes, '
                       'd’où des parts parfois supérieures à 100 %.</p></sc-if>\n') + html[j:]
    html = ret(html, 'return { steps: steps, actions: actions, watch: watch, tiles: tiles, regions: regions, map: map', ',' + UI_RET[:-1] +
               ", fz: M_.fz, hero: M_.hero, heroSub: M_.heroSub, mEnr: M_.mEnr, mEnrP: M_.mEnrP, mEnrC: M_.mEnrC, mCar: M_.mCar, mCarR: M_.mCarR,"
               " mAb: M_.mAb, mAbP: M_.mAbP, mId: M_.mId, mIdS1: M_.mIdS1, mIdS2: M_.mIdS2, mAu: M_.mAu, mAuOk: M_.mAuOk, mAuKo: M_.mAuKo,"
               " regAvg: pc_(regs.reduce((a, r) => a + r[4], 0) / Math.max(1, regs.reduce((a, r) => a + r[2], 0)) * 100)")
    return html


# ------------------------------------------------------------------ Authentifications
def usage(html):
    html = core(html, P.data(['ok', 'ko', 'req'], cats={'tReq': ('req', 'auth', 'req', 'taut'), 'tKo': ('ko', 'auth', 'ko', 'taut'),
                                                         'cKo': ('ko', 'auth', 'ko', 'cause')}, min_date=dt.date(2025, 2, 1)))
    html = band(html)
    js = ("\n    const OK_ = PER.v('ok'), KO_ = PER.v('ko'), REQ_ = OK_ + KO_;"
          "\n    const fixTo_ = (vals, total) => { const r = vals.map(Math.round); const d = total - r.reduce((a, c) => a + c, 0); if (r.length) r[r.indexOf(Math.max.apply(null, r))] += d; return r; };"
          "\n    const TQ_ = fixTo_(PER.cat('tReq').v, REQ_), TK_ = fixTo_(PER.cat('tKo').v, KO_), CK_ = fixTo_(PER.cat('cKo').v, KO_);"
          "\n    const types_ = ['Biométrique', 'Code à usage unique', 'Démographique', 'Combinée'].map((l, i) => { const rt = TQ_[i] ? TK_[i] / TQ_[i] * 100 : 0;"
          " return { label: l, n: nf_(TQ_[i]), part: pc_(REQ_ ? TQ_[i] / REQ_ * 100 : 0), f: nf_(TK_[i]), rate: TQ_[i] ? pc_(rt) : '–', hi: rt >= 50, cls: rt >= 50 ? 'au-hi' : '' }; });"
          "\n    const cmax_ = Math.max.apply(null, CK_.concat([1]));"
          "\n    const causes_ = ['Empreinte non concordante', 'Qualité de capture insuffisante', 'NIU ou identifiant virtuel invalide ou inactif', 'Code OTP expiré ou erroné', 'Autres causes']"
          ".map((l, i) => ({ rank: String(i + 1), label: l, n: nf_(CK_[i]), p: pc_(KO_ ? CK_[i] / KO_ * 100 : 0), w: (CK_[i] / cmax_ * 100).toFixed(1) }));")
    html = _swap_exact(html, JS_UTIL, JS_UTIL + js)
    html = sub_once(html, r'const W = \[.*?\];', "const W = PER.weeks(['ok', 'ko']).map((w) => [w.lab, w.long, w.v[0] + w.v[1], (w.v[0] + w.v[1]) ? w.v[1] / (w.v[0] + w.v[1]) : 0, w.inR]);")
    html = swap(html, "band: i === hov ? 'rgba(42,120,214,0.07)' : 'transparent',", "band: i === hov ? 'rgba(42,120,214,0.07)' : 'transparent', dim: w[4] ? '' : 'v8-dim',")
    html = swap(html, 'class="ab-vb" style="background: {{w.band}}"', 'class="ab-vb {{w.dim}}" style="background: {{w.band}}"')
    html = big(html, '510 499', 'auBig')
    html = split(html, 'Réussies 42,3 %, échouées 57,7 %', 'auSp', 2)
    html = card(html, 'Réussies', 'auOk', 'auOkS')
    html = card(html, 'Échouées', 'auKo', 'auKoS')
    html = card(html, 'Biométriques', 'auBio', 'auBioS')
    html = card(html, 'Code à usage unique', 'auOtp', 'auOtpS')
    html = card(html, 'Démographiques et combinées', 'auDem', 'auDemS')
    tri = re.search(r'<svg width="11" height="11" viewBox="0 0 24 24" role="img" aria-label="Taux d’échec de 50 % ou plus".*?</svg>', html, re.S).group(0)
    html = sub_once(html, r'<div role="row" class="ab-tr au-t5"><span role="rowheader">.*?<div role="row" class="ab-tr au-t5 ab-tot">.*?</div>',
                    lambda m: ('<sc-for list="{{types}}" as="t" hint-placeholder-count="4"><div role="row" class="ab-tr au-t5"><span role="rowheader"><span class="au-tl"><span>{{t.label}}</span></span></span>'
                               '<span role="cell">{{t.n}}</span><span role="cell">{{t.part}}</span><span role="cell">{{t.f}}</span><span role="cell"><strong class="{{t.cls}}">'
                               '<sc-if value="{{t.hi}}" hint-placeholder-val="{{false}}">' + tri + '</sc-if>{{t.rate}}</strong></span></div></sc-for>\n'
                               '<div role="row" class="ab-tr au-t5 ab-tot"><span role="rowheader">Total</span><span role="cell">{{tyN}}</span><span role="cell">100 %</span>'
                               '<span role="cell">{{tyF}}</span><span role="cell">{{tyR}}</span></div>'))
    html = sub_once(html, r'<div role="row" class="au-cr">.*?</div>(?=\n</div>\n</div>\n</section>)',
                    lambda m: ('<sc-for list="{{causes}}" as="c" hint-placeholder-count="5"><div role="row" class="au-cr"><span role="cell" class="ab-rkn">{{c.rank}}</span>'
                               '<span role="rowheader" class="au-cl">{{c.label}}</span><span role="cell" class="au-cn"><strong>{{c.n}}</strong><span>{{c.p}}</span></span>'
                               '<span role="cell" aria-hidden="true" class="au-cb"><span style="width: {{c.w}}%"></span></span></div></sc-for>'))
    html = swap(html, '<p class="en-sub">294 763 échecs, du plus fréquent au moins fréquent.</p>', '<p class="en-sub">{{cauSub}}</p>')
    html = swap(html, '<p class="en-sub">12 dernières semaines complètes.</p>', '<p class="en-sub">{{wkSub}}</p>')
    html = ret(html, 'return { weeks: weeks, readout: readout', ',' + UI_RET[:-1] +
               ", auBig: nf_(REQ_), auSp: { f1: OK_, f2: KO_, aria: 'Réussies ' + pc_(REQ_ ? OK_ / REQ_ * 100 : 0) + ', échouées ' + pc_(REQ_ ? KO_ / REQ_ * 100 : 0) },"
               " auOk: nf_(OK_), auOkS: pc_(REQ_ ? OK_ / REQ_ * 100 : 0) + ' des requêtes', auKo: nf_(KO_), auKoS: pc_(REQ_ ? KO_ / REQ_ * 100 : 0) + ' des requêtes',"
               " auBio: nf_(TQ_[0]), auBioS: pc_(REQ_ ? TQ_[0] / REQ_ * 100 : 0) + ' des requêtes', auOtp: nf_(TQ_[1]), auOtpS: pc_(REQ_ ? TQ_[1] / REQ_ * 100 : 0) + ' des requêtes',"
               " auDem: nf_(TQ_[2] + TQ_[3]), auDemS: pc_(REQ_ ? (TQ_[2] + TQ_[3]) / REQ_ * 100 : 0) + ' des requêtes',"
               " types: types_, tyN: nf_(REQ_), tyF: nf_(KO_), tyR: pc_(REQ_ ? KO_ / REQ_ * 100 : 0), causes: causes_, cauSub: nf_(KO_) + ' échecs, du plus fréquent au moins fréquent.',"
               " wkSub: " + WEEK_SUB)
    return html


# ------------------------------------------------------------------ ABIS
def bio(html):
    keys = ['a_ins', 'a_dedup', 'a_adj', 'a_trt', 'a_hit', 'a_nohit', 'a_eins', 'a_eid', 'a_eadj']
    html = core(html, P.data(keys))
    html = band(html)
    for name, k in (('Requêtes d’insertion', 'abIns'), ('Requêtes de déduplication', 'abDed')):
        html = card(html, name, k)
    html = big(html, '41 870', 'abAdj')
    html = split(html, 'Requêtes d’adjudication : HIT 16 002, NO HIT 23 203, En attente 2 353, En erreur 312', 'abSpA', 4)
    for name, k in (('Cas d’adjudication traités', 'abTrt'), ('Dossiers en attente de traitement', 'abAtt'), ('Dossiers traités avec statut HIT', 'abHit'),
                    ('Dossiers traités NO HIT', 'abNoh'), ('Erreurs d’insertion', 'abEi'), ('Erreurs d’identification', 'abEd'), ('Erreurs d’adjudication', 'abEa')):
        html = card(html, name, k, k + 'S')
    html = big(html, '2 273', 'abErr')
    html = split(html, 'Erreurs ABIS par type : Insertion 857, Identification 1 104, Adjudication 312', 'abSpE', 3)
    html = tag(html, 'qualite', 'perTagQ')
    html = swap(html, 'renderVals() {\n    const PER = this.perCore(this.state || {});' + JS_UTIL + '\n    return {};',
                'renderVals() {\n    const PER = this.perCore(this.state || {});' + JS_UTIL +
                "\n    const g = (k) => PER.v('a_' + k);"
                "\n    const ins = g('ins'), ded = g('dedup'), adj = g('adj'), trt = g('trt'), hit = g('hit'), noh = g('nohit'), ei = g('eins'), ed = g('eid'), ea = g('eadj');"
                "\n    const att = Math.max(0, adj - trt - ea), err = ei + ed + ea, p = (x, y, d) => pc_(y ? x / y * 100 : 0, d);"
                "\n    return {" + UI_RET +
                " perTagQ: 'Toute la période, hors filtre Période',"
                " abIns: nf_(ins), abDed: nf_(ded), abAdj: nf_(adj),"
                " abSpA: { f1: hit, f2: noh, f3: att, f4: ea, aria: 'Requêtes d’adjudication : HIT ' + nf_(hit) + ', NO HIT ' + nf_(noh) + ', En attente ' + nf_(att) + ', En erreur ' + nf_(ea) },"
                " abTrt: nf_(trt), abTrtS: p(trt, adj) + ' des requêtes reçues', abAtt: nf_(att), abAttS: p(att, adj) + ' des requêtes reçues',"
                " abHit: nf_(hit), abHitS: 'Doublon confirmé : ' + p(hit, trt) + ' des cas traités', abNoh: nf_(noh), abNohS: 'Aucun doublon : ' + p(noh, trt) + ' des cas traités',"
                " abErr: nf_(err), abSpE: { f1: ei, f2: ed, f3: ea, aria: 'Erreurs ABIS par type : Insertion ' + nf_(ei) + ', Identification ' + nf_(ed) + ', Adjudication ' + nf_(ea) },"
                " abEi: nf_(ei), abEiS: p(ei, ins, 2) + ' des requêtes d’insertion', abEd: nf_(ed), abEdS: p(ed, ded, 2) + ' des requêtes de déduplication',"
                " abEa: nf_(ea), abEaS: p(ea, adj, 2) + ' des requêtes d’adjudication' };")
    return html


# ------------------------------------------------------------------ IDPS : un seul jour d'activité
def idps(html):
    n = (P.IDPS_DAY - P.START).days + 1
    s = [0] * n
    s[-1] = 14
    html = core(html, P.data([], end=P.IDPS_DAY, max_date=P.IDPS_DAY, extra={'idp': s}))
    html = band(html)
    start = html.index('<section aria-labelledby="ordres"')
    end = html.index('\n</main>')
    empty = ('<sc-if value="{{idOff}}" hint-placeholder-val="{{false}}"><section aria-labelledby="idps-vide" class="v7-panel">'
             '<div class="v7-head"><div><h2 id="idps-vide" class="en-h2">Aucun ordre IDPS sur cette période</h2>'
             '<p class="en-sub">Le seul jour d’activité IDPS est le 03/07/2026 : 14 ordres reçus, tous en erreur. Choisissez une période qui contient cette date.</p>'
             '</div></div></section></sc-if>\n')
    html = html[:start] + '<sc-if value="{{idOn}}" hint-placeholder-val="{{true}}">' + html[start:end] + '</sc-if>\n' + empty + html[end:]
    html = swap(html, 'return { weeks: weeks, wkRead: wkRead', 'return { weeks: weeks, wkRead: wkRead,' + UI_RET[:-1] +
                ", idOn: PER.v('idp') > 0, idOff: PER.v('idp') === 0")
    return html


FIXERS = {'Main.dc.html': main, 'Enrolement.dc.html': enrol, 'Cartes.dc.html': cartes, 'Biometrie.dc.html': bio, 'Idps.dc.html': idps, 'Usage.dc.html': usage}


def fix(name, html):
    return FIXERS[name](html) if name in FIXERS else html
