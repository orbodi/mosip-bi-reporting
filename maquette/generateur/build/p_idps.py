"""Onglet IDPS : ordres d'impression et erreurs (chiffres du BI actuel)."""
from common import *

FILTERS = PERIODE + REGION + DIVIDER + select('Type d’erreur', ['Tous les types', 'Personnalisation', 'Contrôle qualité', 'Supervision'], min_w=180)

I_KO = '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; fill: none; stroke: #D03B3B; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round"><circle cx="12" cy="12" r="10"></circle><line x1="9" y1="9" x2="15" y2="15"></line><line x1="15" y1="9" x2="9" y2="15"></line></svg>'
I_WARN = '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; fill: #FAB219; stroke: none"><path d="M12 2 1 21h22L12 2z"></path></svg>'
ARROW = '<svg width="22" height="14" viewBox="0 0 22 14" aria-hidden="true" style="flex-shrink: 0; align-self: center"><path d="M1 7 H19 M14 2 L20 7 L14 12" fill="none" stroke="#9AA7B5" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path></svg>'


def box(label, value, sub=''):
    return ('<div style="flex: 1 1 130px; min-width: 0; border: 1px solid #DCE3E9; border-radius: 6px; padding: 14px 16px; display: flex; flex-direction: column; gap: 2px">'
            '<span style="font-size: 13px; color: #4B5A6E">%s</span><span style="font-size: 30px; font-weight: 600; letter-spacing: -0.01em">%s</span>%s</div>'
            % (label, value, ('<span style="font-size: 12px; color: #4B5A6E">%s</span>' % sub) if sub else ''))


# ---------- 1. Ordres ----------
HERO = '''<section aria-labelledby="ordres" style="position: relative; background: #FFFFFF; border-radius: 8px; padding: 36px 40px; box-sizing: border-box; display: flex; flex-direction: column; gap: 22px">
''' + BRACKETS + '''<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 4px 24px">
<h2 id="ordres" style="margin: 0; font-size: 22px; font-weight: 600; letter-spacing: -0.01em">Ordres d’impression reçus depuis MOSIP</h2>
<span style="font-size: 13px; color: #4B5A6E">Dernier ordre le {{dernier}}</span>
</div>
<div style="display: flex; flex-wrap: wrap; gap: 24px 40px; align-items: stretch">
<div style="flex: 3 1 520px; min-width: 0; display: flex; flex-direction: column; gap: 14px">
<div style="display: flex; gap: 8px; align-items: stretch">''' + box('Ordres reçus', '14') + ARROW + box('En attente', '14') + ARROW + box('Cartes imprimées', '0') + '''</div>
<span style="font-size: 13px; color: #4B5A6E">Taux de traitement : <strong style="color: #071B35">0 %</strong></span>
<span style="display: inline-flex; align-items: center; gap: 8px; align-self: flex-start; padding: 6px 12px; border-radius: 6px; background: #FFF5DA; font-size: 13px; color: #6B4A00">''' + I_WARN + '''Les 14 ordres sont à la fois en attente et en erreur</span>
</div>
<div style="flex: 1 1 220px; min-width: 0; display: flex; flex-direction: column; justify-content: center; gap: 4px; padding: 18px 22px; border-radius: 8px; background: #FCEBEB">
<span style="display: inline-flex; align-items: center; gap: 8px; font-size: 13px; color: #6E1414">''' + I_KO + '''Taux d’échec</span>
<span style="font-size: clamp(40px, 8vw, 52px); font-weight: 600; letter-spacing: -0.02em; line-height: 1.05; color: #6E1414">100 %</span>
<span style="font-size: 13px; color: #6E1414">14 erreurs pour 14 ordres</span>
</div>
</div>
</section>
'''

# ---------- 2. Où les ordres échouent (étapes de production) ----------
STAGES = [('Personnalisation', 14, 3), ('Contrôle qualité', 11, 5), ('Supervision', 6, 6)]


def stage_row(name, n_in, n_err):
    ok = n_in - n_err
    w_ok, w_err = ok / 14 * 100, n_err / 14 * 100
    seg_ok = f'<div title="{name} : {ok} ordres passent" style="width: {w_ok:.1f}%; background: #1C5CAB"></div>' if ok else ''
    seg_err = f'<div title="{name} : {n_err} erreurs" style="width: {w_err:.1f}%; background: #D03B3B"></div>'
    return f'''<div role="row" style="display: grid; grid-template-columns: 170px 90px minmax(0, 1fr) 120px; gap: 16px; align-items: center; padding: 12px 0; border-top: 1px solid #EEF2F5">
<span role="rowheader" style="font-weight: 600">{name}</span>
<span role="cell" style="text-align: right">{n_in}</span>
<span role="cell" style="display: flex; gap: 2px; height: 14px">{seg_ok}{seg_err}</span>
<span role="cell" style="display: inline-flex; align-items: center; justify-content: flex-end; gap: 6px; font-weight: 600; color: #6E1414">{I_KO}{n_err}</span>
</div>'''


