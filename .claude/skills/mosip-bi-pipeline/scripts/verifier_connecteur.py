#!/usr/bin/env python3
"""Vérifie une configuration de connecteur Debezium PostgreSQL au regard des règles du skill mosip-bi-pipeline.

Usage : python verifier_connecteur.py connecteur.json [autre.json ...]
Accepte le format de l'API Kafka Connect ({"name": ..., "config": {...}}) ou un objet de configuration à plat.
Code de sortie : 0 si aucune erreur (les avertissements n'échouent pas), 1 sinon. Bibliothèque standard seulement.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Colonnes jamais capturées (textes libres, contenus de requêtes, données d'identité ou biométriques).
COLONNES_INTERDITES = {
    "req_text",
    "resp_text",
    "res_text",
    "additional_info",
    "status_comment",
    "remarks",
    "client_status_comment",
    "uin",
    "uin_data",
    "uin_hash",
    "bio_data",
    "biometric",
    "full_name",
    "first_name",
    "last_name",
    "date_of_birth",
    "dob",
    "phone",
    "phone_number",
    "mobile_number",
    "email",
    "pincode",
    "photo",
}
# Interdites hors des référentiels « master » (où « name » désigne un lieu ou un centre, pas une personne).
COLONNES_PERSONNELLES_HORS_MASTER = {"name", "address", "addr_line1", "addr_line2", "addr_line3"}
# Tables d'identité, de documents, de biométrie ou de déduplication démographique : jamais capturées.
TABLES_INTERDITES = {
    "individual_demographic_dedup",
    "uin",
    "uin_h",
    "uin_biometric",
    "uin_biometric_h",
    "uin_document",
    "uin_document_h",
    "applicant_demographic",
    "applicant_document",
}
ENVIRONNEMENTS = ("dev", "test", "recette", "qualif", "preprod", "prod")
PROPRIETES_SECRETES = (
    "password",
    "secret",
    "token",
    "sasl.jaas.config",
    "ssl.keystore.password",
    "ssl.key.password",
    "ssl.truststore.password",
)
REFERENCE_SECRET = re.compile(r"^\$\{(file|env|vault|directory|aws|azure|gcp)[^}]*\}$")


def charger(chemin: Path) -> dict[str, str]:
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    config = donnees.get("config", donnees)
    if not isinstance(config, dict):
        raise ValueError("objet de configuration introuvable")
    return {str(k): str(v) for k, v in config.items()}


def verifier(config: dict[str, str]) -> tuple[list[str], list[str]]:
    erreurs: list[str] = []
    avertissements: list[str] = []
    get = config.get

    if get("connector.class") != "io.debezium.connector.postgresql.PostgresConnector":
        erreurs.append("connector.class doit être io.debezium.connector.postgresql.PostgresConnector")
    if get("plugin.name") != "pgoutput":
        erreurs.append("plugin.name doit valoir pgoutput (le défaut est decoderbufs)")
    if not get("topic.prefix"):
        erreurs.append("topic.prefix manquant (ne plus le changer une fois en service)")
    if not get("slot.name"):
        erreurs.append("slot.name manquant : nommer le slot explicitement (avec l'environnement)")
    elif not re.fullmatch(r"[a-z0-9_]+", get("slot.name", "")):
        erreurs.append("slot.name : minuscules, chiffres et _ uniquement")
    if get("slot.drop.on.stop", "false").lower() == "true":
        erreurs.append("slot.drop.on.stop=true interdit : un slot ne se supprime que par une procédure validée")
    if get("publication.autocreate.mode", "all_tables") != "disabled":
        erreurs.append("publication.autocreate.mode doit valoir disabled (publication créée par le DBA, FOR TABLE ...)")
    if not get("publication.name"):
        erreurs.append("publication.name manquant")

    tables = get("table.include.list", "")
    if not tables:
        erreurs.append("table.include.list manquant : lister explicitement les tables capturées")
    elif any(motif in tables for motif in (".*", "\\..*")) or re.search(r"(^|,)\s*[a-z_]+\.\*", tables):
        erreurs.append("table.include.list ne doit pas capturer un schéma entier par motif")
    if get("schema.include.list") and not tables:
        erreurs.append("schema.include.list seul capture tout le schéma : utiliser table.include.list")
    noms_tables = {t.strip().split(".")[-1].lower() for t in tables.split(",") if t.strip()}
    sensibles = sorted(noms_tables & TABLES_INTERDITES)
    if sensibles:
        erreurs.append(f"tables à données d'identité ou biométriques capturées : {', '.join(sensibles)}")

    mode_ssl = get("database.sslmode", "")
    if mode_ssl in ("disable", "allow", "prefer"):
        erreurs.append(f"database.sslmode={mode_ssl} : flux non garanti chiffré ; require au minimum")
    elif not mode_ssl:
        avertissements.append("database.sslmode absent (défaut prefer) : fixer require ou verify-full")

    # Cohérence d'environnement entre le nom, le slot et le préfixe des topics.
    def environnement(valeur: str) -> set[str]:
        jetons = set(re.split(r"[^a-z0-9]+", valeur.lower()))
        return {e for e in ENVIRONNEMENTS if e in jetons}

    envs = {cle: environnement(get(cle, "")) for cle in ("name", "slot.name", "topic.prefix")}
    trouves = set().union(*envs.values())
    if len(trouves) > 1:
        erreurs.append(f"environnements incohérents entre name, slot.name et topic.prefix : {sorted(trouves)}")
    elif not trouves:
        avertissements.append("aucun environnement (dev, recette, prod…) dans name, slot.name ou topic.prefix")
    hote = get("database.hostname", "").lower()
    if not hote.startswith("${") and trouves and "prod" not in trouves and "prod" in hote:
        erreurs.append(f"connecteur {sorted(trouves)} pointant vers un hôte de production ({hote})")

    colonnes = get("column.include.list", "")
    if not colonnes:
        erreurs.append("column.include.list manquant : minimisation obligatoire des colonnes")
    else:
        if get("column.exclude.list"):
            erreurs.append("column.include.list et column.exclude.list ne se combinent pas")
        # Chaque entrée est une expression « schema.table.colonne » ; on ne regarde que la partie colonne.
        noms: set[str] = set()
        for entree in colonnes.split(","):
            morceaux = entree.strip().split(".", 2)
            partie_colonne = morceaux[2] if len(morceaux) == 3 else entree
            trouves_ici = {n.lower() for n in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", partie_colonne)}
            interdites_ici = COLONNES_INTERDITES
            if morceaux[0].strip().lower() != "master":
                interdites_ici = COLONNES_INTERDITES | COLONNES_PERSONNELLES_HORS_MASTER
            noms.update(trouves_ici & interdites_ici)
        interdites = sorted(noms)
        if interdites:
            erreurs.append(f"colonnes interdites dans column.include.list : {', '.join(interdites)}")

    mode = get("snapshot.mode", "initial")
    if mode == "never":
        erreurs.append("snapshot.mode=never n'existe plus (Debezium 3.x) : utiliser no_data")
    elif mode == "always":
        erreurs.append("snapshot.mode=always relit toutes les tables à chaque redémarrage : à éviter")
    elif mode == "no_data" and not get("signal.data.collection"):
        erreurs.append("snapshot.mode=no_data sans snapshot incrémental : l'existant ne serait jamais chargé")
    elif mode not in {"initial", "initial_only", "no_data", "when_needed", "configuration_based", "custom"}:
        avertissements.append(f"snapshot.mode={mode} : valeur à vérifier dans la documentation de la version déployée")

    if "t" not in {x.strip() for x in get("skipped.operations", "t").split(",")}:
        avertissements.append(
            "skipped.operations ne contient pas t : les TRUNCATE seront émis (le job doit s'arrêter dessus)"
        )
    if get("decimal.handling.mode") == "double":
        avertissements.append("decimal.handling.mode=double : perte de précision possible, préférer string ou precise")
    if get("heartbeat.action.query") or get("signal.data.collection"):
        avertissements.append(
            "heartbeat.action.query / signal.data.collection écrivent dans la base MOSIP : dérogation écrite requise"
        )
    if not get("heartbeat.interval.ms") or get("heartbeat.interval.ms") == "0":
        avertissements.append(
            "heartbeat.interval.ms absent : le slot peut retenir du WAL si les tables capturées sont calmes"
        )
    if get("errors.log.include.messages", "false").lower() == "true":
        erreurs.append("errors.log.include.messages=true écrirait des identifiants dans les journaux")
    if get("delete.handling.mode") or get("transforms.unwrap.delete.handling.mode"):
        erreurs.append("delete.handling.mode a été supprimé (Debezium 3.2) : voir delete.tombstone.handling.mode")
    if "ExtractNewRecordState" in json.dumps(config):
        avertissements.append("SMT ExtractNewRecordState : le job Spark a besoin de op, before et source.lsn")

    for cle, valeur in config.items():
        if any(s in cle.lower() for s in PROPRIETES_SECRETES) and valeur and not REFERENCE_SECRET.match(valeur):
            erreurs.append(f"{cle} : valeur en clair ; utiliser ${{file:...}} ou ${{env:...}}")
        if cle.startswith("column.mask.hash") and ".with.salt." in cle:
            sel = cle.split(".with.salt.", 1)[1]
            if sel and not sel.startswith("${"):
                avertissements.append(f"{cle} : le sel figure dans le nom de la propriété ; le gérer comme un secret")

    return erreurs, avertissements


def main(arguments: list[str]) -> int:
    if not arguments:
        print(__doc__)
        return 2
    code = 0
    for nom in arguments:
        chemin = Path(nom)
        try:
            erreurs, avertissements = verifier(charger(chemin))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"{chemin} : illisible ({exc})")
            code = 1
            continue
        etat = "OK" if not erreurs else "ÉCHEC"
        print(f"{chemin} : {etat} ({len(erreurs)} erreur(s), {len(avertissements)} avertissement(s))")
        for e in erreurs:
            print(f"  ERREUR  {e}")
        for a in avertissements:
            print(f"  ATTENTION  {a}")
        if erreurs:
            code = 1
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
