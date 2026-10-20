"""Tests du job des pré-inscriptions : deux tables MOSIP, priorité de la table _consumed, idempotence, recalcul."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import psycopg
from pyspark.sql import Row

from streaming.enrolement import job as socle
from streaming.preinscription import job

CLE = b"cle-de-test"
TOPIC_DEMANDE = "mosip.test.prereg.applicant_demographic"
TOPIC_CONSOMMEE = "mosip.test.prereg.applicant_demographic_consumed"
JOUR = date(2026, 1, 10)
JOUR_2 = date(2026, 1, 11)


def micro(jour: date, heure: int = 9) -> int:
    return int(datetime(jour.year, jour.month, jour.day, heure, 0, tzinfo=timezone.utc).timestamp() * 1_000_000)


def evenement(prereg: str, op: str, lsn: int, statut: str = "Booked", jour: date = JOUR, heure: int = 9) -> dict:
    apres = {"prereg_id": prereg, "status_code": statut, "cr_dtimes": micro(jour, heure), "upd_dtimes": None}
    return {
        "before": {"prereg_id": prereg} if op in ("u", "d") else None,
        "after": None if op == "d" else apres,
        "source": {"lsn": lsn, "txId": lsn, "ts_ms": 1_792_400_000_000 + lsn, "snapshot": "false"},
        "op": op,
        "ts_ms": 1_792_400_000_000 + lsn,
    }


def message(topic: str, prereg: str | None, valeur, offset: int) -> Row:
    cle = None if prereg is None else json.dumps({"prereg_id": prereg}).encode()
    corps = None if valeur is None else json.dumps(valeur).encode()
    return Row(topic=topic, partition=0, offset=offset, key=cle, value=corps)


def config(**autres) -> socle.Config:
    valeurs = {
        "topics": f"{TOPIC_DEMANDE},{TOPIC_CONSOMMEE}",
        "checkpoint": "",
        "requete": "etat_prereg@g1",
        "dsn_datamart": "",
        "cle_hmac": CLE,
    }
    return socle.Config(**{**valeurs, **autres})


def lancer(spark, dsn: str, messages: list[Row], lot_id: int, cfg: socle.Config | None = None) -> None:
    lot = spark.createDataFrame(messages, socle.MESSAGE_KAFKA)
    job.traiter_lot(cfg or config(), lambda: psycopg.connect(dsn, autocommit=False))(lot, lot_id)


def faits(dsn: str) -> list[tuple]:
    with psycopg.connect(dsn) as c:
        return c.execute(
            "select jour, statut, demandes, consommees from bi.fait_preinscription_jour order by jour, statut"
        ).fetchall()


def valeur(dsn: str, sql: str):
    with psycopg.connect(dsn) as c:
        return c.execute(sql).fetchone()[0]


def lot_initial() -> list[Row]:
    return [
        message(TOPIC_DEMANDE, "P1", evenement("P1", "c", 100, "Booked"), 0),
        message(TOPIC_DEMANDE, "P2", evenement("P2", "c", 101, "Pending_Appointment"), 1),
        message(TOPIC_DEMANDE, "P3", evenement("P3", "c", 102, "Statut_inconnu", JOUR_2), 2),
        message(TOPIC_DEMANDE, "P4", evenement("P4", "c", 103, "Booked", JOUR_2, heure=11), 3),
    ]


def test_table_source_d_apres_le_topic():
    assert job.table_source(TOPIC_DEMANDE) == "demande"
    assert job.table_source(TOPIC_CONSOMMEE) == "consommee"
    assert job.table_source("mosip.test.prereg.reg_appointment") is None


def test_un_topic_inconnu_est_rejete(spark):
    lot = spark.createDataFrame(
        [message("mosip.test.prereg.reg_appointment", "P1", evenement("P1", "c", 10), 0)], socle.MESSAGE_KAFKA
    )
    (ligne,) = job.decoder(lot).collect()
    assert (ligne["action"], ligne["motif"]) == ("rejet", "topic_inconnu")


def test_lot_complet_par_statut_sans_prereg_id(spark, base):
    lancer(spark, base, lot_initial(), 0)

    assert faits(base) == [
        (JOUR, "en_attente", 1, 0),
        (JOUR, "reservee", 1, 0),
        (JOUR_2, "non_classe", 1, 0),
        (JOUR_2, "reservee", 1, 0),
    ]
    with psycopg.connect(base) as c:
        lignes = c.execute("select * from etat.preinscription").fetchall()
    assert len(lignes) == 4
    assert not any(p in str(ligne) for ligne in lignes for p in ("P1", "P2", "P3", "P4"))
    # « Dernière demande » : création la plus récente reçue (11h00 le 11/01) gardée si plus récente que l'existant.
    assert valeur(base, "select derniere_donnee from bi.source_fraicheur where source = 'preinscription'") == datetime(
        2026, 1, 14, 11, 28, tzinfo=timezone.utc
    )
    with psycopg.connect(base) as c:
        controles = {ligne[0]: ligne[1] for ligne in c.execute("select * from pipeline.controler_preinscription()")}
    assert controles == {"preinscription_etat_egal_faits": "ok", "preinscription_non_classees": "alerte"}


def test_une_demande_consommee_compte_une_fois_et_est_honoree(spark, base):
    lancer(spark, base, lot_initial(), 0)
    # MOSIP copie la demande dans _consumed puis la retire de la table active.
    lancer(
        spark,
        base,
        [
            message(TOPIC_CONSOMMEE, "P1", evenement("P1", "c", 200, "Booked"), 4),
            message(TOPIC_DEMANDE, "P1", evenement("P1", "d", 201), 5),
            message(TOPIC_DEMANDE, "P1", None, 6),
        ],
        1,
    )
    assert faits(base)[:2] == [(JOUR, "en_attente", 1, 0), (JOUR, "reservee", 1, 1)]
    # Ordre inverse (suppression avant la copie) : même résultat, la demande ne disparaît pas.
    lancer(
        spark,
        base,
        [
            message(TOPIC_DEMANDE, "P2", evenement("P2", "d", 300), 7),
            message(TOPIC_CONSOMMEE, "P2", evenement("P2", "c", 301, "Pending_Appointment"), 8),
        ],
        2,
    )
    assert faits(base)[:2] == [(JOUR, "en_attente", 1, 1), (JOUR, "reservee", 1, 1)]


def test_lot_rejoue_et_ancien_evenement_sans_effet(spark, base):
    lancer(spark, base, lot_initial(), 0)
    avant = faits(base)
    lancer(spark, base, lot_initial(), 0)
    lancer(spark, base, [message(TOPIC_DEMANDE, "P2", evenement("P2", "u", 50, "Booked"), 9)], 1)  # LSN ancien
    assert faits(base) == avant
    # Nouvelle génération de checkpoint : relecture complète sans double comptage.
    lancer(spark, base, lot_initial(), 0, config(requete="etat_prereg@g2"))
    assert faits(base) == avant


def test_changement_de_statut_et_suppression(spark, base):
    lancer(spark, base, lot_initial(), 0)
    lancer(spark, base, [message(TOPIC_DEMANDE, "P2", evenement("P2", "u", 400, "Booked"), 10)], 1)
    assert faits(base)[:1] == [(JOUR, "reservee", 2, 0)]
    lancer(spark, base, [message(TOPIC_DEMANDE, "P2", evenement("P2", "d", 401), 11)], 2)
    assert faits(base)[:1] == [(JOUR, "reservee", 1, 0)]
    assert valeur(base, "select count(*) from etat.preinscription where _supprime") == 1