FAIL = '''<section aria-labelledby="echecs" style="''' + CARD + '''; display: flex; flex-direction: column; gap: 10px">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-end; gap: 8px 24px">
<div>
<h2 id="echecs" style="''' + H2 + '''">Où les ordres échouent</h2>
<p style="''' + SUB + '''">Étapes de production d’une carte, dans l’ordre.</p>
</div>
<span style="display: flex; gap: 18px; font-size: 13px; color: #4B5A6E"><span style="display: inline-flex; align-items: center; gap: 6px"><span style="width: 10px; height: 10px; border-radius: 2px; background: #1C5CAB"></span>Ordres qui passent</span><span style="display: inline-flex; align-items: center; gap: 6px"><span style="width: 10px; height: 10px; border-radius: 2px; background: #D03B3B"></span>Erreurs</span></span>
</div>
<div style="overflow-x: auto">
<div role="table" aria-label="Ordres par étape de production" style="min-width: 640px; font-variant-numeric: tabular-nums">
<div role="row" style="display: grid; grid-template-columns: 170px 90px minmax(0, 1fr) 120px; gap: 16px; padding: 6px 0; font-size: 12px; color: #4B5A6E">
<span role="columnheader">Étape</span><span role="columnheader" style="text-align: right">Ordres entrés</span><span role="columnheader">Sur les 14 ordres reçus</span><span role="columnheader" style="text-align: right">Erreurs</span>
</div>
''' + ''.join(stage_row(*s) for s in STAGES) + '''
<div role="row" style="display: grid; grid-template-columns: 170px 90px minmax(0, 1fr) 120px; gap: 16px; align-items: center; padding: 12px 0; border-top: 1px solid #DCE3E9">
<span role="rowheader" style="font-weight: 600">Cartes imprimées</span>
<span role="cell" style="text-align: right; font-weight: 600">0</span>
<span role="cell" style="height: 14px; background: #F3F5F8; border-radius: 0 4px 4px 0"></span>
<span role="cell"></span>
</div>
</div>
</div>
</section>
'''

# ---------- 3. Erreurs par type + régions ----------
def err_row(label, n, last):
    return f'''<div role="row" style="display: grid; grid-template-columns: 220px minmax(0, 1fr) 36px; gap: 12px; align-items: center; padding: 10px 0; border-top: 1px solid #EEF2F5">
<span role="rowheader" style="display: flex; flex-direction: column"><span style="font-size: 14px; font-weight: 500">{label}</span><span style="font-size: 12px; color: #4B5A6E">dernière le {last}</span></span>
<span role="cell" aria-hidden="true" style="height: 12px; background: #F3F5F8; border-radius: 0 4px 4px 0"><span style="display: block; height: 12px; width: {n / 6 * 100:.1f}%; background: #D03B3B; border-radius: 0 4px 4px 0"></span></span>
<span role="cell" style="text-align: right; font-weight: 600">{n}</span>
</div>'''


REGIONS = [('Savanes', 14, 14, 0, 14), ('Kara', 0, 0, 0, 0), ('Centrale', 0, 0, 0, 0), ('Plateaux', 0, 0, 0, 0), ('Maritime', 0, 0, 0, 0), ('Grand Lomé', 0, 0, 0, 0)]


def reg_row(name, rec, att, imp, err):
    c = '#071B35' if rec else '#9AA7B5'
    return (f'<div role="row" style="display: grid; grid-template-columns: minmax(110px, 1fr) 80px 90px 80px 70px; gap: 12px; align-items: center; padding: 9px 0; border-top: 1px solid #EEF2F5; color: {c}">'
            f'<span role="rowheader" style="font-weight: {600 if rec else 400}">{name}</span><span role="cell" style="text-align: right">{rec}</span>'
            f'<span role="cell" style="text-align: right">{att}</span><span role="cell" style="text-align: right">{imp}</span>'
            f'<span role="cell" style="text-align: right; font-weight: {600 if err else 400}; color: {"#6E1414" if err else c}">{err}</span></div>')


