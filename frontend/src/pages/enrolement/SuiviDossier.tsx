import { useState, type FormEvent } from 'react';
import {
  Button,
  Dialog,
  DialogTrigger,
  Heading,
  Input,
  Label,
  Modal,
  ModalOverlay,
  Text,
  TextField,
} from 'react-aria-components';
import type { SuiviDossier } from '../../api/client';
import { useSuiviDossier } from '../../api/enrolement';
import { miseAJourFr } from '../../lib/format';
import {
  MESSAGE_FORMAT,
  etatDossier,
  jalonsDossier,
  messageErreur,
  nettoyerRid,
  ridValide,
  statutEtape,
  typeDemande,
} from '../../lib/suivi';
import './suivi.css';

const Loupe = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    aria-hidden="true"
  >
    <circle cx="11" cy="11" r="7" />
    <path d="m20 20-3.5-3.5" />
  </svg>
);

/** Résultat d'une recherche : état, centre, étape et motif de MOSIP, jalons datés. Jamais le RID. */
function Resultat({ dossier, nouvelle }: { dossier: SuiviDossier; nouvelle: () => void }) {
  const etat = etatDossier(dossier);
  const lieu = [dossier.centre.prefecture, dossier.centre.region].filter(Boolean).join(', ');
  const detailEtape = dossier.motif?.libelle ?? statutEtape(dossier.etape?.statut);
  return (
    <div className="suivi__resultat">
      <div className="suivi__haut">
        <span className={`suivi__etat suivi__etat--${etat.ton}`}>
          <i aria-hidden="true" />
          {etat.libelle}
        </span>
        <span className="texte-2">{typeDemande(dossier.typeDemande)}</span>
      </div>
      <dl className="suivi__infos">
        <div>
          <dt>Centre</dt>
          <dd>
            <strong>{dossier.centre.nom}</strong>
            {lieu && <span>{lieu}</span>}
          </dd>
        </div>
        {dossier.etape && (
          <div>
            <dt>{dossier.devenir === 'niu' ? 'Dernière étape' : 'Arrêté à l’étape'}</dt>
            <dd>
              <strong>{dossier.etape.libelle}</strong>
              {detailEtape && <span>{detailEtape}</span>}
            </dd>
          </div>
        )}
      </dl>
      {dossier.motif?.commentaire && (
        <p className="suivi__message">
          Message de MOSIP :{' '}
          <span lang="en" className="suivi__message-texte">
            {dossier.motif.commentaire}
          </span>
        </p>
      )}
      <ol className="suivi__jalons" aria-label="Jalons du dossier">
        {jalonsDossier(dossier).map((j) => (
          <li key={j.cle} className={`jalon jalon--${j.etat}`}>
            <span className="jalon__point" aria-hidden="true" />
            <span className="jalon__libelle">
              {j.libelle}
              {j.etat === 'actuel' && <span className="visuellement-cache"> (étape actuelle)</span>}
              {j.etat === 'a-venir' && <span className="visuellement-cache"> (à venir)</span>}
            </span>
            <span className="jalon__quand">{j.quand}</span>
          </li>
        ))}
      </ol>
      <div className="suivi__pied">
        <span className="texte-2">Informations du {miseAJourFr(dossier.majLe)}</span>
        <Button className="suivi__bouton suivi__bouton--clair" onPress={nouvelle}>
          Nouvelle recherche
        </Button>
      </div>
    </div>
  );
}

/** Contenu de la fenêtre : saisie du RID (vidé dès la recherche lancée), puis le résultat ou l'erreur. */
function FenetreSuivi({ fermer }: { fermer: () => void }) {
  const suivi = useSuiviDossier();
  const [rid, setRid] = useState('');
  const [formatInvalide, setFormatInvalide] = useState(false);

  const rechercher = (e: FormEvent) => {
    e.preventDefault();
    if (!ridValide(rid)) {
      setFormatInvalide(true);
      return;
    }
    setFormatInvalide(false);
    suivi.mutate(rid);
    // Le RID ne reste pas à l'écran : le champ est vidé dès l'envoi.
    setRid('');
  };

  const erreur = formatInvalide ? MESSAGE_FORMAT : suivi.isError ? messageErreur(suivi.error) : null;

  return (
    <>
      <div className="suivi__entete">
        <Heading slot="title" className="suivi__titre">
          Suivre un dossier
        </Heading>
        <Button
          className="suivi__fermer"
          aria-label="Fermer"
          onPress={() => {
            suivi.reset();
            fermer();
          }}
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            aria-hidden="true"
          >
            <path d="M6 6l12 12M18 6 6 18" />
          </svg>
        </Button>
      </div>
      <div className="suivi__corps">
        {suivi.data ? (
          <Resultat dossier={suivi.data} nouvelle={() => suivi.reset()} />
        ) : (
          <form onSubmit={rechercher} noValidate>
            <TextField
              className="suivi__saisie"
              value={rid}
              onChange={(v) => {
                setRid(nettoyerRid(v));
                setFormatInvalide(false);
              }}
              autoFocus
            >
              <Label className="suivi__label">Numéro d’inscription (RID)</Label>
              <div className="suivi__champ">
                <Input inputMode="numeric" autoComplete="off" spellCheck={false} placeholder="29 chiffres" />
                <Button type="submit" className="suivi__bouton" isDisabled={suivi.isPending}>
                  {suivi.isPending ? 'Recherche…' : 'Rechercher'}
                </Button>
              </div>
              <Text slot="description" className="texte-2 suivi__aide">
                Le RID n’est ni conservé ni réaffiché après la recherche.
              </Text>
            </TextField>
            {erreur && (
              <p className="suivi__erreur" role="alert">
                {erreur}
              </p>
            )}
          </form>
        )}
      </div>
    </>
  );
}

/**
 * Bouton « Suivre un dossier » du bandeau de la page Enrôlement et sa fenêtre (lot 5b-2, décision du 29/10/2026) :
 * recherche exacte d'un dossier par son RID (POST /enrolement/suivi, le RID dans le corps). Le RID est vidé dès la
 * recherche lancée et n'est jamais réaffiché ; la recherche est journalisée côté API, sans le RID. Fenêtre modale
 * React Aria : focus gardé dedans, Échap ou la croix pour fermer ; à la fermeture, rien n'est gardé.
 */
export function SuiviDossierBouton() {
  return (
    <DialogTrigger>
      <Button className="bouton-suivi">
        <Loupe />
        Suivre un dossier
      </Button>
      <ModalOverlay className="suivi__voile" isDismissable>
        <Modal className="suivi__fenetre">
          <Dialog className="suivi__dialogue">{({ close }) => <FenetreSuivi fermer={close} />}</Dialog>
        </Modal>
      </ModalOverlay>
    </DialogTrigger>
  );
}
