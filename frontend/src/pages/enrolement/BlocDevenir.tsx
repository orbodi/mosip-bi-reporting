import { useDevenirInscriptions } from '../../api/enrolement';
import { Icone } from '../../composants/blocs/Icone';
import { devenirInconnu, estConnu } from '../../lib/blocsVides';
import { nf, part, pct } from '../../lib/format';
import { useFiltreRegion } from '../../lib/useFiltreRegion';
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
}

/**
 * Bloc « Devenir des inscriptions » (maquette Enrôlement) : NIU générés, en cours, échoués, rejetés.
 * Suit le filtre Période ; relu toutes les 30 s (pipeline temps réel). Contrôle affiché si des statuts MOSIP n'ont
 * pas encore de correspondance validée (« non classées »), jamais réparties d'office.
 */
export function BlocDevenir() {
  const { choix, plage } = usePlagePeriode('enrolement');
  // Ne suit pas le filtre Région (décision P3 de docs/plans/enrolement.md) : la pastille le signale.
  const filtreRegion = useFiltreRegion();
  const depuisLeDebut = choix === 'tout';
  const { data, isPending, isError } = useDevenirInscriptions(
    depuisLeDebut ? undefined : plage,
    depuisLeDebut || !!plage,
  );

  // Sans réponse de l'API, les cartes restent en place avec « – » (lib/blocsVides.ts).
  const d = data ?? devenirInconnu();
  const connu = estConnu(d.inscriptions);
  const statuts: Statut[] = [
    { cle: 'niu', libelle: 'NIU générés', valeur: d.niuGeneres },
    { cle: 'en-cours', libelle: 'En cours', valeur: d.enCours },
    { cle: 'echoue', libelle: 'Échoués', valeur: d.echouees },
    { cle: 'rejete', libelle: 'Rejetés', valeur: d.rejetees },
    ...(d.nonClassees > 0
      ? [{ cle: 'non-classe' as const, libelle: 'Non classés', valeur: d.nonClassees }]
      : []),
  ];
  const total = d.inscriptions;
  const description = statuts.map((s) => `${s.libelle} ${pct(part(s.valeur, total))}`).join(', ');

  return (
    <section className="panneau bloc-principal bloc-devenir" aria-labelledby="titre-devenir">
      <div className="bloc-devenir__entete">
        <h2 id="titre-devenir" className="titre-bloc">
          Devenir des inscriptions
        </h2>
        <span
          className="pastille-portee"
          title={filtreRegion.actif ? 'Ce bloc ne suit pas le filtre Région' : undefined}
        >
          {data?.perimetre ?? 'Ensemble du Togo'}
        </span>
      </div>
      <p className="texte-2 bloc-devenir__note">Actualisé automatiquement toutes les 30 secondes.</p>

      {isPending && <p className="texte-2 etat-chargement">Chargement des chiffres…</p>}
      {isError && (
        <p role="alert" className="alerte-donnees alerte-donnees--haut">
          Chiffres indisponibles pour le moment. Ils réapparaîtront dès que l’API répondra.
        </p>
      )}
      {data && total === 0 && <p className="texte-2">Aucune inscription sur la période.</p>}

      <p className="bloc-devenir__principal">
        <span className="chiffre bloc-devenir__valeur">{nf(d.niuGeneres)}</span>
        <span className="bloc-devenir__unite">
          NIU générés, soit {pct(part(d.niuGeneres, total))} des {nf(total)} inscriptions
        </span>
      </p>
      <div
        className="barre-statuts"
        role="img"
        aria-label={
          connu ? `Devenir des inscriptions : ${description}` : 'Devenir des inscriptions : non disponible'
        }
      >
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
