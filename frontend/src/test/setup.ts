import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => cleanup());

// jsdom n'implémente pas le défilement ; le routeur l'appelle à chaque navigation.
window.scrollTo = () => {};

// jsdom n'implémente pas le canvas : ECharts (rendu SVG) s'en sert seulement pour mesurer le texte et passe à une
// estimation quand il n'a pas de contexte. On évite ainsi le message « Not implemented » à chaque graphique.
HTMLCanvasElement.prototype.getContext = () => null;
