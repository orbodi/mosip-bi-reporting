import {
  useCausesEchec,
  usePaquets,
  usePartenaires,
  useSemainesAuthentification,
  useTypesAuthentification,
  useUsagers,
} from '../../api/authentifications';
import { GraphiqueHebdo } from '../../composants/blocs/GraphiqueHebdo';
import { Drapeau } from '../../composants/blocs/Icone';
import { CarteIndicateur, GrandChiffre } from '../../composants/blocs/Indicateur';
import { Panneau } from '../../composants/blocs/Panneau';
import { Jauge, Legende, Repartition } from '../../composants/blocs/Repartition';
import { Bandeau } from '../../composants/coque/Bandeau';
import { FiltresPage } from '../../composants/coque/FiltresPage';
import {
  alerteEchec,
  chiffresPaquets,
  chiffresUsagers,
  desRequetes,
  detailOtp,
  detailPartenaires,
  lignesAppelants,
  lignesCauses,
  lignesTypes,
  pastillePartenaires,
  semainesAuthentification,
  type LigneCause,
} from '../../lib/authentifications';
import { dateFr, nf, part, pct, semaineFr } from '../../lib/format';
import { useFinPeriode, usePlageApi } from '../../lib/usePlagePeriode';
import type { DefinitionPage } from '../pages';
import './authentifications.css';

