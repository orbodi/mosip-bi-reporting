package tg.anid.bi.enrolement;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.ArgumentMatchers.isNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;

import tg.anid.bi.commun.PorteeUtilisateur;
import tg.anid.bi.commun.RequeteInvalide;

class EnrolementServiceTest {

    private static final LocalDate MERCREDI_14_JANVIER = LocalDate.parse("2026-01-14");

    private final EnrolementRepository repository = mock(EnrolementRepository.class);
    private final EnrolementService service = new EnrolementService(repository, new PorteeUtilisateur());

    @AfterEach
    void nettoyer() {
        SecurityContextHolder.clearContext();
    }

    private static void connecterRegional(String zone) {
        Jwt jeton = Jwt.withTokenValue("jeton").header("alg", "none").claim("zone", zone).build();
        SecurityContextHolder.getContext().setAuthentication(
                new JwtAuthenticationToken(jeton, List.of(new SimpleGrantedAuthority("ROLE_BI_REGIONAL"))));
    }

    @Test
    void douzeSemainesCompletesJusquAuDernierDimanche() {
        List<LocalDate> lundis = EnrolementService.lundisDesSemainesCompletes(MERCREDI_14_JANVIER, 12);

        // Comme la maquette : du 20/10 au 05/01 quand la dernière donnée est le mercredi 14/01/2026.
        assertThat(lundis).hasSize(12);
        assertThat(lundis.getFirst()).isEqualTo("2025-10-20");
        assertThat(lundis.getLast()).isEqualTo("2026-01-05");
        assertThat(lundis).allSatisfy(lundi -> assertThat(lundi.getDayOfWeek()).hasToString("MONDAY"));
    }

    @Test
    void unDimancheTermineSaSemaineMaisUnLundiNeLaCommencePas() {
        assertThat(EnrolementService.lundisDesSemainesCompletes(LocalDate.parse("2026-01-11"), 12).getLast())
                .isEqualTo("2026-01-05");
        assertThat(EnrolementService.lundisDesSemainesCompletes(LocalDate.parse("2026-01-18"), 12).getLast())
                .isEqualTo("2026-01-12");
        assertThat(EnrolementService.lundisDesSemainesCompletes(LocalDate.parse("2026-01-12"), 12).getLast())
                .isEqualTo("2026-01-05");
    }

    @Test
    void uneSemaineEstDansLaPeriodeSiUnDeSesJoursYEst() {
        LocalDate lundi = LocalDate.parse("2026-01-05");
        assertThat(EnrolementService.touchePeriode(lundi, null, null)).isTrue();
        assertThat(EnrolementService.touchePeriode(lundi, LocalDate.parse("2026-01-11"), null)).isTrue();
        assertThat(EnrolementService.touchePeriode(lundi, LocalDate.parse("2026-01-12"), null)).isFalse();
        assertThat(EnrolementService.touchePeriode(lundi, null, LocalDate.parse("2026-01-05"))).isTrue();
        assertThat(EnrolementService.touchePeriode(lundi, null, LocalDate.parse("2026-01-04"))).isFalse();
    }

