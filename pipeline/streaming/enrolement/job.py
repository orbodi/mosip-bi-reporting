"""Job temps réel de l'enrôlement : topic Debezium de regprc.registration → Data Mart.

Chaîne : MOSIP regprc.registration → Debezium → Kafka → ce job → etat.registration → bi.fait_enrolement_jour.
Principes (skill mosip-bi-pipeline) :
- schéma explicite aligné sur le DDL MOSIP v1.1.5 et sur column.include.list du connecteur ;
- dernier événement par clé dans le lot, garde LSN dans le Data Mart, suppression logique ;
- registre des lots dans la même transaction que les écritures : un lot rejoué est sans effet ;
- faits recalculés depuis l'état courant pour les cases (jour, centre) touchées, jamais incrémentés ;
- RID jamais écrit : empreinte HMAC-SHA-256 (clé secrète) et code centre dérivé ;
- rejets sans contenu de message ; arrêt sur TRUNCATE ou au-delà d'un seuil de rejets.

Lancement : python -m streaming.enrolement.job (configuration par variables d'environnement, voir Config).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Iterable

from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.streaming import StreamingQueryListener

LOG = logging.getLogger("bi_cdc.enrolement")

PAQUET_KAFKA_DEFAUT = "org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0"


# ------------------------------------------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    topics: str  # liste explicite séparée par des virgules
    checkpoint: str  # stockage durable (volume) : le perdre = nouvelle génération de requête
    requete: str  # nom + génération de checkpoint, ex. "etat_regprc@g1"
    dsn_datamart: str  # DSN libpq du Data Mart
    cle_hmac: bytes  # clé secrète de pseudonymisation, différente par environnement
    kafka_bootstrap: str = ""
    source: str = "kafka"  # « kafka », ou « parquet » pour les tests (répertoire de messages simulés)
    chemin_source: str = ""
    max_offsets: int = 5_000
    seuil_rejets: int = 100
    intervalle: str = "10 seconds"
    partitions_shuffle: int = 4
    attente_datamart_s: int = 600

    @staticmethod
    def depuis_env(env: dict[str, str] | None = None) -> "Config":
        env = dict(os.environ if env is None else env)

        def requis(nom: str) -> str:
            valeur = env.get(nom)
            if not valeur:
                raise RuntimeError(f"Variable d'environnement manquante : {nom}")
            return valeur

        source = env.get("SOURCE", "kafka")
        return Config(
            topics=requis("TOPICS"),
            checkpoint=requis("CHECKPOINT_LOCATION"),
            requete=requis("NOM_REQUETE"),
            dsn_datamart=requis("DATAMART_DSN"),
            cle_hmac=requis("CLE_HMAC").encode("utf-8"),
            kafka_bootstrap=requis("KAFKA_BOOTSTRAP") if source == "kafka" else env.get("KAFKA_BOOTSTRAP", ""),
            source=source,
            chemin_source=env.get("CHEMIN_SOURCE", ""),
            max_offsets=int(env.get("MAX_OFFSETS_PAR_LOT", "5000")),
            seuil_rejets=int(env.get("SEUIL_REJETS", "100")),
            intervalle=env.get("INTERVALLE_LOT", "10 seconds"),
            partitions_shuffle=int(env.get("PARTITIONS_SHUFFLE", "4")),
            attente_datamart_s=int(env.get("ATTENTE_DATAMART_S", "600")),
        )


class ArretPipeline(RuntimeError):
    """Situation qui exige une décision humaine : le lot n'est pas appliqué et la requête s'arrête."""


# ------------------------------------------------------------------------------------------------------------------
# Schémas explicites (DDL regprc.registration v1.1.5, colonnes retenues par le connecteur)
# time.precision.mode=adaptive : un TIMESTAMP PostgreSQL de précision 6 (défaut) arrive en microsecondes depuis
# l'époque (io.debezium.time.MicroTimestamp). À vérifier sur un message réel en recette.
# ------------------------------------------------------------------------------------------------------------------
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
# Forme d'un message Kafka (source « parquet » des tests) : mêmes colonnes que la source Kafka de Spark.
MESSAGE_KAFKA = T.StructType(
    [
        T.StructField("topic", T.StringType()),
        T.StructField("partition", T.IntegerType()),
        T.StructField("offset", T.LongType()),
        T.StructField("key", T.BinaryType()),
        T.StructField("value", T.BinaryType()),
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


# ------------------------------------------------------------------------------------------------------------------
# Transformations Spark (pures, testables sur un DataFrame statique)
# ------------------------------------------------------------------------------------------------------------------
def decoder(brut: DataFrame, ligne: T.StructType, cle: T.StructType, champ_cle: str = "id") -> DataFrame:
    """Décode les messages Kafka (key/value binaires) et classe chaque événement.

    action : upsert | suppression | tombstone | truncate | ignore | rejet
    `champ_cle` : colonne de la clé primaire MOSIP dans la clé du message (id, prereg_id…).
    """
    evt = F.from_json(F.col("valeur_json"), enveloppe(ligne))  # PERMISSIVE
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
    cle_ok = F.col(f"cle.{champ_cle}").isNotNull()
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
        F.col(f"cle.{champ_cle}").alias("cle_id"),
        F.col("evt.op").alias("op"),
        F.col("evt.source.lsn").alias("lsn"),
        F.col("evt.source.ts_ms").alias("source_ts_ms"),
        F.col("evt.after").alias("apres"),
        action.alias("action"),
        F.when(action == "rejet", motif).alias("motif"),
        F.when(F.col("valeur_json").isNotNull(), F.sha2(F.col("valeur_json"), 256)).alias("empreinte_valeur"),
    )


def dernier_par_cle(evenements: DataFrame, cles: tuple[str, ...] = ("cle_id",)) -> DataFrame:
    """Garde, pour chaque clé, l'événement le plus récent du lot (LSN puis offset).

    `cles` : colonnes qui identifient une ligne MOSIP ; ajouter « topic » quand un job lit plusieurs tables.
    """
    fenetre = Window.partitionBy(*cles).orderBy(F.col("lsn").desc(), F.col("offset").desc())
    return (
        evenements.where(F.col("action").isin("upsert", "suppression"))
        .withColumn("_rang", F.row_number().over(fenetre))
        .where(F.col("_rang") == 1)
        .drop("_rang")
    )


# ------------------------------------------------------------------------------------------------------------------
# Dérivations et conversions (Python pur)
# ------------------------------------------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------------------------------------------
# Écriture idempotente dans le Data Mart (une transaction par lot)
# ------------------------------------------------------------------------------------------------------------------
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

RECALCUL = "select bi.recalculer_enrolement_jour(%s::date[], %s::text[])"

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

            # Cases (jour, centre) avant la mise à jour : un changement de statut ou de date déplace une inscription.
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
                cur.execute(RECALCUL, (list(jours), list(centres)))

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


# ------------------------------------------------------------------------------------------------------------------
# Traitement d'un micro-lot (foreachBatch)
# ------------------------------------------------------------------------------------------------------------------
def traiter_lot(cfg: Config, connecter: Callable[[], Any]):
    """Construit la fonction foreachBatch. `connecter()` renvoie une connexion psycopg (injectée pour les tests)."""

    def _traiter(lot: DataFrame, lot_id: int) -> None:
        evenements = decoder(lot, LIGNE_REGISTRATION, CLE_REGISTRATION).persist()
        try:
            par_action = evenements.groupBy("action").agg(F.count("*").alias("n")).collect()
            comptes = {r["action"]: r["n"] for r in par_action}
            if not comptes:
                return  # lot vide : rien à écrire, pas même le registre
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
        p = event.progress
        if p.numInputRows:
            LOG.info("Progression : lot %s, %s messages, %.0f ms", p.batchId, p.numInputRows, p.batchDuration)

    def onQueryIdle(self, event) -> None:  # noqa: N802
        pass

    def onQueryTerminated(self, event) -> None:  # noqa: N802
        if event.exception:
            LOG.error("Requête arrêtée : %s, exception : %s", event.id, event.exception)


# ------------------------------------------------------------------------------------------------------------------
# Démarrage
# ------------------------------------------------------------------------------------------------------------------
def attendre_datamart(
    connecter: Callable[[], Any],
    delai_s: int,
    fonction: str = "bi.recalculer_enrolement_jour(date[], text[])",
    migration: str = "V2",
) -> None:
    """Attend que les migrations Flyway du Data Mart soient passées (l'API les applique à son démarrage).

    `fonction` : fonction de recalcul dont le job a besoin, créée par la `migration` indiquée.
    """
    limite = time.monotonic() + delai_s
    while True:
        try:
            with connecter() as connexion, connexion.cursor() as cur:
                cur.execute(
                    "select to_regclass('pipeline.lot_traite') is not null and to_regprocedure(%s) is not null",
                    (fonction,),
                )
                if cur.fetchone()[0]:
                    return
                attente = f"migration {migration} absente"
        except Exception as erreur:  # base pas encore démarrée
            attente = type(erreur).__name__
        if time.monotonic() > limite:
            raise RuntimeError("Data Mart indisponible ou migrations absentes : démarrer l'API (Flyway) puis relancer")
        LOG.info("En attente du Data Mart (%s) : l'API applique les migrations au démarrage", attente)
        time.sleep(5)


def verifier_generation(cfg: Config, connecter: Callable[[], Any]) -> None:
    """Refuse de démarrer sur un checkpoint neuf si la requête a déjà appliqué des lots.

    Spark renumérote les lots à partir de 0 avec un nouveau checkpoint : sous le même nom de requête, le registre
    les prendrait pour des lots déjà appliqués et les ignorerait (données perdues sans erreur). Un checkpoint neuf
    exige donc une nouvelle génération (ex. etat_regprc@g2), qui relit le topic sans double comptage (garde LSN).
    """
    chemin = cfg.checkpoint.removeprefix("file:")
    if "://" in chemin:
        LOG.warning("Checkpoint distant (%s) : contrôle de génération non effectué", cfg.checkpoint)
        return
    if os.path.exists(os.path.join(chemin, "metadata")):
        return
    with connecter() as connexion, connexion.cursor() as cur:
        cur.execute("select count(*) from pipeline.lot_traite where requete = %s", (cfg.requete,))
        deja = cur.fetchone()[0]
    if deja:
        raise ArretPipeline(
            f"Checkpoint absent ({cfg.checkpoint}) alors que {cfg.requete} a déjà {deja} lots appliqués : "
            "changer de génération (NOM_REQUETE et CHECKPOINT_LOCATION, ex. @g2), ou restaurer le checkpoint"
        )


def lire_source(spark: SparkSession, cfg: Config) -> DataFrame:
    if cfg.source == "kafka":
        return (
            spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", cfg.kafka_bootstrap)
            .option("subscribe", cfg.topics)
            .option("startingOffsets", "earliest")
            .option("failOnDataLoss", "true")
            .option("maxOffsetsPerTrigger", cfg.max_offsets)
            .load()
        )
    if cfg.source == "parquet":  # tests : messages Kafka simulés déposés dans un répertoire
        return spark.readStream.schema(MESSAGE_KAFKA).option("maxFilesPerTrigger", 1).parquet(cfg.chemin_source)
    raise ValueError(f"Source inconnue : {cfg.source}")


def session_spark(cfg: Config) -> SparkSession:
    constructeur = (
        SparkSession.builder.appName(cfg.requete)
        .config("spark.sql.shuffle.partitions", str(cfg.partitions_shuffle))
        .config("spark.sql.session.timeZone", "UTC")
    )
    if cfg.source == "kafka":
        constructeur = constructeur.config(
            "spark.jars.packages", os.environ.get("SPARK_KAFKA_PAQUET", PAQUET_KAFKA_DEFAUT)
        )
        if os.environ.get("SPARK_IVY"):
            constructeur = constructeur.config("spark.jars.ivy", os.environ["SPARK_IVY"])
    return constructeur.getOrCreate()


def demarrer(cfg: Config, connecter: Callable[[], Any], spark: SparkSession | None = None):
    """Démarre la requête de streaming et la renvoie (sans attendre sa fin)."""
    spark = spark or session_spark(cfg)
    spark.streams.addListener(JournalProgression())
    return (
        lire_source(spark, cfg)
        .writeStream.queryName(cfg.requete.replace("@", "_"))
        .foreachBatch(traiter_lot(cfg, connecter))
        .option("checkpointLocation", cfg.checkpoint)
        .trigger(processingTime=cfg.intervalle)
        .start()
    )


def main() -> None:
    import psycopg  # import local : le module reste importable pour les tests sans psycopg

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    cfg = Config.depuis_env()

    def connecter():
        return psycopg.connect(cfg.dsn_datamart, autocommit=False)

    attendre_datamart(connecter, cfg.attente_datamart_s)
    verifier_generation(cfg, connecter)
    LOG.info("Démarrage de %s (source %s, lot toutes les %s)", cfg.requete, cfg.source, cfg.intervalle)
    demarrer(cfg, connecter).awaitTermination()


if __name__ == "__main__":
    main()