DETAIL = '''<div style="display: flex; flex-wrap: wrap; gap: 24px; align-items: stretch">
<section aria-labelledby="types" style="flex: 1 1 440px; min-width: 0; ''' + CARD + '''; display: flex; flex-direction: column; gap: 6px">
<div>
<h2 id="types" style="''' + H2 + '''">Erreurs par type</h2>
<p style="''' + SUB + '''">14 erreurs au total, toutes le 3 juillet 2026.</p>
</div>
<div role="table" aria-label="Erreurs d’impression par type" style="margin-top: 6px; font-variant-numeric: tabular-nums">''' \
    + err_row('Supervision', 6, '03/07/2026 à 16h48') + err_row('Contrôle qualité', 5, '03/07/2026 à 17h09') + err_row('Personnalisation', 3, '03/07/2026 à 17h01') + '''</div>
</section>
<section aria-labelledby="regions-idps" style="flex: 1 1 440px; min-width: 0; ''' + CARD + '''; display: flex; flex-direction: column; gap: 6px">
<div>
<h2 id="regions-idps" style="''' + H2 + '''">Ordres et erreurs par région</h2>
<p style="''' + SUB + '''">Régions du nord au sud.</p>
</div>
<div style="overflow-x: auto">
<div role="table" aria-label="Ordres IDPS par région" style="min-width: 470px; margin-top: 6px; font-variant-numeric: tabular-nums">
<div role="row" style="display: grid; grid-template-columns: minmax(110px, 1fr) 80px 90px 80px 70px; gap: 12px; padding: 6px 0; font-size: 12px; color: #4B5A6E">
<span role="columnheader">Région</span><span role="columnheader" style="text-align: right">Reçus</span><span role="columnheader" style="text-align: right">En attente</span><span role="columnheader" style="text-align: right">Imprimés</span><span role="columnheader" style="text-align: right">Erreurs</span>
</div>
''' + ''.join(reg_row(*r) for r in REGIONS) + '''
</div>
</div>
</section>
</div>
'''

# ---------- 4. Activité par semaine ----------
cols = []
for w in range(1, 40):
    rec, err = (14, 14) if w == 27 else (0, 0)
    tip = f'Semaine {w} : {rec} ordres reçus, {err} erreurs' if rec else f'Semaine {w} : aucun ordre'
    cols.append(f'<div title="{tip}" style="flex: 1 1 0; display: flex; align-items: flex-end; justify-content: center; gap: 1px; height: 64px">'
                f'<span style="width: 40%; height: {64 if rec else 1}px; background: {"#013781" if rec else "#DCE3E9"}; border-radius: 2px 2px 0 0"></span>'
                f'<span style="width: 40%; height: {64 if err else 1}px; background: {"#D03B3B" if err else "#DCE3E9"}; border-radius: 2px 2px 0 0"></span></div>')
months = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.']

WEEKS = '''<section aria-labelledby="semaines-idps" style="''' + CARD + '''; display: flex; flex-direction: column; gap: 10px">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-end; gap: 8px 24px">
<div>
<h2 id="semaines-idps" style="''' + H2 + '''">Ordres et erreurs par semaine, 2026</h2>
<p style="''' + SUB + '''">Une seule semaine active : celle du 29 juin au 5 juillet.</p>
</div>
<span style="display: flex; gap: 18px; font-size: 13px; color: #4B5A6E"><span style="display: inline-flex; align-items: center; gap: 6px"><span style="width: 10px; height: 10px; border-radius: 2px; background: #013781"></span>Ordres reçus</span><span style="display: inline-flex; align-items: center; gap: 6px"><span style="width: 10px; height: 10px; border-radius: 2px; background: #D03B3B"></span>Erreurs</span></span>
</div>
<div style="overflow-x: auto"><div style="min-width: 640px">
<div role="img" aria-label="Ordres IDPS par semaine en 2026 : 14 ordres et 14 erreurs, tous la semaine du 29 juin" style="display: flex; gap: 3px; border-bottom: 1px solid #9AA7B5">''' + ''.join(cols) + '''</div>
<div aria-hidden="true" style="display: grid; grid-template-columns: repeat(9, minmax(0, 1fr)); font-size: 12px; color: #4B5A6E; padding-top: 4px">''' + ''.join(f'<span>{m}</span>' for m in months) + '''</div>
</div></div>
</section>
'''

BODY = title('IDPS : ordres et erreurs d’impression') + HERO + FAIL + DETAIL + WEEKS

SCRIPT = r'''class Component extends DCLogic {
  renderVals() {
    return { dernier: '03/07/2026 à 17h09' };
  }
}'''


def build():
    return page('IDPS', 'Idps.dc.html', FILTERS, BODY, SCRIPT, 1730, '')
