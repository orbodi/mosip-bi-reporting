"""Test de l'enregistrement du connecteur contre un faux Kafka Connect qui démarre lentement."""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from outils import enregistrer_connecteur as outil


class FauxConnect(BaseHTTPRequestHandler):
    """Santé d'abord en 503, PUT d'abord en 409 (rééquilibrage), puis connecteur RUNNING."""

    appels: list[str] = []
    sante = 0
    puts = 0

    def log_message(self, *args):  # silence
        pass

    def repondre(self, statut: int, corps: dict | None = None):
        texte = json.dumps(corps or {}).encode()
        self.send_response(statut)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(texte)))
        self.end_headers()
        self.wfile.write(texte)

    def do_GET(self):  # noqa: N802
        FauxConnect.appels.append(f"GET {self.path}")
        if self.path == "/health":
            FauxConnect.sante += 1
            self.repondre(200 if FauxConnect.sante > 1 else 503, {"status": "healthy"})
        elif self.path.endswith("/status"):
            self.repondre(200, {"connector": {"state": "RUNNING"}, "tasks": [{"id": 0, "state": "RUNNING"}]})
        else:
            self.repondre(404)

    def do_PUT(self):  # noqa: N802
        longueur = int(self.headers["Content-Length"])
        config = json.loads(self.rfile.read(longueur))
        FauxConnect.appels.append(f"PUT {self.path} {config['slot.name']}")
        FauxConnect.puts += 1
        self.repondre(409 if FauxConnect.puts == 1 else 201, {"name": "x"})


def test_enregistre_malgre_un_worker_lent(tmp_path, monkeypatch):
    monkeypatch.setattr(outil.time, "sleep", lambda _s: None)
    serveur = HTTPServer(("127.0.0.1", 0), FauxConnect)
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    fichier = tmp_path / "c.json"
    fichier.write_text(json.dumps({"name": "bi-cdc-regprc-dev", "config": {"slot.name": "bi_cdc_regprc_dev"}}))
    try:
        code = outil.main([str(fichier), "--connect", f"http://127.0.0.1:{serveur.server_port}", "--delai", "30"])
    finally:
        serveur.shutdown()
    assert code == 0
    assert FauxConnect.appels.count("PUT /connectors/bi-cdc-regprc-dev/config bi_cdc_regprc_dev") == 2
    assert FauxConnect.appels[-1] == "GET /connectors/bi-cdc-regprc-dev/status"
