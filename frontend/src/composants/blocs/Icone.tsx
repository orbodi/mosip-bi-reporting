import type { ReactElement } from 'react';

/**
 * Pictogrammes au trait de la maquette (bleu ANID, touches de jaune), décoratifs (aria-hidden).
 * Couleurs : jetons --bleu, --or et --surface.
 */
const B = 'var(--bleu)';
const Y = 'var(--or)';
const F = 'var(--surface)';
const p = { stroke: B, strokeWidth: 2.2, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const };

const ICONES: Record<string, ReactElement> = {
  calendrierOk: (
    <g fill="none">
      <rect x="7" y="10" width="34" height="30" rx="4" fill={Y} fillOpacity=".35" {...p} />
      <path d="M7 18h34M16 6v8M32 6v8M17 29l5 5 9-10" {...p} />
    </g>
  ),
  calendrierX: (
    <g fill="none">
      <rect x="7" y="10" width="34" height="30" rx="4" fill={Y} fillOpacity=".35" {...p} />
      <path d="M7 18h34M16 6v8M32 6v8M19 25l10 10M29 25 19 35" {...p} />
    </g>
  ),
  sablier: (
    <g fill="none">
      <path d="M14 6h20M14 42h20M16 6c0 10 16 12 16 18S16 32 16 42M32 6c0 10-16 12-16 18s16 8 16 18" {...p} />
      <path d="M18 40c2-5 10-5 12 0z" fill={Y} stroke="none" />
    </g>
  ),
  personneOk: (
    <g fill="none">
      <circle cx="20" cy="15" r="7" fill={Y} fillOpacity=".5" {...p} />
      <path d="M6 38c1-8 7-12 14-12s10 2 12 5" {...p} />
      <circle cx="35" cy="34" r="7" fill={F} {...p} />
      <path d="m32 34 2 2 4-4" {...p} />
    </g>
  ),
  personnes: (
    <g fill="none">
      <circle cx="17" cy="16" r="6" fill={Y} fillOpacity=".5" {...p} />
      <circle cx="32" cy="17" r="5" {...p} />
      <path d="M5 37c1-7 6-10 12-10s11 3 12 10M28 27c5 0 13 2 14 9" {...p} />
    </g>
  ),
  femme: (
    <g fill="none">
      <circle cx="24" cy="12" r="6" fill={Y} fillOpacity=".5" {...p} />
      <path d="M24 21c-5 0-8 4-9 9l-3 8h24l-3-8c-1-5-4-9-9-9zM20 38v4M28 38v4" {...p} />
    </g>
  ),
  homme: (
    <g fill="none">
      <circle cx="24" cy="12" r="6" fill={Y} fillOpacity=".5" {...p} />
      <path d="M14 36v-7c0-5 4-8 10-8s10 3 10 8v7M19 29v13M29 29v13" {...p} />
    </g>
  ),
  horloge: (
    <g fill="none">
      <circle cx="24" cy="24" r="17" fill={Y} fillOpacity=".55" {...p} />
      <path d="M24 13v11l7 5" {...p} />
    </g>
  ),
  diese: (
    <g fill="none">
      <rect x="6" y="9" width="36" height="30" rx="5" fill={Y} fillOpacity=".45" {...p} />
      <path d="M20 15l-3 18M31 15l-3 18M14 21h22M13 28h22" {...p} />
    </g>
  ),
  cycle: (
    <g fill="none">
      <circle cx="24" cy="24" r="8" fill={Y} fillOpacity=".6" {...p} />
      <path d="M38 20a15 15 0 0 0-27-6M10 28a15 15 0 0 0 27 6M11 6v8h8M37 42v-8h-8" {...p} />
    </g>
  ),
  alerte: (
    <g fill="none">
      <path d="M24 6 4 41h40z" fill={Y} fillOpacity=".55" {...p} />
      <path d="M24 19v10M24 35v.5" {...p} />
    </g>
  ),
  croix: (
    <g fill="none">
      <circle cx="24" cy="24" r="17" fill={Y} fillOpacity=".55" {...p} />
      <path d="m18 18 12 12M30 18 18 30" {...p} />
    </g>
  ),
  document: (
    <g fill="none">
      <path d="M11 5h18l9 9v29H11z" fill={Y} fillOpacity=".35" {...p} />
      <path d="M29 5v9h9M17 22h14M17 29h14M17 36h9" {...p} />
    </g>
  ),
  imprimante: (
    <g fill="none">
      <rect x="6" y="18" width="36" height="16" rx="3" {...p} />
      <path d="M14 18V7h20v11" {...p} />
      <rect x="14" y="28" width="20" height="13" fill={Y} fillOpacity=".55" {...p} />
      <path d="M18 33h12M18 37h8" {...p} />
    </g>
  ),
  carteId: (
    <g fill="none">
      <rect x="5" y="10" width="38" height="28" rx="4" fill={Y} fillOpacity=".35" {...p} />
      <rect x="10" y="17" width="10" height="12" rx="1.5" {...p} />
      <path d="M25 19h12M25 25h12M25 31h8" {...p} />
    </g>
  ),
  carteHorloge: (
    <g fill="none">
      <rect x="4" y="9" width="32" height="24" rx="4" fill={Y} fillOpacity=".35" {...p} />
      <path d="M9 16h8v8H9zM21 17h10M21 22h10" {...p} />
      <circle cx="35" cy="34" r="8" fill={F} {...p} />
      <path d="M35 30v4l3 2" {...p} />
    </g>
  ),
  chrono: (
    <g fill="none">
      <circle cx="24" cy="27" r="15" fill={Y} fillOpacity=".55" {...p} />
      <path d="M24 27v-7M20 6h8M24 6v6M36 13l3-3" {...p} />
    </g>
  ),
  basePlus: (
    <g fill="none">
      <ellipse cx="20" cy="11" rx="13" ry="5" fill={Y} fillOpacity=".55" {...p} />
      <path d="M7 11v24c0 3 6 5 13 5M33 11v12M7 19c0 3 6 5 13 5s13-2 13-5M7 27c0 3 6 5 13 5" {...p} />
      <circle cx="35" cy="35" r="7" fill={F} {...p} />
      <path d="M35 31v8M31 35h8" {...p} />
    </g>
  ),
  loupe: (
    <g fill="none">
      <circle cx="20" cy="20" r="13" fill={Y} fillOpacity=".5" {...p} />
      <path d="M14 20h12M30 30l11 11" {...p} />
    </g>
  ),
  dossierOk: (
    <g fill="none">
      <path d="M5 12h14l4 5h20v22H5z" fill={Y} fillOpacity=".4" {...p} />
      <path d="m17 28 5 5 9-9" {...p} />
    </g>
  ),
  doublon: (
    <g fill="none">
      <circle cx="12" cy="16" r="5" fill={Y} fillOpacity=".5" {...p} />
      <circle cx="36" cy="16" r="5" fill={Y} fillOpacity=".5" {...p} />
      <path d="M3 34c1-6 4-9 9-9s8 3 9 9M27 34c1-6 4-9 9-9s8 3 9 9M21 16h6M21 21h6" {...p} />
    </g>
  ),
  balance: (
    <g fill="none">
      <path d="M24 7v32M14 40h20M10 13h28M10 13l-6 14h12zM38 13l-6 14h12z" {...p} />
      <path d="M4 27a6 4 0 0 0 12 0zM32 27a6 4 0 0 0 12 0z" fill={Y} fillOpacity=".6" stroke="none" />
    </g>
  ),
  visage: (
    <g fill="none">
      <path d="M6 14V8h6M36 8h6v6M42 34v6h-6M12 40H6v-6" {...p} />
      <circle cx="24" cy="19" r="6" fill={Y} fillOpacity=".55" {...p} />
      <path d="M13 36c2-6 6-9 11-9s9 3 11 9" {...p} />
    </g>
  ),
  oeil: (
    <g fill="none">
      <path d="M3 24s8-12 21-12 21 12 21 12-8 12-21 12S3 24 3 24z" {...p} />
      <circle cx="24" cy="24" r="7" fill={Y} fillOpacity=".7" {...p} />
      <circle cx="24" cy="24" r="2" fill={B} />
    </g>
  ),
  empreinte: (
    <g fill="none">
      <circle cx="24" cy="24" r="19" fill={Y} fillOpacity=".45" stroke="none" />
      <path
        d="M16 36c-2-4-3-8-3-12a11 11 0 0 1 22 0M20 38c-2-4-3-9-3-14a7 7 0 0 1 14 0c0 4 0 9-2 13M24 24c0 6-1 11-3 15M28 31c0 3-1 6-2 8M13 16a14 14 0 0 1 22 0"
        {...p}
      />
    </g>
  ),
  immeuble: (
    <g fill="none">
      <rect x="9" y="12" width="16" height="30" fill={Y} fillOpacity=".4" {...p} />
      <path
        d="M25 20h14v22H25M5 42h38M14 18h2M19 18h2M14 24h2M19 24h2M14 30h2M19 30h2M30 26h4M30 32h4M14 6l6-2 5 3v5"
        {...p}
      />
    </g>
  ),
  telephone: (
    <g fill="none">
      <rect x="13" y="4" width="22" height="40" rx="4" fill={Y} fillOpacity=".35" {...p} />
      <rect x="17" y="18" width="14" height="8" rx="2" fill={F} {...p} />
      <path d="M20 22h.5M24 22h.5M28 22h.5M21 38h6" {...p} />
    </g>
  ),
  bouclier: (
    <g fill="none">
      <path d="M24 4 8 10v12c0 10 7 18 16 22 9-4 16-12 16-22V10z" fill={Y} fillOpacity=".55" {...p} />
      <path d="m17 24 5 5 9-10" {...p} />
    </g>
  ),
  inscription: (
    <g fill="none">
      <rect x="5" y="5" width="26" height="32" rx="3" fill={Y} fillOpacity=".35" {...p} />
      <circle cx="18" cy="16" r="5" {...p} />
      <path d="M10 31c1-5 4-8 8-8s7 3 8 8" {...p} />
      <circle cx="36" cy="36" r="8" fill={F} {...p} />
      <path d="M36 32v8M32 36h8" {...p} />
    </g>
  ),
  baseHorloge: (
    <g fill="none">
      <ellipse cx="20" cy="11" rx="13" ry="5" fill={Y} fillOpacity=".55" {...p} />
      <path d="M7 11v24c0 3 6 5 13 5M33 11v12M7 19c0 3 6 5 13 5s13-2 13-5M7 27c0 3 6 5 13 5" {...p} />
      <circle cx="35" cy="35" r="8" fill={F} {...p} />
      <path d="M35 31v4l3 2" {...p} />
    </g>
  ),
};