    @Test
    void lesSemainesSansDonneeValentZeroEtLaFinEstBorneeALaDerniereDonnee() {
        when(repository.niuDisponibles()).thenReturn(true);
        when(repository.derniereDonnee()).thenReturn(Optional.of(MERCREDI_14_JANVIER));
        LocalDate premierLundi = LocalDate.parse("2025-10-20");
        LocalDate dernierDimanche = LocalDate.parse("2026-01-11");
        when(repository.inscriptionsParSemaine(premierLundi, dernierDimanche, null))
                .thenReturn(Map.of(LocalDate.parse("2026-01-05"), 20230L));
        when(repository.niuParSemaine(premierLundi, dernierDimanche, null))
                .thenReturn(Map.of(LocalDate.parse("2026-01-05"), 17626L));

        // « au » après la dernière donnée : les semaines s'arrêtent à la dernière donnée.
        InscriptionsParSemaine s = service.semaines(LocalDate.parse("2025-12-20"), LocalDate.parse("2026-03-31"), null);

        assertThat(s.perimetre()).isEqualTo("Ensemble du Togo");
        assertThat(s.niuDisponibles()).isTrue();
        assertThat(s.semaines()).hasSize(12);
        InscriptionsParSemaine.Semaine derniere = s.semaines().getLast();
        assertThat(derniere.lundi()).isEqualTo("2026-01-05");
        assertThat(derniere.inscriptions()).isEqualTo(20230);
        assertThat(derniere.niuGeneres()).isEqualTo(17626);
        assertThat(s.semaines().getFirst().inscriptions()).isZero();
        // Semaines avant le 20/12 hors période (affichées en clair), celle du 15/12 la touche.
        assertThat(s.semaines()).filteredOn(InscriptionsParSemaine.Semaine::dansLaPeriode)
                .extracting(InscriptionsParSemaine.Semaine::lundi)
                .containsExactly(LocalDate.parse("2025-12-15"), LocalDate.parse("2025-12-22"),
                        LocalDate.parse("2025-12-29"), LocalDate.parse("2026-01-05"));
    }

    @Test
    void sansAucuneDonneeLaListeDesSemainesEstVide() {
        when(repository.derniereDonnee()).thenReturn(Optional.empty());

        InscriptionsParSemaine s = service.semaines(null, null, null);

        assertThat(s.semaines()).isEmpty();
        assertThat(s.niuDisponibles()).isFalse();
    }

    @Test
    void lesCentresSontNumerotesDansLOrdreDuClassement() {
        when(repository.topCentres(isNull(), isNull(), isNull(), eq("rejets"), eq(5))).thenReturn(List.of(
                new EnrolementRepository.Centre("10011", "Centre A", "Tône", "Savanes", 120, 3000),
                new EnrolementRepository.Centre("10021", "Centre B", "Kozah", "Kara", 80, 4000)));

        TopCentres top = service.centres(null, null, null, "rejets");

        assertThat(top.classement()).isEqualTo("rejets");
        assertThat(top.centres()).extracting(TopCentres.CentreClasse::rang).containsExactly(1, 2);
        assertThat(top.centres().getFirst().prefecture()).isEqualTo("Tône");
    }

    @Test
    void unClassementInconnuEstRefuse() {
        assertThatThrownBy(() -> service.centres(null, null, null, "pire"))
                .isInstanceOf(RequeteInvalide.class);
    }

    @Test
    void desDatesInverseesSontRefuseesPourChaqueBloc() {
        LocalDate du = LocalDate.parse("2026-01-14");
        LocalDate au = LocalDate.parse("2026-01-01");
        when(repository.topCentres(any(), any(), any(), any(), anyInt())).thenReturn(List.of());

        assertThatThrownBy(() -> service.semaines(du, au, null)).isInstanceOf(RequeteInvalide.class);
        assertThatThrownBy(() -> service.preinscriptions(du, au)).isInstanceOf(RequeteInvalide.class);
        assertThatThrownBy(() -> service.ageSexe(du, au, null)).isInstanceOf(RequeteInvalide.class);
        assertThatThrownBy(() -> service.territoire(du, au, null)).isInstanceOf(RequeteInvalide.class);
        assertThatThrownBy(() -> service.centres(du, au, null, "inscriptions")).isInstanceOf(RequeteInvalide.class);
    }

    @Test
    void lesPreinscriptionsSontNationalesAvecLaDerniereDemandeEtSansSexe() {
        OffsetDateTime derniere = OffsetDateTime.parse("2026-01-14T11:28:00Z");
        when(repository.preinscriptionsDisponibles()).thenReturn(true);
        when(repository.preinscriptions(null, null)).thenReturn(
                new EnrolementRepository.TotauxPreinscription(606850, 546964, 59886, 0, 0, 450000, 0, 0, 0));
        when(repository.derniereDemande()).thenReturn(Optional.of(derniere));

        Preinscriptions p = service.preinscriptions(null, null);

        assertThat(p.perimetre()).isEqualTo("Ensemble du Togo");
        assertThat(p.disponible()).isTrue();
        assertThat(p.demandes()).isEqualTo(606850);
        assertThat(p.rendezVousReserves() + p.enAttenteRendezVous() + p.expirees() + p.annulees()
                + p.nonClassees()).isEqualTo(p.demandes());
        assertThat(p.honorees()).isEqualTo(450000);
        assertThat(p.femmes()).isNull();
        assertThat(p.hommes()).isNull();
        assertThat(p.derniereDemande()).isEqualTo(derniere);
    }

