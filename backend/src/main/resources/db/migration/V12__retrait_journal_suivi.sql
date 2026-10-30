-- Retrait du registre des recherches du suivi d'un dossier (décision du responsable, 30/10/2026). La fenêtre de suivi
-- n'affiche ni nom, ni NIU, ni coordonnées, et un RID ne permet pas, en pratique, de remonter à une personne : le
-- registre (V8 : quand, qui, résultat ; jamais le RID) n'avait plus d'utilité. L'API n'y écrit plus depuis ce
-- changement ; la table et ses lignes sont supprimées.
drop table if exists bi.journal_suivi;