/** Variante blanche des pictogrammes de la frise du parcours (sur pastille bleue). */
const W = {
  fill: 'none',
  stroke: F,
  strokeWidth: 2.6,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
};
const BLANCHES: Record<string, ReactElement> = {
  calendrierOk: (
    <g>
      <rect x="7" y="10" width="34" height="30" rx="4" {...W} />
      <path d="M7 18h34M16 6v8M32 6v8M17 29l5 5 9-10" {...W} />
    </g>
  ),
  personne: (
    <g>
      <circle cx="24" cy="16" r="7" {...W} />
      <path d="M10 40c1-9 7-13 14-13s13 4 14 13" {...W} />
    </g>
  ),
  engrenage: (
    <g>
      <circle cx="24" cy="24" r="5" {...W} />
      <circle cx="24" cy="24" r="12" {...W} />
      <path
        d="M24 5v7M24 36v7M5 24h7M36 24h7M10.6 10.6l5 5M32.4 32.4l5 5M10.6 37.4l5-5M32.4 15.6l5-5"
        {...W}
      />
    </g>
  ),
  diese: (
    <g>
      <rect x="6" y="9" width="36" height="30" rx="5" {...W} />
      <path d="M20 15l-3 18M31 15l-3 18M14 21h22M13 28h22" {...W} />
    </g>
  ),
  document: (
    <g>
      <path d="M11 5h18l9 9v29H11z" {...W} />
      <path d="M29 5v9h9M17 23h14M17 30h14M17 37h9" {...W} />
    </g>
  ),
  imprimante: (
    <g>
      <rect x="6" y="18" width="36" height="16" rx="3" {...W} />
      <path d="M14 18V7h20v11M14 28h20v13H14z" {...W} />
    </g>
  ),
  remise: (
    <g>
      <rect x="6" y="11" width="36" height="24" rx="4" stroke="var(--encre)" strokeWidth={2.6} fill="none" />
      <path
        d="M11 18h9v9h-9zM25 19h11M25 24h11M25 29h7"
        stroke="var(--encre)"
        strokeWidth={2.6}
        fill="none"
        strokeLinecap="round"
      />
    </g>
  ),
};

