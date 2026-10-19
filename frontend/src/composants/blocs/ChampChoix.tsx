import {
  Button,
  Header,
  Label,
  ListBox,
  ListBoxItem,
  ListBoxSection,
  Popover,
  Select,
  SelectValue,
} from 'react-aria-components';
import { Chevron } from './Icone';

export interface OptionChoix {
  id: string;
  libelle: string;
}

interface Props {
  libelle: string;
  valeur: string;
  options: OptionChoix[];
  /** Options regroupées sous un intitulé (ex. « Années », « Mois »), après les options simples. */
  groupes?: { titre: string; options: OptionChoix[] }[];
  onChange: (id: string) => void;
  desactive?: boolean;
  /** Raison affichée au survol quand le champ est désactivé. */
  raison?: string;
}

/** Liste de choix de l'Exploration (React Aria Select : clavier et lecteurs d'écran). */
export function ChampChoix({ libelle, valeur, options, groupes = [], onChange, desactive, raison }: Props) {
  return (
    <Select
      className="champ-choix"
      value={valeur}
      onChange={(cle) => cle !== null && onChange(String(cle))}
      isDisabled={desactive}
    >
      <Label className="champ-choix__libelle">{libelle}</Label>
      <Button className="champ-choix__bouton" aria-description={desactive ? raison : undefined}>
        <SelectValue className="champ-choix__valeur" />
        <Chevron bas taille={12} />
      </Button>
      <Popover className="liste-popover">
        <ListBox className="liste">
          {options.map((o) => (
            <ListBoxItem key={o.id} id={o.id} className="liste__option">
              {o.libelle}
            </ListBoxItem>
          ))}
          {groupes.map((g) => (
            <ListBoxSection key={g.titre}>
              <Header className="liste__groupe">{g.titre}</Header>
              {g.options.map((o) => (
                <ListBoxItem key={o.id} id={o.id} className="liste__option">
                  {o.libelle}
                </ListBoxItem>
              ))}
            </ListBoxSection>
          ))}
        </ListBox>
      </Popover>
    </Select>
  );
}
