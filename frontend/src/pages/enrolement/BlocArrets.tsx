import { useState } from 'react';
import { Tab, TabList, TabPanel, Tabs } from 'react-aria-components';
import { useMotifs } from '../../api/enrolement';
import { IconeStatut } from '../../composants/blocs/Icone';
import { nf, pct } from '../../lib/format';
import {
  colonnesArrets,
  largeurBarre,
  type CleArret,
  type ColonneArret,
  type LigneArret,
} from '../../lib/traitement';
import { usePlageApi } from '../../lib/usePlagePeriode';
import './enrolement.css';

/** Seuil des paquets bloqués quand l'API ne l'a pas encore donné (MotifsArret.seuilJours). */
const SEUIL_JOURS = 30;

/** Barre de la part du motif dans l'onglet ; en cours : bloqués (rayures) puis récents. */
function Barre({ ligne, colonne }: { ligne: LigneArret; colonne: ColonneArret }) {
  const enCours = colonne.cle === 'en-cours';
  const teinte = ligne.autres ? 'motif-arret__barre--autres' : `statut--${colonne.cle}`;
  return (
    <span className="motif-arret__piste" aria-hidden="true">
      {enCours && ligne.bloques > 0 && (
        <span className="motif-bloque" style={{ width: `${largeurBarre(ligne.bloques, colonne.total)}%` }} />
      )}
      <span
        className={teinte}
        style={{
          width: `${largeurBarre(enCours ? ligne.valeur - ligne.bloques : ligne.valeur, colonne.total)}%`,
        }}
      />
    </span>
  );
}

/** Motifs d'un onglet : nom, paquets, part, barre, étape · message de MOSIP ; en cours, bloqués et récents. */
function Motifs({ colonne, seuil }: { colonne: ColonneArret; seuil: number }) {
  const enCours = colonne.cle === 'en-cours';
  return (
    <>
      {enCours && (
        <p className="arrets__bloques">
          <i className="motif-bloque" aria-hidden="true" />
          <span>
            <strong className="chiffre">{nf(colonne.bloques)}</strong> sans activité depuis plus de {seuil}{' '}
            jours
          </span>
        </p>
      )}
      <div className="motif-arret motif-arret--entete" aria-hidden="true">
        <span>Motif</span>
        <span className="motif-arret__valeur">Paquets</span>
        <span className="motif-arret__part">Part</span>
      </div>
      <ul className="arrets__motifs" aria-label={`${colonne.titre} par motif`}>
        {colonne.lignes.map((l) => (
          <li key={l.cle} className={`motif-arret${l.autres ? ' motif-arret--autres' : ''}`}>
            <span className="motif-arret__nom">{l.libelle}</span>
            <span className="motif-arret__valeur chiffre">{nf(l.valeur)}</span>
            <span className="motif-arret__part chiffre">{pct(l.part)}</span>
            <Barre ligne={l} colonne={colonne} />
            <p className="motif-arret__source">
              {l.etape}
              {l.etape && l.commentaire && ' · '}
              {l.commentaire && (
                <span className="motif-arret__commentaire" lang="en">
                  {l.commentaire}
                </span>
              )}
            </p>
            {enCours && (
              <p className="motif-arret__detail">
                {l.bloques > 0 && (
                  <>
                    <strong className="chiffre">{nf(l.bloques)}</strong> sans activité depuis {seuil} jours
                    ·{' '}
                  </>
                )}
                <span className="chiffre">{nf(l.valeur - l.bloques)}</span> récents
              </p>
            )}
          </li>
        ))}
      </ul>
    </>
  );
}

/**
 * Bloc « Où s'arrêtent les paquets » (décisions des 26 et 28/10/2026) : trois onglets (rejetés, échoués, en cours),
 * chacun avec son icône, son nombre et, dessous, ses motifs donnés par MOSIP (status_comment traduit fidèlement par le
 * catalogue des motifs), du plus fréquent au moins fréquent, avec leur étape principale et le message de MOSIP
 * (GET /enrolement/motifs). National. Onglets React Aria comme le « Top des centres » : flèches du clavier, Rejetés à
 * l'ouverture, rien dans l'adresse.
 */
export function BlocArrets() {
  const { plage, prete } = usePlageApi('enrolement');
  const { data, isPending } = useMotifs(plage, prete);
  const { sansNiu, colonnes } = colonnesArrets(data);
  const seuil = data?.seuilJours ?? SEUIL_JOURS;
  const [onglet, setOnglet] = useState<CleArret>('rejete');

  return (
    <section className="panneau bloc-pleine-largeur bloc-arrets" aria-labelledby="titre-arrets">
      <div className="bloc__entete">
        <div>
          <div className="bloc__titre">
            <h2 id="titre-arrets" className="titre-bloc">
              Où s’arrêtent les paquets
            </h2>
            <span className="pastille-portee">{data?.perimetre ?? 'Ensemble du Togo'}</span>
          </div>
          <p className="texte-2 bloc__sous-titre">
            <strong className="chiffre">{nf(sansNiu)}</strong> paquets n’ont pas encore abouti à un NIU.
          </p>
        </div>
      </div>
      {isPending && <p className="texte-2 etat-chargement">Chargement des chiffres…</p>}
      <Tabs selectedKey={onglet} onSelectionChange={(cle) => setOnglet(cle as CleArret)}>
        <TabList aria-label="Devenir des paquets sans NIU" className="arrets__onglets">
          {colonnes.map((c) => (
            <Tab key={c.cle} id={c.cle} className={`arrets__onglet arrets__onglet--${c.cle}`}>
              <span className="arrets__tuile">
                <IconeStatut statut={c.cle} />
              </span>
              <span className="arrets__texte">
                <span className="arrets__titre">{c.titre}</span>
                <span className="arrets__nombre chiffre">{nf(c.total)}</span>
              </span>
            </Tab>
          ))}
        </TabList>
        {colonnes.map((c) => (
          <TabPanel key={c.cle} id={c.cle} className="arrets__panneau">
            <Motifs colonne={c} seuil={seuil} />
          </TabPanel>
        ))}
      </Tabs>
    </section>
  );
}
