import { ratingDifferenceProbability } from "../probability/simpleElo";
import type {
  ForecastResult,
  Match,
  RuntimeMatch,
  Team,
  TournamentData,
  UserOverride,
} from "../types";

const ROUND_ORDER: Record<string, number> = {
  R32: 1,
  R16: 2,
  QF: 3,
  SF: 4,
  F: 5,
};

export function resolveBaselineForecast(
  tournamentData: TournamentData,
  selectedModelId = tournamentData.models.default_model_id,
): ForecastResult {
  return resolveBracket(tournamentData, [], selectedModelId);
}

export function resolveCurrentScenarioForecast(
  tournamentData: TournamentData,
  overrides: UserOverride[],
  selectedModelId = tournamentData.models.default_model_id,
): ForecastResult {
  return resolveBracket(tournamentData, overrides, selectedModelId);
}

export function resolveBracket(
  tournamentData: TournamentData,
  overrides: UserOverride[] = [],
  selectedModelId = tournamentData.models.default_model_id,
): ForecastResult {
  const teamsById = toTeamMap(tournamentData.teams);
  const requestedOverrides = new Map(overrides.map((override) => [override.match_id, override]));
  const matchesById = new Map<string, RuntimeMatch>();
  const appliedOverrides: UserOverride[] = [];
  const appliedOverrideIds = new Set<string>();

  for (const match of sortMatches(tournamentData.matches)) {
    const teamAId = resolveSlotTeamId(match.slot_a, matchesById);
    const teamBId = resolveSlotTeamId(match.slot_b, matchesById);
    const requestedOverride = requestedOverrides.get(match.match_id);
    const probabilities = calculateMatchProbabilities(teamAId, teamBId, teamsById);
    const winner = selectWinner(teamAId, teamBId, probabilities, requestedOverride);

    if (winner.source === "user_override" && requestedOverride) {
      appliedOverrides.push(requestedOverride);
      appliedOverrideIds.add(requestedOverride.match_id);
    }

    matchesById.set(match.match_id, {
      match_id: match.match_id,
      round_id: match.round_id,
      team_a_id: teamAId,
      team_b_id: teamBId,
      selected_model_id: selectedModelId,
      probability_a: probabilities?.probabilityA ?? null,
      probability_b: probabilities?.probabilityB ?? null,
      winner_team_id: winner.teamId,
      selection_source: winner.source,
      is_locked: false,
      is_overridden: winner.source === "user_override",
    });
  }

  const ignoredOverrides = overrides.filter((override) => !appliedOverrideIds.has(override.match_id));

  return {
    selected_model_id: selectedModelId,
    matches: Array.from(matchesById.values()),
    matchesById,
    appliedOverrides,
    ignoredOverrides,
  };
}

export function clearAllOverrides(): UserOverride[] {
  return [];
}

export function getRuntimeMatch(forecast: ForecastResult, matchId: string): RuntimeMatch {
  const match = forecast.matchesById.get(matchId);
  if (!match) {
    throw new Error(`Unknown runtime match '${matchId}'.`);
  }
  return match;
}

export function sortMatches(matches: Match[]): Match[] {
  return [...matches].sort((left, right) => {
    const roundDelta = ROUND_ORDER[left.round_id] - ROUND_ORDER[right.round_id];
    return roundDelta === 0 ? left.display_order - right.display_order : roundDelta;
  });
}

function toTeamMap(teams: Team[]): Map<string, Team> {
  return new Map(teams.map((team) => [team.team_id, team]));
}

function resolveSlotTeamId(
  slot: Match["slot_a"],
  resolvedMatchesById: Map<string, RuntimeMatch>,
): string | null {
  if (slot.slot_type === "team") {
    return slot.team_id;
  }
  if (slot.slot_type === "winner_of") {
    return resolvedMatchesById.get(slot.source_match_id)?.winner_team_id ?? null;
  }
  return null;
}

function calculateMatchProbabilities(
  teamAId: string | null,
  teamBId: string | null,
  teamsById: Map<string, Team>,
) {
  if (!teamAId || !teamBId) {
    return null;
  }

  const teamA = teamsById.get(teamAId);
  const teamB = teamsById.get(teamBId);
  if (!teamA || !teamB) {
    return null;
  }

  return ratingDifferenceProbability(teamA.rating, teamB.rating);
}

function selectWinner(
  teamAId: string | null,
  teamBId: string | null,
  probabilities: { probabilityA: number; probabilityB: number } | null,
  requestedOverride: UserOverride | undefined,
): { teamId: string | null; source: RuntimeMatch["selection_source"] } {
  if (!teamAId || !teamBId || !probabilities) {
    return { teamId: null, source: "unresolved" };
  }

  if (requestedOverride?.winner_team_id === teamAId || requestedOverride?.winner_team_id === teamBId) {
    return { teamId: requestedOverride.winner_team_id, source: "user_override" };
  }

  return {
    teamId: probabilities.probabilityA >= probabilities.probabilityB ? teamAId : teamBId,
    source: "model",
  };
}

