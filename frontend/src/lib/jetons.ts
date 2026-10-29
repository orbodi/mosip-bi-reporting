/**
 * Lit la valeur d'un jeton de styles/jetons.css (ex. « --serie-1 ») pour les bibliothèques qui demandent une
 * couleur en clair (ECharts). Chaîne vide si le jeton n'existe pas (tests sans CSS).
 */
export function jeton(nom: `--${string}`): string {
  if (typeof window === 'undefined') return '';
  return getComputedStyle(document.documentElement).getPropertyValue(nom).trim();
}

/**
 * Couleur « #rrggbb » mêlée de blanc (part de blanc entre 0 et 1), pour une barre plus claire sans toucher à son
 * étiquette (l'opacité d'ECharts éclaircirait aussi le texte). Couleur inchangée si elle n'est pas « #rrggbb ».
 */
export function eclaircir(couleur: string, part: number): string {
  const m = /^#([0-9a-f]{6})$/i.exec(couleur);
  if (!m) return couleur;
  const canal = (i: number) => {
    const v = parseInt(m[1].slice(i, i + 2), 16);
    return Math.round(v + (255 - v) * part)
      .toString(16)
      .padStart(2, '0');
  };
  return `#${canal(0)}${canal(2)}${canal(4)}`;
}
