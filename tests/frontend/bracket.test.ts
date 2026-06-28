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
    const [firstMatchTeamA, firstMatchTeamB] = fixedTeamIds("R32-01");
    const [secondMatchTeamA, secondMatchTeamB] = fixedTeamIds("R32-02");
    const firstMatchWinner = higherRatedTeam(firstMatchTeamA, firstMatchTeamB, ratingsByTeamId);
    const secondMatchWinner = higherRatedTeam(secondMatchTeamA, secondMatchTeamB, ratingsByTeamId);
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
