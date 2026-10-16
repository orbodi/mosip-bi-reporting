"""Tests du job temps réel de l'enrôlement : décodage, idempotence, recalcul des faits, reprise sur checkpoint."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import psycopg
import pytest
from pyspark.sql import Row

from streaming.enrolement import job

CLE = b"cle-de-test"
TOPIC = "mosip.test.regprc.registration"
JOUR = date(2026, 10, 15)
MICRO_JOUR = int(datetime(2026, 10, 15, 9, 0).replace(tzinfo=timezone.utc).timestamp() * 1_000_000)

RID_A = "10011000010000120261015090000"  # centre 10011 (Savanes 1)
RID_B = "10011000010000220261015090100"
RID_C = "10021000020000320261015090200"  # centre 10021 (Kara 1)
RID_X = "99999000010000420261015090300"  # centre absent du référentiel


def apres(rid: str, statut: str, reg_type: str = "NEW", cr: int = MICRO_JOUR) -> dict:
    return {
        "id": rid, "reg_type": reg_type, "status_code": statut, "latest_trn_type_code": "PACKET_RECEIVER",
        "latest_trn_status_code": "SUCCESS", "latest_trn_dtimes": cr, "reg_stage_name": None,
        "pkt_cr_dtimes": cr - 3_600_000_000, "is_active": True, "cr_dtimes": cr, "upd_dtimes": None,
        "is_deleted": False,
    }  # fmt: skip


def evenement(rid: str, op: str, lsn: int, statut: str = "PROCESSING", **kw) -> dict:
    """Message Debezium (JsonConverter sans schéma) pour regprc.registration."""
    return {
        "before": {"id": rid} if op in ("u", "d") else None,
        "after": None if op == "d" else apres(rid, statut, **kw),
        "source": {"lsn": lsn, "txId": lsn, "ts_ms": 1_792_400_000_000 + lsn, "snapshot": "false"},
        "op": op,
        "ts_ms": 1_792_400_000_000 + lsn,
    }


def message(rid: str | None, valeur, offset: int) -> Row:
    """Message Kafka : clé {"id": rid}, valeur JSON (ou None pour un tombstone, ou texte brut)."""
    cle = None if rid is None else json.dumps({"id": rid}).encode()
    if valeur is None:
        corps = None
    elif isinstance(valeur, str):
        corps = valeur.encode()
    else:
        corps = json.dumps(valeur).encode()
    return Row(topic=TOPIC, partition=0, offset=offset, key=cle, value=corps)


def config(**autres) -> job.Config:
    valeurs = {"topics": TOPIC, "checkpoint": "", "requete": "etat_regprc@g1", "dsn_datamart": "", "cle_hmac": CLE}
    return job.Config(**{**valeurs, **autres})


def lancer(spark, dsn: str, messages: list[Row], lot_id: int, cfg: job.Config | None = None) -> None:
    lot = spark.createDataFrame(messages, job.MESSAGE_KAFKA)
    job.traiter_lot(cfg or config(), lambda: psycopg.connect(dsn, autocommit=False))(lot, lot_id)


def faits(dsn: str) -> list[tuple]:
    with psycopg.connect(dsn) as c:
        return c.execute(
            "select f.jour, z.code, f.type_demande, f.inscriptions, f.niu_generes, f.en_cours, f.echouees,"
            " f.rejetees, f.non_classees from bi.fait_enrolement_jour f join bi.zone z on z.id = f.centre_id"
            " order by 2, 3"
        ).fetchall()


def valeur(dsn: str, sql: str):
    with psycopg.connect(dsn) as c:
        return c.execute(sql).fetchone()[0]


# --------------------------------------------------------------------------------------------------------------
# Décodage (sans base)
# --------------------------------------------------------------------------------------------------------------
def test_decodage_classe_chaque_evenement(spark):
    lot = spark.createDataFrame(
        [
            message(RID_A, evenement(RID_A, "c", 10), 0),
            message(RID_A, evenement(RID_A, "r", 11), 1),
            message(RID_A, evenement(RID_A, "u", 12), 2),
            message(RID_A, evenement(RID_A, "d", 13), 3),
            message(RID_A, None, 4),
            message(None, {"op": "t", "source": {"lsn": 14}}, 5),
            message(None, {"op": "m", "source": {"lsn": 15}}, 6),
            message(RID_A, "ceci n'est pas du JSON", 7),
            message(None, evenement(RID_A, "c", 16), 8),
            message(RID_A, {**evenement(RID_A, "c", 17), "source": {}}, 9),
        ],
        job.MESSAGE_KAFKA,
    )
    resultat = {
        r["offset"]: (r["action"], r["motif"])
        for r in job.decoder(lot, job.LIGNE_REGISTRATION, job.CLE_REGISTRATION).collect()
    }
    assert resultat == {
        0: ("upsert", None),
        1: ("upsert", None),
        2: ("upsert", None),
        3: ("suppression", None),
        4: ("tombstone", None),
        5: ("truncate", None),
        6: ("ignore", None),
        7: ("rejet", "json_illisible_ou_op_absent"),
        8: ("rejet", "cle_absente"),
        9: ("rejet", "lsn_absent"),
    }


def test_dernier_evenement_par_cle_selon_le_lsn(spark):
    lot = spark.createDataFrame(
        [
            message(RID_A, evenement(RID_A, "u", 30, "PROCESSED"), 2),
            message(RID_A, evenement(RID_A, "c", 20), 1),
            message(RID_B, evenement(RID_B, "c", 25), 3),
        ],
        job.MESSAGE_KAFKA,
    )
    derniers = job.dernier_par_cle(job.decoder(lot, job.LIGNE_REGISTRATION, job.CLE_REGISTRATION)).collect()
    assert sorted((r["cle_id"], r["lsn"]) for r in derniers) == [(RID_A, 30), (RID_B, 25)]


def test_derivations_du_rid():
    assert job.centre_depuis_rid(RID_A) == "10011"
    assert job.centre_depuis_rid("AB") is None
    assert job.empreinte(CLE, RID_A) != RID_A and len(job.empreinte(CLE, RID_A)) == 64
    assert job.empreinte(CLE, RID_A) != job.empreinte(b"autre-cle", RID_A)


# --------------------------------------------------------------------------------------------------------------
# Écriture dans le Data Mart (vraies migrations)
# --------------------------------------------------------------------------------------------------------------
def lot_initial() -> list[Row]:
    return [
        message(RID_A, evenement(RID_A, "c", 100, "PROCESSED"), 0),
        message(RID_B, evenement(RID_B, "c", 101, "PROCESSING"), 1),
        message(RID_C, evenement(RID_C, "c", 102, "REJECTED", reg_type="UPDATE"), 2),
        message(RID_X, evenement(RID_X, "c", 103, "CODE_INCONNU"), 3),
    ]


def test_lot_complet_alimente_les_faits_sans_rid(spark, base):
    lancer(spark, base, lot_initial(), 0)

    assert faits(base) == [
        (JOUR, "10011", "NEW", 2, 1, 1, 0, 0, 0),
        (JOUR, "10021", "UPDATE", 1, 0, 0, 0, 1, 0),
        (JOUR, "CENTRE_NON_REFERENCE", "NEW", 1, 0, 0, 0, 0, 1),
    ]
    # Le RID n'est écrit nulle part : ni en clé, ni dans une autre colonne.
    with psycopg.connect(base) as c:
        lignes = c.execute("select * from etat.registration").fetchall()
    assert len(lignes) == 4
    assert not any(rid in str(ligne) for ligne in lignes for rid in (RID_A, RID_B, RID_C, RID_X))
    # Registre, fraîcheur et contrôle qualité.
    assert valeur(base, "select nb_upserts from pipeline.lot_traite where lot_id = 0") == 4
    assert valeur(base, "select derniere_donnee > '2026-01-14' from bi.source_fraicheur where source = 'enrolement'")
    controles = {
        ligne[0]: ligne[1] for ligne in psycopg.connect(base).execute("select * from pipeline.controler_enrolement()")
    }
    assert controles == {"enrolement_etat_egal_faits": "ok", "enrolement_non_classees": "alerte"}


def test_lot_rejoue_sans_effet(spark, base):
    lancer(spark, base, lot_initial(), 0)
    avant = faits(base)
    lancer(spark, base, lot_initial(), 0)  # même lot_id : Spark rejoue après un arrêt brutal
    assert faits(base) == avant
    assert valeur(base, "select count(*) from pipeline.lot_traite") == 1


def test_nouvelle_generation_de_checkpoint_sans_double_comptage(spark, base):
    lancer(spark, base, lot_initial(), 0)
    avant = faits(base)
    # Checkpoint perdu : nouvelle génération qui relit tout le topic depuis le début, lot_id repart à 0.
    lancer(spark, base, lot_initial(), 0, config(requete="etat_regprc@g2"))
    assert faits(base) == avant
    assert valeur(base, "select count(*) from pipeline.lot_traite") == 2


def test_changement_de_statut_deplace_l_inscription(spark, base):
    lancer(spark, base, lot_initial(), 0)
    lancer(spark, base, [message(RID_B, evenement(RID_B, "u", 200, "PROCESSED"), 4)], 1)
    assert faits(base)[0] == (JOUR, "10011", "NEW", 2, 2, 0, 0, 0, 0)


def test_evenement_ancien_ignore_et_suppression_definitive(spark, base):
    lancer(spark, base, lot_initial(), 0)
    lancer(spark, base, [message(RID_A, evenement(RID_A, "u", 50, "REJECTED"), 4)], 1)  # LSN plus ancien
    assert faits(base)[0] == (JOUR, "10011", "NEW", 2, 1, 1, 0, 0, 0)

    lancer(spark, base, [message(RID_A, evenement(RID_A, "d", 300), 5), message(RID_A, None, 6)], 2)
    assert faits(base)[0] == (JOUR, "10011", "NEW", 1, 0, 1, 0, 0, 0)
    # Rejeu d'une ancienne création après la suppression : la garde LSN empêche la résurrection.
    lancer(spark, base, [message(RID_A, evenement(RID_A, "c", 100, "PROCESSED"), 0)], 3, config(requete="x@g9"))
    assert faits(base)[0] == (JOUR, "10011", "NEW", 1, 0, 1, 0, 0, 0)


def test_meme_cle_plusieurs_fois_dans_un_lot(spark, base):
    lancer(
        spark,
        base,
        [
            message(RID_A, evenement(RID_A, "c", 100, "PROCESSING"), 0),
            message(RID_A, evenement(RID_A, "u", 101, "PROCESSING"), 1),
            message(RID_A, evenement(RID_A, "u", 102, "PROCESSED"), 2),
        ],
        0,
    )
    assert faits(base) == [(JOUR, "10011", "NEW", 1, 1, 0, 0, 0, 0)]


def test_truncate_arrete_sans_rien_appliquer(spark, base):
    lancer(spark, base, lot_initial(), 0)
    avant = faits(base)
    with pytest.raises(job.ArretPipeline):
        lancer(
            spark,
            base,
            [message(None, {"op": "t", "source": {"lsn": 400}}, 7), message(RID_B, evenement(RID_B, "u", 401), 8)],
            1,
        )
    assert faits(base) == avant
    assert valeur(base, "select count(*) from pipeline.lot_traite") == 1


def test_rejets_consignes_sans_contenu_et_seuil(spark, base):
    lancer(spark, base, [message(RID_A, "{json tronqué " + RID_A, 9), *lot_initial()], 0)
    with psycopg.connect(base) as c:
        rejets = c.execute("select motif, empreinte, kafka_offset from pipeline.evenement_rejete").fetchall()
    assert rejets == [("json_illisible_ou_op_absent", rejets[0][1], 9)]
    assert RID_A not in str(rejets)

    trop = [message(RID_A, "x", 20), message(RID_A, "y", 21)]
    with pytest.raises(job.ArretPipeline):
        lancer(spark, base, trop, 1, config(seuil_rejets=1))


# --------------------------------------------------------------------------------------------------------------
# Streaming de bout en bout : arrêt, nouveaux messages, reprise sur le même checkpoint
# --------------------------------------------------------------------------------------------------------------
def test_streaming_reprend_sur_checkpoint_sans_double_comptage(spark, base, tmp_path):
    source, checkpoint = tmp_path / "messages", tmp_path / "checkpoint"
    source.mkdir()
    # Chaque dépôt de messages simulés est un sous-répertoire : le motif « * » les lit tous, une seule fois chacun.
    cfg = config(source="parquet", chemin_source=str(source / "*"), checkpoint=str(checkpoint), intervalle="1 second")

    def deposer(nom: str, messages: list[Row]) -> None:
        spark.createDataFrame(messages, job.MESSAGE_KAFKA).coalesce(1).write.parquet(str(source / nom))

    def connecter():
        return psycopg.connect(base, autocommit=False)

    deposer("lot1", lot_initial())
    requete = job.demarrer(cfg, connecter, spark)
    requete.processAllAvailable()
    requete.stop()
    assert sum(f[3] for f in faits(base)) == 4

    deposer("lot2", [message(RID_B, evenement(RID_B, "u", 200, "PROCESSED"), 4)])
    requete = job.demarrer(cfg, connecter, spark)  # même checkpoint : ne relit que lot2
    requete.processAllAvailable()
    requete.stop()

    assert faits(base)[0] == (JOUR, "10011", "NEW", 2, 2, 0, 0, 0, 0)
    assert valeur(base, "select count(*) from pipeline.lot_traite") == 2
    assert valeur(base, "select sum(nb_upserts) from pipeline.lot_traite") == 5

    # Checkpoint existant : démarrage accepté. Checkpoint perdu sous le même nom : refus, sinon les lots
    # renumérotés à partir de 0 seraient pris pour des lots déjà appliqués.
    job.verifier_generation(cfg, connecter)
    perdu = job.Config(**{**cfg.__dict__, "checkpoint": str(tmp_path / "checkpoint-neuf")})
    with pytest.raises(job.ArretPipeline, match="changer de génération"):
        job.verifier_generation(perdu, connecter)
    job.verifier_generation(job.Config(**{**perdu.__dict__, "requete": "etat_regprc@g2"}), connecter)
