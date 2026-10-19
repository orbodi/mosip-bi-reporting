import type { LigneZone } from '../../api/client';
import { useTerritoire } from '../../api/enrolement';
import { CARTE_REGIONS, carteRegion } from '../../composants/carte/fondsDeCarte';
import { nf, part, pct } from '../../lib/format';
import { SEUIL_ALERTE_REJET, alerteRejet, tauxNiu, tauxRejet } from '../../lib/territoire';
import { useFiltreRegion } from '../../lib/useFiltreRegion';
import { usePlageApi } from '../../lib/usePlagePeriode';
import { CarteTerritoire } from './CarteTerritoire';

function Chevron() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" className="chevron">
      <polyline points="9 6 15 12 9 18" />
    </svg>
  );
}

/**
 * Bloc « Territoire » (maquette Enrôlement) : vue nationale par région, ou préfectures de la région du filtre.
 * Carte colorée selon le taux de NIU générés et tableau des zones (alerte ▲ au-delà de 3,5 % de rejets). Cliquer une
 * région (carte, liste ou tableau) revient à choisir cette région dans le filtre du bandeau : l'adresse change.
 */
export function BlocTerritoire() {
  const { plage, prete } = usePlageApi('enrolement');
  const { code, region, regional, choisir } = useFiltreRegion();
  const { data, isPending, isError } = useTerritoire(plage, code, prete);
  // Total national pour situer une région (« 31,1 % du total national ») ; sans objet pour un utilisateur régional.
  const national = useTerritoire(plage, undefined, prete && !!code && !regional);

  const nomZone = code ? (region?.nom ?? data?.perimetre ?? '') : undefined;
  const ouvrir = !code && !regional ? (l: LigneZone) => choisir(l.code, { historique: true }) : undefined;
  const lignes = data?.lignes ?? [];
  const regionsComptees = lignes.filter((l) => !l.horsReferentiel).length;
  const totalNational =
    national.data && national.data.perimetre === 'Ensemble du Togo' ? national.data.inscriptions : undefined;

  return (
    <section className="panneau bloc-pleine-largeur bloc-territoire" aria-labelledby="titre-territoire">
      <div className="territoire__entete">
        <div>
          <nav aria-label="Fil d’Ariane du territoire" className="fil-ariane">
            {nomZone && !regional ? (
              <>
                <button
                  type="button"
                  className="fil-ariane__lien"
                  onClick={() => choisir(undefined, { historique: true })}
                >
                  Togo
                </button>
                <Chevron />
                <span aria-current="location">{nomZone}</span>
              </>
            ) : (
              <span aria-current="location">{nomZone ?? 'Togo'}</span>
            )}
          </nav>
          <h2 id="titre-territoire" className="titre-bloc">
            {nomZone ? `Territoire : région ${nomZone}` : 'Territoire : vue nationale'}
          </h2>
          <p className="texte-2 bloc__sous-titre">
            Carte colorée selon le taux de NIU : part des inscriptions qui ont leur NIU.
            {ouvrir && ' Cliquez sur une région pour voir ses préfectures.'}
          </p>
        </div>
        {data && (
          <dl className="territoire__chiffres" aria-label="Chiffres de la zone">
            <div>
              <dt>Inscriptions</dt>
              <dd className="chiffre territoire__valeur">{nf(data.inscriptions)}</dd>
              <dd className="texte-2">
                {!code
                  ? `dans ${regionsComptees} régions`
                  : totalNational !== undefined
                    ? `${pct(part(data.inscriptions, totalNational))} du total national`
                    : `région ${nomZone}`}
              </dd>
            </div>
            <div>
              <dt>NIU générés</dt>
              <dd className="chiffre territoire__valeur">{nf(data.niuGeneres)}</dd>
              <dd className="texte-2">{pct(tauxNiu(data))} des inscriptions</dd>
            </div>
          </dl>
        )}
      </div>

      {isPending && <p className="texte-2">Chargement des chiffres…</p>}
      {isError && (
        <p role="alert" className="alerte-donnees">
          Chiffres indisponibles pour le moment. Ils réapparaîtront dès que l’API répondra.
        </p>
      )}

      {data && (
        <div className="territoire__corps">
          <CarteTerritoire
            fond={nomZone ? carteRegion(nomZone) : CARTE_REGIONS}
            zone={{ nom: nomZone ?? 'Togo', chiffres: data }}
            lignes={lignes}
            titreListe={nomZone ? 'Préfectures, du nord au sud' : 'Régions, du nord au sud'}
            libelleCarte={
              nomZone
                ? `Carte de la région ${nomZone} et de ses préfectures, colorée selon le taux de NIU générés`
                : 'Carte des régions du Togo, colorée selon le taux de NIU générés'
            }
            onOuvrir={ouvrir}
          />

          <div className="territoire__tableau">
            <table className="tableau tableau-zones">
              <caption className="tableau-zones__titre">
                {nomZone ? `Préfectures de la région ${nomZone}` : 'Régions'}
              </caption>
              <thead>
                <tr>
                  <th scope="col">Zone</th>
                  <th scope="col" className="tableau__nombre col-secondaire">
                    Inscriptions
                  </th>
                  <th scope="col" className="tableau__nombre">
                    NIU générés
                  </th>
                  <th scope="col" className="tableau__nombre">
                    Rejets
                  </th>
                  <th scope="col" className="tableau__nombre col-secondaire">
                    Échoués
                  </th>
                  <th scope="col" className="tableau__nombre col-secondaire">
                    En cours
                  </th>
                  <th scope="col" className="tableau__nombre col-secondaire">
                    Délai médian
                  </th>
                </tr>
              </thead>
              <tbody>
                {lignes.map((l) => {
                  const alerte = alerteRejet(l);
                  return (
                    <tr key={l.code}>
                      <th scope="row">
                        {ouvrir && !l.horsReferentiel ? (
                          <button type="button" className="tableau-zones__ouvrir" onClick={() => ouvrir(l)}>
                            {l.nom}
                            <Chevron />
                          </button>
                        ) : (
                          <span className="tableau-zones__nom">{l.nom}</span>
                        )}
                      </th>
                      <td className="chiffre tableau__nombre col-secondaire">{nf(l.inscriptions)}</td>
                      <td className="chiffre tableau__nombre">{nf(l.niuGeneres)}</td>
                      <td
                        className={`chiffre tableau__nombre${alerte ? ' tableau-zones__alerte' : ''}`}
                        title={`Taux de rejet : ${pct(tauxRejet(l))}`}
                      >
                        {alerte && (
                          <span className="alerte-rejet" aria-label="Taux de rejet élevé">
                            ▲{' '}
                          </span>
                        )}
                        {nf(l.rejetees)}
                        {alerte && <span className="tableau-zones__taux texte-2">{pct(tauxRejet(l))}</span>}
                      </td>
                      <td className="chiffre tableau__nombre col-secondaire">{nf(l.echouees)}</td>
                      <td className="chiffre tableau__nombre col-secondaire">{nf(l.enCours)}</td>
                      <td className="chiffre tableau__nombre col-secondaire" title="Non disponible">
                        –
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <p className="texte-2 tableau-zones__note">
              <span className="alerte-rejet" aria-hidden="true">
                ▲
              </span>{' '}
              Taux de rejet de {pct(SEUIL_ALERTE_REJET / 100)} ou plus (rejets rapportés aux inscriptions de
              la zone).
            </p>
            <p className="texte-2 tableau-zones__note">
              Délai médian : non disponible tant que les délais jusqu’au NIU ne sont pas calculés.
            </p>
            {data.nonClassees > 0 && (
              <p className="alerte-donnees" role="note">
                {nf(data.nonClassees)} inscriptions ont un statut MOSIP sans correspondance validée : comptées
                dans les inscriptions, hors des colonnes de statut.
              </p>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
