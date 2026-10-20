"""Tests du job du profil anonymisé : lecture du JSON, tranches d'âge, région, minimisation, idempotence."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import psycopg
from pyspark.sql import Row

from streaming.enrolement import job as socle
from streaming.profil import job

CLE = b"cle-de-test"
TOPIC = "mosip.test.idrepo.anonymous_profile"
JOUR = date(2026, 1, 10)
MICRO_JOUR = int(datetime(2026, 1, 10, 9, 0, tzinfo=timezone.utc).timestamp() * 1_000_000)


def profil(processus="New", genre="Female", annee="1995", lieux=("SAV-02",), jour="2026-01-10") -> str:
    nouveau = {"yearOfBirth": annee, "gender": genre, "location": list(lieux), "preferredLanguages": ["fra"],
               "channel": ["phone"], "biometricInfo": [{"type": "Finger", "qualityScore": 80}]}  # fmt: skip
    return json.dumps({"processName": processus, "date": jour, "oldProfile": {}, "newProfile": nouveau})


def evenement(ident: str, op: str, lsn: int, texte: str | None = None, supprime: bool = False) -> dict:
    apres = {"id": ident, "profile": texte or profil(), "cr_dtimes": MICRO_JOUR, "is_deleted": supprime}
    return {
        "before": {"id": ident} if op in ("u", "d") else None,
        "after": None if op == "d" else apres,
        "source": {"lsn": lsn, "txId": lsn, "ts_ms": 1_792_400_000_000 + lsn, "snapshot": "false"},
        "op": op,
        "ts_ms": 1_792_400_000_000 + lsn,
    }


def message(ident: str | None, valeur, offset: int) -> Row:
    cle = None if ident is None else json.dumps({"id": ident}).encode()
    corps = None if valeur is None else json.dumps(valeur).encode()
    return Row(topic=TOPIC, partition=0, offset=offset, key=cle, value=corps)


def config(**autres) -> socle.Config:
    valeurs = {"topics": TOPIC, "checkpoint": "", "requete": "etat_profil@g1", "dsn_datamart": "", "cle_hmac": CLE}
    return socle.Config(**{**valeurs, **autres})


def lancer(spark, dsn: str, messages: list[Row], lot_id: int, cfg: socle.Config | None = None) -> None:
    lot = spark.createDataFrame(messages, socle.MESSAGE_KAFKA)
    job.traiter_lot(cfg or config(), lambda: psycopg.connect(dsn, autocommit=False))(lot, lot_id)


def faits(dsn: str) -> list[tuple]:
    with psycopg.connect(dsn) as c:
        return c.execute(
            "select f.jour, z.code, f.sexe, f.tranche_age, f.niu_generes from bi.fait_niu_profil_jour f"
            " join bi.zone z on z.id = f.zone_id order by 2, 3, 4"
        ).fetchall()


# --------------------------------------------------------------------------------------------------------------
# Lecture du profil (sans base)
# --------------------------------------------------------------------------------------------------------------
def test_tranches_de_la_maquette():
    jour = date(2026, 1, 10)
    assert [job.tranche_age(2026 - age, jour) for age in (0, 5, 6, 14, 15, 18, 19, 25, 26, 35, 36, 45, 46, 60, 61)] == [
        "0-5", "0-5", "6-14", "6-14", "15-18", "15-18", "19-25", "19-25", "26-35", "26-35", "36-45", "36-45",
        "46-60", "46-60", "60+",
    ]  # fmt: skip
    assert job.tranche_age(None, jour) == "inconnu"
    assert job.tranche_age(2030, jour) == "inconnu"
    assert job.tranche_age(1850, jour) == "inconnu"


def test_lecture_tolerante_du_profil():
    lu = job.lire_profil(profil(genre=[{"language": "fra", "value": "Female"}], annee=1990))
    assert lu == {"processus": "New", "jour": date(2026, 1, 10), "genre": "Female", "annee_naissance": 1990,
                  "lieux": ["SAV-02"]}  # fmt: skip
    assert job.lire_profil("pas du JSON")["processus"] is None
    assert job.lire_profil(json.dumps({"processName": "Update"}))["genre"] is None
    assert job.lire_profil(profil(annee="inconnue"))["annee_naissance"] is None


# --------------------------------------------------------------------------------------------------------------
# Écriture dans le Data Mart (vraies migrations)
# --------------------------------------------------------------------------------------------------------------
def lot_initial() -> list[Row]:
    return [
        message("A", evenement("A", "c", 100, profil(genre="Female", annee="1995", lieux=["SAV-02"])), 0),
        message("B", evenement("B", "c", 101, profil(genre="Male", annee="2024", lieux=["TG", "KAR"])), 1),
        message("C", evenement("C", "c", 102, profil(genre="Autre", annee="1960", lieux=["inconnu"])), 2),
        message("D", evenement("D", "c", 103, profil(processus="Update", genre="Male", lieux=["SAV-02"])), 3),
        message("E", evenement("E", "c", 104, "{illisible"), 4),
    ]


def test_lot_complet_par_region_sexe_et_tranche(spark, base):
    lancer(spark, base, lot_initial(), 0)

    # Seuls les profils « New » comptent ; genre sans correspondance → I ; lieu inconnu → hors référentiel.
    assert faits(base) == [
        (JOUR, "HORS_REFERENTIEL", "I", "60+", 1),
        (JOUR, "KAR", "H", "0-5", 1),
        (JOUR, "SAV", "F", "26-35", 1),
    ]
    with psycopg.connect(base) as c:
        controles = {ligne[0]: ligne[1] for ligne in c.execute("select * from pipeline.controler_profil_niu()")}
    assert controles == {"profil_niu_etat_egal_faits": "ok", "profil_niu_sans_sexe_ou_age": "alerte"}


def test_ni_json_ni_annee_ni_lieux_dans_le_data_mart(spark, base):
    lancer(spark, base, lot_initial(), 0)
    with psycopg.connect(base) as c:
        colonnes = [r[0] for r in c.execute(
            "select column_name from information_schema.columns where table_schema = 'etat'"
            " and table_name = 'profil_anonyme'").fetchall()]  # fmt: skip
        lignes = c.execute(
            "select processus, jour, genre, tranche_age, code_region, cr_dtimes, is_deleted from etat.profil_anonyme"
        ).fetchall()
    assert not {"profile", "annee_naissance", "lieux", "year_of_birth", "location"} & set(colonnes)
    texte = str(lignes)
    for interdit in ("1995", "2024", "SAV-02", "biometricInfo", "Finger"):
        assert interdit not in texte


def test_lot_rejoue_mise_a_jour_et_suppression(spark, base):
    lancer(spark, base, lot_initial(), 0)
    avant = faits(base)
    lancer(spark, base, lot_initial(), 0)
    assert faits(base) == avant

    # Le profil A est corrigé (homme, Kara), puis B est supprimé, puis C marqué is_deleted.
    lancer(spark, base, [message("A", evenement("A", "u", 200, profil(genre="Male", lieux=["KAR"])), 5)], 1)
    lancer(spark, base, [message("B", evenement("B", "d", 201), 6), message("B", None, 7)], 2)
    lancer(spark, base, [message("C", evenement("C", "u", 202, profil(genre="Autre", annee="1960", lieux=["x"]),
                                                 supprime=True), 8)], 3)  # fmt: skip
    assert faits(base) == [(JOUR, "KAR", "H", "26-35", 1)]

    # Événement plus ancien que l'état : ignoré.
    lancer(spark, base, [message("A", evenement("A", "u", 150, profil(genre="Female", lieux=["SAV-02"])), 9)], 4)
    assert faits(base) == [(JOUR, "KAR", "H", "26-35", 1)]
