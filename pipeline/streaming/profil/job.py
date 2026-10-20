"""Job temps réel du profil anonymisé des NIU : topic Debezium de idrepo.anonymous_profile → Data Mart.

Chaîne : idrepo.anonymous_profile (MOSIP 1.1.5.5 et plus) → Debezium → Kafka → ce job → etat.profil_anonyme
→ bi.fait_niu_profil_jour (décision du 20/10/2026, docs/decisions.md).

Colonnes reçues : id, profile, cr_dtimes, is_deleted (pipeline/cdc/connecteurs/idrepo-dev.json). Le profil est un
JSON publié par MOSIP pour le reporting (processName, date, oldProfile, newProfile avec yearOfBirth, gender,
location…). Minimisation : le job n'en garde que le processus, le jour, le genre, la tranche d'âge et la région ;
le JSON, l'année de naissance et les codes de lieux ne sont jamais écrits ni journalisés.

Mêmes principes que le job de l'enrôlement (streaming/enrolement/job.py, dont il reprend les briques).

Lancement : python -m streaming.profil.job (variables d'environnement : voir streaming.enrolement.job.Config).
"""

from __future__ import annotations

import json
import logging
from datetime import date
from typing import Any, Callable, Iterable

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

from streaming.enrolement import job as base

LOG = logging.getLogger("bi_cdc.profil")

FONCTION_RECALCUL = "bi.recalculer_niu_profil_jour(date[])"

# Structure relevée sur le DDL MOSIP (pipeline/sources/ddl/mosip_idrepo/idrepo-anonymous_profile.sql), colonnes
# retenues par le connecteur. À vérifier sur l'instance (\d+ idrepo.anonymous_profile) avant la recette.
LIGNE_PROFIL = T.StructType(
    [
        T.StructField("id", T.StringType()),
        T.StructField("profile", T.StringType()),
        T.StructField("cr_dtimes", T.LongType()),
        T.StructField("is_deleted", T.BooleanType()),
    ]
)
CLE_PROFIL = T.StructType([T.StructField("id", T.StringType())])

# Tranches de la pyramide de la maquette Enrôlement : (âge maximal inclus, code). « 60+ » = 61 ans et plus.
TRANCHES = ((5, "0-5"), (14, "6-14"), (18, "15-18"), (25, "19-25"), (35, "26-35"), (45, "36-45"), (60, "46-60"))
AGE_MAXIMAL = 130


# ------------------------------------------------------------------------------------------------------------------
# Lecture du profil (Python pur, testable)
# ------------------------------------------------------------------------------------------------------------------
def _texte(valeur: Any) -> str | None:
    """Une valeur simple, ou la première « value » d'une liste multilingue [{"language": …, "value": …}]."""
    if isinstance(valeur, str):
        return valeur.strip() or None
    if isinstance(valeur, list):
        for element in valeur:
            texte = _texte(element.get("value") if isinstance(element, dict) else element)
            if texte:
                return texte
    return None


def _lieux(valeur: Any) -> list[str]:
    if isinstance(valeur, str):
        return [valeur] if valeur.strip() else []
    if isinstance(valeur, list):
        return [t for t in (_texte(v if not isinstance(v, dict) else v.get("value")) for v in valeur) if t]
    return []


def _jour(valeur: Any) -> date | None:
    if isinstance(valeur, str) and len(valeur) >= 10:
        try:
            return date.fromisoformat(valeur[:10])
        except ValueError:
            return None
    return None


def tranche_age(annee_naissance: int | None, jour: date | None) -> str:
    """Tranche de l'âge atteint dans l'année du jour (l'année de naissance seule est connue)."""
    if annee_naissance is None or jour is None:
        return "inconnu"
    age = jour.year - annee_naissance
    if age < 0 or age > AGE_MAXIMAL:
        return "inconnu"
    for maximum, code in TRANCHES:
        if age <= maximum:
            return code
    return "60+"


def lire_profil(texte: str | None) -> dict[str, Any]:
    """Champs utiles d'un profil JSON ; valeurs nulles si le JSON est illisible ou incomplet."""
    vide = {"processus": None, "jour": None, "genre": None, "annee_naissance": None, "lieux": []}
    if not texte:
        return vide
    try:
        profil = json.loads(texte)
    except (TypeError, ValueError):
        return vide
    if not isinstance(profil, dict):
        return vide
    nouveau = profil.get("newProfile") if isinstance(profil.get("newProfile"), dict) else {}
    annee = nouveau.get("yearOfBirth")
    try:
        annee_naissance = int(str(annee).strip()) if annee not in (None, "") else None
    except ValueError:
        annee_naissance = None
    return {
        "processus": _texte(profil.get("processName")),
        "jour": _jour(profil.get("date")),
        "genre": _texte(nouveau.get("gender")),
        "annee_naissance": annee_naissance,
        "lieux": _lieux(nouveau.get("location")),
    }


