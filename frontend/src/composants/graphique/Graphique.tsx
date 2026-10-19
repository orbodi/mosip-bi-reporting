import { useCallback, useEffect, useRef } from 'react';
import type { ECharts, EChartsCoreOption } from './echarts';
import './graphique.css';

/** Élément visé par la souris : nom (zone d'une carte) ou rang de la donnée (barre d'une série). */
export interface CibleGraphique {
  nom?: string;
  indice?: number;
}

interface Props {
  option: EChartsCoreOption;
  hauteur: number;
  /** Description du graphique pour les lecteurs d'écran (role="img"). */
  libelle: string;
  /** Fond de carte SVG à déclarer avant l'option (série « map »). */
  carte?: { nom: string; svg: string };
  onSurvol?: (cible: CibleGraphique | null) => void;
  onClic?: (cible: CibleGraphique) => void;
}

interface EvenementECharts {
  name?: string;
  dataIndex?: number;
}

type Moteur = (typeof import('./echarts'))['echarts'];

const cible = (e: EvenementECharts): CibleGraphique => ({ nom: e.name, indice: e.dataIndex });

/**
 * Graphique Apache ECharts, chargé à la demande (paquet séparé, la coque s'affiche sans l'attendre). Il ne porte que
 * l'image : chaque bloc fournit aussi un titre, une légende lisible et un équivalent texte ou tableau (CLAUDE.md du
 * front). Les couleurs viennent des jetons (lib/jetons.ts).
 */
export function Graphique({ option, hauteur, libelle, carte, onSurvol, onClic }: Props) {
  const conteneur = useRef<HTMLDivElement>(null);
  const moteur = useRef<Moteur | null>(null);
  const instance = useRef<ECharts | null>(null);
  const derniers = useRef({ option, carte, onSurvol, onClic });

  const appliquer = useCallback(() => {
    const e = moteur.current;
    const g = instance.current;
    if (!e || !g) return;
    const { option: o, carte: c } = derniers.current;
    if (c && !e.getMap(c.nom)) e.registerMap(c.nom, { svg: c.svg });
    g.setOption(o, { notMerge: true });
  }, []);

  useEffect(() => {
    derniers.current = { option, carte, onSurvol, onClic };
  });

  useEffect(() => {
    let annule = false;
    let liberer = () => {};
    void import('./echarts').then(({ echarts }) => {
      const element = conteneur.current;
      if (annule || !element) return;
      const graphique = echarts.init(element, undefined, { renderer: 'svg' });
      moteur.current = echarts;
      instance.current = graphique;
      graphique.on('mouseover', (e) => derniers.current.onSurvol?.(cible(e as EvenementECharts)));
      graphique.on('globalout', () => derniers.current.onSurvol?.(null));
      graphique.on('click', (e) => derniers.current.onClic?.(cible(e as EvenementECharts)));
      const observateur =
        typeof ResizeObserver === 'undefined' ? undefined : new ResizeObserver(() => graphique.resize());
      observateur?.observe(element);
      appliquer();
      liberer = () => {
        observateur?.disconnect();
        graphique.dispose();
        instance.current = null;
      };
    });
    return () => {
      annule = true;
      liberer();
    };
  }, [appliquer]);

  // L'option et la carte suivent les props (lues dans derniers, mis à jour juste avant).
  useEffect(() => appliquer(), [appliquer, option, carte]);

  return (
    <div ref={conteneur} className="graphique" role="img" aria-label={libelle} style={{ height: hauteur }} />
  );
}
