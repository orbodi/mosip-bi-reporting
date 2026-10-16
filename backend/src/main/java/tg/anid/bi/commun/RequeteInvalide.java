package tg.anid.bi.commun;

/** Paramètres de requête incohérents (ex. date « du » après la date « au ») : réponse 400. */
public class RequeteInvalide extends RuntimeException {

    public RequeteInvalide(String message) {
        super(message);
    }
}
