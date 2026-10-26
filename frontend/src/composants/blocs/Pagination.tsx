import { nf } from '../../lib/format';
import { TAILLES_PAGE, numerosDePage, type TaillePage } from '../../lib/pagination';
import { Chevron } from './Icone';
import './blocs.css';

interface Props {
  /** Page affichée (de 0), nombre de pages, rang de la première et de la dernière ligne, nombre de lignes. */
  page: number;
  pages: number;
  debut: number;
  fin: number;
  total: number;
  taille: TaillePage;
  /** Ce que comptent les lignes, au pluriel (« localités »), pour les lecteurs d'écran. */
  quoi: string;
  onPage: (page: number) => void;
  onTaille: (taille: TaillePage) => void;
}

/**
 * Pagination sous un tableau : « 21–40 sur 137 », choix de 10 ou 20 lignes par page, pages numérotées. Absente quand
 * toutes les lignes tiennent dans la plus petite page.
 */
export function Pagination({ page, pages, debut, fin, total, taille, quoi, onPage, onTaille }: Props) {
  if (total <= TAILLES_PAGE[0]) return null;
  return (
    <div className="pagination">
      <p className="texte-2 pagination__position" aria-live="polite">
        {nf(debut)}–{nf(fin)} sur {nf(total)} {quoi}
      </p>
      <div className="pagination__taille" role="group" aria-label="Lignes par page">
        <span className="texte-2" aria-hidden="true">
          Par page :
        </span>
        {TAILLES_PAGE.map((t) => (
          <button
            key={t}
            type="button"
            className="pagination__bouton"
            aria-pressed={t === taille}
            aria-label={`${t} lignes par page`}
            onClick={() => onTaille(t)}
          >
            {t}
          </button>
        ))}
      </div>
      {pages > 1 && (
        <nav className="pagination__pages" aria-label={`Pages du tableau des ${quoi}`}>
          <button
            type="button"
            className="pagination__bouton"
            aria-label="Page précédente"
            disabled={page === 0}
            onClick={() => onPage(page - 1)}
          >
            <Chevron gauche taille={12} />
          </button>
          {numerosDePage(page, pages).map((n, i) =>
            n === '…' ? (
              <span key={`trou-${i}`} className="texte-2 pagination__trou" aria-hidden="true">
                …
              </span>
            ) : (
              <button
                key={n}
                type="button"
                className="pagination__bouton"
                aria-label={`Page ${n + 1}`}
                aria-current={n === page ? 'page' : undefined}
                onClick={() => onPage(n)}
              >
                {n + 1}
              </button>
            ),
          )}
          <button
            type="button"
            className="pagination__bouton"
            aria-label="Page suivante"
            disabled={page === pages - 1}
            onClick={() => onPage(page + 1)}
          >
            <Chevron taille={12} />
          </button>
        </nav>
      )}
    </div>
  );
}
