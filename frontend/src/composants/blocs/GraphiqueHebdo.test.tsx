import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { nf } from '../../lib/format';
import { GraphiqueHebdo } from './GraphiqueHebdo';

describe('GraphiqueHebdo', () => {
  it('graphique et tableau des semaines en onglets, le graphique ouvert à l’arrivée (07/11/2026)', async () => {
    const utilisateur = userEvent.setup();
    render(
      <GraphiqueHebdo
        semaines={[
          { lundi: '2026-10-26', valeurs: { reussies: 400, echouees: 160 } },
          { lundi: '2026-11-02', valeurs: { reussies: 420, echouees: 170 } },
        ]}
        series={[
          { cle: 'reussies', libelle: 'Réussies', couleur: 'serie-1', type: 'pile' },
          { cle: 'echouees', libelle: 'Échouées', couleur: 'rouge', type: 'pile' },
        ]}
        lecture={(s) => `Semaine du ${s.lundi}`}
        libelle="Requêtes par semaine"
      />,
    );

    expect(screen.getByRole('tab', { name: 'Graphique', selected: true })).toBeInTheDocument();
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
    expect(screen.queryByText('Voir le tableau des semaines')).not.toBeInTheDocument();

    await utilisateur.click(screen.getByRole('tab', { name: 'Tableau' }));
    const lignes = within(screen.getByRole('table', { name: 'Requêtes par semaine' })).getAllByRole('row');
    expect(lignes).toHaveLength(3);
    expect(lignes[2]).toHaveTextContent(`${nf(420)}${nf(170)}`.replace(/\s+/g, ' '));
    // La lecture de la semaine reste au-dessus du tableau.
    expect(screen.getByText('Semaine du 2026-11-02')).toBeInTheDocument();
  });
});
