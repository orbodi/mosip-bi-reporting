import type {
  AuthentificationsParSemaine,
  CausesEchec,
  PartenairesEtCanaux,
  RequetesUsagers,
  TypesAuthentification,
  VerificationsPaquets,
} from '../api/client';
import { depuisApi, estConnu, semainesVides, type SemaineValeurs } from './blocsVides';
import { nf, part, pct } from './format';

/**
 * Règles d'affichage de la page Authentifications (docs/indicateurs.md, section Authentifications ; décisions des 03
 * et 04/11/2026). Deux périmètres jamais additionnés : les usagers (partenaires, portail du résident, USSD) et les
 * vérifications biométriques du traitement des paquets. Les parts sont calculées ici, depuis les nombres bruts de l'API.
 */

/** Chiffres du bloc des usagers ; valeur inconnue (NaN, affichée 0) sans réponse ou sans source. */
export interface ChiffresUsagers {
  requetes: number;
  reussies: number;
  echouees: number;
  biometriques: number;
  otp: number;
  demographiquesEtCombinees: number;
  partenairesRaccordes: number;
  requetesPartenaires: number;
  partenaires: string[];
  demandesOtp: number;
  demandesOtpEnvoyees: number;
  codesOtp: number;
  codesOtpUtilises: number;
}

export function chiffresUsagers(api?: RequetesUsagers): ChiffresUsagers {
  const a = api?.disponible ? api : undefined;
  return {
    requetes: depuisApi(a?.requetes),
    reussies: depuisApi(a?.reussies),
    echouees: depuisApi(a?.echouees),
    biometriques: depuisApi(a?.biometriques),
    otp: depuisApi(a?.otp),
    demographiquesEtCombinees: depuisApi(a?.demographiquesEtCombinees),
    partenairesRaccordes: depuisApi(a?.partenairesRaccordes),
    requetesPartenaires: depuisApi(a?.requetesPartenaires),
    partenaires: a?.partenaires ?? [],
    demandesOtp: depuisApi(a?.demandesOtp),
    demandesOtpEnvoyees: depuisApi(a?.demandesOtpEnvoyees),
    codesOtp: depuisApi(a?.codesOtp),
    codesOtpUtilises: depuisApi(a?.codesOtpUtilises),
  };
}

/** « 70,4 % des requêtes » : part d'un nombre dans les requêtes des usagers. */
export const desRequetes = (n: number, c: ChiffresUsagers) => `${pct(part(n, c.requetes))} des requêtes`;

/**
 * Détail de la carte « Code à usage unique » : « 89,4 % des requêtes ; 2 380 codes envoyés, 60,5 % utilisés ». Les
 * codes envoyés sont les demandes acceptées par IDA ; la part utilisée vient de ida.otp_transaction (tous appelants).
 */
export function detailOtp(c: ChiffresUsagers): string {
  return `${desRequetes(c.otp, c)} ; ${nf(c.demandesOtpEnvoyees)} codes envoyés, ${pct(part(c.codesOtpUtilises, c.codesOtp))} utilisés`;
}

/** Détail de la carte « Partenaires raccordés » : « Atos, 75,3 % des requêtes » ou « 3 partenaires, … ». */
export function detailPartenaires(c: ChiffresUsagers): string {
  const partRequetes = desRequetes(c.requetesPartenaires, c);
  if (!estConnu(c.partenairesRaccordes)) return partRequetes;
  if (c.partenairesRaccordes === 0) return 'Aucun partenaire sur la période';
  if (c.partenairesRaccordes === 1 && c.partenaires.length) return `${c.partenaires[0]}, ${partRequetes}`;
  return `${nf(c.partenairesRaccordes)} partenaires, ${partRequetes}`;
}

/** Libellés des types d'authentification (codes de l'API), dans l'ordre de la maquette. */
export const TYPES_AUTHENTIFICATION = [
  { code: 'biometrique', libelle: 'Biométrique' },
  { code: 'otp', libelle: 'Code à usage unique' },
  { code: 'demographique', libelle: 'Démographique' },
  { code: 'combinee', libelle: 'Combinée' },
  { code: 'sans_mode', libelle: 'Sans mode d’authentification' },
  { code: 'non_classe', libelle: 'Non classé' },
] as const;

/** Taux d'échec de 50 % ou plus (arrondi à une décimale) : drapeau ▲ du tableau. */
export const alerteEchec = (taux: number) => Number.isFinite(taux) && Math.round(taux * 1000) / 10 >= 50;

export interface LigneType {
  code: string;
  libelle: string;
  requetes: number;
  echecs: number;
}

