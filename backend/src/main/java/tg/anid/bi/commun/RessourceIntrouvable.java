package tg.anid.bi.commun;

/** Ressource demandée absente (ex. code de zone inconnu) : réponse 404. */
public class RessourceIntrouvable extends RuntimeException {

    public RessourceIntrouvable(String message) {
        super(message);
    }
}
