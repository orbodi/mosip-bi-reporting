import { Bandeau } from '../composants/coque/Bandeau';
import type { DefinitionPage } from './pages';

/**
 * Page du socle : bandeau réel et liste des blocs à construire d'après la maquette.
 * À remplacer bloc par bloc (voir docs/feuille-de-route.md et la skill /nouveau-kpi).
 */
export function PageAConstruire({ page }: { page: DefinitionPage }) {
  return (
    <>
      <Bandeau titre={page.titre} source={page.source} />
      <div className="contenu">
        <section className="panneau" aria-labelledby="a-construire">
          <h2 id="a-construire" className="titre-bloc">
            Page à construire
          </h2>
          <p className="texte-2">
            Référence : <code>maquette/pages/{page.maquette}.dc.html</code> et{' '}
            <code>maquette/captures/{page.maquette}-1440.png</code>. Blocs dans l’ordre de la maquette :
          </p>
          <ol>
            {page.blocs.map((bloc) => (
              <li key={bloc}>{bloc}</li>
            ))}
          </ol>
        </section>
      </div>
    </>
  );
}
