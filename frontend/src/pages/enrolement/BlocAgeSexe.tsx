import { Pyramide } from '../../composants/blocs/Pyramide';
import { pyramideInconnue } from '../../lib/blocsVides';
import { useFiltreRegion } from '../../lib/useFiltreRegion';

/**
 * Bloc « NIU générés par âge et par sexe » : pyramide de la maquette. MOSIP 1.1.5 n'a pas de source anonymisée
 * (anonymous_profile à partir de 1.1.5.5) ; le Data Mart range tout en « inconnu » tant que la source n'est pas
 * décidée (docs/decisions.md, pipeline point 1). Indicateurs à 0 en attendant (décision du 20/10/2026), rien n'est
 * estimé.
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
      <Pyramide lignes={pyramideInconnue()} libelle="Répartition des NIU par tranche d’âge et par sexe" />
    </section>
  );
}
