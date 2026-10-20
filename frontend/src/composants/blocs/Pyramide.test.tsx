import { render, screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Pyramide } from './Pyramide';

describe('Pyramide', () => {
  it('chiffres connus : totaux et parts par sexe, barres proportionnelles', () => {
    render(
      <Pyramide
        libelle="Pyramide"
        lignes={[
          { tranche: '19 à 25', femmes: 300, hommes: 100 },
          { tranche: '0 à 5', femmes: 150, hommes: 450 },
        ]}
      />,
    );
    expect(screen.getByText(/^Femmes :/).textContent).toMatch(/Femmes : 450 \(45,0\s%\)/);
    expect(screen.getByText(/^Hommes :/).textContent).toMatch(/Hommes : 550 \(55,0\s%\)/);
    const ligne = within(screen.getAllByRole('row')[2]);
    expect(ligne.getByRole('rowheader')).toHaveTextContent('0 à 5');
    const [femmes, hommes] = ligne.getAllByRole('cell');
    expect(femmes).toHaveTextContent('150');
    expect(hommes.querySelector('.pyramide__barre--hommes')).toHaveStyle({ width: '70%' });
    expect(femmes.querySelector('.pyramide__barre--femmes')).toHaveStyle({ width: `${(150 / 450) * 70}%` });
  });
});
