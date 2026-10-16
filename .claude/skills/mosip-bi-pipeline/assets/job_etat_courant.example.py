"""Job de streaming : topic Debezium de regprc.registration -> état courant et faits du Data Mart.

Modèle à adapter (references/spark-streaming.md, references/datamart.md). Principes :
- schéma explicite aligné sur le DDL MOSIP v1.1.5 et sur column.include.list du connecteur ;
- dernier événement par clé dans le lot, garde LSN dans le Data Mart, suppression logique ;
- registre des lots dans la même transaction que les écritures : un lot rejoué est sans effet ;
- RID jamais écrit : empreinte HMAC-SHA-256 (clé secrète) et code centre dérivé ;
- rejets sans contenu de message ; arrêt sur TRUNCATE ou au-delà d'un seuil de rejets.

Dépendances : pyspark 4.x, psycopg 3, paquet Kafka de Spark (spark-sql-kafka-0-10) au lancement.
Configuration par variables d'environnement (aucun secret dans le code) : voir Config.depuis_env().
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.streaming import StreamingQueryListener

LOG = logging.getLogger("bi_cdc.etat_registration")


# --------------------------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    kafka_bootstrap: str
    topics: str  # liste explicite séparée par des virgules
    checkpoint: str  # stockage durable et partagé
    requete: str  # nom + génération de checkpoint, ex. "etat_regprc@g1"
    dsn_datamart: str  # DSN libpq sans mot de passe (PGPASSFILE ou PGPASSWORD fournis par l'environnement)
    cle_hmac: bytes  # clé secrète de pseudonymisation, différente par environnement
    max_offsets: int = 50_000
    seuil_rejets: int = 100
    intervalle: str = "1 minute"

    @staticmethod
    def depuis_env() -> "Config":
        def requis(nom: str) -> str:
            valeur = os.environ.get(nom)
            if not valeur:
                raise RuntimeError(f"Variable d'environnement manquante : {nom}")
            return valeur

        return Config(
            kafka_bootstrap=requis("KAFKA_BOOTSTRAP"),
            topics=requis("TOPICS"),
            checkpoint=requis("CHECKPOINT_LOCATION"),
            requete=requis("NOM_REQUETE"),
            dsn_datamart=requis("DATAMART_DSN"),
            cle_hmac=requis("CLE_HMAC").encode("utf-8"),
            max_offsets=int(os.environ.get("MAX_OFFSETS_PAR_LOT", "50000")),
            seuil_rejets=int(os.environ.get("SEUIL_REJETS", "100")),
            intervalle=os.environ.get("INTERVALLE_LOT", "1 minute"),
        )


class ArretPipeline(RuntimeError):
    """Situation qui exige une décision humaine : le lot n'est pas appliqué et la requête s'arrête."""


# --------------------------------------------------------------------------------------------------
# Schémas explicites (DDL regprc.registration v1.1.5, colonnes retenues seulement)
# time.precision.mode=adaptive : un TIMESTAMP PostgreSQL de précision 6 (défaut) arrive en microsecondes
# depuis l'époque (io.debezium.time.MicroTimestamp). À vérifier sur un message réel en recette.
# --------------------------------------------------------------------------------------------------
LIGNE_REGISTRATION = T.StructType(
    [
        T.StructField("id", T.StringType()),
        T.StructField("reg_type", T.StringType()),
        T.StructField("status_code", T.StringType()),
        T.StructField("latest_trn_type_code", T.StringType()),
        T.StructField("latest_trn_status_code", T.StringType()),
        T.StructField("latest_trn_dtimes", T.LongType()),
        T.StructField("reg_stage_name", T.StringType()),
        T.StructField("pkt_cr_dtimes", T.LongType()),
        T.StructField("is_active", T.BooleanType()),
        T.StructField("cr_dtimes", T.LongType()),
        T.StructField("upd_dtimes", T.LongType()),
        T.StructField("is_deleted", T.BooleanType()),
    ]
)
CLE_REGISTRATION = T.StructType([T.StructField("id", T.StringType())])
SOURCE = T.StructType(
    [
        T.StructField("lsn", T.LongType()),
        T.StructField("txId", T.LongType()),
        T.StructField("ts_ms", T.LongType()),
        T.StructField("snapshot", T.StringType()),
    ]
)


def enveloppe(ligne: T.StructType) -> T.StructType:
    return T.StructType(
        [
            T.StructField("before", ligne),
            T.StructField("after", ligne),
            T.StructField("source", SOURCE),
            T.StructField("op", T.StringType()),
            T.StructField("ts_ms", T.LongType()),
        ]
    )


# --------------------------------------------------------------------------------------------------
# Transformations Spark (pures, testables sur un DataFrame statique)
# --------------------------------------------------------------------------------------------------
def decoder(brut: DataFrame, ligne: T.StructType, cle: T.StructType) -> DataFrame:
    """Décode les messages Kafka (key/value binaires) et classe chaque événement.

    action : upsert | suppression | tombstone | truncate | ignore | rejet
    """
    evt = F.from_json(F.col("valeur_json"), enveloppe(ligne))  # PERMISSIVE : JSON illisible -> null
    decode = (
        brut.select(
            "topic",
            "partition",
            "offset",
            F.col("key").cast("string").alias("cle_json"),
            F.col("value").cast("string").alias("valeur_json"),
        )
        .withColumn("evt", evt)
        .withColumn("cle", F.from_json(F.col("cle_json"), cle))
    )
    cle_ok = F.col("cle.id").isNotNull()
    lsn_ok = F.col("evt.source.lsn").isNotNull()
    action = (
        F.when(F.col("valeur_json").isNull(), F.lit("tombstone"))
        .when(F.col("evt.op").isin("c", "r", "u") & F.col("evt.after").isNotNull() & cle_ok & lsn_ok, F.lit("upsert"))
        .when((F.col("evt.op") == "d") & cle_ok & lsn_ok, F.lit("suppression"))
        .when(F.col("evt.op") == "t", F.lit("truncate"))
        .when(F.col("evt.op") == "m", F.lit("ignore"))
        .otherwise(F.lit("rejet"))
    )
    motif = (
        # Spark 4 (PERMISSIVE) : un JSON illisible donne une structure aux champs nuls, d'où le test sur op.
        F.when(F.col("evt").isNull() | F.col("evt.op").isNull(), F.lit("json_illisible_ou_op_absent"))
        .when(~cle_ok, F.lit("cle_absente"))
        .when(~lsn_ok, F.lit("lsn_absent"))
        .when(F.col("evt.op").isin("c", "r", "u"), F.lit("after_absent"))
        .otherwise(F.lit("op_inconnu"))
    )
    return decode.select(
        "topic",
        "partition",
        "offset",
        F.col("cle.id").alias("cle_id"),
        F.col("evt.op").alias("op"),
        F.col("evt.source.lsn").alias("lsn"),
        F.col("evt.source.ts_ms").alias("source_ts_ms"),
        F.col("evt.after").alias("apres"),
        action.alias("action"),
        F.when(action == "rejet", motif).alias("motif"),
        F.when(F.col("valeur_json").isNotNull(), F.sha2(F.col("valeur_json"), 256)).alias("empreinte_valeur"),
    )


def dernier_par_cle(evenements: DataFrame) -> DataFrame:
    """Garde, pour chaque clé, l'événement le plus récent du lot (LSN puis offset)."""
    fenetre = Window.partitionBy("cle_id").orderBy(F.col("lsn").desc(), F.col("offset").desc())
    return (
        evenements.where(F.col("action").isin("upsert", "suppression"))
        .withColumn("_rang", F.row_number().over(fenetre))
        .where(F.col("_rang") == 1)
        .drop("_rang")
    )


