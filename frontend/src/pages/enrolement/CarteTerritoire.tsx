import type { LigneZone } from '../../api/client';
import { CarteZones } from '../../composants/carte/CarteZones';
import type { FondDeCarte } from '../../composants/carte/fondsDeCarte';
import { pct } from '../../lib/format';
import {
  CLASSES_TAUX_NIU,
  classeTauxNiu,
  lectureZone,
  tauxNiu,
  type ChiffresZone,
} from '../../lib/territoire';

interface Props {
  /** Fond de carte des sous-zones ; undefined si aucun contour ne correspond à la zone. */
  fond?: FondDeCarte;
  /** Zone affichée (Togo ou la région choisie) et ses chiffres. */
  zone: { nom: string; chiffres: ChiffresZone };
  lignes: LigneZone[];
  /** « Régions, du nord au sud » ou « Préfectures, du nord au sud ». */
  titreListe: string;
  libelleCarte: string;
  /** Ouvre une sous-zone (une région depuis la vue nationale) ; absent quand on ne peut pas descendre. */
  onOuvrir?: (ligne: LigneZone) => void;
  /** Libellé lu par les lecteurs d'écran sur une zone ouvrable (« Voir ses préfectures »). */
  libelleOuvrir?: string;
  /** Nom de la zone mise en évidence (préfecture ouverte, ou qui contient la zone ouverte). */
  selection?: string;
}

/** Carte du bloc Territoire : zones colorées selon le taux de NIU générés (classes de la maquette). */
export function CarteTerritoire({
  fond,
  zone,
  lignes,
  titreListe,
  libelleCarte,
  onOuvrir,
  libelleOuvrir,
  selection,
}: Props) {
  return (
    <CarteZones
      fond={fond}
      zone={{
        nom: zone.nom,
        valeur: pct(tauxNiu(zone.chiffres)),
        lecture: lectureZone(zone.nom, zone.chiffres),
      }}
      zones={lignes
        .filter((l) => !l.horsReferentiel || l.inscriptions > 0)
        .map((l) => ({
          code: l.code,
          nom: l.nom,
          valeur: pct(tauxNiu(l)),
          classe: classeTauxNiu(tauxNiu(l)),
          lecture: lectureZone(l.nom, l),
          ouvrable: !l.horsReferentiel,
        }))}
      titreListe={titreListe}
      libelleCarte={libelleCarte}
      libelleOuvrir={libelleOuvrir}
      selection={selection}
      legende={{ titre: 'Taux de NIU générés', libelles: CLASSES_TAUX_NIU.map((c) => c.libelle) }}
      onOuvrir={
        onOuvrir
          ? (code) => {
              const ligne = lignes.find((l) => l.code === code);
              if (ligne) onOuvrir(ligne);
            }
          : undefined
      }
    />
  );
}
