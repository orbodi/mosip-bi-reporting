import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import p_main, p_main_v2, p_enrol, p_bio, p_cartes, p_idps, p_usage, p_tech, clean
OUT = pathlib.Path(__file__).resolve().parent.parent / 'maquette' / 'project'
pages = {'Main.dc.html': p_main_v2.build(), 'Enrolement.dc.html': p_enrol.build(), 'Biometrie.dc.html': p_bio.build(), 'Cartes.dc.html': p_cartes.build(), 'Idps.dc.html': p_idps.build(),
         'Usage.dc.html': p_usage.build(), 'Technique.dc.html': p_tech.build()}
for name, html in pages.items():
    html = clean.clean(name, html)
    assert '{{' in html and '</x-dc>' in html
    (OUT / name).write_text(html)
    print(name, len(html))