# --------------------------------------------------------------------------------------------------
# Dérivations et conversions (Python pur)
# --------------------------------------------------------------------------------------------------
_EPOQUE = datetime(1970, 1, 1)


def empreinte(cle_hmac: bytes, valeur: str) -> str:
    return hmac.new(cle_hmac, valeur.encode("utf-8"), hashlib.sha256).hexdigest()


def centre_depuis_rid(rid: str | None) -> str | None:
    """Préfixe du RID = identifiant du centre selon la convention MOSIP (à vérifier sur l'instance)."""
    if rid and len(rid) >= 5 and rid[:5].isdigit():
        return rid[:5]
    return None


def micro_vers_timestamp(valeur: int | None) -> datetime | None:
    return None if valeur is None else _EPOQUE + timedelta(microseconds=valeur)


def ms_vers_instant(valeur: int | None) -> datetime | None:
    return None if valeur is None else datetime.fromtimestamp(valeur / 1000, tz=timezone.utc)


def ligne_etat(cle_hmac: bytes, ev: dict[str, Any]) -> dict[str, Any]:
    a = ev["apres"]
    return {
        "rid_empreinte": empreinte(cle_hmac, ev["cle_id"]),
        "code_centre": centre_depuis_rid(ev["cle_id"]),
        "reg_type": a["reg_type"],
        "status_code": a["status_code"],
        "latest_trn_type_code": a["latest_trn_type_code"],
        "latest_trn_status_code": a["latest_trn_status_code"],
        "latest_trn_dtimes": micro_vers_timestamp(a["latest_trn_dtimes"]),
        "reg_stage_name": a["reg_stage_name"],
        "pkt_cr_dtimes": micro_vers_timestamp(a["pkt_cr_dtimes"]),
        "is_active": a["is_active"],
        "cr_dtimes": micro_vers_timestamp(a["cr_dtimes"]),
        "upd_dtimes": micro_vers_timestamp(a["upd_dtimes"]),
        "is_deleted": a["is_deleted"],
        "_lsn": ev["lsn"],
        "_source_ts": ms_vers_instant(ev["source_ts_ms"]),
    }


