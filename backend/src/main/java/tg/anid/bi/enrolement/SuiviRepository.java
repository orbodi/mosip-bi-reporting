package tg.anid.bi.enrolement;

import java.time.OffsetDateTime;
import java.util.Optional;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

/** Lecture de bi.suivi_dossier par empreinte, écriture du journal des recherches (migration V8). */
@Repository
public class SuiviRepository {

    private final JdbcClient jdbc;

    public SuiviRepository(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    /** Une ligne de bi.suivi_dossier, avec le code et le nom de son centre. */
    public record Ligne(String centreCode, String centreNom, String typeDemande, OffsetDateTime enroleLe,
                        OffsetDateTime synchroniseLe, boolean refusPoste, OffsetDateTime recuLe,
                        OffsetDateTime niuLe, String devenir, String etape, String etapeLibelle, String etapeStatut,
                        OffsetDateTime derniereTransactionLe, OffsetDateTime majLe) {
    }

    /** Le dossier dont l'empreinte du RID est {@code empreinte}, s'il existe. */
    public Optional<Ligne> parEmpreinte(byte[] empreinte) {
        return jdbc.sql("""
                        select z.code as centre_code, z.nom as centre_nom, s.type_demande, s.enrole_le,
                               s.synchronise_le, s.refus_poste, s.recu_le, s.niu_le, s.devenir, s.etape,
                               s.etape_libelle, s.etape_statut, s.derniere_transaction_le, s.maj_le
                        from bi.suivi_dossier s
                        join bi.zone z on z.id = s.centre_id
                        where s.empreinte = :empreinte
                        """)
                .param("empreinte", empreinte)
                .query((rs, ligne) -> new Ligne(
                        rs.getString("centre_code"),
                        rs.getString("centre_nom"),
                        rs.getString("type_demande"),
                        rs.getObject("enrole_le", OffsetDateTime.class),
                        rs.getObject("synchronise_le", OffsetDateTime.class),
                        rs.getBoolean("refus_poste"),
                        rs.getObject("recu_le", OffsetDateTime.class),
                        rs.getObject("niu_le", OffsetDateTime.class),
                        rs.getString("devenir"),
                        rs.getString("etape"),
                        rs.getString("etape_libelle"),
                        rs.getString("etape_statut"),
                        rs.getObject("derniere_transaction_le", OffsetDateTime.class),
                        rs.getObject("maj_le", OffsetDateTime.class)))
                .optional();
    }

    /** Une recherche au journal : qui et avec quel résultat (trouve, introuvable, format) ; jamais le RID. */
    public void journaliser(String utilisateur, String resultat) {
        jdbc.sql("insert into bi.journal_suivi (utilisateur, resultat) values (:utilisateur, :resultat)")
                .param("utilisateur", utilisateur)
                .param("resultat", resultat)
                .update();
    }
}