/** Classement des causes d'échec d'un périmètre (maquette : rang, motif, jauge, nombre et part). */
function Causes({ titre, lignes, total }: { titre: string; lignes: LigneCause[]; total: number }) {
  const max = Math.max(...lignes.map((l) => (Number.isFinite(l.echecs) ? l.echecs : 0)), 1);
  return (
    <table className="classement">
      <caption className="visuellement-cache">{titre}</caption>
      <tbody>
        {lignes.map((c, i) => (
          <tr key={c.code}>
            <td className="classement__rang">{i + 1}</td>
            <th scope="row">
              <span className="classement__nom">{c.libelle}</span>
            </th>
            <td className="erreur__jauge">
              <Jauge valeur={c.echecs} max={max} couleur="rouge" />
            </td>
            <td>
              <span className="classement__valeur chiffre">{nf(c.echecs)}</span>
              <span className="classement__detail">{pct(part(c.echecs, total))}</span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

/**
 * Authentifications (maquette/pages/Usage.dc.html, adaptée le 04/11/2026), lot 9 : ida.auth_transaction et
 * ida.otp_transaction (GET /api/v1/authentifications/…). Deux périmètres jamais additionnés (option A, 03/11/2026) :
 * les usagers (partenaires, portail du résident, USSD) en haut ; les vérifications biométriques du traitement des
 * paquets dans le dernier bloc. Pas de territoire : tout est national.
 */
export function PageAuthentifications({ page }: { page: DefinitionPage }) {
  const { plage, prete } = usePlageApi(page.source);
  const fin = useFinPeriode(page.source);

  const usagers = useUsagers(plage, prete);
  const types = useTypesAuthentification(plage, prete);
  const causesUsagers = useCausesEchec('usagers', plage, prete);
  const partenaires = usePartenaires(plage, prete);
  const semainesApi = useSemainesAuthentification(plage, prete);
  const paquets = usePaquets(plage, prete);
  const causesPaquets = useCausesEchec('paquets', plage, prete);

  const c = chiffresUsagers(usagers.data);
  const lignes = lignesTypes(types.data);
  const echecsUsagers = causesUsagers.data?.echecs ?? Number.NaN;
  const appelants = lignesAppelants(partenaires.data);
  const semaines = semainesAuthentification(semainesApi.data, fin);
  const p = chiffresPaquets(paquets.data);
  const echecsPaquets = causesPaquets.data?.echecs ?? Number.NaN;
  const somme = (cle: 'requetes' | 'reussies' | 'demandesOtp') => appelants.reduce((t, a) => t + a[cle], 0);

  return (
    <>
      <Bandeau titre={page.titre} source={page.source} filtres={<FiltresPage />} />
      <div className="contenu page-m">
        <Panneau
          id="titre-requetes"
          titre="Requêtes d’authentification des usagers"
          sousTitre="Partenaires, portail du résident et USSD."
          coins
          sansMarge
        >
          <div className="duo">
            <div className="duo__principal">
              <GrandChiffre valeur={nf(c.requetes)} detail="requêtes de vérification d’identité reçues" />
              <Repartition
                libelle="Requêtes réussies et échouées"
                parts={[
                  { libelle: 'Réussies', valeur: c.reussies, couleur: 'serie-1' },
                  { libelle: 'Échouées', valeur: c.echouees, couleur: 'rouge' },
                ]}
              />
              <Legende
                elements={[
                  { libelle: 'Réussies', couleur: 'serie-1' },
                  { libelle: 'Échouées', couleur: 'rouge' },
                ]}
              />
            </div>
            <div className="duo__cartes">
              <div className="cartes-m cartes-m--3">
                <CarteIndicateur
                  icone="personneOk"
                  nom="Réussies"
                  valeur={nf(c.reussies)}
                  detail={desRequetes(c.reussies, c)}
                />
                <CarteIndicateur
                  icone="croix"
                  nom="Échouées"
                  valeur={nf(c.echouees)}
                  detail={desRequetes(c.echouees, c)}
                />
                <CarteIndicateur
                  icone="empreinte"
                  nom="Biométriques"
                  valeur={nf(c.biometriques)}
                  detail={desRequetes(c.biometriques, c)}
                />
                <CarteIndicateur
                  icone="telephone"
                  nom="Code OTP"
                  valeur={nf(c.otp)}
                  detail={detailOtp(c)}
                />
                <CarteIndicateur
                  icone="carteId"
                  nom="Démographiques et combinées"
                  valeur={nf(c.demographiquesEtCombinees)}
                  detail={desRequetes(c.demographiquesEtCombinees, c)}
                />
                <CarteIndicateur
                  icone="immeuble"
                  nom="Partenaires raccordés"
                  valeur={nf(c.partenairesRaccordes)}
                  detail={detailPartenaires(c)}
                />
              </div>
            </div>
          </div>
        </Panneau>

        <Panneau
          id="titre-partenaires"
          titre="Partenaires et canaux"
          pastille={<span className="pastille-portee">{pastillePartenaires(partenaires.data)}</span>}
        >
          <div
            className="tableau-m-defile"
            tabIndex={0}
            role="group"
            aria-label="Tableau des partenaires, défilable horizontalement"
          >
            <table className="tableau-m tableau-partenaires">
              <caption className="visuellement-cache">Requêtes par partenaire et par canal</caption>
              <thead>
                <tr>
                  <th scope="col">Partenaire ou canal</th>
                  <th scope="col">Type</th>
                  <th scope="col">Requêtes</th>
                  <th scope="col">Part</th>
                  <th scope="col">Réussies</th>
                  <th scope="col">Taux d’échec</th>
                  <th scope="col">Codes OTP demandés</th>
                  <th scope="col">Dernière requête</th>
                </tr>
              </thead>
              <tbody>
                {appelants.map((a) => (
                  <tr key={a.cle}>
                    <th scope="row">{a.type === 'Partenaire' ? <strong>{a.nom}</strong> : a.nom}</th>
                    <td>{a.type}</td>
                    <td>{nf(a.requetes)}</td>
                    <td>{pct(part(a.requetes, c.requetes))}</td>
                    <td>{nf(a.reussies)}</td>
                    <td>
                      <strong>{a.requetes === 0 ? '—' : pct(part(a.requetes - a.reussies, a.requetes))}</strong>
                    </td>
                    <td>{nf(a.demandesOtp)}</td>
                    <td>{a.derniereRequete ? dateFr(a.derniereRequete) : '—'}</td>
                  </tr>
                ))}
                <tr className="total">
                  <th scope="row">Total</th>
                  <td />
                  <td>{nf(somme('requetes'))}</td>
                  <td>{pct(part(somme('requetes'), somme('requetes')))}</td>
                  <td>{nf(somme('reussies'))}</td>
                  <td>{pct(part(somme('requetes') - somme('reussies'), somme('requetes')))}</td>
                  <td>{nf(somme('demandesOtp'))}</td>
                  <td />
                </tr>
              </tbody>
            </table>
          </div>
        </Panneau>

        <Panneau
          id="titre-requetes-semaine"
          titre="Requêtes par semaine"
          aside={
            <Legende
              elements={[
                { libelle: 'Réussies', couleur: 'serie-1' },
                { libelle: 'Échouées', couleur: 'rouge' },
              ]}
            />
          }
        >
          <GraphiqueHebdo
            semaines={semaines}
            hauteur={260}
            etiquettes
            libelle="Requêtes réussies et échouées des usagers par semaine"
            series={[
              { cle: 'reussies', libelle: 'Réussies', couleur: 'serie-1', type: 'barre' },
              { cle: 'echouees', libelle: 'Échouées', couleur: 'rouge', type: 'barre' },
            ]}
            lecture={(s) =>
              `Semaine ${semaineFr(s.lundi)} : ${nf(s.valeurs.reussies + s.valeurs.echouees)} requêtes, ${nf(s.valeurs.reussies)} réussies et ${nf(s.valeurs.echouees)} échouées.`
            }
          />
        </Panneau>

        <Panneau
          id="titre-types-auth"
          titre="Par type d’authentification"
          sousTitre="Requêtes et échecs des usagers pour chaque type."
        >
          <div
            className="tableau-m-defile"
            tabIndex={0}
            role="group"
            aria-label="Tableau, défilable horizontalement"
          >
            <table className="tableau-m">
              <caption className="visuellement-cache">
                Requêtes et échecs par type d’authentification
              </caption>
              <thead>
                <tr>
                  <th scope="col">Type</th>
                  <th scope="col">Requêtes</th>
                  <th scope="col">Échecs</th>
                  <th scope="col">Taux d’échec</th>
                </tr>
              </thead>
              <tbody>
                {lignes.map((t) => {
                  const taux = part(t.echecs, t.requetes);
                  return (
                    <tr key={t.code}>
                      <th scope="row">{t.libelle}</th>
                      <td>{nf(t.requetes)}</td>
                      <td>{nf(t.echecs)}</td>
                      <td>
                        {alerteEchec(taux) && <Drapeau libelle="Alerte : taux d’échec de 50 % ou plus" />}
                        <strong>{Number.isFinite(t.requetes) && t.requetes === 0 ? '—' : pct(taux)}</strong>
                      </td>
                    </tr>
                  );
                })}
                <tr className="total">
                  <th scope="row">Total</th>
                  <td>{nf(c.requetes)}</td>
                  <td>{nf(c.echouees)}</td>
                  <td>{pct(part(c.echouees, c.requetes))}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Panneau>
        <Panneau
          id="titre-causes"
          titre="Causes des échecs"
          sousTitre={`${nf(echecsUsagers)} échecs des usagers, du plus fréquent au moins fréquent.`}
        >
          <Causes
            titre="Causes des échecs des usagers"
            lignes={lignesCauses('usagers', causesUsagers.data)}
            total={echecsUsagers}
          />
        </Panneau>

        <Panneau
          id="titre-paquets"
          titre="Vérifications biométriques du traitement des paquets"
          pastille={<span className="pastille-portee">Ensemble du Togo</span>}
          sansMarge
        >
          <div className="duo">
            <div className="duo__principal">
              <GrandChiffre valeur={nf(p.verifications)} detail="vérifications biométriques" />
              <Repartition
                libelle="Vérifications réussies et échouées"
                parts={[
                  { libelle: 'Réussies', valeur: p.reussies, couleur: 'serie-1' },
                  { libelle: 'Échouées', valeur: p.echouees, couleur: 'rouge' },
                ]}
              />
              <Legende
                elements={[
                  {
                    libelle: 'Réussies',
                    couleur: 'serie-1',
                    note: `${nf(p.reussies)} (${pct(part(p.reussies, p.verifications))})`,
                  },
                  {
                    libelle: 'Échouées',
                    couleur: 'rouge',
                    note: `${nf(p.echouees)} (${pct(part(p.echouees, p.verifications))})`,
                  },
                ]}
              />
            </div>
            <div className="duo__cartes">
              <p className="authentifications__groupe">Causes des échecs</p>
              <Causes
                titre="Causes des échecs des vérifications du traitement des paquets"
                lignes={lignesCauses('paquets', causesPaquets.data)}
                total={echecsPaquets}
              />
            </div>
          </div>
        </Panneau>
      </div>
    </>
  );
}
