import { describe, expect, it } from "vitest";

import tournamentDataJson from "../../frontend/public/data/tournament.json";
import {
  getRuntimeMatch,
  resolveBaselineForecast,
} from "../../frontend/src/domain/bracket/resolveBracket";
import type { TournamentData } from "../../frontend/src/domain/types";

const tournamentData = tournamentDataJson as TournamentData;

describe("baseline bracket resolution", () => {
  it("propagates model winners to the correct downstream match slots", () => {
    const forecast = resolveBaselineForecast(tournamentData);
    const ratingsByTeamId = new Map(
      tournamentData.teams.map((team) => [team.team_id, team.rating]),
    );
    const firstMatchWinner = higherRatedTeam("t01", "t02", ratingsByTeamId);
    const secondMatchWinner = higherRatedTeam("t03", "t04", ratingsByTeamId);
    const roundOf16Winner = higherRatedTeam(
      firstMatchWinner,
      secondMatchWinner,
      ratingsByTeamId,
    );

    expect(getRuntimeMatch(forecast, "R32-01").winner_team_id).toBe(firstMatchWinner);
    expect(getRuntimeMatch(forecast, "R32-02").winner_team_id).toBe(secondMatchWinner);

    const roundOf16Match = getRuntimeMatch(forecast, "R16-01");
    expect(roundOf16Match.team_a_id).toBe(firstMatchWinner);
    expect(roundOf16Match.team_b_id).toBe(secondMatchWinner);
    expect(roundOf16Match.winner_team_id).toBe(roundOf16Winner);
    expect(roundOf16Match.selection_source).toBe("model");
  });
});

function higherRatedTeam(
  teamAId: string,
  teamBId: string,
  ratingsByTeamId: Map<string, number>,
) {
  const ratingA = ratingsByTeamId.get(teamAId);
  const ratingB = ratingsByTeamId.get(teamBId);

  if (ratingA === undefined || ratingB === undefined) {
    throw new Error(`Missing test rating for ${teamAId} or ${teamBId}.`);
  }

  return ratingA >= ratingB ? teamAId : teamBId;
}
