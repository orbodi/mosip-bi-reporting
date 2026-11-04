package tg.anid.bi.authentifications;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.ArgumentMatchers.isNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.junit.jupiter.api.Test;

import tg.anid.bi.commun.RequeteInvalide;

class AuthentificationsServiceTest {

    private final AuthentificationsRepository repository = mock(AuthentificationsRepository.class);
    private final AuthentificationsService service = new AuthentificationsService(repository);

    @Test
    void sansSourceLeBlocDesUsagersEstNonDisponibleSansLireLesFaits() {
        when(repository.disponible()).thenReturn(false);

        RequetesUsagers u = service.usagers(null, null);

        assertThat(u.disponible()).isFalse();
        assertThat(u.requetes()).isNull();
        assertThat(u.partenaires()).isEmpty();
        verify(repository, never()).totaux(any(), any(), any());
    }

    @Test
    void usagersSeulementLesPartenairesComptentCommeRaccordes() {
        when(repository.disponible()).thenReturn(true);
        when(repository.totaux(eq("usagers"), isNull(), isNull())).thenReturn(
                new AuthentificationsRepository.Totaux(2186, 1538, 648, 0, 1, 1955, 0, 230, 0));
        when(repository.otp(isNull(), isNull())).thenReturn(new AuthentificationsRepository.Otp(2732, 352, 2380, 1440));
        when(repository.appelants(isNull(), isNull())).thenReturn(List.of(
                new AuthentificationsRepository.Appelant("AU-ANID", "partenaire", "Atos", 1645, 1142, 2159,
                        LocalDate.parse("2026-11-03")),
                new AuthentificationsRepository.Appelant("mosip-resident-client", "portail", "Portail du résident", 517,
                        377, 560, LocalDate.parse("2026-11-03"))));

        RequetesUsagers u = service.usagers(null, null);

        assertThat(u.requetes()).isEqualTo(2186);
        assertThat(u.partenairesRaccordes()).isEqualTo(1);
        assertThat(u.partenaires()).containsExactly("Atos");
        assertThat(u.requetesPartenaires()).isEqualTo(1645);
        assertThat(u.demandesOtpEnvoyees()).isEqualTo(2380);
        assertThat(u.codesOtpUtilises()).isEqualTo(1440);
    }

    @Test
    void typesCompletesAZeroDansLOrdreFixe() {
        when(repository.parType(isNull(), isNull())).thenReturn(Map.of("otp", new long[] {10, 2}));

        TypesAuthentification t = service.types(null, null);

        assertThat(t.types()).hasSize(6);
        assertThat(t.types().get(1).code()).isEqualTo("otp");
        assertThat(t.types().get(1).echecs()).isEqualTo(2);
        assertThat(t.types().getFirst().requetes()).isZero();
    }

    @Test
    void causesUsagersParDefautEtPerimetreInconnuRefuse() {
        when(repository.causes(eq("usagers"), isNull(), isNull())).thenReturn(List.of(
                new CausesEchec.Motif("OTP_REFUSE", "Code OTP ou eKYC refusé", 417),
                new CausesEchec.Motif("SANS_MODE", "Aucun mode d'authentification demandé", 230)));

        CausesEchec c = service.causes(null, null, null);

        assertThat(c.perimetre()).isEqualTo("usagers");
        assertThat(c.echecs()).isEqualTo(647);
        assertThatThrownBy(() -> service.causes("tout", null, null)).isInstanceOf(RequeteInvalide.class);
    }

    @Test
    void semainesVidesSansDonnee() {
        when(repository.derniereDonnee()).thenReturn(Optional.empty());

        assertThat(service.semaines(null, null).semaines()).isEmpty();
    }

    @Test
    void semainesBorneesALaFinDeLaPeriode() {
        when(repository.derniereDonnee()).thenReturn(Optional.of(LocalDate.parse("2026-11-04")));
        when(repository.usagersParSemaine(LocalDate.parse("2026-07-13"), LocalDate.parse("2026-10-04")))
                .thenReturn(Map.of(LocalDate.parse("2026-09-28"), new long[] {361, 151}));

        AuthentificationsParSemaine s = service.semaines(null, LocalDate.parse("2026-10-07"));

        assertThat(s.semaines()).hasSize(12);
        assertThat(s.semaines().getLast().lundi()).isEqualTo(LocalDate.parse("2026-09-28"));
        assertThat(s.semaines().getLast().reussies()).isEqualTo(361);
    }

    @Test
    void periodeInverseeRefusee() {
        assertThatThrownBy(() -> service.usagers(LocalDate.parse("2026-10-31"), LocalDate.parse("2026-10-01")))
                .isInstanceOf(RequeteInvalide.class);
    }
}
