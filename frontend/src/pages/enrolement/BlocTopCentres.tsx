import { useState } from 'react';
import { Tab, TabList, TabPanel, Tabs } from 'react-aria-components';
import type { CentreClasse } from '../../api/client';
import { useTopCentres, type ClassementCentres } from '../../api/enrolement';
import { nf } from '../../lib/format';
import { usePlageApi } from '../../lib/usePlagePeriode';

interface Onglet {
  id: ClassementCentres;
  libelle: string;
  colonne: string;
  /** Précision sous l'en-tête de la colonne des valeurs. */
  precision?: string;
  vide: string;
}

const VIDE_PERIODE = 'Aucun centre de ce classement sur la période.';

const ONGLETS: Onglet[] = [
  { id: 'inscriptions', libelle: 'Plus d’enregistrements', colonne: 'Inscriptions', vide: VIDE_PERIODE },
  { id: 'echecs', libelle: 'Plus d’échecs', colonne: 'Échecs', vide: VIDE_PERIODE },
  { id: 'rejets', libelle: 'Plus de rejets', colonne: 'Rejets', vide: VIDE_PERIODE },
  // Stock à l'heure du calcul : paquets synchronisés par le poste, pas encore reçus par MOSIP après 7 jours.
  {
    id: 'remontee',
    libelle: 'Remontée la plus lente',
    colonne: 'Paquets en retard',
    precision: 'synchronisés, non reçus après 7 jours',
    vide: 'Aucun centre n’a de paquet synchronisé non reçu depuis plus de 7 jours.',
  },
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

function Classement({ onglet }: { onglet: Onglet }) {
  const classement = onglet.id;
  const { plage, prete } = usePlageApi('enrolement');
  // National : le bloc ne suit pas la zone ouverte dans le bloc Territoire.
  const { data, isPending } = useTopCentres(plage, undefined, classement, prete);

  if (data && data.centres.length === 0) {
    return <p className="texte-2">{onglet.vide}</p>;
  }
  // Sans réponse de l'API, le tableau garde ses cinq rangs, chiffres à 0.
  const centres = data?.centres ?? CENTRES_INCONNUS;
  return (
    <>
      {isPending && <p className="texte-2 etat-chargement">Chargement des chiffres…</p>}
      <table className="tableau tableau-centres">
        <caption className="visuellement-cache">
          {onglet.libelle} : {data?.perimetre ?? 'Ensemble du Togo'}
        </caption>
        <thead>
          <tr>
            <th scope="col">Rang</th>
            <th scope="col">Centre</th>
            <th scope="col" className="tableau__nombre">
              {onglet.colonne}
              {onglet.precision && (
                <>
                  {' '}
                  <span className="texte-2 tableau-centres__precision">{onglet.precision}</span>
                </>
              )}
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
 * ou le plus de paquets synchronisés non reçus après 7 jours (remontée la plus lente), sur tout le Togo.
 * Onglets React Aria : flèches du clavier pour changer de classement.
 */
export function BlocTopCentres() {
  const [onglet, setOnglet] = useState<ClassementCentres>('inscriptions');

  return (
    <section className="panneau bloc-top-centres" aria-labelledby="titre-top-centres">
      <h2 id="titre-top-centres" className="titre-bloc">
        Top des centres
      </h2>
      <p className="texte-2 bloc__sous-titre">Ensemble du Togo</p>
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
            <Classement onglet={o} />
          </TabPanel>
        ))}
      </Tabs>
    </section>
  );
}
