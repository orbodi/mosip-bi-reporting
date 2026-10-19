/**
 * Signale qu'une source n'est pas encore raccordée au BI : la page garde la mise en page de la maquette, les chiffres
 * restent « – » (jamais de zéro ni de valeur inventée).
 */
export function NoteSource({ source }: { source: string }) {
  return (
    <p className="note-source" role="note">
      <strong>Source « {source} » pas encore raccordée au BI.</strong> La page présente la mise en page de la
      maquette ; les chiffres s’afficheront dès que l’API de cette source sera disponible.
    </p>
  );
}