    @Test
    void leSexeDesPreinscriptionsEstRenduDesQuIlEstConnu() {
        when(repository.preinscriptionsDisponibles()).thenReturn(true);
        when(repository.preinscriptions(null, null)).thenReturn(
                new EnrolementRepository.TotauxPreinscription(1000, 900, 100, 0, 0, 0, 0, 520, 430));

        Preinscriptions p = service.preinscriptions(null, null);

        assertThat(p.femmes()).isEqualTo(520);
        assertThat(p.hommes()).isEqualTo(430);
        assertThat(p.demandes() - p.femmes() - p.hommes()).isEqualTo(50);
    }

    @Test
    void leProfilDesPreinscritsAHuitTranchesEtLesCinqPremieresNationalites() {
        when(repository.profilPreinscriptionsDisponible()).thenReturn(true);
        when(repository.preinscriptionsParProfil(null, null)).thenReturn(List.of(
                new EnrolementRepository.CasePreinscription("F", "26-35", "TOGO", 500),
                new EnrolementRepository.CasePreinscription("H", "26-35", "TOGO", 400),
                new EnrolementRepository.CasePreinscription("H", "19-25", "BENIN", 30),
                new EnrolementRepository.CasePreinscription("F", "6-14", "GHANA", 20),
                new EnrolementRepository.CasePreinscription("H", "36-45", "NIGERIA", 9),
                new EnrolementRepository.CasePreinscription("F", "46-60", "BURKINA FASO", 8),
                new EnrolementRepository.CasePreinscription("H", "60+", "MALI", 3),
                new EnrolementRepository.CasePreinscription("F", "15-18", "NIGER", 2),
                new EnrolementRepository.CasePreinscription("F", "inconnu", "TOGO", 6),
                new EnrolementRepository.CasePreinscription("H", "inconnu", "TOGO", 4),
                new EnrolementRepository.CasePreinscription("I", "inconnu", "Non renseignée", 70)));

        ProfilPreinscriptions p = service.profilPreinscriptions(null, null);

        assertThat(p.disponible()).isTrue();
        assertThat(p.tranches()).hasSize(9);
        assertThat(p.tranches().getLast()).satisfies(t -> {
            assertThat(t.tranche()).isEqualTo("inconnu");
            assertThat(t.femmes()).isEqualTo(6);
            assertThat(t.hommes()).isEqualTo(4);
        });
        assertThat(p.tranches()).filteredOn(t -> t.tranche().equals("26-35")).singleElement()
                .satisfies(t -> {
                    assertThat(t.femmes()).isEqualTo(500);
                    assertThat(t.hommes()).isEqualTo(400);
                });
        assertThat(p.nonRenseignes()).isEqualTo(70);
        assertThat(p.nationalites()).extracting(ProfilPreinscriptions.Nationalite::nom)
                .containsExactly("TOGO", "BENIN", "GHANA", "NIGERIA", "BURKINA FASO", "Autres", "Non renseignée");
        assertThat(p.nationalites().get(5).demandes()).isEqualTo(5);
        long totalTranches = p.tranches().stream().mapToLong(t -> t.femmes() + t.hommes()).sum();
        long totalNationalites = p.nationalites().stream().mapToLong(ProfilPreinscriptions.Nationalite::demandes).sum();
        assertThat(totalTranches + p.nonRenseignes()).isEqualTo(totalNationalites).isEqualTo(1052);
        long femmes = p.tranches().stream().mapToLong(AgeSexe.Tranche::femmes).sum();
        assertThat(femmes).isEqualTo(536);
    }

