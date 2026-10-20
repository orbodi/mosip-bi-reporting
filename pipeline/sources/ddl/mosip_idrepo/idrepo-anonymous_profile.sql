-- Structure de référence de idrepo.anonymous_profile, relevée le 20/10/2026 (pas une copie du fichier officiel).
-- Source : https://github.com/mosip/id-repository/blob/release-1.2.0/db_scripts/mosip_idrepo/ddl/idrepo-anonymous_profile.sql
-- La table apparaît en MOSIP 1.1.5.5 (docs.mosip.io/1.1.5/architecture/anonymous-profiling-support) ; elle est absente
-- du tag v1.1.5 (mosip_idrepo_ddl_deploy.sql voisin). Vérifier l'instance réelle avec la partie A de
-- pipeline/cdc/connecteurs/prerequis-idrepo.sql avant toute capture.
--
-- Colonnes capturées par le BI : id (empreinte HMAC), profile (lu par le job, jamais écrit), cr_dtimes, is_deleted.
-- Non capturées : cr_by, upd_by (identifiants d'utilisateurs), upd_dtimes, del_dtimes.

CREATE TABLE idrepo.anonymous_profile (
    id          character varying(36)  NOT NULL,
    profile     character varying      NOT NULL,
    cr_by       character varying(256) NOT NULL,
    cr_dtimes   timestamp              NOT NULL,
    upd_by      character varying(256),
    upd_dtimes  timestamp,
    is_deleted  boolean                DEFAULT FALSE,
    del_dtimes  timestamp,
    CONSTRAINT pk_profile PRIMARY KEY (id)
);
