package tg.anid.bi.authentifications;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDate;
import java.util.List;

/**
 * Bloc « Partenaires et canaux » : qui envoie les requêtes des usagers (partenaires, portail du résident, USSD), du
 * plus actif au moins actif. Le code MOSIP de l'appelant n'est pas renvoyé (décision du 04/11/2026). Contrôle : somme
 * des requêtes = requetes du bloc des usagers.
 *
 * @param du                   première date incluse, ou null
 * @param au                   dernière date incluse, ou null
 * @param partenairesRaccordes appelants de canal partenaire de la liste
 * @param appelants            une ligne par appelant ayant au moins une requête ou une demande de code sur la période
 */
public record PartenairesEtCanaux(LocalDate du, LocalDate au, long partenairesRaccordes, List<Appelant> appelants) {

    /**
     * Un appelant.
     *
     * @param canal           partenaire, portail, ussd ou non_classe
     * @param nom             nom déclaré dans MOSIP (partenaire) ou nom du service de l'ANID
     * @param requetes        authentifications envoyées
     * @param reussies        dont réussies
     * @param demandesOtp     demandes d'envoi d'un code OTP
     * @param derniereRequete jour de la requête ou de la demande de code la plus récente de la période
     */
    @Schema(name = "AppelantAuthentification")
    public record Appelant(String canal, String nom, long requetes, long reussies, long demandesOtp,
                           LocalDate derniereRequete) {
    }
}
