import { Bandeau } from '../../composants/coque/Bandeau';
import type { DefinitionPage } from '../pages';
import { BlocDevenir } from './BlocDevenir';

const BLOCS_FAITS = ['Devenir des inscriptions'];

/** Page Enrôlement : blocs construits au fil de l'eau, les autres restent listés d'après la maquette. */
export function PageEnrolement({ page }: { page: DefinitionPage }) {
  const restants = page.blocs.filter((bloc) => !BLOCS_FAITS.includes(bloc));
  return (
    <>
      <Bandeau titre={page.titre} source={page.source} />
      <div className="contenu grille-page">
        <BlocDevenir />
        <section className="panneau" aria-labelledby="blocs-a-construire">
          <h2 id="blocs-a-construire" className="titre-bloc">
            Blocs à construire
          </h2>
          <p className="texte-2">
            Référence : <code>maquette/pages/{page.maquette}.dc.html</code>. Dans l’ordre de la maquette :
          </p>
          <ol>
            {restants.map((bloc) => (
              <li key={bloc}>{bloc}</li>
            ))}
          </ol>
        </section>
      </div>
    </>
  );
}