    @Test
    void sansProfilAlimenteLeProfilDesPreinscritsEstNonDisponible() {
        when(repository.profilPreinscriptionsDisponible()).thenReturn(false);

        ProfilPreinscriptions p = service.profilPreinscriptions(null, null);

        assertThat(p.disponible()).isFalse();
        assertThat(p.tranches()).hasSize(9).allSatisfy(t -> assertThat(t.femmes()).isNull());
        assertThat(p.nationalites()).isEmpty();
    }

    @Test
    void unUtilisateurRegionalNeRecoitPasLeProfilNational() {
        connecterRegional("KAR");
        when(repository.nomZone("KAR")).thenReturn(Optional.of("Kara"));

        ProfilPreinscriptions p = service.profilPreinscriptions(null, null);

        assertThat(p.perimetre()).isEqualTo("Kara");
        assertThat(p.disponible()).isFalse();
    }

    @Test
    void sansDonneesDuPipelineLesPreinscriptionsSontNonDisponibles() {
        when(repository.preinscriptionsDisponibles()).thenReturn(false);

        Preinscriptions p = service.preinscriptions(null, null);

        assertThat(p.disponible()).isFalse();
        assertThat(p.demandes()).isNull();
        assertThat(p.derniereDemande()).isNull();
    }

    @Test
    void unUtilisateurRegionalNeRecoitPasLesPreinscriptionsNationales() {
        connecterRegional("KAR");
        when(repository.nomZone("KAR")).thenReturn(Optional.of("Kara"));
        when(repository.preinscriptionsDisponibles()).thenReturn(true);

        Preinscriptions p = service.preinscriptions(null, null);

        assertThat(p.perimetre()).isEqualTo("Kara");
        assertThat(p.disponible()).isFalse();
        assertThat(p.demandes()).isNull();
    }

    @Test
    void laPyramideALesHuitTranchesEtCompteLesNonRenseignesAPart() {
        when(repository.profilsDisponibles()).thenReturn(true);
        when(repository.niuParSexeEtAge(null, null, null)).thenReturn(List.of(
                new EnrolementRepository.CaseProfil("F", "26-35", 126),
                new EnrolementRepository.CaseProfil("H", "26-35", 111),
                new EnrolementRepository.CaseProfil("H", "0-5", 12),
                new EnrolementRepository.CaseProfil("I", "26-35", 7),
                new EnrolementRepository.CaseProfil("F", "inconnu", 3)));

        AgeSexe a = service.ageSexe(null, null, null);

        assertThat(a.disponible()).isTrue();
        assertThat(a.tranches()).extracting(AgeSexe.Tranche::tranche)
                .containsExactly("0-5", "6-14", "15-18", "19-25", "26-35", "36-45", "46-60", "60+");
        AgeSexe.Tranche t = a.tranches().get(4);
        assertThat(t.femmes()).isEqualTo(126);
        assertThat(t.hommes()).isEqualTo(111);
        assertThat(a.tranches().getFirst().femmes()).isZero();
        assertThat(a.tranches().getFirst().hommes()).isEqualTo(12);
        assertThat(a.nonRenseignes()).isEqualTo(10);
    }

    @Test
    void sansProfilsLaPyramideGardeSesTranchesSansChiffres() {
        when(repository.profilsDisponibles()).thenReturn(false);

        AgeSexe a = service.ageSexe(null, null, null);

        assertThat(a.disponible()).isFalse();
        assertThat(a.tranches()).hasSize(8).allSatisfy(t -> assertThat(t.femmes()).isNull());
        assertThat(a.nonRenseignes()).isNull();
    }

    @Test
    void laPyramideNExistePasPourUnePrefecture() {
        when(repository.nomZone("SAV-02")).thenReturn(Optional.of("Tône"));
        when(repository.estRegion("SAV-02")).thenReturn(false);

        assertThatThrownBy(() -> service.ageSexe(null, null, "SAV-02")).isInstanceOf(RequeteInvalide.class);
    }
}
