import type { RuntimeMatch, Team } from "../../domain/types";

interface MatchCardProps {
  match: RuntimeMatch;
  teamsById: Map<string, Team>;
  onWinnerOverride: (matchId: string, winnerTeamId: string) => void;
}

export function MatchCard({
  match,
  teamsById,
  onWinnerOverride,
}: MatchCardProps) {
  const teamA = match.team_a_id ? teamsById.get(match.team_a_id) ?? null : null;
  const teamB = match.team_b_id ? teamsById.get(match.team_b_id) ?? null : null;

  return (
    <article
      className={`match-card ${match.is_overridden ? "match-card-overridden" : ""}`}
      aria-labelledby={`${match.match_id}-title`}
    >
      <header className="match-card-header">
        <h4 id={`${match.match_id}-title`}>{match.match_id}</h4>
        <span className="source-pill">{selectionLabel(match.selection_source)}</span>
      </header>
      <div className="team-choice-list">
        <TeamChoice
          matchId={match.match_id}
          team={teamA}
          probability={match.probability_a}
          isWinner={match.winner_team_id === teamA?.team_id}
          onWinnerOverride={onWinnerOverride}
        />
        <TeamChoice
          matchId={match.match_id}
          team={teamB}
          probability={match.probability_b}
          isWinner={match.winner_team_id === teamB?.team_id}
          onWinnerOverride={onWinnerOverride}
        />
      </div>
    </article>
  );
}

interface TeamChoiceProps {
  matchId: string;
  team: Team | null;
  probability: number | null;
  isWinner: boolean;
  onWinnerOverride: (matchId: string, winnerTeamId: string) => void;
}

function TeamChoice({
  matchId,
  team,
  probability,
  isWinner,
  onWinnerOverride,
}: TeamChoiceProps) {
  if (!team) {
    return (
      <div className="team-choice team-choice-empty">
        <span className="team-name">To be resolved</span>
        <span className="probability-value">-</span>
      </div>
    );
  }

  return (
    <button
      type="button"
      className={`team-choice ${isWinner ? "team-choice-winner" : ""}`}
      onClick={() => onWinnerOverride(matchId, team.team_id)}
      aria-pressed={isWinner}
      aria-label={`Select ${team.display_name} as winner of ${matchId}`}
    >
      <span className="team-identity">
        <span className="team-flag" aria-hidden="true">
          {team.flag_value}
        </span>
        <span className="team-name">{team.short_name}</span>
      </span>
      <span className="probability-value">{formatPercent(probability)}</span>
    </button>
  );
}

function selectionLabel(selectionSource: RuntimeMatch["selection_source"]) {
  if (selectionSource === "user_override") {
    return "User pick";
  }
  if (selectionSource === "official_lock") {
    return "Official";
  }
  if (selectionSource === "unresolved") {
    return "Open";
  }
  return "Model";
}

function formatPercent(value: number | null) {
  if (value === null) {
    return "-";
  }

  return new Intl.NumberFormat("en", {
    style: "percent",
    maximumFractionDigits: 0,
  }).format(value);
}