export type NomIcone = keyof typeof ICONES;

export function Icone({
  nom,
  taille = 40,
  blanche = false,
}: {
  nom: string;
  taille?: number;
  blanche?: boolean;
}) {
  return (
    <svg
      width={taille}
      height={taille}
      viewBox="0 0 48 48"
      aria-hidden="true"
      focusable="false"
      className="icone"
    >
      {(blanche ? BLANCHES[nom] : undefined) ?? ICONES[nom] ?? null}
    </svg>
  );
}

/**
 * Icônes de statut d'un paquet (rejeté, échoué, en cours), au trait, dessinées sur un même cercle : d'après Lucide
 * (circle-x, circle-alert, clock ; licence ISC, https://lucide.dev). Couleur du texte parent (currentColor), décoratives.
 */
const STATUTS: Record<'rejete' | 'echoue' | 'en-cours', ReactElement> = {
  rejete: <path d="m15 9-6 6M9 9l6 6" />,
  echoue: <path d="M12 8v4M12 16h.01" />,
  'en-cours': <path d="M12 6v6l4 2" />,
};

export function IconeStatut({
  statut,
  taille = 20,
}: {
  statut: 'rejete' | 'echoue' | 'en-cours';
  taille?: number;
}) {
  return (
    <svg
      width={taille}
      height={taille}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      className="icone-statut"
    >
      <circle cx="12" cy="12" r="10" />
      {STATUTS[statut]}
    </svg>
  );
}

/** Triangle d'alerte (▲), avec un libellé pour les lecteurs d'écran. */
export function Drapeau({ libelle }: { libelle?: string }) {
  return (
    <svg
      width="11"
      height="11"
      viewBox="0 0 24 24"
      className="drapeau"
      {...(libelle ? { role: 'img', 'aria-label': libelle } : { 'aria-hidden': true })}
    >
      <path d="M12 2 1 21h22L12 2z" />
    </svg>
  );
}

export function Chevron({
  bas = false,
  gauche = false,
  taille = 14,
}: {
  bas?: boolean;
  /** Pointe vers la gauche (page précédente). */
  gauche?: boolean;
  taille?: number;
}) {
  const points = bas ? '6 9 12 15 18 9' : gauche ? '15 6 9 12 15 18' : '9 6 15 12 9 18';
  return (
    <svg width={taille} height={taille} viewBox="0 0 24 24" aria-hidden="true" className="chevron">
      <polyline points={points} />
    </svg>
  );
}
