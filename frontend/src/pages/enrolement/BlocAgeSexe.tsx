import { useAgeSexe } from '../../api/enrolement';
import { BarresHorizontales } from '../../composants/blocs/BarresHorizontales';
import { Panneau } from '../../composants/blocs/Panneau';
import { Pyramide } from '../../composants/blocs/Pyramide';
import { lignesPyramide } from '../../lib/blocsVides';
import { usePlageApi } from '../../lib/usePlagePeriode';

/**
 * Bloc « NIU générés par âge, sexe et nationalité », mis en page comme le « Profil des pré-inscrits » (décision du
 * 28/10/2026) : nationalités à gauche, pyramide âge et sexe à droite (GET /api/v1/enrolement/age-sexe). National.
 * Source à venir : API d'enrichissement démographique, comme pour les pré-inscriptions (lot 6). D'ici là, les huit
 * tranches restent à 0, barres vides, et la liste des nationalités est vide : rien n'est estimé.
 */
export function BlocAgeSexe() {
  const { plage, prete } = usePlageApi('enrolement');
  const { data } = useAgeSexe(plage, undefined, prete);

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
          {/* Lot 6 : nationalités des NIU depuis l'API d'enrichissement (bi.fait_niu_nationalite_jour). */}
          <BarresHorizontales elements={[]} libelle="NIU générés par nationalité" />
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
