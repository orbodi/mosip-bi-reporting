"""Job temps réel des pré-inscriptions : topics Debezium de mosip_prereg → Data Mart.

Chaîne : prereg.applicant_demographic et prereg.applicant_demographic_consumed → Debezium → Kafka → ce job
→ etat.preinscription → bi.fait_preinscription_jour (décision du 20/10/2026, docs/decisions.md).

Colonnes reçues : prereg_id, status_code, cr_dtimes, upd_dtimes (column.include.list du connecteur
pipeline/cdc/connecteurs/prereg-dev.json). Les colonnes d'identité (demog_detail, demog_detail_hash, cr_appuser_id)
ne sont jamais capturées. Le prereg_id est remplacé par son empreinte HMAC avant toute écriture.

Mêmes principes que le job de l'enrôlement (streaming/enrolement/job.py, dont il reprend les briques) : schéma
explicite, dernier événement par clé, garde LSN, suppression logique, registre des lots dans la même transaction,
faits recalculés depuis l'état courant pour les jours touchés, rejets sans contenu, arrêt sur TRUNCATE.

Lancement : python -m streaming.preinscription.job (variables d'environnement : voir streaming.enrolement.job.Config).
"""

from __future__ import annotations

import json
import logging
from datetime import timezone
from typing import Any, Callable, Iterable

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

from streaming.enrolement import job as base

LOG = logging.getLogger("bi_cdc.preinscription")

FONCTION_RECALCUL = "bi.recalculer_preinscription_jour(date[])"

# DDL officiels v1.1.5 (pipeline/sources/ddl/mosip_prereg/), colonnes retenues par le connecteur.
LIGNE_PREREG = T.StructType(
    [
        T.StructField("prereg_id", T.StringType()),
        T.StructField("status_code", T.StringType()),
        T.StructField("cr_dtimes", T.LongType()),
        T.StructField("upd_dtimes", T.LongType()),
    ]
)
CLE_PREREG = T.StructType([T.StructField("prereg_id", T.StringType())])


def table_source(topic: str | None) -> str | None:
    """Table MOSIP d'un topic Debezium (<prefixe>.prereg.<table>) : « demande », « consommee » ou None."""
    if not topic:
        return None
    if topic.endswith(".applicant_demographic_consumed"):
        return "consommee"
    if topic.endswith(".applicant_demographic"):
        return "demande"
    return None


def decoder(brut: DataFrame) -> DataFrame:
    """Décode les deux topics et rejette un message venu d'une autre table (motif topic_inconnu)."""
    evenements = base.decoder(brut, LIGNE_PREREG, CLE_PREREG, champ_cle="prereg_id")
    connu = F.col("topic").endswith(".applicant_demographic") | F.col("topic").endswith(
        ".applicant_demographic_consumed"
    )
    hors_table = ~connu & F.col("action").isin("upsert", "suppression")
    return (
        evenements.withColumn("_hors_table", hors_table)
        .withColumn("action", F.when(F.col("_hors_table"), F.lit("rejet")).otherwise(F.col("action")))
        .withColumn("motif", F.when(F.col("_hors_table"), F.lit("topic_inconnu")).otherwise(F.col("motif")))
        .drop("_hors_table")
    )


def ligne_etat(cle_hmac: bytes, ev: dict[str, Any]) -> dict[str, Any]:
    a = ev["apres"]
    return {
        "prereg_empreinte": base.empreinte(cle_hmac, ev["cle_id"]),
        "table_source": table_source(ev["topic"]),
        "status_code": a["status_code"],
        "cr_dtimes": base.micro_vers_timestamp(a["cr_dtimes"]),
        "upd_dtimes": base.micro_vers_timestamp(a["upd_dtimes"]),
        "_lsn": ev["lsn"],
        "_source_ts": base.ms_vers_instant(ev["source_ts_ms"]),
    }


# ------------------------------------------------------------------------------------------------------------------
# Écriture idempotente dans le Data Mart (une transaction par lot)
# ------------------------------------------------------------------------------------------------------------------
UPSERT = """
insert into etat.preinscription as cible (
    prereg_empreinte, table_source, status_code, cr_dtimes, upd_dtimes, _lsn, _supprime, _source_ts, _maj_pipeline)
values (
    %(prereg_empreinte)s, %(table_source)s, %(status_code)s, %(cr_dtimes)s, %(upd_dtimes)s, %(_lsn)s, false,
    %(_source_ts)s, now())
on conflict (prereg_empreinte, table_source) do update set
    status_code = excluded.status_code, cr_dtimes = excluded.cr_dtimes, upd_dtimes = excluded.upd_dtimes,
    _lsn = excluded._lsn, _supprime = false, _source_ts = excluded._source_ts, _maj_pipeline = now()
where excluded._lsn > cible._lsn
"""

SUPPRESSION = """
insert into etat.preinscription as cible (prereg_empreinte, table_source, _lsn, _supprime, _source_ts, _maj_pipeline)
values (%(prereg_empreinte)s, %(table_source)s, %(_lsn)s, true, %(_source_ts)s, now())
on conflict (prereg_empreinte, table_source) do update set
    _supprime = true, _lsn = excluded._lsn, _source_ts = excluded._source_ts, _maj_pipeline = now()
where excluded._lsn > cible._lsn
"""

# Jours de toutes les lignes (active et _consumed) des demandes touchées, avant la mise à jour.
JOURS_EXISTANTS = """
select distinct cr_dtimes::date
from etat.preinscription
where prereg_empreinte = any(%s) and cr_dtimes is not null
"""