# --------------------------------------------------------------------------------------------------
# Écriture idempotente dans le Data Mart (une transaction par lot)
# --------------------------------------------------------------------------------------------------
UPSERT = """
insert into etat.registration as cible (
    rid_empreinte, code_centre, reg_type, status_code, latest_trn_type_code, latest_trn_status_code,
    latest_trn_dtimes, reg_stage_name, pkt_cr_dtimes, is_active, cr_dtimes, upd_dtimes, is_deleted,
    _lsn, _supprime, _source_ts, _maj_pipeline)
values (
    %(rid_empreinte)s, %(code_centre)s, %(reg_type)s, %(status_code)s, %(latest_trn_type_code)s,
    %(latest_trn_status_code)s, %(latest_trn_dtimes)s, %(reg_stage_name)s, %(pkt_cr_dtimes)s, %(is_active)s,
    %(cr_dtimes)s, %(upd_dtimes)s, %(is_deleted)s, %(_lsn)s, false, %(_source_ts)s, now())
on conflict (rid_empreinte) do update set
    code_centre = excluded.code_centre, reg_type = excluded.reg_type, status_code = excluded.status_code,
    latest_trn_type_code = excluded.latest_trn_type_code, latest_trn_status_code = excluded.latest_trn_status_code,
    latest_trn_dtimes = excluded.latest_trn_dtimes, reg_stage_name = excluded.reg_stage_name,
    pkt_cr_dtimes = excluded.pkt_cr_dtimes, is_active = excluded.is_active, cr_dtimes = excluded.cr_dtimes,
    upd_dtimes = excluded.upd_dtimes, is_deleted = excluded.is_deleted, _lsn = excluded._lsn,
    _supprime = false, _source_ts = excluded._source_ts, _maj_pipeline = now()
where excluded._lsn > cible._lsn
"""

SUPPRESSION = """
insert into etat.registration as cible (rid_empreinte, _lsn, _supprime, _source_ts, _maj_pipeline)
values (%(rid_empreinte)s, %(_lsn)s, true, %(_source_ts)s, now())
on conflict (rid_empreinte) do update set
    _supprime = true, _lsn = excluded._lsn, _source_ts = excluded._source_ts, _maj_pipeline = now()
where excluded._lsn > cible._lsn
"""

