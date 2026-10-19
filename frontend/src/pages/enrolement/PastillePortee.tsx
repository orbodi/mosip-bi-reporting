/** Pastille des blocs qui ne suivent pas le filtre Région (maquette : « Ensemble du Togo »). */
export function PastillePortee({ perimetre }: { perimetre?: string }) {
  return (
    <span className="pastille-portee" title="Ce bloc ne suit pas le filtre Région">
      {perimetre ?? 'Ensemble du Togo'}
    </span>
  );
}