RECALCUL = "select bi.recalculer_preinscription_jour(%s::date[])"

# « Dernière demande » : création de la demande la plus récente (heure UTC de MOSIP).
FRAICHEUR = """
insert into bi.source_fraicheur (source, libelle, ordre, premiere_donnee, derniere_donnee, dernier_chargement)
values ('preinscription', 'Pré-inscription', 6, %(premiere)s, %(derniere)s, now())
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
    """Applique un lot dans une seule transaction. Renvoie False si le lot était déjà appliqué."""
    derniers = list(derniers)
    upserts = [ligne_etat(cle_hmac, ev) for ev in derniers if ev["action"] == "upsert"]
    suppressions = [
        {
            "prereg_empreinte": base.empreinte(cle_hmac, ev["cle_id"]),
            "table_source": table_source(ev["topic"]),
            "_lsn": ev["lsn"],
            "_source_ts": base.ms_vers_instant(ev["source_ts_ms"]),
        }
        for ev in derniers
        if ev["action"] == "suppression"
    ]
    try:
        with connexion.cursor() as cur:
            cur.execute("select pg_advisory_xact_lock(hashtext(%s))", (requete,))
            cur.execute("select 1 from pipeline.lot_traite where requete = %s and lot_id = %s", (requete, lot_id))
            if cur.fetchone():
                connexion.rollback()
                LOG.info("Lot %s déjà appliqué pour %s : ignoré", lot_id, requete)
                return False

            touchees = sorted({u["prereg_empreinte"] for u in upserts} | {s["prereg_empreinte"] for s in suppressions})
            jours: set[Any] = set()
            if touchees:
                cur.execute(JOURS_EXISTANTS, (touchees,))
                jours.update(j for (j,) in cur.fetchall())
            if upserts:
                cur.executemany(UPSERT, upserts)
            if suppressions:
                cur.executemany(SUPPRESSION, suppressions)
            jours.update(u["cr_dtimes"].date() for u in upserts if u["cr_dtimes"])
            if jours:
                cur.execute(RECALCUL, (sorted(jours),))

            rejets = list(rejets)
            if rejets:
                cur.executemany(
                    base.REJET,
                    [
                        (requete, lot_id, r["topic"], r["partition"], r["offset"], r["motif"], r["empreinte_valeur"])
                        for r in rejets
                    ],
                )
            cur.execute(
                base.REGISTRE,
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
            if dates:
                cur.execute(
                    FRAICHEUR,
                    {"premiere": min(dates).date(), "derniere": max(dates).replace(tzinfo=timezone.utc)},
                )
        connexion.commit()
        return True
    except Exception:
        connexion.rollback()
        raise


def traiter_lot(cfg: base.Config, connecter: Callable[[], Any]):
    """Construit la fonction foreachBatch. `connecter()` renvoie une connexion psycopg (injectée pour les tests)."""

    def _traiter(lot: DataFrame, lot_id: int) -> None:
        evenements = decoder(lot).persist()
        try:
            par_action = evenements.groupBy("action").agg(F.count("*").alias("n")).collect()
            comptes = {r["action"]: r["n"] for r in par_action}
            if not comptes:
                return
            if comptes.get("truncate"):
                raise base.ArretPipeline(f"TRUNCATE reçu (lot {lot_id}) : décision humaine requise, lot non appliqué")
            if comptes.get("rejet", 0) > cfg.seuil_rejets:
                raise base.ArretPipeline(f"{comptes['rejet']} rejets dans le lot {lot_id} (seuil {cfg.seuil_rejets})")
            rejets = [
                r.asDict()
                for r in evenements.where(F.col("action") == "rejet")
                .select("topic", "partition", "offset", "motif", "empreinte_valeur")
                .collect()
            ]
            # Une même demande peut changer dans les deux tables : une clé = (topic, prereg_id).
            derniers = [
                r.asDict(recursive=True)
                for r in base.dernier_par_cle(evenements, cles=("topic", "cle_id"))
                .select("topic", "cle_id", "action", "lsn", "source_ts_ms", "apres")
                .collect()
            ]
        finally:
            evenements.unpersist()

        with connecter() as connexion:
            applique = ecrire_lot(connexion, cfg.requete, lot_id, cfg.cle_hmac, derniers, rejets, comptes)
        LOG.info("Lot %s %s : %s", lot_id, "appliqué" if applique else "déjà appliqué", json.dumps(comptes))

    return _traiter


def demarrer(cfg: base.Config, connecter: Callable[[], Any], spark=None):
    """Démarre la requête de streaming et la renvoie (sans attendre sa fin)."""
    spark = spark or base.session_spark(cfg)
    spark.streams.addListener(base.JournalProgression())
    return (
        base.lire_source(spark, cfg)
        .writeStream.queryName(cfg.requete.replace("@", "_"))
        .foreachBatch(traiter_lot(cfg, connecter))
        .option("checkpointLocation", cfg.checkpoint)
        .trigger(processingTime=cfg.intervalle)
        .start()
    )


def main() -> None:
    import psycopg

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    cfg = base.Config.depuis_env()

    def connecter():
        return psycopg.connect(cfg.dsn_datamart, autocommit=False)

    base.attendre_datamart(connecter, cfg.attente_datamart_s, FONCTION_RECALCUL, "V4")
    base.verifier_generation(cfg, connecter)
    LOG.info("Démarrage de %s (source %s, lot toutes les %s)", cfg.requete, cfg.source, cfg.intervalle)
    demarrer(cfg, connecter).awaitTermination()


if __name__ == "__main__":
    main()
