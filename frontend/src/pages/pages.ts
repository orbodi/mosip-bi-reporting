import type { CodeSource } from '../api/meta';

export interface DefinitionPage {
  chemin:
    '/' | '/enrolement' | '/impression-cartes' | '/abis' | '/idps' | '/authentifications' | '/exploration';
  /** Libellé de l'onglet dans l'en-tête. */
  onglet: string;
  /** Titre (h1) du bandeau. */
  titre: string;
  /** Source principale : date de la pastille « Dernière mise à jour » et bornes du filtre Période. */
  source: CodeSource;
  /** Nom des fichiers de la maquette (maquette/pages/<nom>.dc.html, maquette/captures/<nom>-1440.png). */
  maquette: string;
  /** Blocs à construire, dans l'ordre de la maquette. */
  blocs: string[];
  /** L'Exploration a ses propres filtres : pas de filtre Période dans le bandeau. */
  sansPeriode?: boolean;
}

export const PAGES: DefinitionPage[] = [
  {
    chemin: '/',
    onglet: 'Vue d’ensemble',
    titre: 'Vue d’ensemble du parcours citoyen',
    source: 'cartes',
    maquette: 'Main',
    blocs: [
      'De la pré-inscription à la carte en main (frise en 7 étapes, chiffre clé)',
      'Indicateurs clés par module (6 cartes)',
      'Le parcours par région (carte du Togo et tableau)',
    ],
  },
  {
    chemin: '/enrolement',
    onglet: 'Enrôlement',
    titre: 'Enrôlement',
    source: 'enrolement',
    maquette: 'Enrolement',
    blocs: [
      'Pré-inscription',
      'Devenir des inscriptions',
      'Inscriptions et NIU par semaine',
      'Territoire (carte et tableau des zones)',
      'Âge et sexe',
      'Top des centres',
    ],
  },
  {
    chemin: '/impression-cartes',
    onglet: 'Impression des cartes',
    titre: 'Impression des cartes',
    source: 'cartes',
    maquette: 'Cartes',
    blocs: [
      'Impression et remise',
      'Impressions par semaine',
      'Demandes rejetées par semaine',
      'Cartes à remettre par région',
      'Depuis quand ces cartes attendent',
      'Top des centres',
    ],
  },
  {
    chemin: '/abis',
    onglet: 'ABIS',
    titre: 'ABIS',
    source: 'abis',
    maquette: 'Biometrie',
    blocs: [
      'Transactions ABIS',
      'Adjudication',
      'Erreurs ABIS',
      'Qualité des données biométriques',
      'Fingerprint : niveau de qualité et taux d’exploitabilité par doigt',
    ],
  },
  {
    chemin: '/idps',
    onglet: 'IDPS',
    titre: 'IDPS',
    source: 'idps',
    maquette: 'Idps',
    blocs: [
      'Ordres d’impression',
      'Où les ordres échouent',
      'Erreurs par type',
      'Ordres et erreurs par région',
      'Ordres et erreurs par semaine',
    ],
  },
  {
    chemin: '/authentifications',
    onglet: 'Authentifications',
    titre: 'Authentifications',
    source: 'authentifications',
    maquette: 'Usage',
    blocs: [
      'Requêtes d’authentification',
      'Par type d’authentification',
      'Causes des échecs',
      'Requêtes par semaine',
    ],
  },
  {
    chemin: '/exploration',
    onglet: 'Exploration',
    titre: 'Exploration des données',
    source: 'enrolement',
    maquette: 'Technique',
    sansPeriode: true,
    blocs: [
      'Onglets par source',
      'Filtres de la source (période, profil, territoire en cascade)',
      'Réglages : indicateurs, afficher par, valeurs',
      'Tableau croisé et export CSV',
    ],
  },
];