/**
 * Lignes du tableau « Par type d'authentification », de la plus fréquente à la moins fréquente (à égalité, ordre de
 * la maquette). « Non classé » n'apparaît que s'il compte des requêtes. Sans réponse : les types de la maquette à 0.
 */
export function lignesTypes(api?: TypesAuthentification): LigneType[] {
  const lignes = TYPES_AUTHENTIFICATION.map((t) => {
    const l = api?.types.find((x) => x.code === t.code);
    return { code: t.code, libelle: t.libelle, requetes: depuisApi(l?.requetes), echecs: depuisApi(l?.echecs) };
  }).filter((l) => l.code !== 'non_classe' || (estConnu(l.requetes) && l.requetes > 0));
  if (!api) return lignes;
  return lignes
    .map((l, i) => ({ l, i }))
    .sort((a, b) => b.l.requetes - a.l.requetes || a.i - b.i)
    .map(({ l }) => l);
}

export interface LigneCause {
  code: string;
  libelle: string;
  echecs: number;
}

/** Causes affichées sans réponse de l'API, à 0 (les plus fréquentes du relevé du 03/11/2026). */
const CAUSES_SANS_REPONSE: Record<'usagers' | 'paquets', string[]> = {
  usagers: ['Code OTP ou eKYC refusé', 'Aucun mode d’authentification demandé', 'Biométrie non concordante'],
  paquets: [
    'Biométrie non concordante',
    'NIU absent de la base d’authentification',
    'Biométrie absente du dossier d’authentification',
    'Requête non traitée par IDA (erreur technique)',
  ],
};

/** Lignes du classement « Causes des échecs » d'un périmètre, du plus fréquent au moins fréquent (ordre de l'API). */
export function lignesCauses(perimetre: 'usagers' | 'paquets', api?: CausesEchec): LigneCause[] {
  if (!api) {
    return CAUSES_SANS_REPONSE[perimetre].map((libelle) => ({ code: libelle, libelle, echecs: Number.NaN }));
  }
  // Apostrophe typographique, comme les libellés de la page (le catalogue du pipeline écrit l'apostrophe droite).
  return api.motifs.map((m) => ({ code: m.code, libelle: m.libelle.replace(/'/g, '’'), echecs: m.echecs }));
}

export interface LigneAppelant {
  cle: string;
  nom: string;
  type: string;
  requetes: number;
  reussies: number;
  demandesOtp: number;
  derniereRequete?: string;
}

/** Type affiché d'un appelant : partenaire extérieur, ou service de l'ANID (portail du résident, portail mobile, USSD). */
export const typeAppelant = (canal: string) =>
  canal === 'partenaire' ? 'Partenaire' : canal === 'non_classe' ? 'Non classé' : 'Service de l’ANID';

/** Lignes du tableau « Partenaires et canaux », dans l'ordre de l'API (du plus actif au moins actif). */
export function lignesAppelants(api?: PartenairesEtCanaux): LigneAppelant[] {
  return (api?.appelants ?? []).map((a) => ({
    cle: `${a.canal}-${a.nom}`,
    nom: a.nom,
    type: typeAppelant(a.canal),
    requetes: a.requetes,
    reussies: a.reussies,
    demandesOtp: a.demandesOtp,
    derniereRequete: a.derniereRequete ?? undefined,
  }));
}

/** Pastille du bloc : « 1 partenaire raccordé », « 3 partenaires raccordés ». */
export function pastillePartenaires(api?: PartenairesEtCanaux): string {
  const n = depuisApi(api?.partenairesRaccordes);
  return `${nf(n)} ${estConnu(n) && n > 1 ? 'partenaires raccordés' : 'partenaire raccordé'}`;
}

/** Les 12 semaines du graphique des usagers : réussies et échouées, ou 12 semaines inconnues sans réponse. */
export function semainesAuthentification(api: AuthentificationsParSemaine | undefined, fin: string): SemaineValeurs[] {
  if (!api?.semaines.length) return semainesVides(fin, ['reussies', 'echouees']);
  return api.semaines.map((s) => ({ lundi: s.lundi, valeurs: { reussies: s.reussies, echouees: s.echouees } }));
}

/** Chiffres du bloc du traitement des paquets ; inconnus (NaN) sans réponse ou sans source. */
export function chiffresPaquets(api?: VerificationsPaquets) {
  const a = api?.disponible ? api : undefined;
  return {
    verifications: depuisApi(a?.verifications),
    reussies: depuisApi(a?.reussies),
    echouees: depuisApi(a?.echouees),
  };
}
