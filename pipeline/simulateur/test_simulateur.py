"""Tests du simulateur MOSIP (sans base) : format des RID et codes utilisés."""

import random
from datetime import datetime

from simulateur import simulateur as sim

REGLAGES = sim.Reglages(dsn="", centres=("10011", "10012"), part_centre_inconnu=0.0)

# Énumérations MOSIP v1.1.5 (dépôt mosip/registration) : le simulateur ne doit rien utiliser d'autre.
STATUTS_MOSIP = {"FAILED", "REJECTED", "PROCESSING", "PROCESSED", "REPROCESS_FAILED"}
TYPES_MOSIP = {"NEW", "UPDATE", "RES_UPDATE", "CORRECTION", "ACTIVATED", "DEACTIVATED", "LOST", "RES_REPRINT"}


def test_rid_au_format_mosip():
    rid = sim.nouveau_rid(random.Random(1), REGLAGES, datetime(2026, 10, 15, 9, 30, 5))
    assert len(rid) == 29 and rid.isdigit()
    assert rid[:5] in REGLAGES.centres
    assert rid.endswith("20261015093005")


def test_centre_inconnu_quand_demande():
    reglages = sim.Reglages(dsn="", centres=("10011",), part_centre_inconnu=1.0)
    assert sim.nouveau_rid(random.Random(1), reglages, datetime(2026, 1, 1))[:5] == "99999"


def test_codes_issus_des_enumerations_mosip():
    assert {issue[0] for issue in sim.ISSUES} <= STATUTS_MOSIP
    assert {t[0] for t in sim.TYPES} <= TYPES_MOSIP
    hasard = random.Random(3)
    lignes = [sim.ligne(hasard, REGLAGES, datetime(2026, 10, 1), sim.tirer(hasard, sim.ISSUES)) for _ in range(50)]
    assert all(ligne_["status_code"] in STATUTS_MOSIP for ligne_ in lignes)
    en_cours = sim.ligne(hasard, REGLAGES, datetime(2026, 10, 1), None)
    assert en_cours["status_code"] == "PROCESSING" and en_cours["upd_dtimes"] is None
