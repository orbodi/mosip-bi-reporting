"""Simulateur d'activité MOSIP pour le développement : écrit dans la base MOSIP SIMULÉE (deploy/mosip-sim).

Il joue le rôle de MOSIP (pas du BI) : il crée des inscriptions dans regprc.registration puis les fait avancer,
ce qui produit des événements CDC réalistes pour Debezium. Aucune donnée réelle ni personnelle : RID fictifs au
format MOSIP (centre 5 chiffres, machine 5, compteur 5, horodatage aaaammjjhhmmss), aucune autre identité.

Codes repris des énumérations MOSIP v1.1.5 (dépôt mosip/registration) :
- RegistrationStatusCode : PROCESSING, PROCESSED, REJECTED, FAILED, REPROCESS_FAILED ;
- RegistrationType : NEW, UPDATE, LOST, RES_UPDATE ;
- RegistrationTransactionTypeCode / RegistrationTransactionStatusCode pour latest_trn_*.
Les combinaisons et les proportions sont inventées pour la démonstration.

Lancement : python -m simulateur.simulateur [--tours N]   (configuration par variables d'environnement)
"""

from __future__ import annotations

import argparse
import logging
import os
import random
import signal
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

LOG = logging.getLogger("simulateur_mosip")

# Issue d'une inscription en cours : statut final, dernière transaction (type, statut), poids.
ISSUES = [
    ("PROCESSED", "UIN_GENERATOR", "PROCESSED", 930),
    ("REJECTED", "MANUAL_VERIFICATION", "REJECTED", 26),
    ("FAILED", "BIOGRAPHIC_VERIFICATION", "FAILED", 3),
    ("REPROCESS_FAILED", "PACKET_REPROCESS", "REPROCESS_FAILED", 1),
]
TYPES = [("NEW", 990), ("UPDATE", 7), ("LOST", 2), ("RES_UPDATE", 1)]
ETAPES_EN_COURS = [("VALIDATE_PACKET", "IN_PROGRESS"), ("BIOGRAPHIC_VERIFICATION", "IN_PROGRESS")]

INSERTION = """
insert into regprc.registration (
    id, reg_type, status_code, lang_code, latest_trn_type_code, latest_trn_status_code, latest_trn_dtimes,
    pkt_cr_dtimes, is_active, cr_by, cr_dtimes, upd_by, upd_dtimes, is_deleted)
values (%(id)s, %(reg_type)s, %(status_code)s, 'fra', %(trn_type)s, %(trn_statut)s, %(trn_dtimes)s,
        %(pkt_cr_dtimes)s, true, 'simulateur-bi', %(cr_dtimes)s, %(upd_by)s, %(upd_dtimes)s, false)
on conflict (id) do nothing
"""

AVANCEMENT = """
update regprc.registration
set status_code = %(status_code)s, latest_trn_type_code = %(trn_type)s, latest_trn_status_code = %(trn_statut)s,
    latest_trn_dtimes = %(maintenant)s, upd_by = 'simulateur-bi', upd_dtimes = %(maintenant)s
where id = %(id)s and status_code = 'PROCESSING'
"""


@dataclass(frozen=True)
class Reglages:
    dsn: str
    centres: tuple[str, ...]
    initiales: int = 2_000
    jours_historique: int = 60
    intervalle_s: float = 5.0
    nouvelles_min: int = 1
    nouvelles_max: int = 4
    delai_traitement_s: int = 20
    part_centre_inconnu: float = 0.01
    graine: int | None = None

    @staticmethod
    def depuis_env() -> "Reglages":
        dsn = os.environ.get("MOSIP_SIM_DSN")
        if not dsn:
            raise RuntimeError("Variable d'environnement manquante : MOSIP_SIM_DSN")
        centres = tuple(c.strip() for c in os.environ.get("CENTRES", "10011,10012").split(",") if c.strip())
        mini, _, maxi = os.environ.get("NOUVELLES_PAR_TOUR", "1-4").partition("-")
        graine = os.environ.get("GRAINE")
        return Reglages(
            dsn=dsn,
            centres=centres,
            initiales=int(os.environ.get("INSCRIPTIONS_INITIALES", "2000")),
            jours_historique=int(os.environ.get("JOURS_HISTORIQUE", "60")),
            intervalle_s=float(os.environ.get("INTERVALLE_S", "5")),
            nouvelles_min=int(mini),
            nouvelles_max=int(maxi or mini),
            delai_traitement_s=int(os.environ.get("DELAI_TRAITEMENT_S", "20")),
            part_centre_inconnu=float(os.environ.get("PART_CENTRE_INCONNU", "0.01")),
            graine=int(graine) if graine else None,
        )


