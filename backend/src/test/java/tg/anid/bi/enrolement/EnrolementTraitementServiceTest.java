package tg.anid.bi.enrolement;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.isNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.Test;

import tg.anid.bi.commun.RequeteInvalide;
import tg.anid.bi.commun.RessourceIntrouvable;

class EnrolementTraitementServiceTest {

    private final EnrolementTraitementRepository repository = mock(EnrolementTraitementRepository.class);
    private final EnrolementRepository zones = mock(EnrolementRepository.class);
    private final EnrolementTraitementService service = new EnrolementTraitementService(repository, zones);

    private static EnrolementTraitementRepository.Classe classe(int heures, long paquets) {
        return new EnrolementTraitementRepository.Classe(heures, paquets);
    }

    @Test
    void medianeCentileEtMoinsDe24hDepuisLHistogramme() {
        // 10 paquets : 3 à 2 h, 2 à 10 h, 4 à 30 h, 1 à 72 h. Médiane : 5e paquet → 10 h ; 90e centile : 9e → 30 h.
        DelaisTraitement.Mesure m = EnrolementTraitementService.mesure(
                List.of(classe(2, 3), classe(10, 2), classe(30, 4), classe(72, 1)));

        assertThat(m.paquets()).isEqualTo(10);
        assertThat(m.medianeH()).isEqualTo(10);
        assertThat(m.centile90H()).isEqualTo(30);
        assertThat(m.moins24h()).isEqualTo(5);
    }

    @Test
    void sansPaquetLaMedianeEtLeCentileSontNuls() {
        DelaisTraitement.Mesure m = EnrolementTraitementService.mesure(List.of());

        assertThat(m.paquets()).isZero();
        assertThat(m.medianeH()).isNull();
        assertThat(m.centile90H()).isNull();
    }

    @Test
    void lesPetitesEtapesSontRegroupeesEnDernierSaufSiUneSeule() {
        List<EnrolementTraitementRepository.ArretEtape> arrets = List.of(
                new EnrolementTraitementRepository.ArretEtape("rejete", "REFUS_POSTE", "Refus au poste", 25, 400),
                new EnrolementTraitementRepository.ArretEtape("rejete", "UPLOAD_PACKET", "Envoi du paquet", 30, 3),
                new EnrolementTraitementRepository.ArretEtape("rejete", "VALIDATE_PACKET", "Validation", 40, 590),
                new EnrolementTraitementRepository.ArretEtape("rejete", "QUALITY_CHECKER", "Qualité", 60, 7),
                new EnrolementTraitementRepository.ArretEtape("echoue", "OSI_VALIDATE", "Validation opérateur", 45, 200),
                new EnrolementTraitementRepository.ArretEtape("echoue", "PRINTING", "Impression", 80, 1));
        when(repository.arretsParEtape(isNull(), isNull(), isNull())).thenReturn(arrets);

        ArretsParEtape a = service.etapes(null, null, null);

        // Rejets : 1 000 ; Envoi (3) et Qualité (7) font moins de 1 % : « Autres étapes » (10), en dernier.
        assertThat(a.rejets()).extracting(ArretsParEtape.Etape::libelle)
                .containsExactly("Refus au poste", "Validation", "Autres étapes");
        assertThat(a.rejets().getLast().code()).isNull();
        assertThat(a.rejets().getLast().inscriptions()).isEqualTo(10);
        // Échecs : une seule petite étape (Impression, 1 sur 201) garde son nom.
        assertThat(a.echecs()).extracting(ArretsParEtape.Etape::code).containsExactly("OSI_VALIDATE", "PRINTING");
        // Totaux = sommes des lignes (contrôle avec le bloc « Devenir »).
        assertThat(a.totalRejets()).isEqualTo(1000);
        assertThat(a.totalEchecs()).isEqualTo(201);
        assertThat(a.perimetre()).isEqualTo("Ensemble du Togo");
    }

    @Test
    void enCoursTotalEtBloquesSommentLesEtapes() {
        when(repository.enCoursParEtape("KAR")).thenReturn(List.of(
                new EnrolementTraitementRepository.EnCoursEtape("PACKET_RECEIVER", "Réception du paquet", 10, 70, 0),
                new EnrolementTraitementRepository.EnCoursEtape("MANUAL_VERIFICATION", "Vérification manuelle", 55,
                        30, 25)));
        when(zones.nomZone("KAR")).thenReturn(Optional.of("Kara"));

        PaquetsEnCours p = service.enCours("KAR");

        assertThat(p.perimetre()).isEqualTo("Kara");
        assertThat(p.total()).isEqualTo(100);
        assertThat(p.bloques()).isEqualTo(25);
        assertThat(p.seuilJours()).isEqualTo(30);
    }

    @Test
    void zoneInconnueEtDatesInverseesSontRefusees() {
        when(zones.nomZone("XX")).thenReturn(Optional.empty());

        assertThatThrownBy(() -> service.synchronisation("XX")).isInstanceOf(RessourceIntrouvable.class);
        assertThatThrownBy(() -> service.delais(LocalDate.parse("2026-10-20"), LocalDate.parse("2026-10-01"), null))
                .isInstanceOf(RequeteInvalide.class);
    }
}
