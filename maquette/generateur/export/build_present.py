"""Exporte la maquette (7 onglets) en un seul fichier HTML autonome, pour présentation.

- Chaque onglet tourne dans un iframe (srcdoc) avec un petit moteur de rendu (harness) ; les liens entre onglets restent actifs.
- Polices Poppins, logo et fonds d'empreintes embarqués : aucun accès réseau nécessaire.
- Navigation : onglets de chaque page, flèches gauche/droite, touche F (plein écran), adresse #Main, #Cartes...
"""
import base64, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'maquette' / 'project'
OUT = pathlib.Path('/mnt/user-data/outputs/BI_ANID_maquette_presentation.html')

ORDER = [('Main', 'Vue d’ensemble'), ('Enrolement', 'Enrôlement'), ('Cartes', 'Impression des cartes'), ('Biometrie', 'ABIS'),
         ('Idps', 'IDPS'), ('Usage', 'Authentifications'), ('Technique', 'Exploration des données')]


def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode()


ASSETS = {
    'd58a0ac035c394264bf474850f33072f': 'data:image/svg+xml;base64,' + b64(ROOT / 'maquette/assets/anid-logo.svg'),
    'e7c52a49379b090417d28307896de81d': 'data:image/svg+xml;base64,' + b64(ROOT / 'bio/fond-empreintes-clair-v2.svg'),
    '41200b4723504e051b5b0bd1b777ba52': 'data:image/svg+xml;base64,' + b64(ROOT / 'bio/bande-empreintes-v3.svg'),
}
FD = pathlib.Path('/usr/share/fonts/truetype/google-fonts')
FONT_CSS = ''.join(
    "@font-face{font-family:'Poppins';font-style:normal;font-weight:%s;font-display:block;src:url(data:font/ttf;base64,%s) format('truetype')}" % (w, b64(FD / f))
    for w, f in [('400', 'Poppins-Regular.ttf'), ('500', 'Poppins-Medium.ttf'), ('600 700', 'Poppins-Bold.ttf')])

harness = (ROOT / 'render' / 'harness.js').read_text()
# garde la position de défilement quand la page se redessine (clic sur la carte, choix d'une modalité...)
harness = harness.replace("  function render() {\n    const vals = inst.renderVals();",
                          "  function render() {\n    const sy = window.scrollY;\n    const vals = inst.renderVals();")
harness = harness.replace("    host.querySelectorAll('select[value]').forEach((s) => { s.value = s.getAttribute('value'); });\n  }",
                          "    host.querySelectorAll('select[value]').forEach((s) => { s.value = s.getAttribute('value'); });\n    window.scrollTo(0, sy);\n  }")
assert 'window.scrollTo(0, sy)' in harness

NAV = r'''<script>
(function () {
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var h = a.getAttribute('href');
    var m = /^([A-Za-z]+)\.dc\.html(#[\w-]+)?$/.exec(h);
    if (m) { e.preventDefault(); parent.postMessage({ anidNav: 'go', nom: m[1], ancre: m[2] ? m[2].slice(1) : '' }, '*'); return; }
    if (h.charAt(0) === '#') { e.preventDefault(); var el = document.getElementById(h.slice(1)); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  }, true);
  document.addEventListener('keydown', function (e) {
    var t = e.target.tagName;
    if (t === 'INPUT' || t === 'SELECT' || t === 'TEXTAREA') return;
    if (['ArrowRight', 'ArrowLeft', 'PageDown', 'PageUp', 'Home', 'f', 'F'].indexOf(e.key) < 0) return;
    e.preventDefault();
    parent.postMessage({ anidNav: 'key', k: e.key }, '*');
  });
})();
</script>'''


def page_html(name):
    html = (SRC / f'{name}.dc.html').read_text()
    html = html.replace('<script src="./support.js"></script>', '')
    html = re.sub(r'<link rel="preconnect"[^>]*>\n?', '', html)
    html = re.sub(r'<link href="https://fonts\.googleapis\.com[^>]*>\n?', '', html)
    for k in ASSETS:
        html = html.replace(f'/_blob/{k}', f'__ASSET_{k}__')
    assert '/_blob/' not in html, name
    html = html.replace('<head>', '<head>\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<style>__FONTS__</style>', 1)
    html = html.replace('</body>', '<script>' + harness + '</script>\n' + NAV + '\n</body>')
    return html


