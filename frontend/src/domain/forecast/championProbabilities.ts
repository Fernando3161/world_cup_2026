import { sortMatches } from "../bracket/resolveBracket";
import { calculateRatingProbability } from "../probability/modelRegistry";
import type {
  ChampionProbability,
  ForecastResult,
  Match,
  Team,
  TournamentData,
  UserOverride,
} from "../types";

type ProbabilityDistribution = Map<string, number>;

const ROUND_TO_REACH_FIELD: Partial<
  Record<Match["round_id"], keyof Omit<ChampionProbability, "team_id" | "champion_probability" | "selected_model_id">>
> = {
  R16: "round_of_16_probability",
  QF: "quarterfinal_probability",
  SF: "semifinal_probability",
  F: "final_probability",
};

export function calculateChampionProbabilities(
  tournamentData: TournamentData,
  forecast: ForecastResult,
): ChampionProbability[] {
  const teamsById = new Map(tournamentData.teams.map((team) => [team.team_id, team]));
  const matchById = new Map(tournamentData.matches.map((match) => [match.match_id, match]));
  const sanitizedOverrides = new Map(forecast.appliedOverrides.map((override) => [override.match_id, override]));
  const winnerDistributions = new Map<string, ProbabilityDistribution>();
  const probabilitiesByTeamId = initializeChampionProbabilities(
    tournamentData.teams,
    forecast.selected_model_id,
  );

  for (const match of sortMatches(tournamentData.matches)) {
    const slotADistribution = getSlotDistribution(match.slot_a, matchById, winnerDistributions);
    const slotBDistribution = getSlotDistribution(match.slot_b, matchById, winnerDistributions);
    recordRoundReachProbabilities(probabilitiesByTeamId, match.round_id, slotADistribution);
    recordRoundReachProbabilities(probabilitiesByTeamId, match.round_id, slotBDistribution);

    const winnerDistribution = calculateWinnerDistribution(
      slotADistribution,
      slotBDistribution,
      teamsById,
      tournamentData,
      forecast.selected_model_id,
      sanitizedOverrides.get(match.match_id),
    );
    winnerDistributions.set(match.match_id, winnerDistribution);

    if (match.round_id === "F") {
      for (const [teamId, probability] of winnerDistribution) {
        probabilitiesByTeamId.get(teamId)!.champion_probability += probability;
      }
    }
  }

  return tournamentData.teams.map((team) => probabilitiesByTeamId.get(team.team_id)!);
}

export function deriveTopFourChampions(
  championProbabilities: ChampionProbability[],
): ChampionProbability[] {
  return [...championProbabilities]
    .sort((left, right) => {
      const probabilityDelta = right.champion_probability - left.champion_probability;
      return probabilityDelta === 0 ? left.team_id.localeCompare(right.team_id) : probabilityDelta;
    })
    .slice(0, 4);
}

function initializeChampionProbabilities(
  teams: Team[],
  selectedModelId: string,
): Map<string, ChampionProbability> {
  return new Map(
    teams.map((team) => [
      team.team_id,
      {
        team_id: team.team_id,
        champion_probability: 0,
        final_probability: 0,
        semifinal_probability: 0,
        quarterfinal_probability: 0,
        round_of_16_probability: 0,
        selected_model_id: selectedModelId,
      },
    ]),
  );
}

function getSlotDistribution(
  slot: Match["slot_a"],
  matchById: Map<string, Match>,
  winnerDistributions: Map<string, ProbabilityDistribution>,
): ProbabilityDistribution {
  if (slot.slot_type === "team") {
    return new Map([[slot.team_id, 1]]);
  }
  if (slot.slot_type === "winner_of") {
    const sourceMatch = matchById.get(slot.source_match_id);
    if (!sourceMatch) {
      return new Map();
    }
    return new Map(winnerDistributions.get(sourceMatch.match_id) ?? []);
  }
  return new Map();
}

function recordRoundReachProbabilities(
  probabilitiesByTeamId: Map<string, ChampionProbability>,
  roundId: Match["round_id"],
  distribution: ProbabilityDistribution,
): void {
  const field = ROUND_TO_REACH_FIELD[roundId];
  if (!field) {
    return;
  }

  for (const [teamId, probability] of distribution) {
    const championProbability = probabilitiesByTeamId.get(teamId);
    if (championProbability) {
      championProbability[field] += probability;
    }
  }
}

function calculateWinnerDistribution(
  slotADistribution: ProbabilityDistribution,
  slotBDistribution: ProbabilityDistribution,
  teamsById: Map<string, Team>,
  tournamentData: TournamentData,
  selectedModelId: string,
  override: UserOverride | undefined,
): ProbabilityDistribution {
  const winnerDistribution: ProbabilityDistribution = new Map();

  for (const [teamAId, teamAReachProbability] of slotADistribution) {
    for (const [teamBId, teamBReachProbability] of slotBDistribution) {
      if (teamAId === teamBId) {
        continue;
      }

      const matchupProbability = teamAReachProbability * teamBReachProbability;
      if (matchupProbability === 0) {
        continue;
      }

      const teamA = teamsById.get(teamAId);
      const teamB = teamsById.get(teamBId);
      if (!teamA || !teamB) {
        continue;
      }

      const pairProbability = calculateRatingProbability(
        teamA.rating,
        teamB.rating,
        tournamentData,
        selectedModelId,
      );
      const forcedWinner = getForcedWinnerForPair(override, teamAId, teamBId);

      if (forcedWinner === teamAId) {
        addProbability(winnerDistribution, teamAId, matchupProbability);
      } else if (forcedWinner === teamBId) {
        addProbability(winnerDistribution, teamBId, matchupProbability);
      } else {
        addProbability(winnerDistribution, teamAId, matchupProbability * pairProbability.probabilityA);
        addProbability(winnerDistribution, teamBId, matchupProbability * pairProbability.probabilityB);
      }
    }
  }

  return winnerDistribution;
}

function getForcedWinnerForPair(
  override: UserOverride | undefined,
  teamAId: string,
  teamBId: string,
): string | null {
  if (!override) {
    return null;
  }
  return override.winner_team_id === teamAId || override.winner_team_id === teamBId
    ? override.winner_team_id
    : null;
}

function addProbability(distribution: ProbabilityDistribution, teamId: string, probability: number): void {
  distribution.set(teamId, (distribution.get(teamId) ?? 0) + probability);
}
