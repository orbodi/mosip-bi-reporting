import { useDevenirInscriptions } from '../../api/enrolement';
import { nf, part, pct } from '../../lib/format';
import { useFiltreRegion } from '../../lib/useFiltreRegion';
import { usePlagePeriode } from '../../lib/usePlagePeriode';
import './enrolement.css';

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

  const statuts: Statut[] = data
    ? [
        { cle: 'niu', libelle: 'NIU générés', valeur: data.niuGeneres },
        { cle: 'en-cours', libelle: 'En cours', valeur: data.enCours },
        { cle: 'echoue', libelle: 'Échoués', valeur: data.echouees },
        { cle: 'rejete', libelle: 'Rejetés', valeur: data.rejetees },
        ...(data.nonClassees > 0
          ? [{ cle: 'non-classe' as const, libelle: 'Non classés', valeur: data.nonClassees }]
          : []),
      ]
    : [];
  const total = data?.inscriptions ?? 0;
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

      {isPending && <p className="texte-2">Chargement des chiffres…</p>}
      {isError && (
        <p role="alert" className="alerte-donnees">
          Chiffres indisponibles pour le moment. Ils réapparaîtront dès que l’API répondra.
        </p>
      )}
      {data && total === 0 && <p className="texte-2">Aucune inscription sur la période.</p>}

      {data && total > 0 && (
        <>
          <p className="bloc-devenir__principal">
            <span className="chiffre bloc-devenir__valeur">{nf(data.niuGeneres)}</span>
            <span className="bloc-devenir__unite">
              NIU générés, soit {pct(part(data.niuGeneres, total))} des {nf(total)} inscriptions
            </span>
          </p>
          <div className="barre-statuts" role="img" aria-label={`Devenir des inscriptions : ${description}`}>
            {statuts.map((s) => (
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
                <span className="carte-statut__libelle">
                  <i className={`puce-statut statut--${s.cle}`} aria-hidden="true" />
                  {s.libelle}
                </span>
                <span className="chiffre carte-statut__valeur">{nf(s.valeur)}</span>
                <span className="texte-2 carte-statut__part">{pct(part(s.valeur, total))}</span>
              </li>
            ))}
          </ul>
          {data.nonClassees > 0 && (
            <p className="alerte-donnees" role="note">
              {nf(data.nonClassees)} inscriptions ont un statut MOSIP sans correspondance validée : elles sont
              comptées à part en attendant la règle de l’équipe MOSIP.
            </p>
          )}
        </>
      )}
    </section>
  );
}