CASES_EXISTANTES = """
select distinct cr_dtimes::date, coalesce(code_centre, 'inconnu')
from etat.registration
where rid_empreinte = any(%s) and cr_dtimes is not null
"""

REJET = """
insert into pipeline.evenement_rejete (requete, lot_id, topic, partition, kafka_offset, motif, empreinte)
values (%s, %s, %s, %s, %s, %s, %s)
on conflict (topic, partition, kafka_offset) do nothing
"""

REGISTRE = """
insert into pipeline.lot_traite (requete, lot_id, nb_upserts, nb_suppressions, nb_ignores, nb_rejets)
values (%s, %s, %s, %s, %s, %s)
"""

FRAICHEUR = """
insert into bi.source_fraicheur (source, libelle, ordre, premiere_donnee, derniere_donnee, dernier_chargement)
values ('enrolement', 'Enrôlement', 1, %(premiere)s, %(derniere)s, now())
on conflict (source) do update set
    premiere_donnee = least(coalesce(bi.source_fraicheur.premiere_donnee, excluded.premiere_donnee),
                            excluded.premiere_donnee),
    derniere_donnee = greatest(coalesce(bi.source_fraicheur.derniere_donnee, excluded.derniere_donnee),
                               excluded.derniere_donnee),
    dernier_chargement = now()
"""


def ecrire_lot(
    connexion: Any,
    requete: str,
    lot_id: int,
    cle_hmac: bytes,
    derniers: Iterable[dict[str, Any]],
    rejets: Iterable[dict[str, Any]],
    comptes: dict[str, int],
) -> bool:
    """Applique un lot dans une seule transaction. Renvoie False si le lot était déjà appliqué.

    `connexion` est une connexion psycopg 3 ouverte, hors autocommit ; la fonction valide ou annule elle-même.
    """
    derniers = list(derniers)
    upserts = [ligne_etat(cle_hmac, ev) for ev in derniers if ev["action"] == "upsert"]
    suppressions = [
        {
            "rid_empreinte": empreinte(cle_hmac, ev["cle_id"]),
            "_lsn": ev["lsn"],
            "_source_ts": ms_vers_instant(ev["source_ts_ms"]),
        }
        for ev in derniers
        if ev["action"] == "suppression"
    ]
    try:
        with connexion.cursor() as cur:
            # Un seul écrivain par requête, puis contrôle du registre.
            cur.execute("select pg_advisory_xact_lock(hashtext(%s))", (requete,))
            cur.execute("select 1 from pipeline.lot_traite where requete = %s and lot_id = %s", (requete, lot_id))
            if cur.fetchone():
                connexion.rollback()
                LOG.info("Lot %s déjà appliqué pour %s : ignoré", lot_id, requete)
                return False

            touchees = [u["rid_empreinte"] for u in upserts] + [s["rid_empreinte"] for s in suppressions]
            cases: set[tuple[Any, str]] = set()
            if touchees:
                cur.execute(CASES_EXISTANTES, (touchees,))
                cases.update((jour, centre) for jour, centre in cur.fetchall())
            if upserts:
                cur.executemany(UPSERT, upserts)
            if suppressions:
                cur.executemany(SUPPRESSION, suppressions)
            cases.update((u["cr_dtimes"].date(), u["code_centre"] or "inconnu") for u in upserts if u["cr_dtimes"])
            if cases:
                jours, centres = zip(*sorted(cases), strict=True)
                cur.execute("select bi.recalculer_enrolement(%s::date[], %s::text[])", (list(jours), list(centres)))

            rejets = list(rejets)
            if rejets:
                cur.executemany(
                    REJET,
                    [
                        (requete, lot_id, r["topic"], r["partition"], r["offset"], r["motif"], r["empreinte_valeur"])
                        for r in rejets
                    ],
                )
            cur.execute(
                REGISTRE,
                (
                    requete,
                    lot_id,
                    comptes.get("upsert", 0),
                    comptes.get("suppression", 0),
                    comptes.get("tombstone", 0) + comptes.get("ignore", 0),
                    comptes.get("rejet", 0),
                ),
            )
            dates = [u["cr_dtimes"] for u in upserts if u["cr_dtimes"]]
            sources = [ev["_source_ts"] for ev in upserts + suppressions if ev["_source_ts"]]
            if dates or sources:
                cur.execute(
                    FRAICHEUR,
                    {
                        "premiere": min(dates).date() if dates else None,
                        "derniere": max(sources) if sources else None,
                    },
                )
        connexion.commit()
        return True
    except Exception:
        connexion.rollback()
        raise