def maintenant() -> datetime:
    """Horodatage UTC sans fuseau, comme les colonnes timestamp de MOSIP."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def tirer(hasard: random.Random, choix: list[tuple]) -> tuple:
    return hasard.choices(choix, weights=[c[-1] for c in choix], k=1)[0]


def nouveau_rid(hasard: random.Random, reglages: Reglages, quand: datetime) -> str:
    if hasard.random() < reglages.part_centre_inconnu:
        centre = "99999"  # centre absent du référentiel : doit apparaître en « Centre non référencé »
    else:
        centre = hasard.choice(reglages.centres)
    machine = f"{hasard.randint(1, 30):05d}"
    compteur = f"{hasard.randint(0, 99_999):05d}"
    return f"{centre}{machine}{compteur}{quand:%Y%m%d%H%M%S}"


def ligne(hasard: random.Random, reglages: Reglages, cree: datetime, issue: tuple | None) -> dict:
    reg_type = tirer(hasard, TYPES)[0]
    pkt = cree - timedelta(minutes=hasard.randint(5, 240))
    if issue is None:
        trn_type, trn_statut = hasard.choice(ETAPES_EN_COURS)
        statut, maj, trn_dtimes = "PROCESSING", None, cree
    else:
        statut, trn_type, trn_statut, _ = issue
        maj = cree + timedelta(days=hasard.randint(0, 9), minutes=hasard.randint(1, 600))
        maj = min(maj, maintenant())
        trn_dtimes = maj
    return {
        "id": nouveau_rid(hasard, reglages, cree),
        "reg_type": reg_type,
        "status_code": statut,
        "trn_type": trn_type,
        "trn_statut": trn_statut,
        "trn_dtimes": trn_dtimes,
        "pkt_cr_dtimes": pkt,
        "cr_dtimes": cree,
        "upd_by": "simulateur-bi" if maj else None,
        "upd_dtimes": maj,
    }


def historique(connexion, hasard: random.Random, reglages: Reglages) -> int:
    """Remplit la table si elle est vide : inscriptions des derniers jours, presque toutes traitées."""
    with connexion.cursor() as cur:
        cur.execute("select exists (select 1 from regprc.registration)")
        if cur.fetchone()[0]:
            return 0
        fin = maintenant()
        lignes = []
        for _ in range(reglages.initiales):
            cree = fin - timedelta(seconds=hasard.randint(60, reglages.jours_historique * 86_400))
            recente = (fin - cree) < timedelta(days=3)
            issue = None if (recente and hasard.random() < 0.4) or hasard.random() < 0.02 else tirer(hasard, ISSUES)
            lignes.append(ligne(hasard, reglages, cree, issue))
        cur.executemany(INSERTION, lignes)
    connexion.commit()
    return len(lignes)


def tour(connexion, hasard: random.Random, reglages: Reglages) -> tuple[int, int]:
    """Un pas de simulation : nouvelles inscriptions, puis avancement d'inscriptions en cours."""
    instant = maintenant()
    nouvelles = [
        ligne(hasard, reglages, instant, None)
        for _ in range(hasard.randint(reglages.nouvelles_min, reglages.nouvelles_max))
    ]
    with connexion.cursor() as cur:
        cur.executemany(INSERTION, nouvelles)
        cur.execute(
            "select id from regprc.registration where status_code = 'PROCESSING' and cr_dtimes < %s"
            " order by cr_dtimes limit %s for update skip locked",
            (instant - timedelta(seconds=reglages.delai_traitement_s), len(nouvelles) + 1),
        )
        a_avancer = [r[0] for r in cur.fetchall()]
        avancees = 0
        for rid in a_avancer:
            if hasard.random() < 0.2:
                continue  # reste en cours plus longtemps
            statut, trn_type, trn_statut, _ = tirer(hasard, ISSUES)
            cur.execute(
                AVANCEMENT,
                {
                    "id": rid,
                    "status_code": statut,
                    "trn_type": trn_type,
                    "trn_statut": trn_statut,
                    "maintenant": instant,
                },
            )
            avancees += cur.rowcount
    connexion.commit()
    return len(nouvelles), avancees


def main(argv: list[str] | None = None) -> None:
    import psycopg

    parseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parseur.add_argument("--tours", type=int, default=0, help="nombre de pas puis arrêt (0 = sans fin)")
    args = parseur.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    reglages = Reglages.depuis_env()
    hasard = random.Random(reglages.graine)

    arret = {"demande": False}
    signal.signal(signal.SIGTERM, lambda *_: arret.update(demande=True))

    connexion = None
    for _ in range(60):  # la base simulée peut démarrer après le simulateur
        try:
            connexion = psycopg.connect(reglages.dsn)
            break
        except psycopg.OperationalError:
            LOG.info("En attente de la base MOSIP simulée…")
            time.sleep(2)
    if connexion is None:
        raise RuntimeError("Base MOSIP simulée injoignable")

    with connexion:
        creees = historique(connexion, hasard, reglages)
        if creees:
            LOG.info("Historique créé : %s inscriptions fictives", creees)
        n = 0
        while not arret["demande"] and (args.tours == 0 or n < args.tours):
            nouvelles, avancees = tour(connexion, hasard, reglages)
            n += 1
            LOG.info("Tour %s : nouvelles inscriptions %s, traitements terminés %s", n, nouvelles, avancees)
            if args.tours == 0 or n < args.tours:
                time.sleep(reglages.intervalle_s)


if __name__ == "__main__":
    main()
