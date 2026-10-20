import { useAgeSexe } from '../../api/enrolement';
import { Pyramide } from '../../composants/blocs/Pyramide';
import { lignesPyramide } from '../../lib/blocsVides';
import { useFiltreRegion } from '../../lib/useFiltreRegion';
import { usePlageApi } from '../../lib/usePlagePeriode';

/**
 * Bloc « NIU générés par âge et par sexe » : pyramide de la maquette, alimentée par le profil anonymisé de MOSIP
 * (GET /api/v1/enrolement/age-sexe, décision du 20/10/2026). Suit les filtres Période et Région. Sans données, les
 * huit tranches restent à 0, barres vides : rien n'est estimé.
 */
export function BlocAgeSexe() {
  const { region, code } = useFiltreRegion();
  const { plage, prete } = usePlageApi('enrolement');
  const { data } = useAgeSexe(plage, code, prete);

  return (
    <section className="panneau bloc-age-sexe" aria-labelledby="titre-age-sexe">
      <h2 id="titre-age-sexe" className="titre-bloc">
        NIU générés par âge et par sexe
      </h2>
      <p className="texte-2 bloc__sous-titre">
        {region ? `Région ${region.nom}` : 'Ensemble du Togo'}, nombre de NIU générés par tranche d’âge
      </p>
      <Pyramide lignes={lignesPyramide(data)} libelle="Répartition des NIU par tranche d’âge et par sexe" />
    </section>
  );
}
