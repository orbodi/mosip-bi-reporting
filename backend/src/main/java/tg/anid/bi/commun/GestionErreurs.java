package tg.anid.bi.commun;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataAccessException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/** Erreurs au format Problem Details (RFC 9457), sans détail technique côté client. */
@RestControllerAdvice
public class GestionErreurs {

    private static final Logger LOG = LoggerFactory.getLogger(GestionErreurs.class);

    @ExceptionHandler(RequeteInvalide.class)
    ProblemDetail requeteInvalide(RequeteInvalide e) {
        ProblemDetail probleme = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, e.getMessage());
        probleme.setTitle("Paramètres invalides");
        return probleme;
    }

    @ExceptionHandler(RessourceIntrouvable.class)
    ProblemDetail introuvable(RessourceIntrouvable e) {
        ProblemDetail probleme = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, e.getMessage());
        probleme.setTitle("Introuvable");
        return probleme;
    }

    @ExceptionHandler(AccessDeniedException.class)
    ProblemDetail horsPortee(AccessDeniedException e) {
        ProblemDetail probleme = ProblemDetail.forStatusAndDetail(HttpStatus.FORBIDDEN, e.getMessage());
        probleme.setTitle("Accès refusé");
        return probleme;
    }

    @ExceptionHandler(DataAccessException.class)
    ProblemDetail baseIndisponible(DataAccessException e) {
        LOG.error("Erreur d'accès à la base BI", e);
        ProblemDetail probleme = ProblemDetail.forStatus(HttpStatus.SERVICE_UNAVAILABLE);
        probleme.setTitle("Base BI indisponible");
        probleme.setDetail("Les données ne peuvent pas être lues pour le moment.");
        return probleme;
    }
}
