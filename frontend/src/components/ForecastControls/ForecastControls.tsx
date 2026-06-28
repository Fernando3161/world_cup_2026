import type {
  ChampionProbability,
  ProbabilityModelMetadata,
  Team,
  TournamentData,
} from "../../domain/types";

interface ForecastControlsProps {
  tournamentData: TournamentData;
  teamsById: Map<string, Team>;
  selectableModels: ProbabilityModelMetadata[];
  selectedModelId: string;
  baselineChampion: ChampionProbability;
  scenarioChampion: ChampionProbability;
  appliedOverrideCount: number;
  ignoredOverrideCount: number;
  hasOverrides: boolean;
  onModelChange: (modelId: string) => void;
  onResetOverrides: () => void;
}

export function ForecastControls({
  tournamentData,
  teamsById,
  selectableModels,
  selectedModelId,
  baselineChampion,
  scenarioChampion,
  appliedOverrideCount,
  ignoredOverrideCount,
  hasOverrides,
  onModelChange,
  onResetOverrides,
}: ForecastControlsProps) {
  const selectedModel = selectableModels.find((model) => model.model_id === selectedModelId);

  return (
    <>
      <section className="control-card model-status" aria-labelledby="model-status-title">
        <p className="eyebrow">Model</p>
        <h2 id="model-status-title">Forecast engine</h2>
        <div className="model-toggle" role="radiogroup" aria-label="Forecast probability model">
          {selectableModels.map((model) => (
            <button
              className={`model-option ${model.model_id === selectedModelId ? "model-option-active" : ""}`}
              type="button"
              role="radio"
              aria-checked={model.model_id === selectedModelId}
              key={model.model_id}
              onClick={() => onModelChange(model.model_id)}
            >
              <strong>{model.display_name}</strong>
              <span>{model.model_id === selectedModelId ? "Active" : "Select"}</span>
            </button>
          ))}
        </div>
        <p className="model-caption">
          Active model: {selectedModel?.display_name ?? selectedModelId}. Ratings snapshot:{" "}
          {tournamentData.models.rating_snapshot_date}.
        </p>
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