def ligne_etat(cle_hmac: bytes, ev: dict[str, Any]) -> dict[str, Any]:
    a = ev["apres"]
    cr = base.micro_vers_timestamp(a["cr_dtimes"])
    profil = lire_profil(a["profile"])
    jour = profil["jour"] or (cr.date() if cr else None)
    return {
        "profil_empreinte": base.empreinte(cle_hmac, ev["cle_id"]),
        "processus": profil["processus"],
        "jour": jour,
        "genre": profil["genre"],
        "tranche_age": tranche_age(profil["annee_naissance"], jour),
        "lieux": profil["lieux"],  # paramètre de bi.region_des_lieux seulement, jamais écrit
        "cr_dtimes": cr,
        "is_deleted": a["is_deleted"],
        "_lsn": ev["lsn"],
        "_source_ts": base.ms_vers_instant(ev["source_ts_ms"]),
    }


# ------------------------------------------------------------------------------------------------------------------
# Écriture idempotente dans le Data Mart (une transaction par lot)
# ------------------------------------------------------------------------------------------------------------------
UPSERT = """
insert into etat.profil_anonyme as cible (
    profil_empreinte, processus, jour, genre, tranche_age, code_region, cr_dtimes, is_deleted,
    _lsn, _supprime, _source_ts, _maj_pipeline)
values (
    %(profil_empreinte)s, %(processus)s, %(jour)s, %(genre)s, %(tranche_age)s,
    bi.region_des_lieux(%(lieux)s::text[]), %(cr_dtimes)s, %(is_deleted)s, %(_lsn)s, false, %(_source_ts)s, now())
on conflict (profil_empreinte) do update set
    processus = excluded.processus, jour = excluded.jour, genre = excluded.genre,
    tranche_age = excluded.tranche_age, code_region = excluded.code_region, cr_dtimes = excluded.cr_dtimes,
    is_deleted = excluded.is_deleted, _lsn = excluded._lsn, _supprime = false, _source_ts = excluded._source_ts,
    _maj_pipeline = now()
where excluded._lsn > cible._lsn
"""

SUPPRESSION = """
insert into etat.profil_anonyme as cible (profil_empreinte, _lsn, _supprime, _source_ts, _maj_pipeline)
values (%(profil_empreinte)s, %(_lsn)s, true, %(_source_ts)s, now())
on conflict (profil_empreinte) do update set
    _supprime = true, _lsn = excluded._lsn, _source_ts = excluded._source_ts, _maj_pipeline = now()
where excluded._lsn > cible._lsn
"""

JOURS_EXISTANTS = """
select distinct jour from etat.profil_anonyme where profil_empreinte = any(%s) and jour is not null
"""

RECALCUL = "select bi.recalculer_niu_profil_jour(%s::date[])"


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
            "profil_empreinte": base.empreinte(cle_hmac, ev["cle_id"]),
            "_lsn": ev["lsn"],
            "_source_ts": base.ms_vers_instant(ev["source_ts_ms"]),
        }
        for ev in derniers
        if ev["action"] == "suppression"
    ]
    illisibles = sum(1 for u in upserts if u["processus"] is None)
    try:
        with connexion.cursor() as cur:
            cur.execute("select pg_advisory_xact_lock(hashtext(%s))", (requete,))
            cur.execute("select 1 from pipeline.lot_traite where requete = %s and lot_id = %s", (requete, lot_id))
            if cur.fetchone():
                connexion.rollback()
                LOG.info("Lot %s déjà appliqué pour %s : ignoré", lot_id, requete)
                return False

            touchees = sorted({u["profil_empreinte"] for u in upserts} | {s["profil_empreinte"] for s in suppressions})
            jours: set[Any] = set()
            if touchees:
                cur.execute(JOURS_EXISTANTS, (touchees,))
                jours.update(j for (j,) in cur.fetchall())
            if upserts:
                cur.executemany(UPSERT, upserts)
            if suppressions:
                cur.executemany(SUPPRESSION, suppressions)
            jours.update(u["jour"] for u in upserts if u["jour"])
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
        connexion.commit()
    except Exception:
        connexion.rollback()
        raise
    if illisibles:
        LOG.warning("Lot %s : %s profils sans processus lisible (exclus des faits)", lot_id, illisibles)
    return True


def traiter_lot(cfg: base.Config, connecter: Callable[[], Any]):
    """Construit la fonction foreachBatch. `connecter()` renvoie une connexion psycopg (injectée pour les tests)."""

    def _traiter(lot: DataFrame, lot_id: int) -> None:
        evenements = base.decoder(lot, LIGNE_PROFIL, CLE_PROFIL).persist()
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
            derniers = [
                r.asDict(recursive=True)
                for r in base.dernier_par_cle(evenements)
                .select("cle_id", "action", "lsn", "source_ts_ms", "apres")
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