PAGES = {n: page_html(n) for n, _ in ORDER}

LOGO = ASSETS['d58a0ac035c394264bf474850f33072f']
INFO = {
    'Main': ('Le parcours du citoyen en sept étapes, de la pré-inscription à la carte en main, les chiffres clés de chaque module et la carte des régions.',
             [('3 278 239', 'inscriptions'), ('1 770 796', 'cartes remises')]),
    'Enrolement': ('Pré-inscription, devenir des inscriptions, évolution par semaine, territoire jusqu’aux préfectures, âge et sexe, top des centres.',
                   [('3 058 886', 'NIU générés'), ('86 496', 'rejets')]),
    'Cartes': ('Impression et remise, impressions et rejets par semaine, cartes à remettre par région, ancienneté, top des centres.',
               [('3 101 590', 'cartes expédiées'), ('1 330 794', 'à remettre')]),
    'Biometrie': ('Transactions, adjudication, erreurs et qualité des biométries, selon le document IN Groupe v0.2.',
                  [('3 158 734', 'déduplications'), ('41 870', 'adjudications')]),
    'Idps': ('Nouveau circuit d’impression, en pilote : ordres reçus, étapes où ils échouent, erreurs par type.',
             [('14', 'ordres reçus'), ('14', 'en erreur')]),
    'Usage': ('Requêtes de vérification d’identité, types d’authentification, causes des échecs, évolution par semaine.',
              [('510 499', 'requêtes'), ('294 763', 'échouées')]),
    'Technique': ('Les 24 indicateurs des cinq sources à croiser : période, territoire jusqu’au centre, profil, export CSV.',
                  [('24', 'indicateurs'), ('5', 'sources')]),
}
ARROW = ('<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" style="fill:none;stroke:currentColor;stroke-width:2.2;'
         'stroke-linecap:round;stroke-linejoin:round"><path d="M5 12h14M13 6l6 6-6 6"></path></svg>')
CARDS = ''.join(
    f'<a class="pg{" une" if i == 0 else ""}" href="{n}.dc.html"><span class="num">{i + 1}</span><span class="txt"><span class="nom">{label}</span>'
    f'<span class="desc">{INFO[n][0]}</span><span class="chiffres">'
    + ''.join(f'<span><strong>{v}</strong> {u}</span>' for v, u in INFO[n][1])
    + f'</span></span><span class="go">Ouvrir{ARROW}</span></a>\n'
    for i, (n, label) in enumerate(ORDER))
