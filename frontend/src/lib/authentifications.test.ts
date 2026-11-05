import { describe, expect, it } from 'vitest';
import {
  alerteEchec,
  chiffresPaquets,
  chiffresUsagers,
  desRequetes,
  detailOtp,
  detailPartenaires,
  lignesAppelants,
  lignesCauses,
  lignesTypes,
  pastillePartenaires,
  semainesAuthentification,
} from './authentifications';

const USAGERS = {
  perimetre: 'Ensemble du Togo',
  disponible: true,
  requetes: 2186,
  reussies: 1538,
  echouees: 648,
  autresStatuts: 0,
  biometriques: 1,
  otp: 1955,
  demographiquesEtCombinees: 0,
  sansMode: 230,
  nonClassees: 0,
  partenairesRaccordes: 1,
  requetesPartenaires: 1645,
  partenaires: ['Atos'],
  demandesOtp: 2732,
  demandesOtpEnvoyees: 2380,
  codesOtp: 83873,
  codesOtpUtilises: 50781,
};

describe('Authentifications', () => {
  it('usagers : chiffres de l’API, inconnus tant que la source n’est pas disponible', () => {
    const c = chiffresUsagers(USAGERS);
    expect(c.reussies + c.echouees).toBe(c.requetes);
    expect(desRequetes(c.reussies, c)).toMatch(/^70,4\s% des requêtes$/);
    expect(Number.isNaN(chiffresUsagers({ ...USAGERS, disponible: false }).requetes)).toBe(true);
    expect(Number.isNaN(chiffresUsagers(undefined).otp)).toBe(true);
  });

  it('carte du code OTP : part des requêtes, codes envoyés et part utilisée', () => {
    expect(detailOtp(chiffresUsagers(USAGERS))).toMatch(
      /^89,4\s% des requêtes ; 2\s380 codes envoyés, 60,5\s% utilisés$/,
    );
  });

  it('carte des partenaires : le nom quand il n’y en a qu’un, sinon le nombre', () => {
    expect(detailPartenaires(chiffresUsagers(USAGERS))).toMatch(/^Atos, 75,3\s% des requêtes$/);
    expect(
      detailPartenaires(chiffresUsagers({ ...USAGERS, partenairesRaccordes: 3, partenaires: ['A', 'B', 'C'] })),
    ).toMatch(/^3 partenaires, 75,3\s% des requêtes$/);
    expect(detailPartenaires(chiffresUsagers({ ...USAGERS, partenairesRaccordes: 0, partenaires: [] }))).toBe(
      'Aucun partenaire sur la période',
    );
    expect(detailPartenaires(chiffresUsagers(undefined))).toMatch(/^0,0\s% des requêtes$/);
  });

  it('types : du plus fréquent au moins fréquent, non classé seulement s’il compte', () => {
    const api = {
      types: [
        { code: 'biometrique', requetes: 1, echecs: 1 },
        { code: 'otp', requetes: 1955, echecs: 417 },
        { code: 'demographique', requetes: 0, echecs: 0 },
        { code: 'combinee', requetes: 0, echecs: 0 },
        { code: 'sans_mode', requetes: 230, echecs: 230 },
        { code: 'non_classe', requetes: 0, echecs: 0 },
      ],
    };
    expect(lignesTypes(api).map((l) => l.libelle)).toEqual([
      'Code OTP',
      'Sans mode d’authentification',
      'Biométrique',
      'Démographique',
      'Combinée',
    ]);
    expect(lignesTypes(undefined)).toHaveLength(5);
    expect(lignesTypes(undefined)[0].libelle).toBe('Biométrique');
    expect(alerteEchec(230 / 230)).toBe(true);
    expect(alerteEchec(417 / 1955)).toBe(false);
    expect(alerteEchec(0.4996)).toBe(true);
    expect(alerteEchec(Number.NaN)).toBe(false);
  });

  it('causes : ordre de l’API, apostrophe typographique, causes à 0 sans réponse', () => {
    const lignes = lignesCauses('usagers', {
      perimetre: 'usagers',
      echecs: 647,
      motifs: [
        { code: 'OTP_REFUSE', libelle: 'Code OTP ou eKYC refusé', echecs: 417 },
        { code: 'SANS_MODE', libelle: "Aucun mode d'authentification demandé", echecs: 230 },
      ],
    });
    expect(lignes.map((l) => l.libelle)).toEqual(['Code OTP ou eKYC refusé', 'Aucun mode d’authentification demandé']);
    const vides = lignesCauses('paquets', undefined);
    expect(vides).toHaveLength(4);
    expect(vides.every((l) => Number.isNaN(l.echecs))).toBe(true);
  });

  it('partenaires et canaux : type affiché, pas de code MOSIP, pastille au singulier ou au pluriel', () => {
    const api = {
      partenairesRaccordes: 1,
      appelants: [
        { canal: 'partenaire', nom: 'Atos', requetes: 1645, reussies: 1142, demandesOtp: 2159, derniereRequete: '2026-11-03' },
        { canal: 'portail', nom: 'Portail du résident', requetes: 517, reussies: 377, demandesOtp: 560 },
        { canal: 'ussd', nom: 'USSD', requetes: 24, reussies: 19, demandesOtp: 13, derniereRequete: null },
      ],
    };
    const lignes = lignesAppelants(api);
    expect(lignes.map((l) => l.type)).toEqual(['Partenaire', 'Service de l’ANID', 'Service de l’ANID']);
    expect(lignes[2].derniereRequete).toBeUndefined();
    expect(pastillePartenaires(api)).toBe('1 partenaire raccordé');
    expect(pastillePartenaires({ ...api, partenairesRaccordes: 3 })).toBe('3 partenaires raccordés');
    expect(lignesAppelants(undefined)).toEqual([]);
  });

  it('semaines et paquets : séries de l’API, ou inconnues sans réponse', () => {
    const api = { semaines: [{ lundi: '2026-10-26', dansPeriode: true, reussies: 361, echouees: 151 }] };
    expect(semainesAuthentification(api, '2026-11-04')).toEqual([
      { lundi: '2026-10-26', valeurs: { reussies: 361, echouees: 151 } },
    ]);
    expect(semainesAuthentification(undefined, '2026-11-04')).toHaveLength(12);
    const p = chiffresPaquets({ disponible: true, verifications: 170151, reussies: 25253, echouees: 144898 });
    expect(p.reussies + p.echouees).toBe(p.verifications);
    expect(Number.isNaN(chiffresPaquets(undefined).verifications)).toBe(true);
  });
});
