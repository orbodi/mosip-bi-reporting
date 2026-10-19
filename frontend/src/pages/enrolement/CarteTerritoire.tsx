import { useMemo, useState } from 'react';
import type { LigneZone } from '../../api/client';
import { contourDe, type FondDeCarte } from '../../composants/carte/fondsDeCarte';
import { Graphique } from '../../composants/graphique/Graphique';
import type { EChartsCoreOption } from '../../composants/graphique/echarts';
import { pct } from '../../lib/format';
import { jeton } from '../../lib/jetons';
import {
  CLASSES_TAUX_NIU,
  classeTauxNiu,
  cleNom,
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
}

/** Couleur ECharts d'une zone (jeton de sa classe) ; gris sans inscription. */
const couleurClasse = (chiffres: ChiffresZone) => {
  const classe = classeTauxNiu(tauxNiu(chiffres));
  return classe < 0 ? jeton('--trait') : jeton(CLASSES_TAUX_NIU[classe].jeton);
};

/** Même couleur en CSS pour la liste et la légende (classes de enrolement.css). */
const classeCss = (indice: number) => `classe-niu classe-niu--${indice < 0 ? 'aucune' : indice}`;

/**
 * Carte du bloc Territoire : liste des zones à gauche (clavier, lecteurs d'écran), carte ECharts colorée selon le taux
 * de NIU générés, légende des classes et source des contours. Survol ou focus d'une zone : lecture au-dessus de la liste.
 */
export function CarteTerritoire({ fond, zone, lignes, titreListe, libelleCarte, onOuvrir }: Props) {
  const [survol, setSurvol] = useState<string | null>(null);
  const ligneDe = (nom: string) => lignes.find((l) => cleNom(l.nom) === cleNom(nom));
  const ciblee = survol ? ligneDe(survol) : undefined;
  const lecture = ciblee ? lectureZone(ciblee.nom, ciblee) : lectureZone(zone.nom, zone.chiffres);

  const option = useMemo<EChartsCoreOption | undefined>(() => {
    if (!fond) return undefined;
    const texte = { color: jeton('--encre'), borderColor: jeton('--surface') };
    return {
      animation: false,
      tooltip: { show: false },
      series: [
        {
          type: 'map',
          map: fond.nom,
          roam: false,
          selectedMode: false,
          aspectScale: 1,
          left: 4,
          right: 4,
          top: 4,
          bottom: 4,
          label: {
            show: true,
            color: texte.color,
            fontFamily: jeton('--police') || undefined,
            fontSize: 11,
            fontWeight: 600,
            textBorderColor: texte.borderColor,
            textBorderWidth: 3,
          },
          labelLayout: { hideOverlap: true },
          itemStyle: { borderColor: jeton('--surface'), borderWidth: 1 },
          data: fond.contours.map((c) => {
            const ligne = lignes.find((l) => cleNom(l.nom) === cleNom(c.nom));
            const couleur = ligne ? couleurClasse(ligne) : jeton('--trait');
            return {
              name: c.nom,
              itemStyle: { areaColor: couleur },
              emphasis: {
                itemStyle: { areaColor: couleur, borderColor: jeton('--or'), borderWidth: 2 },
                label: { show: true },
              },
            };
          }),
        },
      ],
    };
  }, [fond, lignes]);

  const sansContour = fond ? lignes.filter((l) => !l.horsReferentiel && !contourDe(fond, l.nom)) : [];

  return (
    <div className="carte-territoire">
      <div className="carte-territoire__liste">
        <p className="carte-territoire__titre-liste texte-2">{titreListe}</p>
        <p className="carte-territoire__lecture" aria-live="polite">
          {lecture}
        </p>
        <div
          role="group"
          aria-label="Choisir une zone"
          className="carte-territoire__zones"
          onMouseLeave={() => setSurvol(null)}
        >
          <div className="zone-choix zone-choix--active" aria-current="true">
            <span className="zone-choix__nom">{zone.nom}</span>
            <span className="chiffre">{pct(tauxNiu(zone.chiffres))}</span>
          </div>
          {lignes.map((l) => {
            const ouvrable = !!onOuvrir && !l.horsReferentiel;
            return (
              <button
                key={l.code}
                type="button"
                className={`zone-choix zone-choix--bouton${survol === l.nom ? ' zone-choix--survol' : ''}`}
                aria-label={
                  ouvrable ? `${lectureZone(l.nom, l)}. Voir ses préfectures` : lectureZone(l.nom, l)
                }
                onClick={() => (ouvrable ? onOuvrir(l) : setSurvol(l.nom))}
                onMouseEnter={() => setSurvol(l.nom)}
                onFocus={() => setSurvol(l.nom)}
                onBlur={() => setSurvol(null)}
              >
                <i className={classeCss(classeTauxNiu(tauxNiu(l)))} aria-hidden="true" />
                <span className="zone-choix__nom">{l.nom}</span>
                <span className="chiffre">{pct(tauxNiu(l))}</span>
              </button>
            );
          })}
        </div>
      </div>

      <figure className="carte-territoire__carte">
        {fond && option ? (
          <Graphique
            option={option}
            carte={fond}
            hauteur={fond.contours.length > 6 ? 380 : 440}
            libelle={libelleCarte}
            onSurvol={(c) => setSurvol(c?.nom ?? null)}
            onClic={(c) => {
              const ligne = c.nom ? ligneDe(c.nom) : undefined;
              if (ligne && onOuvrir && !ligne.horsReferentiel) onOuvrir(ligne);
              else setSurvol(c.nom ?? null);
            }}
          />
        ) : (
          <p className="texte-2">Pas de contour disponible pour cette zone.</p>
        )}
        <figcaption>
          <p className="carte-territoire__legende-titre texte-2">Taux de NIU générés</p>
          <ul className="carte-territoire__legende">
            {CLASSES_TAUX_NIU.map((c, i) => (
              <li key={c.jeton}>
                <i className={classeCss(i)} aria-hidden="true" />
                {c.libelle}
              </li>
            ))}
          </ul>
          {sansContour.length > 0 && (
            <p className="texte-2 carte-territoire__note">
              Sans contour sur la carte : {sansContour.map((l) => l.nom).join(', ')}.
            </p>
          )}
          <p className="texte-2 carte-territoire__source">
            Contours : © contributeurs OpenStreetMap, geoBoundaries.
          </p>
        </figcaption>
      </figure>
    </div>
  );
}
