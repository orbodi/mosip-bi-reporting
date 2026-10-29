import { useAgeSexe } from '../../api/enrolement';
import { BarresHorizontales } from '../../composants/blocs/BarresHorizontales';
import { Panneau } from '../../composants/blocs/Panneau';
import { Pyramide } from '../../composants/blocs/Pyramide';
import { lignesPyramide } from '../../lib/blocsVides';
import { usePlageApi } from '../../lib/usePlagePeriode';

/**
 * Bloc « NIU générés par âge, sexe et nationalité », mis en page comme le « Profil des pré-inscrits » (décision du
 * 28/10/2026) : nationalités à gauche (les cinq premières, puis « Autres » et « Non renseignée »), pyramide âge et sexe
 * à droite (GET /api/v1/enrolement/age-sexe). National. Source : enrichissement des NIU par l'ID Repository de MOSIP
 * (lot 6), au jour de génération du NIU. Sans données, les huit tranches restent à 0, barres vides, et la liste des
 * nationalités est vide : rien n'est estimé.
 */
export function BlocAgeSexe() {
  const { plage, prete } = usePlageApi('enrolement');
  const { data } = useAgeSexe(plage, undefined, prete);
  const nationalites = (data?.nationalites ?? []).map((n) => ({
    libelle: n.nom,
    valeur: n.niuGeneres,
    couleur: 'bleu' as const,
  }));

  return (
    <Panneau
      id="titre-age-sexe"
      titre="NIU générés par âge, sexe et nationalité"
      sousTitre="Ensemble du Togo, NIU générés par tranche d’âge, sexe et nationalité"
      className="bloc-pleine-largeur bloc-age-sexe"
      sansMarge
    >
      <div className="duo">
        <div className="duo__principal">
          <h3 className="h3-m">Nationalités</h3>
          <BarresHorizontales elements={nationalites} libelle="NIU générés par nationalité" />
        </div>
        <div className="duo__cartes profil-preinscrits__pyramide">
          <h3 className="h3-m">Âge et sexe</h3>
          <Pyramide
            lignes={lignesPyramide(data)}
            libelle="Répartition des NIU par tranche d’âge et par sexe"
          />
        </div>
      </div>
    </Panneau>
  );
}
