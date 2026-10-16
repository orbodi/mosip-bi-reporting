import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import p_main, p_enrol, p_cartes, p_usage, p_tech
OUT = pathlib.Path(__file__).resolve().parent.parent / 'maquette' / 'project'
pages = {'Main.dc.html': p_main.build(), 'Enrolement.dc.html': p_enrol.build(), 'Cartes.dc.html': p_cartes.build(),
         'Usage.dc.html': p_usage.build(), 'Technique.dc.html': p_tech.build()}
for name, html in pages.items():
    assert '{{' in html and '</x-dc>' in html
    (OUT / name).write_text(html)
    print(name, len(html))
