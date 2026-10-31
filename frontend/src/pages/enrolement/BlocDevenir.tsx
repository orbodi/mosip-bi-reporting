import { useDevenirInscriptions } from '../../api/enrolement';
import { Icone } from '../../composants/blocs/Icone';
import { depuisApi, devenirInconnu, estConnu } from '../../lib/blocsVides';
import { nf, part, pct } from '../../lib/format';
import { usePlagePeriode } from '../../lib/usePlagePeriode';
import './enrolement.css';

/** Pictogrammes des cartes de statut (maquette). */
const ICONE_STATUT: Record<Statut['cle'], string> = {
  niu: 'diese',
  'en-cours': 'cycle',
  echoue: 'alerte',
  rejete: 'croix',
  'non-classe': 'document',
};

interface Statut {
  cle: 'niu' | 'en-cours' | 'echoue' | 'rejete' | 'non-classe';
  libelle: string;
  valeur: number;
  /** Paquets en cours bloqués depuis plus de 30 jours (carte « En cours »). */
  bloques?: number;
  /** Paquets en cours que MOSIP reprendra, dernière transaction REPROCESS (carte « En cours »). */
  enReprocessing?: number;
}

/**
 * Bloc « Devenir des inscriptions » (maquette Enrôlement) : NIU générés, en cours (dont bloqués, dont en
 * reprocessing), échoués, rejetés.
 * Variante A du 31/10/2026 : chaque chiffre qui précise un autre se place à côté de lui, sans être un statut de plus.
 * Les demandes de mise à jour et de NIU perdu, sous le total des inscriptions dont elles font partie ; les dossiers en
 * reprocessing (dernière transaction MOSIP REPROCESS), dans la carte En cours. Ni la barre ni la somme des statuts ne
 * changent.
 * Suit le filtre Période ; relu toutes les 30 s (pipeline temps réel). Contrôle affiché si des statuts MOSIP n'ont
 * pas encore de correspondance validée (« non classées »), jamais réparties d'office.
 */
export function BlocDevenir() {
  const { choix, plage } = usePlagePeriode('enrolement');
  // Ne suit pas le filtre Région (décision P3 de docs/plans/enrolement.md) : la pastille le signale.
  const depuisLeDebut = choix === 'tout';
  const { data, isPending } = useDevenirInscriptions(
    depuisLeDebut ? undefined : plage,
    depuisLeDebut || !!plage,
  );

  // Sans réponse de l'API, les cartes restent en place avec des chiffres à 0 (lib/blocsVides.ts).
  const d = data ?? devenirInconnu();
  const connu = estConnu(d.inscriptions);
  const statuts: Statut[] = [
    { cle: 'niu', libelle: 'NIU générés', valeur: d.niuGeneres },
    // « dont N bloqués » : stock sans date, absent quand une période est demandée (bloques null de l'API).
    {
      cle: 'en-cours',
      libelle: 'En cours',
      valeur: d.enCours,
      bloques: !data || data.bloques != null ? depuisApi(data?.bloques) : undefined,
      enReprocessing: depuisApi(d.enReprocessing),
    },
    { cle: 'echoue', libelle: 'Échoués', valeur: d.echouees },
    { cle: 'rejete', libelle: 'Rejetés', valeur: d.rejetees },
    ...(d.nonClassees > 0
      ? [{ cle: 'non-classe' as const, libelle: 'Non classés', valeur: d.nonClassees }]
      : []),
  ];
  const total = d.inscriptions;
  // Parties des inscriptions selon le type de demande (UPDATE et RES_UPDATE, LOST), sous le total.
  const demandes = [
    { cle: 'mise-a-jour', libelle: 'Demandes de mise à jour', valeur: depuisApi(d.demandesMiseAJour) },
    { cle: 'niu-perdu', libelle: 'Demandes de NIU perdu', valeur: depuisApi(d.demandesNiuPerdu) },
  ];
  const description = statuts.map((s) => `${s.libelle} ${pct(part(s.valeur, total))}`).join(', ');

  return (
    <section className="panneau bloc-principal bloc-devenir" aria-labelledby="titre-devenir">
      <div className="bloc-devenir__entete">
        <h2 id="titre-devenir" className="titre-bloc">
          Devenir des inscriptions
        </h2>
        <span className="pastille-portee">{data?.perimetre ?? 'Ensemble du Togo'}</span>
      </div>
      <p className="texte-2 bloc-devenir__note">Actualisé automatiquement toutes les 30 secondes.</p>

      {isPending && <p className="texte-2 etat-chargement">Chargement des chiffres…</p>}
      {data && total === 0 && <p className="texte-2">Aucune inscription sur la période.</p>}

      <p className="bloc-devenir__principal">
        <span className="chiffre bloc-devenir__valeur">{nf(d.niuGeneres)}</span>
        <span className="bloc-devenir__unite">
          NIU générés, soit {pct(part(d.niuGeneres, total))} des {nf(total)} inscriptions
        </span>
      </p>
      <div role="group" aria-label="Types de demande parmi les inscriptions">
        <dl className="cartes-demandes">
          {demandes.map((t) => (
            <div key={t.cle} className="carte-demande">
              <dt className="carte-demande__libelle">{t.libelle}</dt>
              <dd className="carte-demande__chiffres">
                <span className="chiffre carte-demande__valeur">{nf(t.valeur)}</span>
                <span className="texte-2 carte-demande__part">{pct(part(t.valeur, total))}</span>
              </dd>
            </div>
          ))}
        </dl>
      </div>
      <div className="barre-statuts" role="img" aria-label={`Devenir des inscriptions : ${description}`}>
        {connu &&
          total > 0 &&
          statuts.map((s) => (
            <span
              key={s.cle}
              className={`barre-statuts__part statut--${s.cle}`}
              style={{ flexGrow: s.valeur }}
              title={`${s.libelle} : ${nf(s.valeur)}`}
            />
          ))}
      </div>
      <ul className="cartes-statuts">
        {statuts.map((s) => (
          <li key={s.cle} className="carte-statut">
            <Icone nom={ICONE_STATUT[s.cle]} />
            <div className="carte-statut__corps">
              <span className="carte-statut__libelle">
                <i className={`puce-statut statut--${s.cle}`} aria-hidden="true" />
                {s.libelle}
              </span>
              <span className="chiffre carte-statut__valeur">{nf(s.valeur)}</span>
              <span className="texte-2 carte-statut__part">{pct(part(s.valeur, total))}</span>
              {s.bloques !== undefined && (
                <span className="carte-statut__detail">
                  dont <strong className="chiffre">{nf(s.bloques)}</strong> bloqués depuis plus de 30 jours
                </span>
              )}
              {s.enReprocessing !== undefined && (
                <span className="carte-statut__encart">
                  <span className="carte-statut__encart-libelle">En reprocessing</span>
                  <span className="chiffre carte-statut__encart-valeur">{nf(s.enReprocessing)}</span>
                </span>
              )}
            </div>
          </li>
        ))}
      </ul>
      {d.nonClassees > 0 && (
        <p className="alerte-donnees" role="note">
          {nf(d.nonClassees)} inscriptions ont un statut MOSIP sans correspondance validée : elles sont
          comptées à part en attendant la règle de l’équipe MOSIP.
        </p>
      )}
    </section>
  );
}
