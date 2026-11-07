import { describe, expect, it } from 'vitest';
import {
  basculerIndicateur,
  changerSource,
  ecrireRecherche,
  lireEtat,
  reinitialiser,
  trierLignes,
  trierPar,
  validerExploration,
} from './etatExploration';

describe('État de l’Exploration dans l’adresse', () => {
  it('sans paramètre : Enrôlement, inscriptions, toute la période, rien dans l’adresse', () => {
    const etat = lireEtat({});
    expect(etat).toMatchObject({ source: 'enrol', indicateurs: ['ins'], periode: 'tout', chemin: [], mode: 'n' });
    expect(Object.values(ecrireRecherche(etat)).filter((v) => v !== undefined)).toEqual([]);
  });

  it('aller-retour d’une vue complète', () => {
    const recherche = {
      source: 'cartes',
      indicateurs: 'dem,rem',
      quand: 'R:moisprec',
      zones: 'SAV.SAV-02',
      par: 'mois',
      valeurs: 'pt',
      tri: 'rem:desc',
    };
    const etat = lireEtat(recherche);
    expect(etat).toMatchObject({
      source: 'cartes',
      indicateurs: ['dem', 'rem'],
      periode: 'R:moisprec',
      chemin: ['SAV', 'SAV-02'],
      par: 'mois',
      mode: 'pt',
      tri: { colonne: 'rem', sens: 'desc' },
    });
    expect(ecrireRecherche(etat)).toMatchObject(recherche);
  });

  it('valeurs inconnues écartées : source, indicateurs, filtres sans données, tri sur une colonne absente', () => {
    expect(lireEtat({ source: 'xyz' }).source).toBe('enrol');
    expect(lireEtat({ indicateurs: 'zzz' }).indicateurs).toEqual(['ins']);
    // Sexe et âge de l'Enrôlement (lot E2) : codes de l'API ; un ancien lien « sexe=Femmes » ne garde rien.
    expect(lireEtat({ sexe: 'Femmes' }).filtres).toEqual({});
    expect(lireEtat({ sexe: 'F', age: '60+', nat: 'Togo' }).filtres).toEqual({ sexe: 'F', age: '60+', nat: 'Togo' });
    expect(lireEtat({ age: '18-25' }).filtres).toEqual({});
    expect(lireEtat({ source: 'auth', taut: 'otp', sexe: 'Femmes' }).filtres).toEqual({ taut: 'otp' });
    expect(lireEtat({ tri: 'zzz:desc' }).tri).toBeUndefined();
    // Authentifications : pas de territoire.
    expect(lireEtat({ source: 'auth', zones: 'SAV' }).chemin).toEqual([]);
  });

  it('validation des formes : période, zones, nombres lus par le routeur', () => {
    expect(validerExploration({ quand: 'R:30j', zones: 10011, par: 'mois' })).toEqual({
      quand: 'R:30j',
      zones: '10011',
      par: 'mois',
    });
    expect(validerExploration({ quand: 'hier', zones: 'SAV;drop', valeurs: 'x', tri: 'ins' })).toEqual({});
    expect(validerExploration({ quand: 'P:2026-10-02:' })).toEqual({ quand: 'P:2026-10-02:' });
  });

  it('changer de source garde la période et repart du premier indicateur', () => {
    const etat = lireEtat({ indicateurs: 'ins,niu', quand: 'A:2026', zones: 'SAV', tri: 'ins:desc' });
    expect(changerSource(etat, 'auth')).toMatchObject({
      source: 'auth',
      indicateurs: ['req'],
      periode: 'A:2026',
      chemin: [],
      tri: undefined,
    });
    expect(reinitialiser(etat)).toMatchObject({ source: 'enrol', indicateurs: ['ins'], periode: 'tout', chemin: [] });
  });

  it('indicateurs : ordre du catalogue, le dernier reste coché', () => {
    const etat = lireEtat({});
    expect(basculerIndicateur(etat, 'pre').indicateurs).toEqual(['ins', 'pre']);
    expect(basculerIndicateur(lireEtat({ indicateurs: 'pre' }), 'ins').indicateurs).toEqual(['ins', 'pre']);
    expect(basculerIndicateur(etat, 'ins').indicateurs).toEqual(['ins']);
  });

  it('tri : décroissant, croissant, puis ordre naturel ; valeurs inconnues en dernier', () => {
    let etat = lireEtat({});
    etat = trierPar(etat, 'ins');
    expect(etat.tri).toEqual({ colonne: 'ins', sens: 'desc' });
    etat = trierPar(etat, 'ins');
    expect(etat.tri).toEqual({ colonne: 'ins', sens: 'asc' });
    expect(trierPar(etat, 'ins').tri).toBeUndefined();
    expect(trierPar(lireEtat({}), 'libelle').tri).toEqual({ colonne: 'libelle', sens: 'asc' });

    const lignes = [
      { libelle: 'Kara', valeurs: [386000] },
      { libelle: 'Éthiopie', valeurs: [Number.NaN] },
      { libelle: 'Savanes', valeurs: [450239] },
      { libelle: 'Centrale', valeurs: [312000] },
    ];
    const noms = (tri: Parameters<typeof trierLignes>[1]) => trierLignes(lignes, tri, ['ins']).map((l) => l.libelle);
    expect(noms(undefined)).toEqual(['Kara', 'Éthiopie', 'Savanes', 'Centrale']);
    expect(noms({ colonne: 'ins', sens: 'desc' })).toEqual(['Savanes', 'Kara', 'Centrale', 'Éthiopie']);
    expect(noms({ colonne: 'ins', sens: 'asc' })).toEqual(['Centrale', 'Kara', 'Savanes', 'Éthiopie']);
    expect(noms({ colonne: 'libelle', sens: 'asc' })).toEqual(['Centrale', 'Éthiopie', 'Kara', 'Savanes']);
  });
});
