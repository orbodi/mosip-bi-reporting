import { useNavigate } from '@tanstack/react-router';
import { Button, Label, ListBox, ListBoxItem, Popover, Select, SelectValue } from 'react-aria-components';
import type { CodeSource } from '../../api/meta';
import { dateFr } from '../../lib/format';
import type { FiltresUrl } from '../../lib/filtresUrl';
import { CHOIX_PERIODE, LIBELLES_PERIODE, estChoixPeriode } from '../../lib/periode';
import { usePlagePeriode } from '../../lib/usePlagePeriode';

/**
 * Filtre Période du bandeau. Le choix vit dans l'adresse (?periode=7j, ?periode=perso&du=…&au=…).
 * Les périodes relatives se terminent à la dernière donnée de la source de la page.
 */
export function FiltrePeriode({ source }: { source: CodeSource }) {
  const naviguer = useNavigate();
  const { choix, donnees, plage } = usePlagePeriode(source);

  const changer = (nouveaux: FiltresUrl) =>
    naviguer({ to: '.', search: (precedent: FiltresUrl) => ({ ...precedent, ...nouveaux }), replace: true });

  return (
    <div className="filtre-periode">
      <Select
        className="pastille-filtre"
        value={choix}
        onChange={(cle) => {
          if (!estChoixPeriode(cle)) return;
          changer(
            cle === 'perso'
              ? { periode: cle, du: plage?.du, au: plage?.au }
              : { periode: cle === 'tout' ? undefined : cle, du: undefined, au: undefined },
          );
        }}
      >
        <Label className="pastille-filtre__libelle">Période</Label>
        <Button className="pastille-filtre__bouton">
          <SelectValue />
          <svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true">
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </Button>
        <Popover className="liste-popover">
          <ListBox className="liste">
            {CHOIX_PERIODE.map((c) => (
              <ListBoxItem key={c} id={c} className="liste__option">
                {LIBELLES_PERIODE[c]}
              </ListBoxItem>
            ))}
          </ListBox>
        </Popover>
      </Select>

      {choix === 'perso' && donnees && (
        <div className="filtre-periode__dates">
          <label>
            Du
            <input
              type="date"
              value={plage?.du ?? ''}
              min={donnees.du}
              max={donnees.au}
              onChange={(e) => changer({ du: e.target.value || undefined })}
            />
          </label>
          <label>
            au
            <input
              type="date"
              value={plage?.au ?? ''}
              min={donnees.du}
              max={donnees.au}
              onChange={(e) => changer({ au: e.target.value || undefined })}
            />
          </label>
        </div>
      )}

      {choix !== 'tout' && choix !== 'perso' && plage && (
        <p className="filtre-periode__plage">
          Du {dateFr(plage.du)} au {dateFr(plage.au)}
        </p>
      )}
    </div>
  );
}
