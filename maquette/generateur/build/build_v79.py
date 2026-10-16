import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import p_main, p_main_v2, p_main_v3, p_enrol, p_enrol_v5, p_bio, p_bio_v5, p_bio_v6, p_cartes, p_cartes_v5, p_idps, p_usage, p_tech, clean
OUT = pathlib.Path(__file__).resolve().parent.parent / 'maquette' / 'project'
pages = {'Main.dc.html': p_main_v3.build(), 'Enrolement.dc.html': p_enrol_v5.build(), 'Biometrie.dc.html': p_bio_v6.build(), 'Cartes.dc.html': p_cartes_v5.build(), 'Idps.dc.html': p_idps.build(),
         'Usage.dc.html': p_usage.build(), 'Technique.dc.html': p_tech.build()}
for name, html in pages.items():
    if name not in ('Enrolement.dc.html', 'Cartes.dc.html', 'Biometrie.dc.html'):  # p_enrol_v5 applique déjà les règles de nettoyage au script repris
        html = clean.clean(name, html)
    assert ('{{' in html or name == 'Biometrie.dc.html') and '</x-dc>' in html
    (OUT / name).write_text(html)
    print(name, len(html))
