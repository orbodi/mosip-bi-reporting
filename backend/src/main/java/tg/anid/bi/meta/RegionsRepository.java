package tg.anid.bi.meta;

import java.util.List;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

@Repository
public class RegionsRepository {

    /** Zone technique de la migration V2 (centres absents du référentiel) : pas une région du filtre. */
    static final String ZONE_HORS_REFERENTIEL = "HORS_REFERENTIEL";

    private final JdbcClient jdbc;

    public RegionsRepository(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    /** Régions du référentiel, du nord au sud. */
    public List<Region> regions() {
        return jdbc.sql("""
                        select code, nom
                        from bi.zone
                        where niveau = 'region' and code <> :horsReferentiel
                        order by ordre, nom
                        """)
                .param("horsReferentiel", ZONE_HORS_REFERENTIEL)
                .query((rs, ligne) -> new Region(rs.getString("code"), rs.getString("nom")))
                .list();
    }
}
