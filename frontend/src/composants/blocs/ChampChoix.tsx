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
  /** Option visible mais impossible à choisir (grisée), avec sa raison sous le libellé. */
  desactive?: boolean;
  raison?: string;
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

function Option({ o }: { o: OptionChoix }) {
  return (
    <ListBoxItem id={o.id} textValue={o.libelle} className="liste__option">
      {o.libelle}
      {o.desactive && o.raison && <span className="liste__raison">{o.raison}</span>}
    </ListBoxItem>
  );
}

/**
 * Liste de choix de l'Exploration (React Aria Select : clavier et lecteurs d'écran). Champ désactivé : sa raison
 * s'affiche au survol (title) et se lit au lecteur d'écran (aria-description). Option désactivée : grisée, raison
 * sous son libellé.
 */
export function ChampChoix({ libelle, valeur, options, groupes = [], onChange, desactive, raison }: Props) {
  const desactivees = [...options, ...groupes.flatMap((g) => g.options)]
    .filter((o) => o.desactive)
    .map((o) => o.id);
  return (
    <Select
      className="champ-choix"
      value={valeur}
      onChange={(cle) => cle !== null && onChange(String(cle))}
      isDisabled={desactive}
      disabledKeys={desactivees}
    >
      <Label className="champ-choix__libelle">{libelle}</Label>
      {/* Raison au survol : sur une enveloppe, le bouton désactivé ne reçoit pas la souris partout. */}
      <span className="champ-choix__cadre" title={desactive ? raison : undefined}>
        <Button className="champ-choix__bouton" aria-description={desactive ? raison : undefined}>
          <SelectValue className="champ-choix__valeur" />
          <Chevron bas taille={12} />
        </Button>
      </span>
      <Popover className="liste-popover">
        <ListBox className="liste">
          {options.map((o) => (
            <Option key={o.id} o={o} />
          ))}
          {groupes.map((g) => (
            <ListBoxSection key={g.titre}>
              <Header className="liste__groupe">{g.titre}</Header>
              {g.options.map((o) => (
                <Option key={o.id} o={o} />
              ))}
            </ListBoxSection>
          ))}
        </ListBox>
      </Popover>
    </Select>
  );
}
