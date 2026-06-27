import type { TournamentData } from "../../domain/types";

interface MethodNotesProps {
  tournamentData: TournamentData;
}

export function MethodNotes({ tournamentData }: MethodNotesProps) {
  const model = tournamentData.models.available_models.find(
    (availableModel) => availableModel.model_id === tournamentData.models.default_model_id,
  );

  return (
    <section className="section-block method-notes" aria-labelledby="method-title">
      <div className="section-heading">
        <p className="eyebrow">Method</p>
        <h2 id="method-title">About this forecast</h2>
      </div>
      <div className="notes-grid">
        <p>
          The MVP uses a simple rating-difference model. For each possible
          knockout match, the browser converts the two team ratings into an
          advancement probability and then propagates those probabilities through
          the bracket exactly.
        </p>
        <dl className="metadata-list">
          <div>
            <dt>Model</dt>
            <dd>{model?.display_name ?? tournamentData.models.default_model_id}</dd>
          </div>
          <div>
            <dt>Rating source</dt>
            <dd>{tournamentData.models.rating_source}</dd>
          </div>
          <div>
            <dt>Snapshot kind</dt>
            <dd>{tournamentData.models.rating_snapshot_kind}</dd>
          </div>
          <div>
            <dt>Data version</dt>
            <dd>{tournamentData.tournament.data_version}</dd>
          </div>
        </dl>
      </div>
      {tournamentData.tournament.data_note ? (
        <p className="fixture-warning">{tournamentData.tournament.data_note}</p>
      ) : null}
    </section>
  );
}
