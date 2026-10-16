"""Enregistre (ou met à jour) un connecteur Debezium dans Kafka Connect, puis attend qu'il tourne.

Développement : lancé par le service « connect-init » de deploy/docker-compose.yml. Idempotent (PUT de la
configuration). En recette et en production, l'enregistrement d'un connecteur est une action validée par
l'exploitation (skill mosip-bi-pipeline, règle 1) : ne pas utiliser cet outil sans cette validation.

Usage : python -m outils.enregistrer_connecteur <fichier.json> [--connect http://connect:8083] [--delai 600]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

# Au premier démarrage, le worker crée ses topics internes et Debezium valide la connexion TLS à la base avant de
# répondre au PUT : la réponse peut prendre bien plus de 10 s sur un poste chargé.
DELAI_REQUETE_S = 120


def appeler(methode: str, url: str, corps: dict | None = None, delai: float = 10) -> tuple[int, dict | list | None]:
    donnees = None if corps is None else json.dumps(corps).encode("utf-8")
    requete = urllib.request.Request(url, data=donnees, method=methode, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(requete, timeout=delai) as reponse:
            texte = reponse.read().decode("utf-8")
            return reponse.status, json.loads(texte) if texte else None
    except urllib.error.HTTPError as erreur:
        texte = erreur.read().decode("utf-8")
        return erreur.code, json.loads(texte) if texte.startswith("{") else {"message": texte}


def attendre_connect(base: str, limite: float) -> None:
    """Attend que le worker soit prêt : /health (Kafka récent), sinon /connector-plugins."""
    while time.monotonic() < limite:
        try:
            statut, _ = appeler("GET", f"{base}/health")
            if statut == 404:
                statut, _ = appeler("GET", f"{base}/connector-plugins")
            if statut == 200:
                return
        except OSError:
            pass
        print("En attente de Kafka Connect…", flush=True)
        time.sleep(5)
    raise SystemExit(f"Kafka Connect pas prêt sur {base}")


def enregistrer(base: str, nom: str, config: dict, limite: float) -> int:
    """PUT de la configuration, répété tant que le worker démarre (délai, 409, 5xx)."""
    while time.monotonic() < limite:
        try:
            statut, reponse = appeler("PUT", f"{base}/connectors/{nom}/config", config, DELAI_REQUETE_S)
        except OSError as erreur:
            print(f"Worker occupé ({type(erreur).__name__}), nouvel essai…", flush=True)
            time.sleep(5)
            continue
        if statut in (200, 201):
            return statut
        if statut == 409 or statut >= 500:
            print(f"Worker pas encore prêt ({statut}), nouvel essai…", flush=True)
            time.sleep(5)
            continue
        print(f"Échec de l'enregistrement de {nom} : {statut} {reponse}", file=sys.stderr)
        raise SystemExit(1)
    raise SystemExit(f"Connecteur {nom} non enregistré dans le délai")


def attendre_running(base: str, nom: str, limite: float) -> int:
    while time.monotonic() < limite:
        try:
            statut, etat = appeler("GET", f"{base}/connectors/{nom}/status")
        except OSError:
            statut, etat = 0, None
        if statut == 200 and isinstance(etat, dict):
            connecteur = etat["connector"]["state"]
            taches = [t["state"] for t in etat.get("tasks", [])]
            if "FAILED" in taches or connecteur == "FAILED":
                trace = next((t.get("trace", "") for t in etat.get("tasks", []) if t["state"] == "FAILED"), "")
                print(f"Connecteur {nom} en échec :\n{trace[:2000]}", file=sys.stderr)
                return 1
            if connecteur == "RUNNING" and taches and all(t == "RUNNING" for t in taches):
                print(f"Connecteur {nom} : RUNNING", flush=True)
                return 0
        time.sleep(3)
    print(f"Connecteur {nom} pas démarré dans le délai", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(description="Enregistre un connecteur Debezium (développement).")
    parseur.add_argument("fichier")
    parseur.add_argument("--connect", default="http://connect:8083")
    parseur.add_argument("--delai", type=int, default=600, help="attente maximale totale en secondes")
    args = parseur.parse_args(argv)

    with open(args.fichier, encoding="utf-8") as f:
        definition = json.load(f)
    nom, config = definition["name"], definition["config"]

    limite = time.monotonic() + args.delai
    attendre_connect(args.connect, limite)
    statut = enregistrer(args.connect, nom, config, limite)
    print(f"Connecteur {nom} {'créé' if statut == 201 else 'mis à jour'}", flush=True)
    return attendre_running(args.connect, nom, limite)


if __name__ == "__main__":
    sys.exit(main())
