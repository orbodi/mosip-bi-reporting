import { useFiltreRegion } from '../../lib/useFiltreRegion';

/**
 * Bloc « NIU générés par âge et par sexe » : non disponible (CLAUDE.md, règle « Sexe et âge »). MOSIP 1.1.5 n'a pas
 * de source anonymisée (anonymous_profile à partir de 1.1.5.5) ; le Data Mart range tout en « inconnu » tant que la
 * source n'est pas décidée (docs/decisions.md, pipeline point 1). Aucun chiffre n'est estimé.
 */
export function BlocAgeSexe() {
  const { region } = useFiltreRegion();
  return (
    <section className="panneau bloc-age-sexe" aria-labelledby="titre-age-sexe">
      <h2 id="titre-age-sexe" className="titre-bloc">
        NIU générés par âge et par sexe
      </h2>
      <p className="texte-2 bloc__sous-titre">
        {region ? `Région ${region.nom}` : 'Ensemble du Togo'}, nombre de NIU générés par tranche d’âge
      </p>
      <div className="non-disponible" role="note">
        <p className="non-disponible__titre">Non disponible</p>
        <p className="texte-2">
          La version de MOSIP en service ne fournit pas le sexe et l’âge sous une forme anonymisée. La
          pyramide s’affichera quand la source aura été décidée ; aucun chiffre n’est estimé en attendant.
        </p>
      </div>
    </section>
  );
}
