import { Button, Label, ListBox, ListBoxItem, Popover, Select, SelectValue } from 'react-aria-components';
import { useFiltreRegion } from '../../lib/useFiltreRegion';

const TOUTES = 'toutes';

/**
 * Filtre Région du bandeau (Vue d'ensemble, Enrôlement, Impression des cartes). Le choix vit dans l'adresse
 * (?region=KAR). Les blocs qui ne le suivent pas l'indiquent par la pastille « Ensemble du Togo ». Un utilisateur
 * régional ne se voit proposer que sa région (liste fournie par l'API).
 */
export function FiltreRegion() {
  const { regions, region, choisir } = useFiltreRegion();
  const regional = regions.length === 1;
  const options = regional ? regions : [{ code: TOUTES, nom: 'Toutes les régions' }, ...regions];

  return (
    <Select
      className="pastille-filtre"
      value={region?.code ?? TOUTES}
      isDisabled={regional}
      onChange={(cle) => choisir(cle === TOUTES || cle === null ? undefined : String(cle))}
    >
      <Label className="pastille-filtre__libelle">Région</Label>
      <Button className="pastille-filtre__bouton">
        <SelectValue />
        {!regional && (
          <svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true">
            <polyline points="6 9 12 15 18 9" />
          </svg>
        )}
      </Button>
      <Popover className="liste-popover">
        <ListBox className="liste" items={options}>
          {(r) => (
            <ListBoxItem id={r.code} className="liste__option">
              {r.nom}
            </ListBoxItem>
          )}
        </ListBox>
      </Popover>
    </Select>
  );
}
