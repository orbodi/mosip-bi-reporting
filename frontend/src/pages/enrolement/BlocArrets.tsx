import { useEnCours, useEtapes } from '../../api/enrolement';
import { nf, pct } from '../../lib/format';
import { colonnesArrets, largeurBarre, type ColonneArret, type LigneArret } from '../../lib/traitement';
import { usePlageApi } from '../../lib/usePlagePeriode';
import './enrolement.css';

/** Seuil des paquets bloqués quand l'API ne l'a pas encore donné (PaquetsEnCours.seuilJours). */
const SEUIL_JOURS = 30;

function Piste({ ligne, colonne }: { ligne: LigneArret; colonne: ColonneArret }) {
  if (colonne.cle !== 'en-cours') {
    return (
      <span className="etape-arret__piste" aria-hidden="true">
        <span
          className={`statut--${colonne.cle}`}
          style={{ width: `${largeurBarre(ligne.valeur, colonne.total)}%` }}
        />
      </span>
    );
  }
  return (
    <span className="etape-arret__piste" aria-hidden="true">
      {ligne.bloques > 0 && (
        <span className="motif-bloque" style={{ width: `${largeurBarre(ligne.bloques, colonne.total)}%` }} />
      )}
      <span
        className="statut--en-cours"
        style={{ width: `${largeurBarre(ligne.valeur - ligne.bloques, colonne.total)}%` }}
      />
    </span>
  );
}

function Colonne({ colonne, seuil }: { colonne: ColonneArret; seuil: number }) {
  const enCours = colonne.cle === 'en-cours';
  const id = `arret-${colonne.cle}`;
  return (
    <article className={`arret arret--${colonne.cle}`} aria-labelledby={id}>
      <header className="arret__tete">
        <h3 className="arret__titre" id={id}>
          <i className={`puce-statut statut--${colonne.cle}`} aria-hidden="true" />
          {colonne.titre}
        </h3>
        <p className="arret__total">
          <span className="chiffre arret__nombre">{nf(colonne.total)}</span>
          <span className="arret__part">paquets, {pct(colonne.part)} des paquets sans NIU</span>
        </p>
        {enCours && (
          <p className="arret__bloques">
            <i className="motif-bloque" aria-hidden="true" />
            <span>
              <strong className="chiffre">{nf(colonne.bloques)}</strong> bloqués depuis plus de {seuil} jours
            </span>
          </p>
        )}
      </header>
      <ul className="arret__etapes" aria-label={`${colonne.titre} par étape`}>
        {colonne.lignes.map((l) => (
          <li key={l.cle} className={`etape-arret${l.principale ? ' etape-arret--principale' : ''}`}>
            <div className="etape-arret__ligne">
              <span className="etape-arret__nom">{l.libelle}</span>
              <span className="etape-arret__valeur chiffre">{nf(l.valeur)}</span>
            </div>
            <div className="etape-arret__ligne etape-arret__ligne--2">
              {l.code ? <span className="etape-arret__code">{l.code}</span> : <span />}
              <span className="etape-arret__pct chiffre">{pct(l.part)}</span>
            </div>
            <Piste ligne={l} colonne={colonne} />
            {enCours && (
              <p className="etape-arret__detail">
                {l.bloques > 0 && (
                  <>
                    <strong className="chiffre">{nf(l.bloques)}</strong> bloqués ·{' '}
                  </>
                )}
                <span className="chiffre">{nf(l.valeur - l.bloques)}</span> récents
              </p>
            )}
          </li>
        ))}
      </ul>
      {enCours && (
        <ul className="arret__legende" aria-label="Légende">
          <li>
            <i className="motif-bloque" aria-hidden="true" />
            Bloqués : aucune activité depuis plus de {seuil} jours
          </li>
          <li>
            <i className="statut--en-cours" aria-hidden="true" />
            Récents
          </li>
        </ul>
      )}
    </article>
  );
}

/**
 * Bloc « Où s'arrêtent les paquets » : pour chaque paquet sans NIU, l'étape du traitement où il s'est arrêté
 * (rejetés, échoués : GET /enrolement/etapes) ou où il attend (en cours, dont bloqués : GET /enrolement/en-cours),
 * dans l'ordre du traitement. National. Les barres sont la part de la colonne ; les nombres sont écrits à côté.
 */
export function BlocArrets() {
  const { plage, prete } = usePlageApi('enrolement');
  const etapes = useEtapes(plage, prete);
  const enCours = useEnCours();
  const { sansNiu, colonnes } = colonnesArrets(etapes.data, enCours.data);
  const seuil = enCours.data?.seuilJours ?? SEUIL_JOURS;

  return (
    <section className="panneau bloc-pleine-largeur bloc-arrets" aria-labelledby="titre-arrets">
      <div className="bloc__entete">
        <div>
          <div className="bloc__titre">
            <h2 id="titre-arrets" className="titre-bloc">
              Où s’arrêtent les paquets
            </h2>
            <span className="pastille-portee">{etapes.data?.perimetre ?? 'Ensemble du Togo'}</span>
          </div>
          <p className="texte-2 bloc__sous-titre">
            <strong className="chiffre">{nf(sansNiu)}</strong> paquets n’ont pas de NIU. Pour chacun, l’étape
            du traitement où il s’est arrêté, dans l’ordre du traitement.
          </p>
        </div>
      </div>
      {(etapes.isPending || enCours.isPending) && (
        <p className="texte-2 etat-chargement">Chargement des chiffres…</p>
      )}
      <div className="arrets">
        {colonnes.map((c) => (
          <Colonne key={c.cle} colonne={c} seuil={seuil} />
        ))}
      </div>
    </section>
  );
}
