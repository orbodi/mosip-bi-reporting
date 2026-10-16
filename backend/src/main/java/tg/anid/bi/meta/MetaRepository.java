package tg.anid.bi.meta;

import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.List;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

@Repository
public class MetaRepository {

    private final JdbcClient jdbc;

    public MetaRepository(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    public List<FraicheurSource> fraicheurs() {
        return jdbc.sql("""
                        select source, libelle, premiere_donnee, derniere_donnee, dernier_chargement
                        from bi.source_fraicheur
                        order by ordre
                        """)
                .query((rs, ligne) -> new FraicheurSource(
                        rs.getString("source"),
                        rs.getString("libelle"),
                        rs.getObject("premiere_donnee", LocalDate.class),
                        rs.getObject("derniere_donnee", OffsetDateTime.class),
                        rs.getObject("dernier_chargement", OffsetDateTime.class)))
                .list();
    }
}
