import '@testing-library/jest-dom/vitest';
import { cleanup, configure } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => cleanup());

// findBy… et waitFor attendent 8 s au lieu de 1 : sur le serveur, la suite tourne à côté du front en service, un
// processus par fichier (20 à la fois), et le premier rendu d'une page complète peut dépasser 3 s sans être faux
// (25/10/2026, porté de 3 à 8 s le 26/10/2026 avec les blocs du lot 5). Un test faux échoue toujours, plus tard.
configure({ asyncUtilTimeout: 8000 });

// jsdom n'implémente pas le défilement ; le routeur l'appelle à chaque navigation.
window.scrollTo = () => {};

// jsdom n'implémente pas le canvas : ECharts (rendu SVG) s'en sert seulement pour mesurer le texte et passe à une
// estimation quand il n'a pas de contexte. On évite ainsi le message « Not implemented » à chaque graphique.
HTMLCanvasElement.prototype.getContext = () => null;
