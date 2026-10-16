"""Pièces communes de la maquette BI ANID v3 (assemblées en fichiers .dc.html autonomes)."""

LOGO = '/_blob/d58a0ac035c394264bf474850f33072f'

TABS = [
    ('Main.dc.html', 'Vue d’ensemble'),
    ('Enrolement.dc.html', 'Enrôlement'),
    ('Cartes.dc.html', 'Cartes'),
    ('Usage.dc.html', 'Usage'),
    ('Technique.dc.html', 'Qualité et technique'),
]

SELECT_STYLE = 'height: 44px; padding: 0 10px; border: 1px solid #C5CFDA; border-radius: 6px; background: #FFFFFF; font-family: inherit; font-size: 14px; color: #071B35'
LABEL_STYLE = 'display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 500; color: #4B5A6E'
CARD = 'background: #FFFFFF; border-radius: 8px; padding: 28px; box-sizing: border-box'
H2 = 'margin: 0; font-size: 18px; font-weight: 600; color: #071B35'
SUB = 'margin: 2px 0 0; font-size: 13px; color: #4B5A6E'

BRACKETS = ''.join(
    '<span aria-hidden="true" style="position: absolute; %s; width: 22px; height: 22px; %s"></span>\n' % (pos, b)
    for pos, b in [
        ('top: 14px; left: 14px', 'border-top: 3px solid #FCBA21; border-left: 3px solid #FCBA21; border-top-left-radius: 5px'),
        ('top: 14px; right: 14px', 'border-top: 3px solid #FCBA21; border-right: 3px solid #FCBA21; border-top-right-radius: 5px'),
        ('bottom: 14px; left: 14px', 'border-bottom: 3px solid #FCBA21; border-left: 3px solid #FCBA21; border-bottom-left-radius: 5px'),
        ('bottom: 14px; right: 14px', 'border-bottom: 3px solid #FCBA21; border-right: 3px solid #FCBA21; border-bottom-right-radius: 5px'),
    ]
)

ICON_TRI = '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; fill: %s; stroke: none"><path d="M12 2 1 21h22L12 2z"></path></svg>'


def select(label, options, extra_attrs='', min_w=170, values=None):
    opts = ''.join(
        ('<option value="%s">%s</option>' % (values[i], o)) if values else ('<option>%s</option>' % o)
        for i, o in enumerate(options)
    )
    return ('<label style="%s">%s\n<select %s style="%s; min-width: %dpx">%s</select>\n</label>\n'
            % (LABEL_STYLE, label, extra_attrs, SELECT_STYLE, min_w, opts))


PERIODE = select('Période', ['Depuis le début', '7 derniers jours', '30 derniers jours', '90 derniers jours', 'Période personnalisée'], min_w=180)
REGION = select('Région', ['Toutes les régions', 'Grand Lomé', 'Maritime', 'Plateaux', 'Centrale', 'Kara', 'Savanes'])
DIVIDER = '<span aria-hidden="true" style="align-self: stretch; width: 1px; background: #DCE3E9; margin: 4px 0"></span>\n'

STATUS_CHIP = '''<div role="status" style="margin-left: auto; display: flex; align-items: center; gap: 10px; min-height: 44px; padding: 6px 14px; box-sizing: border-box; border-radius: 6px; background: #FCEBEB; color: #6E1414; font-size: 13px">
<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; fill: none; stroke: #D03B3B; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="7" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
<span><strong style="font-weight: 600">Alimentation interrompue.</strong> Données au 14/01/2026.</span>
</div>
'''


def header(active):
    links = []
    for href, label in TABS:
        if href == active:
            links.append('<a href="%s" aria-current="page" style="display: inline-flex; align-items: center; min-height: 44px; padding: 0 12px; color: #071B35; font-weight: 600; text-decoration: none; white-space: nowrap; box-shadow: inset 0 -3px 0 #FCBA21">%s</a>' % (href, label))
        else:
            links.append('<a href="%s" style="display: inline-flex; align-items: center; min-height: 44px; padding: 0 12px; color: #4B5A6E; font-weight: 500; text-decoration: none; white-space: nowrap">%s</a>' % (href, label))
    return '''<header style="background: #FFFFFF; border-bottom: 1px solid #DCE3E9">
<div style="max-width: 1376px; margin: 0 auto; padding: 10px 32px; box-sizing: border-box; display: flex; flex-wrap: wrap; align-items: center; gap: 8px 24px; min-height: 76px">
<div style="display: flex; align-items: center; gap: 16px">
<img src="%s" alt="ANID, Agence nationale d'identification" style="height: 46px; width: auto; display: block">
<span style="padding-left: 16px; border-left: 1px solid #DCE3E9; font-size: 15px; font-weight: 600; color: #013781; white-space: nowrap">BI Reporting</span>
</div>
<nav aria-label="Sections du tableau de bord" style="display: flex; gap: 2px; overflow-x: auto; max-width: 100%%">
%s
</nav>
<div style="margin-left: auto; display: flex; align-items: center; gap: 10px; font-size: 13px; color: #4B5A6E">
<span style="white-space: nowrap">Niveau national</span>
<span aria-hidden="true" style="width: 34px; height: 34px; border-radius: 17px; background: #E3EAF3; color: #013781; display: inline-flex; align-items: center; justify-content: center; font-weight: 600; font-size: 12px">GA</span>
<span style="white-space: nowrap">Global admin</span>
</div>
</div>
</header>
''' % (LOGO, '\n'.join(links))


def filters(inner):
    return '''<div style="background: #FFFFFF; border-bottom: 1px solid #DCE3E9">
<form aria-label="Filtres appliqués à toute la page" style="max-width: 1376px; margin: 0 auto; padding: 12px 32px 14px; box-sizing: border-box; display: flex; flex-wrap: wrap; align-items: flex-end; gap: 12px 16px">
%s%s</form>
</div>
''' % (inner, STATUS_CHIP)


def title(h1, note='Maquette v3, données illustratives'):
    return '''<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 4px 24px">
<h1 style="margin: 0; font-size: 28px; font-weight: 600; letter-spacing: -0.01em; color: #FFFFFF">%s</h1>
<p style="margin: 0; font-size: 13px; color: #D6E0F2">%s</p>
</div>
''' % (h1, note)


def page(doc_title, active, filter_inner, body, script, height, footer):
    return '''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>%s</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
<style>
body{margin:0;background:#F1F4F6}
a{color:#013781}a:hover{color:#071B35}
:focus-visible{outline:2px solid #013781;outline-offset:2px}
.fond-bio{background-color:#F1F4F6;background-image:url(/_blob/e7c52a49379b090417d28307896de81d);background-repeat:repeat;background-size:600px 600px;background-position:center 0}
.bande-bio{background-color:#013781;background-image:url(/_blob/41dd97e6745164acb3d0733253d730e8);background-repeat:no-repeat;background-size:auto 100%%;background-position:right center}
</style>
</helmet>
<div class="fond-bio" style="min-height: 100vh; font-family: Poppins, system-ui, sans-serif; color: #071B35; font-size: 14px; line-height: 1.5">
%s%s<div class="bande-bio" aria-hidden="true" style="height: 230px"></div>
<main style="position: relative; max-width: 1376px; margin: -230px auto 0; padding: 40px 32px 56px; box-sizing: border-box; display: flex; flex-direction: column; gap: 24px">
%s
<p style="margin: 0; font-size: 13px; color: #4B5A6E">%s</p>
</main>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{"$preview":{"width":1440,"height":%d}}'>
%s
</script>
</body>
</html>
''' % (doc_title, header(active), filters(filter_inner), body, footer, height, script)
