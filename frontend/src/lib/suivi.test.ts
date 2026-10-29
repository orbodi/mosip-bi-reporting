import { describe, expect, it } from 'vitest';
import { ErreurApi, type SuiviDossier } from '../api/client';
import {
  MESSAGE_FORMAT,
  MESSAGE_INTROUVABLE,
  etatDossier,
  intituleEtape,
  jalonsDossier,
  messageErreur,
  nettoyerRid,
  ridValide,
  statutEtape,
  typeDemande,
} from './suivi';

const texte = (t: string) => t.replace(/\s+/g, ' ');

const EN_COURS: SuiviDossier = {
  typeDemande: 'NEW',
  devenir: 'en_cours',
  bloque: true,
  centre: { nom: 'EPP Doumassesse I G/B', prefecture: 'Golfe', region: 'Grand Lomé' },
  etape: { code: 'MANUAL_VERIFICATION', libelle: 'Vérification manuelle', statut: 'IN_PROGRESS' },
  motif: {
    code: 'FILE_VERIF_MANUELLE',
    libelle: 'En file d’attente de vérification manuelle',
    commentaire: null,
  },
  derniereActiviteLe: '2026-09-18T09:00:00Z',
  jalons: {
    enroleLe: '2026-09-02T10:14:00Z',
    synchroniseLe: '2026-09-02T17:40:00Z',
    refusPoste: false,
    recuLe: '2026-09-03T08:05:00Z',
    niuLe: null,
  },
  majLe: '2026-10-29T07:30:00Z',
};

describe('Suivi d’un dossier', () => {
  it('RID : chiffres seulement, 29 au plus, valide à 29', () => {
    expect(nettoyerRid('20101 10023-0041 2202610210930 15')).toBe('20101100230041220261021093015');
    expect(nettoyerRid('1'.repeat(35))).toHaveLength(29);
    expect(ridValide('2'.repeat(29))).toBe(true);
    expect(ridValide('2'.repeat(28))).toBe(false);
  });

  it('messages d’erreur sans le RID', () => {
    expect(messageErreur(new ErreurApi(404, 'x'))).toBe(MESSAGE_INTROUVABLE);
    expect(messageErreur(new ErreurApi(400, 'x'))).toBe(MESSAGE_FORMAT);
    expect(messageErreur(new ErreurApi(503, 'x'))).toMatch(/pas disponible/);
    expect(messageErreur(new TypeError('réseau'))).toMatch(/n’a pas abouti/);
  });

  it('état : bloqué avec le nombre de jours sans activité ; libellés des devenirs', () => {
    expect(etatDossier(EN_COURS, new Date('2026-10-29T10:00:00Z'))).toEqual({
      libelle: 'En cours · sans activité depuis 41 jours',
      ton: 'bloque',
    });
    expect(etatDossier({ ...EN_COURS, bloque: false })).toEqual({ libelle: 'En cours', ton: 'en-cours' });
    expect(etatDossier({ ...EN_COURS, devenir: 'niu', bloque: false }).libelle).toBe('NIU généré');
    expect(etatDossier({ ...EN_COURS, devenir: 'non_recu', bloque: false }).libelle).toBe(
      'Synchronisé, pas encore reçu',
    );
  });

  it('« Arrêté à l’étape » seulement pour un dossier rejeté ou échoué', () => {
    expect(intituleEtape('rejete')).toBe('Arrêté à l’étape');
    expect(intituleEtape('echoue')).toBe('Arrêté à l’étape');
    expect(intituleEtape('en_cours')).toBe('Étape en cours');
    expect(intituleEtape('non_classe')).toBe('Étape en cours');
    expect(intituleEtape('niu')).toBe('Dernière étape');
  });

  it('types de demande et statuts en français, codes inconnus gardés', () => {
    expect(typeDemande('NEW')).toBe('Nouvelle inscription');
    expect(typeDemande('ACTIVATED')).toBe('Demande ACTIVATED');
    expect(statutEtape('FAILED')).toBe('Échouée');
    expect(statutEtape('NOUVEAU')).toBe('NOUVEAU');
    expect(statutEtape(null)).toBeNull();
  });

  it('jalons d’un dossier arrêté : étape actuelle, NIU à venir', () => {
    const j = jalonsDossier(EN_COURS);
    expect(j.map((x) => [x.libelle, x.etat])).toEqual([
      ['Enrôlé au poste', 'fait'],
      ['Synchronisé avec MOSIP', 'fait'],
      ['Reçu par MOSIP', 'fait'],
      ['Vérification manuelle', 'actuel'],
      ['NIU généré', 'a-venir'],
    ]);
    expect(texte(j[0].quand)).toBe('02/09/2026 à 10h14');
    expect(texte(j[3].quand)).toBe('dernière activité le 18/09/2026 à 09h00');
  });

  it('jalons d’un NIU, d’un refus au poste et d’un paquet pas encore reçu', () => {
    const niu = jalonsDossier({
      ...EN_COURS,
      devenir: 'niu',
      jalons: { ...EN_COURS.jalons, niuLe: '2026-09-03T11:52:00Z' },
    });
    expect(niu.at(-1)).toMatchObject({ libelle: 'NIU généré', etat: 'fait' });
    expect(niu).toHaveLength(4);

    const rejete = jalonsDossier({ ...EN_COURS, devenir: 'rejete', bloque: false });
    expect(rejete.at(-1)).toMatchObject({ libelle: 'Vérification manuelle', etat: 'arret' });
    expect(texte(rejete.at(-1)!.quand)).toBe('arrêté le 18/09/2026 à 09h00');
    expect(rejete.map((x) => x.libelle)).not.toContain('NIU généré');

    const refus = jalonsDossier({ ...EN_COURS, jalons: { ...EN_COURS.jalons, refusPoste: true } });
    expect(refus[2]).toMatchObject({ libelle: 'Refusé au poste', etat: 'refus' });

    const nonRecu = jalonsDossier({
      ...EN_COURS,
      devenir: 'non_recu',
      jalons: { ...EN_COURS.jalons, recuLe: null },
    });
    expect(nonRecu.map((x) => [x.libelle, x.etat]).slice(2)).toEqual([
      ['Reçu par MOSIP', 'actuel'],
      ['NIU généré', 'a-venir'],
    ]);
  });
});
