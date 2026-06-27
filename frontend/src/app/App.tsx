import { useMemo, useState } from "react";

import tournamentDataJson from "../../public/data/tournament.json";
import { Bracket } from "../components/Bracket/Bracket";
import { ChampionSummary } from "../components/ChampionSummary/ChampionSummary";
import { MethodNotes } from "../components/MethodNotes/MethodNotes";
import {
  clearAllOverrides,
  resolveBaselineForecast,
  resolveCurrentScenarioForecast,
} from "../domain/bracket/resolveBracket";
import {
  calculateChampionProbabilities,
  deriveTopFourChampions,
} from "../domain/forecast";
import type { TournamentData, UserOverride } from "../domain/types";

const tournamentData = tournamentDataJson as TournamentData;

export function App() {
  const [overrides, setOverrides] = useState<UserOverride[]>([]);

  const baselineForecast = useMemo(
    () => resolveBaselineForecast(tournamentData),
    [],
  );
  const scenarioForecast = useMemo(
    () => resolveCurrentScenarioForecast(tournamentData, overrides),
    [overrides],
  );
  const baselineChampionProbabilities = useMemo(
    () => calculateChampionProbabilities(tournamentData, baselineForecast),
    [baselineForecast],
  );
  const scenarioChampionProbabilities = useMemo(
    () => calculateChampionProbabilities(tournamentData, scenarioForecast),
    [scenarioForecast],
  );
  const topScenarioChampions = useMemo(
    () => deriveTopFourChampions(scenarioChampionProbabilities),
    [scenarioChampionProbabilities],
  );
  const teamsById = useMemo(
    () => new Map(tournamentData.teams.map((team) => [team.team_id, team])),
    [],
  );

  const baselineChampion = deriveTopFourChampions(baselineChampionProbabilities)[0];
  const scenarioChampion = topScenarioChampions[0];

  function handleWinnerOverride(matchId: string, winnerTeamId: string) {
    setOverrides((currentOverrides) => [
      ...currentOverrides.filter((override) => override.match_id !== matchId),
      { match_id: matchId, winner_team_id: winnerTeamId },
    ]);
  }

  function handleResetOverrides() {
    setOverrides(clearAllOverrides());
  }

  return (
    <main className="app-shell" aria-labelledby="page-title">
      <header className="masthead">
        <p className="eyebrow">Static knockout forecast</p>
        <div className="masthead-grid">
          <div>
            <h1 id="page-title">World Cup 2026 Knockout Forecast</h1>
            <p className="standfirst">
              A browser-side rating-based forecast for the knockout stage. The
              bracket starts from the Round of 32 and recalculates locally when
              you choose different match winners.
            </p>
          </div>
          <div className="data-note" aria-label="Forecast data note">
            <span className="note-label">Data status</span>
            <strong>Placeholder fixture data</strong>
            <span>
              Ratings and teams are test values for the MVP data contract, not
              real tournament data.
            </span>
          </div>
        </div>
      </header>

      <section className="forecast-controls" aria-labelledby="forecast-mode-title">
        <div>
          <p className="eyebrow">Forecast mode</p>
          <h2 id="forecast-mode-title">Baseline and current scenario</h2>
        </div>
        <div className="mode-grid" role="list">
          <div className="mode-card" role="listitem">
            <span className="mode-label">Baseline forecast</span>
            <strong>{teamName(teamsById, baselineChampion.team_id)}</strong>
            <span>
              Top title probability:{" "}
              {formatPercent(baselineChampion.champion_probability)}
            </span>
          </div>
          <div className="mode-card mode-card-current" role="listitem">
            <span className="mode-label">Current scenario</span>
            <strong>{teamName(teamsById, scenarioChampion.team_id)}</strong>
            <span>
              Overrides applied: {scenarioForecast.appliedOverrides.length}
              {scenarioForecast.ignoredOverrides.length > 0
                ? `, ignored: ${scenarioForecast.ignoredOverrides.length}`
                : ""}
            </span>
          </div>
        </div>
        <button
          className="secondary-action"
          type="button"
          onClick={handleResetOverrides}
          disabled={overrides.length === 0}
        >
          Reset overrides
        </button>
      </section>

      <ChampionSummary
        championProbabilities={topScenarioChampions}
        teamsById={teamsById}
      />

      <Bracket
        matches={scenarioForecast.matches}
        rounds={tournamentData.rounds}
        teamsById={teamsById}
        onWinnerOverride={handleWinnerOverride}
      />

      <MethodNotes tournamentData={tournamentData} />
    </main>
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