COVER = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>__FONTS__
:root{--navy:#1F4E8C;--ink:#071B35;--gold:#FCBA21;--muted:#4B5A6E;--line:#E3E9EF;--ground:#F1F4F6}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;background:var(--ground);font-family:Poppins,system-ui,sans-serif;color:var(--ink);font-size:14px;line-height:1.5}
.bande{background:var(--navy) url(__ASSET_41200b4723504e051b5b0bd1b777ba52__) no-repeat right center/auto 100%;color:#fff}
.bande-in{max-width:1240px;margin:0 auto;padding:36px 32px 120px;display:flex;flex-direction:column;gap:22px}
.tete{display:flex;align-items:center;gap:16px}.tete img{height:48px;filter:brightness(0) invert(1)}
.tete span{padding-left:16px;border-left:1px solid rgba(255,255,255,.35);font-size:16px;font-weight:600}
h1{margin:0;font-size:clamp(28px,4vw,40px);font-weight:600;letter-spacing:-.02em;line-height:1.15;text-wrap:balance}
.sous{margin:0;max-width:720px;font-size:16px;color:rgba(255,255,255,.86)}
.meta{display:flex;flex-wrap:wrap;gap:8px}
.meta span{display:inline-flex;align-items:center;padding:4px 12px;border-radius:999px;background:rgba(255,255,255,.12);font-size:12.5px;font-weight:500}
.meta span.or{background:var(--gold);color:var(--ink);font-weight:600}
main{max-width:1240px;margin:-84px auto 0;padding:0 32px 48px;display:flex;flex-direction:column;gap:20px}
.grille{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.une{grid-column:1/-1}.une .desc{max-width:640px}.une .chiffres{flex-direction:row;gap:4px 28px}
.pg{display:grid;grid-template-columns:auto minmax(0,1fr);grid-template-rows:1fr auto;column-gap:16px;row-gap:14px;padding:22px 22px 18px;border:1px solid var(--line);border-radius:14px;
background:#fff;color:var(--ink);text-decoration:none;box-shadow:0 1px 2px rgba(7,27,53,.06),0 8px 24px rgba(7,27,53,.06);transition:border-color .15s,box-shadow .15s}
.pg:hover,.pg:focus-visible{border-color:var(--navy);box-shadow:0 2px 4px rgba(7,27,53,.08),0 12px 28px rgba(7,27,53,.1);outline:none}
.pg:focus-visible{outline:2px solid var(--navy);outline-offset:2px}
.num{grid-row:1/span 2;width:34px;height:34px;border-radius:17px;background:var(--navy);color:#fff;display:inline-flex;align-items:center;justify-content:center;font-weight:600;font-size:14px}
.txt{display:flex;flex-direction:column;gap:6px;min-width:0}
.nom{font-size:18px;font-weight:600;line-height:1.3}
.desc{color:var(--muted);font-size:13.5px}
.chiffres{display:flex;flex-direction:column;gap:2px;margin-top:6px;font-size:13px;color:var(--muted);font-variant-numeric:tabular-nums}
.chiffres strong{font-size:16px;font-weight:600;color:var(--ink)}
.go{grid-column:2;justify-self:start;display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:600;color:var(--navy)}
.pied{display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px 24px;padding-top:6px;font-size:13px;color:var(--muted)}
kbd{font-family:inherit;font-size:12px;padding:1px 6px;border:1px solid #C5CFDA;border-bottom-width:2px;border-radius:4px;background:#fff}
@media (max-width:1000px){.grille{grid-template-columns:repeat(2,minmax(0,1fr))}}@media (max-width:700px){.bande{background-image:linear-gradient(rgba(31,78,140,.82),rgba(31,78,140,.82)),url(__ASSET_41200b4723504e051b5b0bd1b777ba52__)}.bande-in{padding:28px 16px 104px}.tete img{height:40px}main{padding:0 16px 40px}.grille{grid-template-columns:minmax(0,1fr)}.une .chiffres{flex-direction:column}.pg{padding:18px 16px 16px}}
</style></head><body>
<header class="bande"><div class="bande-in">
<div class="tete"><img src="__ASSET_d58a0ac035c394264bf474850f33072f__" alt="ANID, Agence nationale d'identification"><span>BI Reporting</span></div>
<h1>Maquette du tableau de bord MOSIP</h1>
<p class="sous">Le suivi du citoyen, de la pré-inscription à la carte en main, et les modules ABIS, IDPS et authentification. Chaque page est cliquable, comme dans le produit.</p>
<div class="meta"><span class="or">Version du 9 octobre 2026</span><span>7 pages</span><span>Données au 14/01/2026 (IDPS : 03/07/2026)</span></div>
</div></header>
<main>
<nav class="grille" aria-label="Pages de la maquette">
""" + CARDS + """</nav>
<div class="pied"><span>Données en partie illustratives, cohérentes d’une page à l’autre. Filtres Région et Période actifs.</span>
<span><kbd>←</kbd> <kbd>→</kbd> page précédente ou suivante · <kbd>F</kbd> plein écran · <kbd>Début</kbd> sommaire</span></div>
</main>
""" + NAV + """
</body></html>"""
EYE = ('<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" style="fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round">'
       '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"></path><circle cx="12" cy="12" r="3"></circle></svg>')
# 9 oct. : la page d'accueil devient un écran de connexion façon Keycloak (thème ANID) ; maquette sans vérification ni envoi
LOGIN = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>__FONTS__
:root{--navy:#1F4E8C;--navy-d:#183F73;--ink:#071B35;--muted:#4B5A6E;--line:#8A97A6;--ground:#F1F4F6;--danger:#C9190B;--danger-bg:#FAEAE8}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;min-height:100%;font-family:Poppins,system-ui,sans-serif;font-size:14px;line-height:1.5;color:var(--ink);
background:var(--navy) linear-gradient(rgba(31,78,140,.86),rgba(31,78,140,.86)),url(__ASSET_41200b4723504e051b5b0bd1b777ba52__) no-repeat center/cover;background-color:var(--navy);display:flex;flex-direction:column;align-items:center;justify-content:center;padding:48px 16px 32px}
.realm{display:flex;align-items:center;gap:14px;margin-bottom:28px;color:#fff}
.realm img{height:52px;filter:brightness(0) invert(1)}
.realm span{padding-left:14px;border-left:1px solid rgba(255,255,255,.4);font-size:18px;font-weight:600;letter-spacing:.01em}
.card{width:100%;max-width:460px;background:#fff;border-radius:6px;box-shadow:0 12px 40px rgba(1,27,63,.35);border-top:3px solid #FCBA21}
.card-h{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;padding:28px 32px 4px}
h1{margin:0;font-size:22px;font-weight:600;line-height:1.3;color:var(--ink)}
.lang{position:relative;flex-shrink:0}
.lang select{appearance:none;-webkit-appearance:none;height:32px;padding:0 26px 0 10px;border:1px solid transparent;border-radius:4px;background:transparent;font:500 13px Poppins,system-ui,sans-serif;color:var(--navy);cursor:pointer}
.lang select:hover{border-color:#C5CFDA}.lang::after{content:"";position:absolute;right:10px;top:12px;width:6px;height:6px;border-right:2px solid var(--navy);border-bottom:2px solid var(--navy);transform:rotate(45deg);pointer-events:none}
form{display:flex;flex-direction:column;gap:18px;padding:20px 32px 32px}
.alerte{display:none;gap:10px;align-items:flex-start;padding:10px 12px;border-left:3px solid var(--danger);border-radius:2px;background:var(--danger-bg);color:#7D1007;font-size:13.5px}
.alerte.on{display:flex}.alerte strong{font-weight:600}
.champ{display:flex;flex-direction:column;gap:6px}
label{font-size:13.5px;font-weight:500;color:var(--ink)}
label .req{color:var(--danger);margin-left:2px}
.inp{position:relative;display:flex}
input[type=text],input[type=password]{width:100%;height:42px;padding:0 12px;border:1px solid var(--line);border-bottom-width:2px;border-radius:3px;background:#fff;font:400 15px Poppins,system-ui,sans-serif;color:var(--ink)}
input[type=text]:hover,input[type=password]:hover{border-bottom-color:var(--navy)}
input[type=text]:focus,input[type=password]:focus{outline:none;border-color:var(--navy);box-shadow:0 0 0 3px rgba(31,78,140,.15)}
input.err{border-color:var(--danger)}
.inp input{padding-right:46px}
.oeil{position:absolute;right:4px;top:4px;width:36px;height:34px;display:inline-flex;align-items:center;justify-content:center;border:0;border-radius:3px;background:transparent;color:var(--muted);cursor:pointer}
.oeil:hover{color:var(--navy);background:#EEF4FB}
.oeil[aria-pressed=true]{color:var(--navy)}
.ligne{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.coche{display:inline-flex;align-items:center;gap:8px;font-weight:400;cursor:pointer}
.coche input{width:16px;height:16px;margin:0;accent-color:var(--navy)}
.lien{padding:0;border:0;background:none;font:500 13.5px Poppins,system-ui,sans-serif;color:var(--navy);cursor:pointer;text-decoration:underline;text-underline-offset:3px}
.lien:hover{color:var(--ink)}
.info{display:none;margin:-6px 0 0;font-size:13px;color:var(--muted)}.info.on{display:block}
.btn{height:44px;border:0;border-radius:3px;background:var(--navy);font:600 15px Poppins,system-ui,sans-serif;color:#fff;cursor:pointer}
.btn:hover{background:var(--navy-d)}
:focus-visible{outline:2px solid var(--navy);outline-offset:2px}
.btn:focus-visible{outline-color:#FCBA21}
.pied{margin-top:20px;max-width:460px;width:100%;display:flex;flex-direction:column;align-items:center;gap:2px;text-align:center;font-size:12.5px;color:rgba(255,255,255,.85)}
@media (max-width:700px){body{padding-top:32px;justify-content:flex-start}
.realm img{height:44px}.card-h{padding:22px 20px 4px}form{padding:18px 20px 24px}h1{font-size:20px}input[type=text],input[type=password]{font-size:16px}}
</style></head><body>
<div class="realm"><img src="__ASSET_d58a0ac035c394264bf474850f33072f__" alt="ANID, Agence nationale d'identification"><span>BI Reporting</span></div>
<main class="card">
<div class="card-h"><h1 id="titre">Connectez-vous à votre compte</h1>
<span class="lang"><select id="langue" aria-label="Langue"><option>Français</option><option>English</option></select></span></div>
<form id="f" novalidate autocomplete="off" aria-labelledby="titre">
<div id="alerte" class="alerte" role="alert"><strong>Nom d’utilisateur ou mot de passe invalide.</strong></div>
<div class="champ"><label for="u">Nom d’utilisateur ou e-mail<span class="req" aria-hidden="true">*</span></label>
<input id="u" name="u" type="text" autocomplete="off" autocapitalize="off" spellcheck="false" autofocus></div>
<div class="champ"><label for="p">Mot de passe<span class="req" aria-hidden="true">*</span></label>
<div class="inp"><input id="p" name="p" type="password" autocomplete="new-password">
<button id="oeil" class="oeil" type="button" aria-label="Afficher le mot de passe" aria-pressed="false">""" + EYE + """</button></div></div>
<div class="ligne"><label class="coche"><input id="r" type="checkbox">Se souvenir de moi</label>
<button id="oubli" class="lien" type="button">Mot de passe oublié ?</button></div>
<p id="info" class="info" role="status">Dans la maquette, la réinitialisation du mot de passe n’est pas représentée.</p>
<button id="go" class="btn" type="button">Se connecter</button>
</form>
</main>
<div class="pied"><span>Maquette : aucun identifiant n’est vérifié, enregistré ni envoyé.</span><span>ANID, Togo</span></div>
<script>
(function () {
  var f = document.getElementById('f'), u = document.getElementById('u'), p = document.getElementById('p'), al = document.getElementById('alerte');
  document.getElementById('oeil').addEventListener('click', function () {
    var on = p.type === 'password'; p.type = on ? 'text' : 'password';
    this.setAttribute('aria-pressed', on ? 'true' : 'false'); this.setAttribute('aria-label', on ? 'Masquer le mot de passe' : 'Afficher le mot de passe');
  });
  document.getElementById('oubli').addEventListener('click', function () { document.getElementById('info').className = 'info on'; });
  function entrer() {
    var ok = u.value.trim() !== '' && p.value !== '';
    u.className = u.value.trim() ? '' : 'err'; p.className = p.value ? '' : 'err';
    if (!ok) { al.className = 'alerte on'; (u.value.trim() ? p : u).focus(); return; }
    u.value = ''; p.value = '';
    parent.postMessage({ anidNav: 'go', nom: 'Main', ancre: '' }, '*');
  }
  document.getElementById('go').addEventListener('click', entrer);
  [u, p].forEach(function (x) { x.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); entrer(); } }); });
  f.addEventListener('submit', function (e) { e.preventDefault(); entrer(); });
})();
</script>
""" + NAV + """
</body></html>"""
PAGES = {'Accueil': LOGIN, **PAGES}
SEQ = ['Accueil'] + [n for n, _ in ORDER]

SHELL = '''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Maquette BI ANID</title>
<style>
html,body{margin:0;height:100%;background:#F1F4F6;overflow:hidden}
iframe{display:block;border:0;width:100%;height:100%}
#aide{position:fixed;right:16px;bottom:16px;padding:8px 14px;border-radius:6px;background:rgba(7,27,53,.88);color:#fff;font:500 13px/1.4 system-ui,sans-serif;opacity:0;transition:opacity .4s;pointer-events:none}
#aide.on{opacity:1}
@media (max-width:700px){#aide{display:none}}
#som{position:fixed;left:16px;bottom:16px;z-index:5;display:inline-flex;align-items:center;gap:8px;min-height:40px;padding:0 16px;border:0;border-radius:999px;background:#1F4E8C;color:#fff;font:600 13px/1 Poppins,system-ui,sans-serif;box-shadow:0 6px 18px rgba(7,27,53,.25);cursor:pointer}
#som:hover{background:#071B35}#som:focus-visible{outline:2px solid #FCBA21;outline-offset:2px}
#som[hidden]{display:none}
</style>
</head>
<body>
<iframe id="vue" title="Maquette BI ANID"></iframe>
<div id="aide" role="status" aria-live="polite"></div>
<button id="som" type="button" hidden>Se déconnecter</button>
<script>
var PAGES = __PAGES__;
var SEQ = __SEQ__;
var LABELS = __LABELS__;
var ASSETS = __ASSETS__;
var FONTS = __FONTCSS__;
var vue = document.getElementById('vue'), aide = document.getElementById('aide'), courant = null, tAide = null;
var som = document.getElementById('som'); som.addEventListener('click', function () { __go('Accueil'); });
function montre(txt) { aide.textContent = txt; aide.className = 'on'; clearTimeout(tAide); tAide = setTimeout(function () { aide.className = ''; }, 2200); }
function charge(nom, ancre) {
  if (!PAGES[nom]) nom = 'Accueil';
  var html = PAGES[nom].replace('__FONTS__', FONTS).replace(/__ASSET_(\\w+)__/g, function (_, k) { return ASSETS[k]; });
  courant = nom;
  som.hidden = nom === 'Accueil';
  vue.onload = function () {
    try { vue.contentWindow.focus(); } catch (e) {}
    if (ancre) setTimeout(function () { var el = vue.contentDocument.getElementById(ancre); if (el) el.scrollIntoView({ block: 'start' }); }, 150);
  };
  vue.srcdoc = html;
  document.title = 'BI ANID : ' + LABELS[nom];
  var i = SEQ.indexOf(nom);
  if (i > 0) montre(i + ' / ' + (SEQ.length - 1) + ' · ' + LABELS[nom] + ' · ← → pour naviguer · F plein écran');
}
window.__go = function (nom, ancre) {
  charge(nom, ancre);
  try { history.pushState(null, '', '#' + nom + (ancre ? '/' + ancre : '')); } catch (e) {}
};
window.addEventListener('message', function (e) {
  var d = e.data;
  if (!d || typeof d !== 'object' || !d.anidNav || e.source !== vue.contentWindow) return;
  if (d.anidNav === 'go') __go(String(d.nom || ''), String(d.ancre || ''));
  if (d.anidNav === 'key') __key(String(d.k || ''));
});
window.__key = function (k) {
  var i = SEQ.indexOf(courant);
  if (k === 'ArrowRight' || k === 'PageDown') { if (i < SEQ.length - 1) __go(SEQ[i + 1]); return true; }
  if (k === 'ArrowLeft' || k === 'PageUp') { if (i > 0) __go(SEQ[i - 1]); return true; }
  if (k === 'Home') { __go('Accueil'); return true; }
  if (k === 'f' || k === 'F') {
    try {
      var r = document.fullscreenElement ? document.exitFullscreen() : (document.documentElement.requestFullscreen ? document.documentElement.requestFullscreen() : null);
      if (r && r.catch) r.catch(function () {});
    } catch (e) {}
    return true;
  }
  return false;
};
document.addEventListener('keydown', function (e) { if (__key(e.key)) e.preventDefault(); });
function route() { var h = location.hash.slice(1).split('/'); charge(h[0] || 'Accueil', h[1] || ''); }
window.addEventListener('popstate', route);
route();
</script>
</body>
</html>
'''
labels = {'Accueil': 'connexion', **{n: l for n, l in ORDER}}
out = (SHELL.replace('__PAGES__', json.dumps(PAGES, ensure_ascii=False).replace('</', '<\\/'))
       .replace('__SEQ__', json.dumps(SEQ)).replace('__LABELS__', json.dumps(labels, ensure_ascii=False))
       .replace('__ASSETS__', json.dumps(ASSETS)).replace('__FONTCSS__', json.dumps(FONT_CSS)))
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(out)
print(OUT, round(len(out.encode()) / 1024), 'Ko')
