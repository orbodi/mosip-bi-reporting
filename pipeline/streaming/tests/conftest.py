"""Fixtures des tests du pipeline : un vrai PostgreSQL et une session Spark locale.

Base de test créée à neuf, avec les VRAIES migrations du Data Mart (backend/src/main/resources/db) : V1, V2 puis
les données de démonstration R__. Variables :
- DATAMART_DSN_TEST : DSN d'un PostgreSQL où l'on peut créer une base
  (défaut : host=localhost user=bi dbname=postgres) ;
- MIGRATIONS_DIR : répertoire db/ du backend (défaut : chemin du dépôt).
"""

from __future__ import annotations

import os
import pathlib

import psycopg
import pytest
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from pyspark.sql import SparkSession

RACINE_DEPOT = pathlib.Path(__file__).resolve().parents[3]
MIGRATIONS = pathlib.Path(os.environ.get("MIGRATIONS_DIR", RACINE_DEPOT / "backend/src/main/resources/db"))
DSN_ADMIN = os.environ.get("DATAMART_DSN_TEST", "host=localhost user=bi dbname=postgres")
BASE_TEST = "bi_test_pipeline"


def _fichiers_migration() -> list[pathlib.Path]:
    versionnees = sorted((MIGRATIONS / "migration").glob("V*__*.sql"), key=lambda p: int(p.name[1:].split("__")[0]))
    return [*versionnees, *sorted((MIGRATIONS / "dev").glob("R__*.sql"))]


@pytest.fixture(scope="session")
def dsn() -> str:
    """Crée la base de test et y applique les migrations dans l'ordre de Flyway."""
    with psycopg.connect(DSN_ADMIN, autocommit=True) as admin:
        admin.execute(f"drop database if exists {BASE_TEST} with (force)")
        admin.execute(f"create database {BASE_TEST}")
    params = conninfo_to_dict(DSN_ADMIN)
    params["dbname"] = BASE_TEST
    dsn_test = make_conninfo(**params)
    with psycopg.connect(dsn_test, autocommit=True) as connexion:
        connexion.execute("create schema bi")
        for fichier in _fichiers_migration():
            connexion.execute(fichier.read_text(encoding="utf-8"))
    return dsn_test


@pytest.fixture()
def base(dsn: str):
    """Data Mart remis à l'état initial (migrations et données de démonstration) avant chaque test."""
    with psycopg.connect(dsn, autocommit=True) as connexion:
        connexion.execute(
            "truncate etat.registration, pipeline.lot_traite, pipeline.evenement_rejete, pipeline.controle_qualite,"
            " bi.fait_enrolement_jour"
        )
        connexion.execute(
            "update bi.source_fraicheur set premiere_donnee = '2024-01-01',"
            " derniere_donnee = '2026-01-14 11:42:00+00', dernier_chargement = null where source = 'enrolement'"
        )
    return dsn


@pytest.fixture(scope="session")
def spark():
    session = (
        SparkSession.builder.master("local[2]")
        .appName("tests-pipeline")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield session
    session.stop()
