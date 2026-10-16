"""Vérifie la chaîne temps réel de bout en bout et affiche un compte rendu (développement).

MOSIP simulée → slot logique → connecteur Debezium → job Spark → Data Mart → API.
Lecture seule partout, sauf l'appel à pipeline.controler_enrolement() qui consigne son résultat dans
pipeline.controle_qualite. Aucune donnée personnelle n'est affichée (comptes, états et horodatages seulement).

Usage (depuis la racine du dépôt) :
  docker compose -f deploy/docker-compose.yml run --rm outils python -m outils.verifier_temps_reel
Code de sortie 0 si tout est au vert, 1 sinon.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone

SLOT = os.environ.get("SLOT", "bi_cdc_regprc_dev")
CONNECTEUR = os.environ.get("CONNECTEUR", "bi-cdc-regprc-dev")


@dataclass
class Resultat:
    etape: str
    ok: bool
    detail: str
    alerte: bool = False


def lire_json(url: str):
    with urllib.request.urlopen(url, timeout=10) as reponse:
        return json.loads(reponse.read().decode("utf-8"))


def secondes(depuis: datetime | None) -> str:
    if depuis is None:
        return "jamais"
    if depuis.tzinfo is None:
        depuis = depuis.replace(tzinfo=timezone.utc)
    return f"il y a {(datetime.now(timezone.utc) - depuis).total_seconds():.0f} s"


def verifier() -> list[Resultat]:
    import psycopg

    resultats: list[Resultat] = []
    mosip_dsn, dm_dsn = os.environ["MOSIP_SIM_DSN"], os.environ["DATAMART_DSN"]
    connect, api = os.environ.get("CONNECT_URL", "http://connect:8083"), os.environ.get("API_URL", "http://api:8080")

    # 1. Source et slot
    nb_mosip = None
    try:
        with psycopg.connect(mosip_dsn) as c:
            nb_mosip, derniere = c.execute(
                "select count(*) filter (where not coalesce(is_deleted, false)),"
                " max(greatest(cr_dtimes, coalesce(upd_dtimes, cr_dtimes))) from regprc.registration"
            ).fetchone()
            resultats.append(
                Resultat(
                    "MOSIP simulée", nb_mosip > 0, f"{nb_mosip} inscriptions, dernier changement {secondes(derniere)}"
                )
            )
            slot = c.execute(
                "select active, wal_status, pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn))"
                " from pg_replication_slots where slot_name = %s",
                (SLOT,),
            ).fetchone()
            if slot is None:
                resultats.append(Resultat("Slot logique", False, f"{SLOT} absent (connecteur pas encore démarré ?)"))
            else:
                actif, statut_wal, retenu = slot
                resultats.append(
                    Resultat(
                        "Slot logique",
                        bool(actif) and statut_wal != "lost",
                        f"{SLOT} {'actif' if actif else 'INACTIF'}, wal_status={statut_wal}, WAL retenu {retenu}",
                    )
                )
    except Exception as erreur:  # noqa: BLE001 - compte rendu, pas de trace
        resultats.append(Resultat("MOSIP simulée", False, f"injoignable ({type(erreur).__name__})"))

    # 2. Connecteur
    try:
        etat = lire_json(f"{connect}/connectors/{CONNECTEUR}/status")
        taches = [t["state"] for t in etat.get("tasks", [])]
        ok = etat["connector"]["state"] == "RUNNING" and taches and all(t == "RUNNING" for t in taches)
        resultats.append(
            Resultat("Connecteur Debezium", ok, f"{CONNECTEUR} {etat['connector']['state']}, tâches {taches}")
        )
    except Exception as erreur:  # noqa: BLE001
        resultats.append(Resultat("Connecteur Debezium", False, f"statut illisible ({type(erreur).__name__})"))

    # 3. Job Spark et Data Mart
    nb_faits = None
    try:
        with psycopg.connect(dm_dsn) as c:
            nb_lots, dernier_lot, rejets = c.execute(
                "select count(*), max(traite_le), (select count(*) from pipeline.evenement_rejete)"
                " from pipeline.lot_traite"
            ).fetchone()
            resultats.append(
                Resultat("Job Spark", nb_lots > 0, f"{nb_lots} lots appliqués, dernier {secondes(dernier_lot)}")
            )
            resultats.append(Resultat("Événements rejetés", rejets == 0, f"{rejets}", alerte=rejets > 0))
            nb_etat, source_ts = c.execute(
                "select count(*) filter (where not _supprime and not coalesce(is_deleted, false)), max(_source_ts)"
                " from etat.registration"
            ).fetchone()
            if nb_mosip is not None:
                ecart = nb_mosip - nb_etat
                resultats.append(
                    Resultat(
                        "État courant",
                        ecart == 0,
                        f"{nb_etat} inscriptions (écart avec MOSIP : {ecart}),"
                        f" dernier changement reçu {secondes(source_ts)}",
                        alerte=0 < ecart <= 10,
                    )
                )
            for controle, statut, valeur, detail in c.execute("select * from pipeline.controler_enrolement()"):
                resultats.append(
                    Resultat(
                        f"Contrôle {controle}",
                        statut != "echec",
                        f"{statut} : {detail} (valeur {valeur})",
                        alerte=statut == "alerte",
                    )
                )
            c.commit()
            nb_faits = c.execute("select coalesce(sum(inscriptions), 0) from bi.fait_enrolement_jour").fetchone()[0]
            fraicheur = c.execute(
                "select derniere_donnee, dernier_chargement from bi.source_fraicheur where source = 'enrolement'"
            ).fetchone()
            resultats.append(
                Resultat(
                    "Fraîcheur",
                    fraicheur is not None and fraicheur[1] is not None,
                    f"dernière donnée {secondes(fraicheur[0])}, dernier chargement {secondes(fraicheur[1])}"
                    if fraicheur
                    else "ligne enrolement absente",
                )
            )
    except Exception as erreur:  # noqa: BLE001
        resultats.append(Resultat("Data Mart", False, f"injoignable ou migrations absentes ({type(erreur).__name__})"))

    # 4. API
    try:
        devenir = lire_json(f"{api}/api/v1/enrolement/devenir")
        ok = nb_faits is None or devenir["inscriptions"] == nb_faits
        resultats.append(
            Resultat(
                "API /enrolement/devenir",
                ok,
                f"{devenir['inscriptions']} inscriptions, {devenir['niuGeneres']} NIU générés (faits : {nb_faits})",
            )
        )
    except Exception as erreur:  # noqa: BLE001
        resultats.append(Resultat("API /enrolement/devenir", False, f"injoignable ({type(erreur).__name__})"))
    return resultats


def main() -> int:
    resultats = verifier()
    largeur = max(len(r.etape) for r in resultats)
    for r in resultats:
        marque = "ALERTE" if r.ok and r.alerte else ("OK" if r.ok else "ÉCHEC")
        print(f"{marque:<7} {r.etape:<{largeur}}  {r.detail}")
    echecs = [r for r in resultats if not r.ok]
    print(f"\n{'Chaîne temps réel opérationnelle.' if not echecs else f'{len(echecs)} étape(s) en échec.'}")
    return 0 if not echecs else 1


if __name__ == "__main__":
    sys.exit(main())
