package tg.anid.bi.commun;

/** Fonction indisponible faute de configuration (ex. clé du suivi d'un dossier absente) : réponse 503. */
public class ServiceIndisponible extends RuntimeException {

    public ServiceIndisponible(String message) {
        super(message);
    }
}
