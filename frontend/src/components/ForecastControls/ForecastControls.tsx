import type { ChampionProbability, Team, TournamentData } from "../../domain/types";

interface ForecastControlsProps {
  tournamentData: TournamentData;
  teamsById: Map<string, Team>;
  baselineChampion: ChampionProbability;
  scenarioChampion: ChampionProbability;
  appliedOverrideCount: number;
  ignoredOverrideCount: number;
  hasOverrides: boolean;
  onResetOverrides: () => void;
}

export function ForecastControls({
  tournamentData,
  teamsById,
  baselineChampion,
  scenarioChampion,
  appliedOverrideCount,
  ignoredOverrideCount,
  hasOverrides,
  onResetOverrides,
}: ForecastControlsProps) {
  const simpleModel = tournamentData.models.available_models.find(
    (model) => model.model_id === "simple_elo",
  );

  return (
    <>
      <section className="control-card model-status" aria-labelledby="model-status-title">
        <p className="eyebrow">Model</p>
        <h2 id="model-status-title">Forecast engine</h2>
        <div className="model-toggle" role="list" aria-label="Model availability">
          <span className="model-option model-option-active" role="listitem">
            <strong>{simpleModel?.display_name ?? "Simple Elo"}</strong>
            <span>Active</span>
          </span>
          <span className="model-option model-option-disabled" role="listitem">
            <strong>Historically informed Elo</strong>
            <span>Coming soon</span>
          </span>
        </div>
      </section>

      <section className="control-card scenario-status" aria-labelledby="scenario-status-title">
        <p className="eyebrow">Forecast mode</p>
        <h2 id="scenario-status-title">Baseline vs current</h2>
        <div className="scenario-grid" role="list">
          <div role="listitem">
            <span className="mode-label">Baseline forecast</span>
            <strong>{teamName(teamsById, baselineChampion.team_id)}</strong>
            <span>{formatPercent(baselineChampion.champion_probability)} title probability</span>
          </div>
          <div className="current-scenario" role="listitem">
            <span className="mode-label">Current scenario</span>
            <strong>{teamName(teamsById, scenarioChampion.team_id)}</strong>
            <span>
              {appliedOverrideCount} user pick{appliedOverrideCount === 1 ? "" : "s"}
              {ignoredOverrideCount > 0 ? `, ${ignoredOverrideCount} ignored` : ""}
            </span>
          </div>
        </div>
        <button
          className="secondary-action"
          type="button"
          onClick={onResetOverrides}
          disabled={!hasOverrides}
        >
          Reset scenario
        </button>
      </section>
    </>
  );
}

function teamName(teamsById: Map<string, { display_name: string }>, teamId: string) {
  return teamsById.get(teamId)?.display_name ?? teamId;
}

function formatPercent(value: number) {
  return new Intl.NumberFormat("en", {
    style: "percent",
    maximumFractionDigits: 1,
  }).format(value);
}
