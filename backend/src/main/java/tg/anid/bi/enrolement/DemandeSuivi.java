package tg.anid.bi.enrolement;

/**
 * Corps de POST /api/v1/enrolement/suivi. Le RID voyage dans le corps (jamais dans l'adresse, qui finit dans les
 * journaux des serveurs) ; {@link #toString()} le masque.
 *
 * @param rid numéro d'inscription, 29 chiffres
 */
public record DemandeSuivi(String rid) {

    @Override
    public String toString() {
        return "DemandeSuivi[rid=***]";
    }
}
