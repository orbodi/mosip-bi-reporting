package tg.anid.bi.enrolement;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.time.Clock;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.Test;

import tg.anid.bi.commun.RequeteInvalide;
import tg.anid.bi.commun.RessourceIntrouvable;
import tg.anid.bi.commun.ServiceIndisponible;

class SuiviServiceTest {

    private static final String RID = "20101100230041220261021093015";
    private static final Clock HORLOGE = Clock.fixed(Instant.parse("2026-10-26T10:00:00Z"), ZoneOffset.UTC);

    private final SuiviRepository repository = mock(SuiviRepository.class);
    private final EnrolementRepository zones = mock(EnrolementRepository.class);
    private final SuiviService service = new SuiviService(repository, zones, "cle-du-banc", HORLOGE);

    private static SuiviRepository.Ligne ligne(String devenir, OffsetDateTime derniereTransaction) {
        return new SuiviRepository.Ligne("10011", "EPP Worgou G/A", "NEW",
                OffsetDateTime.parse("2026-07-04T11:18:42Z"), OffsetDateTime.parse("2026-07-04T11:52:00Z"), false,
                OffsetDateTime.parse("2026-07-04T12:03:00Z"), null, devenir, "MANUAL_VERIFICATION",
                "Vérification manuelle", "IN_PROGRESS", derniereTransaction, "FILE_VERIF_MANUELLE",
                "En file d’attente de vérification manuelle", "Manual verification Sent to queue",
                OffsetDateTime.parse("2026-10-26T09:55:00Z"));
    }

    @Test
    void lEmpreinteEstCelleDePgcrypto() {
        // select encode(hmac('20101100230041220261021093015', 'cle-du-banc', 'sha256'), 'hex') sur PostgreSQL.
        assertThat(HexFormat.of().formatHex(SuiviService.empreinte(RID, "cle-du-banc")))
                .isEqualTo("177634ac08f8f97e811318701303e4991ee48aa73dc72092d67490e1a5b9f4b6");
    }

    @Test
    void unDossierEnCoursDepuisPlusDe30JoursEstBloque() {
        when(repository.parEmpreinte(any())).thenReturn(Optional.of(
                ligne("en_cours", OffsetDateTime.parse("2026-07-05T03:10:00Z"))));
        when(zones.ascendants("10011")).thenReturn(List.of(
                new Territoire.ZoneParente("SAV", "Savanes", "region"),
                new Territoire.ZoneParente("SAV-02", "Tône", "prefecture")));

        SuiviDossier d = service.suivre(RID);

        assertThat(d.bloque()).isTrue();
        assertThat(d.centre()).isEqualTo(new SuiviDossier.Centre("EPP Worgou G/A", "Tône", "Savanes"));
        assertThat(d.etape().libelle()).isEqualTo("Vérification manuelle");
        assertThat(d.motif()).isEqualTo(new SuiviDossier.Motif("FILE_VERIF_MANUELLE",
                "En file d’attente de vérification manuelle", "Manual verification Sent to queue"));
        assertThat(d.jalons().niuLe()).isNull();
    }

    @Test
    void unDossierRecentNEstPasBloque() {
        when(repository.parEmpreinte(any())).thenReturn(Optional.of(
                ligne("en_cours", OffsetDateTime.parse("2026-10-20T08:00:00Z"))));

        assertThat(service.suivre(RID).bloque()).isFalse();
    }

    @Test
    void sansMotifPasDeMotifEtUnMotifHorsCatalogueGardeSonCode() {
        SuiviRepository.Ligne l = ligne("en_cours", OffsetDateTime.parse("2026-10-20T08:00:00Z"));
        when(repository.parEmpreinte(any())).thenReturn(Optional.of(new SuiviRepository.Ligne(l.centreCode(),
                l.centreNom(), l.typeDemande(), l.enroleLe(), l.synchroniseLe(), l.refusPoste(), l.recuLe(),
                l.niuLe(), "niu", l.etape(), l.etapeLibelle(), l.etapeStatut(), l.derniereTransactionLe(), null, null,
                null, l.majLe())));
        assertThat(service.suivre(RID).motif()).isNull();

        when(repository.parEmpreinte(any())).thenReturn(Optional.of(new SuiviRepository.Ligne(l.centreCode(),
                l.centreNom(), l.typeDemande(), l.enroleLe(), l.synchroniseLe(), l.refusPoste(), l.recuLe(),
                l.niuLe(), "echoue", l.etape(), l.etapeLibelle(), l.etapeStatut(), l.derniereTransactionLe(),
                "NOUVEAU_MOTIF", null, null, l.majLe())));
        assertThat(service.suivre(RID).motif()).isEqualTo(new SuiviDossier.Motif("NOUVEAU_MOTIF", "NOUVEAU_MOTIF", null));
    }

    @Test
    void unRidMalFormeEstRefuseSansRecherche() {
        assertThatThrownBy(() -> service.suivre("2010110023")).isInstanceOf(RequeteInvalide.class)
                .hasMessage("Le RID compte 29 chiffres.");
        assertThatThrownBy(() -> service.suivre(null)).isInstanceOf(RequeteInvalide.class);
        verify(repository, never()).parEmpreinte(any());
    }

    @Test
    void unRidInconnuDonne404SansLeRidDansLeMessage() {
        when(repository.parEmpreinte(any())).thenReturn(Optional.empty());

        assertThatThrownBy(() -> service.suivre(RID)).isInstanceOf(RessourceIntrouvable.class)
                .hasMessage("Ce RID ne correspond à aucun dossier ou paquet.")
                .hasMessageNotContaining(RID);
    }

    @Test
    void sansCleLeSuiviEstIndisponible() {
        SuiviService sansCle = new SuiviService(repository, zones, "", HORLOGE);

        assertThatThrownBy(() -> sansCle.suivre(RID)).isInstanceOf(ServiceIndisponible.class);
        verify(repository, never()).parEmpreinte(any());
    }
}
