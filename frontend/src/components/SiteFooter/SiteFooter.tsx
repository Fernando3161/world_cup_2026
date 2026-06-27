import type { TournamentData } from "../../domain/types";

interface SiteFooterProps {
  tournamentData: TournamentData;
}

export function SiteFooter({ tournamentData }: SiteFooterProps) {
  return (
    <footer className="site-footer">
      <div>
        <p className="eyebrow">Notes</p>
        <p>
          Forecast probabilities are model estimates, not certainties. The MVP
          uses local static data and browser-side calculations; it is not
          betting advice and does not update from live match or rating feeds.
        </p>
      </div>
      <dl className="footer-meta">
        <div>
          <dt>Author</dt>
          <dd>FPV</dd>
        </div>
        <div>
          <dt>Data version</dt>
          <dd>{tournamentData.tournament.data_version}</dd>
        </div>
        <div>
          <dt>Generated</dt>
          <dd>{tournamentData.tournament.generated_at}</dd>
        </div>
      </dl>
    </footer>
  );
}
