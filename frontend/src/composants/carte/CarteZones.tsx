import { useEffect, useMemo, useRef, useState } from 'react';
import { cleNom } from '../../lib/territoire';
import { jeton } from '../../lib/jetons';
import { Graphique } from '../graphique/Graphique';
import type { EChartsCoreOption } from '../graphique/echarts';
import { cadrage, contourDe, type FondDeCarte } from './fondsDeCarte';
import './carte.css';

/** Jetons des quatre classes de couleur de la maquette, de la plus claire à la plus foncée. */
const JETONS_CLASSES = ['--seq-1', '--seq-2', '--seq-3', '--seq-4'] as const;

export interface ZoneCarte {
  code: string;
  nom: string;
  /** Valeur affichée dans la liste (« 92,6 % »). */
  valeur: string;
  /** Classe de couleur 0 à 3, ou -1 sans donnée (gris). */
  classe: number;
  /** Phrase lue au survol ou au focus (« Kara : 92,6 % de NIU générés… »). */
  lecture: string;
  /** Un clic choisit la zone (région depuis la vue nationale). */
  ouvrable: boolean;
}

interface Props {
  fond?: FondDeCarte;
  /** Zone affichée (Togo ou la région choisie). */
  zone: { nom: string; valeur: string; lecture: string };
  zones: ZoneCarte[];
  titreListe: string;
  libelleCarte: string;
  legende: { titre: string; libelles: readonly string[] };
  /** Libellé ajouté à une zone ouvrable pour les lecteurs d'écran. */
  libelleOuvrir?: string;
  /** Nom de la zone mise en avant (région du filtre). */
  selection?: string;
  onOuvrir?: (code: string) => void;
}

export const classeCss = (indice: number) => `classe-carte classe-carte--${indice < 0 ? 'aucune' : indice}`;

/**
 * Carte du Togo de la maquette : liste des zones (clavier, lecteurs d'écran), carte ECharts colorée en quatre classes,
 * légende et source des contours. Survol ou focus d'une zone : lecture au-dessus de la liste.
 */
export function CarteZones({
  fond,
  zone,
  zones,
  titreListe,
  libelleCarte,
  legende,
  libelleOuvrir = 'Voir ses préfectures',
  selection,
  onOuvrir,
}: Props) {
  const [survol, setSurvol] = useState<string | null>(null);
  const hauteur = fond && fond.contours.length > 6 ? 380 : 440;
  // Largeur du cadre de la carte, pour garder les proportions du Togo (fondsDeCarte.cadrage).
  const cadre = useRef<HTMLDivElement>(null);
  const [largeur, setLargeur] = useState(0);
  const avecCarte = !!fond;
  useEffect(() => {
    const element = cadre.current;
    if (!element || typeof ResizeObserver === 'undefined') return;
    const observateur = new ResizeObserver(([e]) => setLargeur(Math.round(e.contentRect.width)));
    observateur.observe(element);
    return () => observateur.disconnect();
  }, [avecCarte]);
  const zoneDe = (nom: string) => zones.find((z) => cleNom(z.nom) === cleNom(nom));
  const ciblee = survol ? zoneDe(survol) : undefined;

  const option = useMemo<EChartsCoreOption | undefined>(() => {
    if (!fond) return undefined;
    const couleur = (classe: number) => (classe < 0 ? jeton('--trait') : jeton(JETONS_CLASSES[classe]));
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
          ...cadrage(fond, largeur, hauteur),
          label: {
            show: true,
            color: jeton('--encre'),
            fontFamily: jeton('--police') || undefined,
            fontSize: 11,
            fontWeight: 600,
            textBorderColor: jeton('--surface'),
            textBorderWidth: 3,
          },
          labelLayout: { hideOverlap: true },
          itemStyle: { borderColor: jeton('--surface'), borderWidth: 1 },
          data: fond.contours.map((c) => {
            const z = zones.find((x) => cleNom(x.nom) === cleNom(c.nom));
            const fond = couleur(z ? z.classe : -1);
            const choisie = !!selection && cleNom(selection) === cleNom(c.nom);
            return {
              name: c.nom,
              itemStyle: {
                areaColor: fond,
                borderColor: choisie ? jeton('--encre') : jeton('--surface'),
                borderWidth: choisie ? 2 : 1,
              },
              emphasis: {
                itemStyle: { areaColor: fond, borderColor: jeton('--or'), borderWidth: 2 },
                label: { show: true },
              },
            };
          }),
        },
      ],
    };
  }, [fond, zones, selection, largeur, hauteur]);

  const sansContour = fond ? zones.filter((z) => !contourDe(fond, z.nom)) : [];

  return (
    <div className="carte-territoire">
      <div className="carte-territoire__liste">
        <p className="carte-territoire__titre-liste texte-2">{titreListe}</p>
        <p className="carte-territoire__lecture" aria-live="polite">
          {ciblee ? ciblee.lecture : zone.lecture}
        </p>
        <div
          role="group"
          aria-label="Choisir une zone"
          className="carte-territoire__zones"
          onMouseLeave={() => setSurvol(null)}
        >
          <div className="zone-choix zone-choix--active" aria-current="true">
            <span className="zone-choix__nom">{zone.nom}</span>
            <span className="chiffre">{zone.valeur}</span>
          </div>
          {zones.map((z) => {
            const ouvrable = !!onOuvrir && z.ouvrable;
            const choisie = !!selection && cleNom(selection) === cleNom(z.nom);
            return (
              <button
                key={z.code}
                type="button"
                className={`zone-choix zone-choix--bouton${survol === z.nom || choisie ? ' zone-choix--survol' : ''}`}
                aria-label={ouvrable ? `${z.lecture}. ${libelleOuvrir}` : z.lecture}
                aria-pressed={selection !== undefined ? choisie : undefined}
                onClick={() => (ouvrable ? onOuvrir(z.code) : setSurvol(z.nom))}
                onMouseEnter={() => setSurvol(z.nom)}
                onFocus={() => setSurvol(z.nom)}
                onBlur={() => setSurvol(null)}
              >
                <i className={classeCss(z.classe)} aria-hidden="true" />
                <span className="zone-choix__nom">{z.nom}</span>
                <span className="chiffre">{z.valeur}</span>
              </button>
            );
          })}
        </div>
      </div>

      <figure className="carte-territoire__carte">
        {fond && option ? (
          // Empreinte digitale de la maquette derrière la carte (signe de l'ANID, comme le bandeau).
          <div className="carte-territoire__empreinte" ref={cadre}>
            <Graphique
              option={option}
              carte={fond}
              hauteur={hauteur}
              libelle={libelleCarte}
              onSurvol={(c) => setSurvol(c?.nom ?? null)}
              onClic={(c) => {
                const z = c.nom ? zoneDe(c.nom) : undefined;
                if (z && onOuvrir && z.ouvrable) onOuvrir(z.code);
                else setSurvol(c.nom ?? null);
              }}
            />
          </div>
        ) : (
          <p className="texte-2">Pas de contour disponible pour cette zone.</p>
        )}
        <figcaption>
          <p className="carte-territoire__legende-titre texte-2">{legende.titre}</p>
          <ul className="carte-territoire__legende">
            {legende.libelles.map((libelle, i) => (
              <li key={libelle}>
                <i className={classeCss(i)} aria-hidden="true" />
                {libelle}
              </li>
            ))}
          </ul>
          {sansContour.length > 0 && (
            <p className="texte-2 carte-territoire__note">
              Sans contour sur la carte : {sansContour.map((z) => z.nom).join(', ')}.
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
