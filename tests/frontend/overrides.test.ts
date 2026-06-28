import { describe, expect, it } from "vitest";

import tournamentDataJson from "../../frontend/public/data/tournament.json";
import {
  clearAllOverrides,
  getRuntimeMatch,
  resolveBaselineForecast,
  resolveCurrentScenarioForecast,
} from "../../frontend/src/domain/bracket/resolveBracket";
import type { TournamentData, UserOverride } from "../../frontend/src/domain/types";

const tournamentData = tournamentDataJson as TournamentData;

describe("user overrides", () => {
  it("changes downstream matches when an upstream winner is overridden", () => {
    const [firstTeamA] = fixedTeamIds("R32-01");
    const secondMatchWinner = getRuntimeMatch(resolveBaselineForecast(tournamentData), "R32-02").winner_team_id;
    const forecast = resolveCurrentScenarioForecast(tournamentData, [
      { match_id: "R32-01", winner_team_id: firstTeamA },
    ]);

    expect(getRuntimeMatch(forecast, "R32-01").winner_team_id).toBe(firstTeamA);
    expect(getRuntimeMatch(forecast, "R32-01").selection_source).toBe("user_override");
    expect(getRuntimeMatch(forecast, "R16-01").team_a_id).toBe(firstTeamA);
    expect(getRuntimeMatch(forecast, "R16-01").team_b_id).toBe(secondMatchWinner);
  });

  it("ignores invalid downstream overrides after upstream recalculation", () => {
    const [firstTeamA, firstTeamB] = fixedTeamIds("R32-01");
    const secondMatchWinner = getRuntimeMatch(resolveBaselineForecast(tournamentData), "R32-02").winner_team_id;
    const overrides: UserOverride[] = [
      { match_id: "R32-01", winner_team_id: firstTeamA },
      { match_id: "R16-01", winner_team_id: firstTeamB },
    ];

    const forecast = resolveCurrentScenarioForecast(tournamentData, overrides);

    expect(getRuntimeMatch(forecast, "R16-01").team_a_id).toBe(firstTeamA);
    expect(getRuntimeMatch(forecast, "R16-01").team_b_id).toBe(secondMatchWinner);
    expect(getRuntimeMatch(forecast, "R16-01").selection_source).toBe("model");
    expect(forecast.ignoredOverrides).toContainEqual({ match_id: "R16-01", winner_team_id: firstTeamB });
  });

  it("resetting overrides returns the forecast to baseline", () => {
    const baseline = resolveBaselineForecast(tournamentData);
    const reset = resolveCurrentScenarioForecast(tournamentData, clearAllOverrides());

    expect(reset.matches.map((match) => match.winner_team_id)).toEqual(
      baseline.matches.map((match) => match.winner_team_id),
    );
    expect(reset.appliedOverrides).toEqual([]);
    expect(reset.ignoredOverrides).toEqual([]);
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
