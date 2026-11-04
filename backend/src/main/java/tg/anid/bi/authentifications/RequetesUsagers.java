package tg.anid.bi.authentifications;

import java.time.LocalDate;
import java.util.List;

/**
 * Bloc « Requêtes d'authentification des usagers » de la page Authentifications (docs/indicateurs.md : A-REQ, A-OK,
 * A-KO, A-TYPE, A-PART, A-OTP). Usagers : partenaires, portail du résident et USSD ; jamais les vérifications du
 * traitement des paquets (option A, 03/11/2026). Les demandes de code OTP ne sont pas des requêtes : comptées à part.
 * Contrôles : reussies + echouees + autresStatuts = requetes ; biometriques + otp + demographiquesEtCombinees +
 * sansMode + nonClassees = requetes. Les chiffres valent null tant que la source n'est pas alimentée.
 *
 * @param perimetre                 toujours « Ensemble du Togo » (une authentification n'a pas de territoire)
 * @param du                        première date incluse, ou null depuis le début
 * @param au                        dernière date incluse, ou null jusqu'à la dernière donnée
 * @param disponible                faux tant que le pipeline n'a publié aucune authentification
 * @param requetes                  authentifications des usagers sur la période (A-REQ)
 * @param reussies                  dont réussies (A-OK)
 * @param echouees                  dont échouées (A-KO)
 * @param autresStatuts             dont statut MOSIP inconnu (0 attendu)
 * @param biometriques              dont empreinte, iris ou visage seulement (A-TYPE)
 * @param otp                       dont code à usage unique, eKYC par code compris
 * @param demographiquesEtCombinees dont démographiques ou combinant plusieurs familles de modalités
 * @param sansMode                  dont sans modalité (eKYC sans mode demandé)
 * @param nonClassees               dont code de modalité inconnu (0 attendu)
 * @param partenairesRaccordes      partenaires ayant envoyé au moins une requête ou une demande de code (A-PART)
 * @param requetesPartenaires       requêtes envoyées par ces partenaires
 * @param partenaires               noms des partenaires, du plus actif au moins actif
 * @param demandesOtp               demandes d'envoi d'un code OTP des usagers
 * @param demandesOtpEnvoyees       dont acceptées par IDA (code envoyé)
 * @param codesOtp                  codes OTP demandés (ida.otp_transaction, tous appelants)
 * @param codesOtpUtilises          dont utilisés
 */
public record RequetesUsagers(String perimetre, LocalDate du, LocalDate au, boolean disponible, Long requetes,
                              Long reussies, Long echouees, Long autresStatuts, Long biometriques, Long otp,
                              Long demographiquesEtCombinees, Long sansMode, Long nonClassees,
                              Long partenairesRaccordes, Long requetesPartenaires, List<String> partenaires,
                              Long demandesOtp, Long demandesOtpEnvoyees, Long codesOtp, Long codesOtpUtilises) {

    static RequetesUsagers nonDisponible(String perimetre, LocalDate du, LocalDate au) {
        return new RequetesUsagers(perimetre, du, au, false, null, null, null, null, null, null, null, null, null,
                null, null, List.of(), null, null, null, null);
    }
}
