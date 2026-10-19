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
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.junit.jupiter.api.Test;

import tg.anid.bi.commun.PorteeUtilisateur;
import tg.anid.bi.commun.RequeteInvalide;

class EnrolementServiceTest {

    private static final LocalDate MERCREDI_14_JANVIER = LocalDate.parse("2026-01-14");

    private final EnrolementRepository repository = mock(EnrolementRepository.class);
    private final EnrolementService service = new EnrolementService(repository, new PorteeUtilisateur());

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
        assertThatThrownBy(() -> service.territoire(du, au, null)).isInstanceOf(RequeteInvalide.class);
        assertThatThrownBy(() -> service.centres(du, au, null, "inscriptions")).isInstanceOf(RequeteInvalide.class);
    }
}