# --------------------------------------------------------------------------------------------------
# Traitement d'un micro-lot (foreachBatch)
# --------------------------------------------------------------------------------------------------
def traiter_lot(cfg: Config, connecter: Any):
    """Construit la fonction foreachBatch. `connecter()` renvoie une connexion psycopg (injectée pour les tests)."""

    def _traiter(lot: DataFrame, lot_id: int) -> None:
        evenements = decoder(lot, LIGNE_REGISTRATION, CLE_REGISTRATION).persist()
        try:
            par_action = evenements.groupBy("action").agg(F.count("*").alias("n")).collect()
            comptes = {r["action"]: r["n"] for r in par_action}
            if comptes.get("truncate"):
                raise ArretPipeline(f"TRUNCATE reçu (lot {lot_id}) : décision humaine requise, lot non appliqué")
            if comptes.get("rejet", 0) > cfg.seuil_rejets:
                raise ArretPipeline(f"{comptes['rejet']} rejets dans le lot {lot_id} (seuil {cfg.seuil_rejets})")
            rejets = [
                r.asDict()
                for r in evenements.where(F.col("action") == "rejet")
                .select("topic", "partition", "offset", "motif", "empreinte_valeur")
                .collect()
            ]
            derniers = [
                r.asDict(recursive=True)
                for r in dernier_par_cle(evenements)
                .select("cle_id", "action", "lsn", "source_ts_ms", "apres")
                .collect()
            ]
        finally:
            evenements.unpersist()

        with connecter() as connexion:
            applique = ecrire_lot(connexion, cfg.requete, lot_id, cfg.cle_hmac, derniers, rejets, comptes)
        LOG.info("Lot %s %s : %s", lot_id, "appliqué" if applique else "déjà appliqué", json.dumps(comptes))

    return _traiter


class JournalProgression(StreamingQueryListener):
    """Écrit la progression de chaque lot (métriques seulement, aucune donnée)."""

    def onQueryStarted(self, event) -> None:  # noqa: N802 (API Spark)
        LOG.info("Requête démarrée : %s (%s)", event.name, event.id)

    def onQueryProgress(self, event) -> None:  # noqa: N802
        LOG.info("Progression : %s", event.progress.json)

    def onQueryIdle(self, event) -> None:  # noqa: N802
        LOG.info("Requête inactive : %s", event.id)

    def onQueryTerminated(self, event) -> None:  # noqa: N802
        LOG.error("Requête terminée : %s, exception : %s", event.id, event.exception)


def main() -> None:
    import psycopg  # import local : le module reste importable pour les tests sans psycopg

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    cfg = Config.depuis_env()
    spark = SparkSession.builder.appName(cfg.requete).getOrCreate()
    spark.streams.addListener(JournalProgression())

    brut = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", cfg.kafka_bootstrap)
        .option("subscribe", cfg.topics)
        .option("startingOffsets", "earliest")
        .option("failOnDataLoss", "true")
        .option("maxOffsetsPerTrigger", cfg.max_offsets)
        .load()
    )
    requete = (
        brut.writeStream.queryName(cfg.requete.replace("@", "_"))
        .foreachBatch(traiter_lot(cfg, lambda: psycopg.connect(cfg.dsn_datamart, autocommit=False)))
        .option("checkpointLocation", cfg.checkpoint)
        .trigger(processingTime=cfg.intervalle)
        .start()
    )
    requete.awaitTermination()


if __name__ == "__main__":
    main()
