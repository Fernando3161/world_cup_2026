import { describe, expect, it } from "vitest";

import tournamentDataJson from "../../frontend/public/data/tournament.json";
import {
  getRuntimeMatch,
  resolveBaselineForecast,
  resolveCurrentScenarioForecast,
} from "../../frontend/src/domain/bracket/resolveBracket";
import { calculateChampionProbabilities } from "../../frontend/src/domain/forecast";
import {
  calculateRatingProbability,
  getSelectableProbabilityModels,
} from "../../frontend/src/domain/probability/modelRegistry";
import type { TournamentData } from "../../frontend/src/domain/types";

const tournamentData = tournamentDataJson as TournamentData;

describe("historically informed model toggle", () => {
  it("keeps simple Elo probability behavior available", () => {
    const probabilities = calculateRatingProbability(1800, 1800, tournamentData, "simple_elo");

    expect(probabilities.probabilityA).toBeCloseTo(0.5, 12);
    expect(probabilities.probabilityB).toBeCloseTo(0.5, 12);
  });

  it("calculates historically informed probabilities from the calibrated artifact", () => {
    const equal = calculateRatingProbability(1800, 1800, tournamentData, "historically_informed_elo");
    const higher = calculateRatingProbability(1900, 1700, tournamentData, "historically_informed_elo");

    expect(equal.probabilityA).toBeCloseTo(0.5, 12);
    expect(higher.probabilityA).toBeGreaterThan(higher.probabilityB);
    expect(higher.probabilityA + higher.probabilityB).toBeCloseTo(1, 12);
  });

  it("changes match probabilities when the selected model changes", () => {
    const simple = getRuntimeMatch(resolveBaselineForecast(tournamentData, "simple_elo"), "R32-01");
    const historical = getRuntimeMatch(
      resolveBaselineForecast(tournamentData, "historically_informed_elo"),
      "R32-01",
    );

    expect(simple.selected_model_id).toBe("simple_elo");
    expect(historical.selected_model_id).toBe("historically_informed_elo");
    expect(historical.probability_a).not.toBeCloseTo(simple.probability_a ?? 0, 8);
  });

  it("changes champion probabilities when the selected model changes", () => {
    const simpleForecast = resolveBaselineForecast(tournamentData, "simple_elo");
    const historicalForecast = resolveBaselineForecast(tournamentData, "historically_informed_elo");
    const simpleChampions = calculateChampionProbabilities(tournamentData, simpleForecast);
    const historicalChampions = calculateChampionProbabilities(tournamentData, historicalForecast);
    const simpleByTeam = new Map(simpleChampions.map((team) => [team.team_id, team.champion_probability]));
    const changedTeam = historicalChampions.find(
      (team) => Math.abs(team.champion_probability - (simpleByTeam.get(team.team_id) ?? 0)) > 0.0001,
    );

    expect(changedTeam).toBeDefined();
    expect(historicalChampions.reduce((sum, team) => sum + team.champion_probability, 0)).toBeCloseTo(1, 10);
  });

  it("preserves valid user overrides after model changes", () => {
    const [teamA] = fixedTeamIds("R32-01");
    const forecast = resolveCurrentScenarioForecast(
      tournamentData,
      [{ match_id: "R32-01", winner_team_id: teamA }],
      "historically_informed_elo",
    );

    expect(getRuntimeMatch(forecast, "R32-01").winner_team_id).toBe(teamA);
    expect(getRuntimeMatch(forecast, "R32-01").selection_source).toBe("user_override");
    expect(forecast.selected_model_id).toBe("historically_informed_elo");
  });

  it("does not expose the historical model if its artifact is missing", () => {
    const withoutArtifact: TournamentData = {
      ...tournamentData,
      models: {
        ...tournamentData.models,
        calibrated_models: {},
      },
    };

    expect(getSelectableProbabilityModels(withoutArtifact).map((model) => model.model_id)).toEqual(["simple_elo"]);
  });
});

function fixedTeamIds(matchId: string): [string, string] {
  const match = tournamentData.matches.find((candidate) => candidate.match_id === matchId);
  if (
    !match ||
    match.slot_a.slot_type !== "team" ||
    match.slot_b.slot_type !== "team"
  ) {
    throw new Error(`Missing fixed first-round teams for ${matchId}.`);
  }

  return [match.slot_a.team_id, match.slot_b.team_id];
}
