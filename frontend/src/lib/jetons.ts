/**
 * Lit la valeur d'un jeton de styles/jetons.css (ex. « --serie-1 ») pour les bibliothèques qui demandent une
 * couleur en clair (ECharts). Chaîne vide si le jeton n'existe pas (tests sans CSS).
 */
export function jeton(nom: `--${string}`): string {
  if (typeof window === 'undefined') return '';
  return getComputedStyle(document.documentElement).getPropertyValue(nom).trim();
}
