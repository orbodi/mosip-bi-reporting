import { useProfilPreinscriptions } from '../../api/enrolement';
import { BarresHorizontales } from '../../composants/blocs/BarresHorizontales';
import { Panneau } from '../../composants/blocs/Panneau';
import { Pyramide } from '../../composants/blocs/Pyramide';
import { lignesPyramideAvecAgeInconnu } from '../../lib/blocsVides';
import { usePlageApi } from '../../lib/usePlagePeriode';

/**
 * Bloc « Profil des pré-inscrits » : demandes de pré-enrôlement par tranche d'âge et sexe (pyramide) et par
 * nationalité (GET /api/v1/enrolement/preinscriptions/profil). Source : champs extraits de l'API de pré-inscription
 * MOSIP. National, comme le bloc « Pré-inscription ».
 * La pyramide finit par « Âge inconnu » (sexe connu, âge absent) : ses totaux égalent les cartes Femmes et
 * Hommes du bloc « Pré-inscription ». Sans données, les lignes restent à 0 et la liste des nationalités est vide.
 */
export function BlocProfilPreinscription() {
  const { plage, prete } = usePlageApi('enrolement');
  const { data } = useProfilPreinscriptions(plage, prete);
  const nationalites = (data?.nationalites ?? []).map((n) => ({
    libelle: n.nom,
    valeur: n.demandes,
    couleur: 'bleu' as const,
  }));

  return (
    <Panneau
      id="titre-profil-preinscription"
      titre="Profil des pré-inscrits"
      sousTitre="Ensemble du Togo, demandes de pré-enrôlement par tranche d’âge, sexe et nationalité"
      className="bloc-pleine-largeur"
      sansMarge
    >
      <div className="duo">
        <div className="duo__principal">
          <h3 className="h3-m">Nationalités</h3>
          <BarresHorizontales elements={nationalites} libelle="Pré-inscriptions par nationalité" />
        </div>
        <div className="duo__cartes profil-preinscrits__pyramide">
          <h3 className="h3-m">Âge et sexe</h3>
          <Pyramide
            lignes={lignesPyramideAvecAgeInconnu(data)}
            libelle="Répartition des pré-inscriptions par tranche d’âge et par sexe"
          />
        </div>
      </div>
    </Panneau>
  );
}
