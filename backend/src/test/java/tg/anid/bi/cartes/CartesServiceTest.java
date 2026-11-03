package tg.anid.bi.cartes;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.ArgumentMatchers.isNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.time.Clock;
import java.time.Instant;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.junit.jupiter.api.Test;

import tg.anid.bi.commun.RequeteInvalide;
import tg.anid.bi.commun.RessourceIntrouvable;
import tg.anid.bi.enrolement.EnrolementRepository;

class CartesServiceTest {

    private final CartesRepository repository = mock(CartesRepository.class);
    private final EnrolementRepository zones = mock(EnrolementRepository.class);
    private final CartesService service = new CartesService(repository, zones,
            Clock.fixed(Instant.parse("2026-11-03T08:00:00Z"), CartesService.TOGO));

    @Test
    void sansSourceLeBlocImpressionEstNonDisponibleSansLireLesFaits() {
        when(repository.disponible()).thenReturn(false);

        ImpressionRemise i = service.impression(null, null, null);

        assertThat(i.perimetre()).isEqualTo("Ensemble du Togo");
        assertThat(i.disponible()).isFalse();
        assertThat(i.demandes()).isNull();
        assertThat(i.remises()).isNull();
        verify(repository, never()).demandes(any(), any(), any());
    }

    @Test
    void impressionReprendLesTotauxEtLeDelaiMedian() {
        when(repository.disponible()).thenReturn(true);
        when(zones.nomZone("SAV")).thenReturn(Optional.of("Savanes"));
        when(repository.demandes(isNull(), isNull(), eq("SAV"))).thenReturn(
                new CartesRepository.TotauxDemandes(150, 145, 4, 1, 0, 2, LocalDate.parse("2026-10-04"), 12,
                        LocalDate.parse("2026-09-30")));
        when(repository.niuSansCommande("SAV")).thenReturn(new CartesRepository.NiuSansCommande(5, 3));
        when(repository.cartes(isNull(), isNull(), eq("SAV"))).thenReturn(
                new CartesRepository.TotauxCartes(130, 100, 90, 10, 0, 0, 30));
        when(repository.delaiMedianJours(isNull(), isNull(), eq("SAV"))).thenReturn(Optional.of(34));

        ImpressionRemise i = service.impression(null, null, "SAV");

        assertThat(i.perimetre()).isEqualTo("Savanes");
        assertThat(i.demandes()).isEqualTo(150);
        assertThat(i.annulees()).isEqualTo(2);
        assertThat(i.derniereRejetee()).isEqualTo("2026-10-04");
        assertThat(i.remises() + i.aRemettre()).isEqualTo(i.expediees());
        assertThat(i.delaiMedianJours()).isEqualTo(34);
        assertThat(i.erreursIdps()).isEqualTo(12);
        assertThat(i.derniereErreurIdps()).isEqualTo("2026-09-30");
        assertThat(i.niuSansCommande()).isEqualTo(5);
        assertThat(i.niuSansCommandePlus7j()).isEqualTo(3);
    }

    @Test
    void surUnePeriodeLesNiuSansCommandeNeSontPasDonnes() {
        LocalDate du = LocalDate.parse("2026-10-01");
        LocalDate au = LocalDate.parse("2026-10-31");
        when(repository.disponible()).thenReturn(true);
        when(repository.demandes(du, au, null)).thenReturn(
                new CartesRepository.TotauxDemandes(10, 10, 0, 0, 0, 0, null, 0, null));
        when(repository.cartes(du, au, null)).thenReturn(new CartesRepository.TotauxCartes(8, 5, 5, 0, 0, 0, 3));
        when(repository.delaiMedianJours(du, au, null)).thenReturn(Optional.empty());

        ImpressionRemise i = service.impression(du, au, null);

        assertThat(i.niuSansCommande()).isNull();
        assertThat(i.niuSansCommandePlus7j()).isNull();
        verify(repository, never()).niuSansCommande(any());
    }

    @Test
    void zoneInconnueEtPeriodeInverseeSontRefusees() {
        when(zones.nomZone("XXX")).thenReturn(Optional.empty());

        assertThatThrownBy(() -> service.impression(null, null, "XXX")).isInstanceOf(RessourceIntrouvable.class);
        assertThatThrownBy(() -> service.attente(LocalDate.parse("2026-10-31"), LocalDate.parse("2026-10-01"), null))
                .isInstanceOf(RequeteInvalide.class);
    }

    @Test
    void semainesSansDonneeSontVidesEtSemainesSansChiffreValentZero() {
        when(repository.derniereDonnee()).thenReturn(Optional.empty());
        assertThat(service.semaines(null, null, null).semaines()).isEmpty();

        when(repository.derniereDonnee()).thenReturn(Optional.of(LocalDate.parse("2026-01-14")));
        when(repository.demandesParSemaine(any(), any(), isNull()))
                .thenReturn(Map.of(LocalDate.parse("2026-01-05"), new long[] {230, 3, 2}));
        when(repository.expedieesParSemaine(any(), any(), isNull()))
                .thenReturn(Map.of(LocalDate.parse("2026-01-05"), 200L));

        ImpressionsParSemaine s = service.semaines(null, null, null);
        assertThat(s.semaines()).hasSize(12);
        assertThat(s.semaines().getFirst().lundi()).isEqualTo("2025-10-20");
        assertThat(s.semaines().getFirst().demandes()).isZero();
        assertThat(s.semaines().getLast())
                .isEqualTo(new ImpressionsParSemaine.Semaine(LocalDate.parse("2026-01-05"), true, 230, 200, 3, 2));
    }

    @Test
    void attenteDonneLesQuatreTranchesDansLOrdreAvecLeJourDuCalcul() {
        when(repository.aRemettreParAnciennete(isNull(), isNull(), isNull(), eq(LocalDate.parse("2026-11-03"))))
                .thenReturn(Map.of("moins_30j", 96L, "plus_180j", 563L));

        CartesEnAttente a = service.attente(null, null, null);

        assertThat(a.calculeLe()).isEqualTo("2026-11-03");
        assertThat(a.aRemettre()).isEqualTo(659);
        assertThat(a.tranches()).extracting(CartesEnAttente.Tranche::code)
                .containsExactly("moins_30j", "30_90j", "90_180j", "plus_180j");
        assertThat(a.tranches()).extracting(CartesEnAttente.Tranche::cartes).containsExactly(96L, 0L, 0L, 563L);
        assertThat(a.tranches().getLast().avantJours()).isNull();
    }

    @Test
    void topDesCentresNumeroteLesRangsEtAnnulationsFontLeTotal() {
        when(repository.topCentres(isNull(), isNull(), isNull(), eq(5))).thenReturn(List.of(
                new CartesRepository.Centre("10011", "EPP A", "Golfe", "Grand Lomé", 31289, 44370),
                new CartesRepository.Centre("10012", "EPP B", "Golfe", "Grand Lomé", 11818, 16033)));
        when(repository.annulationsParMotif(isNull(), isNull(), isNull())).thenReturn(List.of(
                new AnnulationsParMotif.Motif("CANCEL_PHOTO", "Photo à reprendre", 643),
                new AnnulationsParMotif.Motif("CANCEL_SEX", "Sexe à corriger", 36)));

        assertThat(service.centres(null, null, null).centres())
                .extracting(TopCentresCartes.CentreClasse::rang).containsExactly(1, 2);
        assertThat(service.annulations(null, null, null).total()).isEqualTo(679);
    }
}
