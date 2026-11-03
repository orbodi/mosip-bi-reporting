import { describe, expect, it } from 'vitest';
import {
  alerteARemettre,
  barresAttente,
  chiffresImpression,
  classeARemettre,
  classeAvecCarte,
  lectureARemettre,
  moinsDeLaMoitie,
  noteAttente,
  noteRejeteesAnnulees,
  semainesCartes,
  texteAnnulees,
  texteModesRemise,
  texteNiuSansCommande,
} from './cartes';

const IMPRESSION = {
  perimetre: 'Ensemble du Togo',
  disponible: true,
  demandes: 6195305,
  envoyees: 6192991,
  enAttente: 2306,
  rejetees: 8,
  nonClassees: 0,
  annulees: 693,
  derniereRejetee: '2026-11-02',
  expediees: 6107359,
  remises: 4643568,
  remisesHorsLigne: 4446166,
  remisesEnLigne: 197370,
  remisesSupport: 32,
  remisesAutre: 0,
  aRemettre: 1463791,
  delaiMedianJours: 31,
  erreursIdps: 172354,
  derniereErreurIdps: '2026-01-09',
  niuSansCommande: 58,
  niuSansCommandePlus7j: 3,
};

describe('Impression des cartes', () => {
  it('reprend les chiffres de l’API, inconnus tant que la source n’est pas disponible', () => {
    const c = chiffresImpression(IMPRESSION);
    expect(c.remises + c.aRemettre).toBe(c.expediees);
    expect(c.derniereRejetee).toBe('2026-11-02');

    const vide = chiffresImpression({ perimetre: 'Ensemble du Togo', disponible: false });
    expect(Number.isNaN(vide.demandes)).toBe(true);
    expect(Number.isNaN(chiffresImpression(undefined).remises)).toBe(true);
  });

  it('détaille les modes de remise, sans « sans mode connu » quand il n’y en a pas', () => {
    const texte = texteModesRemise(chiffresImpression(IMPRESSION));
    expect(texte).toMatch(/^Remises : 4\s446\s166 hors ligne · 197\s370 en ligne · 32 par le support$/);
    expect(texteModesRemise(chiffresImpression({ ...IMPRESSION, remisesAutre: 5 }))).toMatch(/5 sans mode connu$/);
  });

  it('annulées : parmi les demandes, motifs en clair et motif inconnu nommé', () => {
    expect(
      texteAnnulees([
        { code: 'CANCEL_PHOTO', libelle: 'Photo à reprendre', demandes: 643 },
        { code: 'CANCEL_SEX', libelle: 'Sexe à corriger', demandes: 36 },
        { code: 'CANCEL_NAME', libelle: 'Nom à corriger', demandes: 10 },
        { code: 'PERSONALIZATION_MANAGER_REPORTED_ERROR', libelle: 'Erreur signalée', demandes: 4 },
      ]),
    ).toBe('Parmi les demandes : photo 643, sexe 36, nom 10, personnalisation 4');
    expect(texteAnnulees([{ code: 'NON_REPERTORIE', libelle: 'Motif non répertorié', demandes: 2 }])).toBe(
      'Parmi les demandes : motif non répertorié 2',
    );
    expect(texteAnnulees()).toBe('Parmi les demandes');
  });

  it('semaines : séries de l’API, ou 12 semaines inconnues sans réponse', () => {
    const api = {
      perimetre: 'Ensemble du Togo',
      semaines: [{ lundi: '2026-01-05', dansPeriode: true, demandes: 230, expediees: 200, rejetees: 1, annulees: 2 }],
    };
    expect(semainesCartes(api, '2026-01-14')).toEqual([
      { lundi: '2026-01-05', valeurs: { imprimees: 200, demandes: 230, rejetees: 1, annulees: 2 } },
    ]);
    const vides = semainesCartes(undefined, '2026-01-14');
    expect(vides).toHaveLength(12);
    expect(Number.isNaN(vides[0].valeurs.annulees)).toBe(true);
    expect(noteRejeteesAnnulees(semainesCartes(api, '2026-01-14'))).toBe(
      'Sur ces 12 semaines : 1 demande rejetée, 2 annulées.',
    );
    expect(noteRejeteesAnnulees(vides)).toBe('Sur ces 12 semaines : 0 demande rejetée, 0 annulée.');
  });

  it('carte des cartes à remettre : classes de la maquette, alerte au-delà de la moitié', () => {
    expect(classeARemettre(0.24)).toBe(0);
    expect(classeARemettre(0.35)).toBe(1);
    expect(classeARemettre(0.5)).toBe(2);
    expect(classeARemettre(0.554)).toBe(3);
    expect(classeARemettre(Number.NaN)).toBe(-1);
    expect(alerteARemettre({ expediees: 1000, aRemettre: 554 })).toBe(true);
    expect(alerteARemettre({ expediees: 1000, aRemettre: 500 })).toBe(false);
    expect(lectureARemettre('Kara', { expediees: 0, aRemettre: 0 })).toBe(
      'Kara : aucune carte expédiée sur la période',
    );
  });

  it('attente : quatre tranches dans l’ordre, part des plus de six mois', () => {
    const api = {
      perimetre: 'Ensemble du Togo',
      calculeLe: '2026-11-03',
      aRemettre: 1463791,
      tranches: [
        { code: 'moins_30j', depuisJours: 0, avantJours: 30, cartes: 121430 },
        { code: '30_90j', depuisJours: 30, avantJours: 90, cartes: 61748 },
        { code: '90_180j', depuisJours: 90, avantJours: 180, cartes: 61014 },
        { code: 'plus_180j', depuisJours: 180, avantJours: null, cartes: 1219599 },
      ],
    };
    expect(barresAttente(api).map((b) => b.libelle)).toEqual([
      'Moins de 30 jours',
      '30 à 90 jours',
      '90 à 180 jours',
      'Plus de 180 jours',
    ]);
    expect(noteAttente(api)).toMatch(/^1\s219\s599 cartes, soit 83,3\s% des cartes à remettre/);
    expect(barresAttente(undefined).every((b) => Number.isNaN(b.valeur))).toBe(true);
  });

  it('Vue d’ensemble : note des seuls NIU bloqués, rien pour des NIU en route ou sur une période', () => {
    expect(texteNiuSansCommande(chiffresImpression(IMPRESSION))).toBe(
      '3 NIU de première inscription sans demande d’impression depuis plus de 7 jours.',
    );
    // Cas habituel : des NIU de moins de 7 jours, dont la commande va suivre ; pas de note.
    expect(
      texteNiuSansCommande(chiffresImpression({ ...IMPRESSION, niuSansCommande: 73, niuSansCommandePlus7j: 0 })),
    ).toBeUndefined();
    expect(
      texteNiuSansCommande(chiffresImpression({ ...IMPRESSION, niuSansCommande: null, niuSansCommandePlus7j: null })),
    ).toBeUndefined();
  });

  it('Vue d’ensemble : part des inscrits avec carte, en quatre classes', () => {
    expect(classeAvecCarte(0.44)).toBe(0);
    expect(classeAvecCarte(0.5)).toBe(2);
    expect(classeAvecCarte(0.74)).toBe(3);
    expect(classeAvecCarte(Number.NaN)).toBe(-1);
    expect(moinsDeLaMoitie(0.49)).toBe(true);
    expect(moinsDeLaMoitie(Number.NaN)).toBe(false);
  });
});
