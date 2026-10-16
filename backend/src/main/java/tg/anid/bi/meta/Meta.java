package tg.anid.bi.meta;

import java.util.List;

/** Informations générales affichées par toutes les pages (pastille « Dernière mise à jour »). */
public record Meta(String application, List<FraicheurSource> sources) {
}
