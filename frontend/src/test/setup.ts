import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => cleanup());

// jsdom n'implémente pas le défilement ; le routeur l'appelle à chaque navigation.
window.scrollTo = () => {};
