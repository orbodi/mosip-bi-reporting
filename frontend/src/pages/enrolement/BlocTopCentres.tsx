import { useState } from 'react';
import { Tab, TabList, TabPanel, Tabs } from 'react-aria-components';
import type { CentreClasse } from '../../api/client';
import { useTopCentres, type ClassementCentres } from '../../api/enrolement';
import { nf } from '../../lib/format';
import { useFiltreRegion } from '../../lib/useFiltreRegion';
import { usePlageApi } from '../../lib/usePlagePeriode';

const ONGLETS: { id: ClassementCentres; libelle: string; colonne: string }[] = [
  { id: 'inscriptions', libelle: 'Plus d’enregistrements', colonne: 'Inscriptions' },
  { id: 'echecs', libelle: 'Plus d’échecs', colonne: 'Échecs' },
  { id: 'rejets', libelle: 'Plus de rejets', colonne: 'Rejets' },
];

const CENTRES_INCONNUS: CentreClasse[] = [1, 2, 3, 4, 5].map((rang) => ({
  rang,
  code: `inconnu-${rang}`,
  nom: '–',
  prefecture: null,
  region: null,
  valeur: Number.NaN,
  inscriptions: Number.NaN,
}));

function Classement({ classement, colonne }: { classement: ClassementCentres; colonne: string }) {
  const { plage, prete } = usePlageApi('enrolement');
  const { code, region } = useFiltreRegion();
  const { data, isPending } = useTopCentres(plage, code, classement, prete);

  if (data && data.centres.length === 0) {
    return (
      <p className="texte-2">
        {region
          ? 'Aucun centre de ce classement ne se trouve dans cette région.'
          : 'Aucun centre de ce classement sur la période.'}
      </p>
    );
  }
  // Sans réponse de l'API, le tableau garde ses cinq rangs, chiffres à 0.
  const centres = data?.centres ?? CENTRES_INCONNUS;
  return (
    <>
      {isPending && <p className="texte-2 etat-chargement">Chargement des chiffres…</p>}
      <table className="tableau tableau-centres">
        <caption className="visuellement-cache">
          {ONGLETS.find((o) => o.id === classement)?.libelle} :{' '}
          {data?.perimetre ?? region?.nom ?? 'Ensemble du Togo'}
        </caption>
        <thead>
          <tr>
            <th scope="col">Rang</th>
            <th scope="col">Centre</th>
            <th scope="col" className="tableau__nombre">
              {colonne}
            </th>
          </tr>
        </thead>
        <tbody>
          {centres.map((c) => (
            <tr key={c.code}>
              <td className="tableau-centres__rang">{c.rang}</td>
              <th scope="row" className="tableau-centres__centre">
                <span className="tableau-centres__nom">{c.nom}</span>
                <span className="texte-2 tableau-centres__lieu">
                  {[c.prefecture, c.region].filter(Boolean).join(', ')}
                </span>
              </th>
              <td className="chiffre tableau__nombre tableau-centres__valeur">{nf(c.valeur)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}

/**
 * Bloc « Top des centres » : les cinq centres qui ont le plus d'inscriptions, d'échecs ou de rejets sur la période,
 * dans la région du filtre (décision P3). Onglets React Aria : flèches du clavier pour changer de classement.
 */
export function BlocTopCentres() {
  const { region } = useFiltreRegion();
  const [onglet, setOnglet] = useState<ClassementCentres>('inscriptions');

  return (
    <section className="panneau bloc-top-centres" aria-labelledby="titre-top-centres">
      <h2 id="titre-top-centres" className="titre-bloc">
        Top des centres
      </h2>
      <p className="texte-2 bloc__sous-titre">{region ? `Région ${region.nom}` : 'Ensemble du Togo'}</p>
      <Tabs selectedKey={onglet} onSelectionChange={(cle) => setOnglet(cle as ClassementCentres)}>
        <TabList aria-label="Classement affiché" className="onglets">
          {ONGLETS.map((o) => (
            <Tab key={o.id} id={o.id} className="onglets__onglet">
              {o.libelle}
            </Tab>
          ))}
        </TabList>
        {ONGLETS.map((o) => (
          <TabPanel key={o.id} id={o.id} className="onglets__panneau">
            <Classement classement={o.id} colonne={o.colonne} />
          </TabPanel>
        ))}
      </Tabs>
    </section>
  );
}
