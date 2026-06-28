import { deriveMobileBracketPods } from "../../domain/bracket/mobilePods";
import { getCompactTeamLabel } from "../../domain/display/teamDisplay";
import type { RuntimeMatch, Team } from "../../domain/types";
import { TeamFlag } from "../TeamFlag/TeamFlag";

interface MobileBracketProps {
  matches: RuntimeMatch[];
  teamsById: Map<string, Team>;
  onWinnerOverride: (matchId: string, winnerTeamId: string) => void;
}

export function MobileBracket({
  matches,
  teamsById,
  onWinnerOverride,
}: MobileBracketProps) {
  const pods = deriveMobileBracketPods(matches);

  return (
    <div className="mobile-bracket-pods" aria-label="Mobile knockout bracket pods">
      <div className="mobile-bracket-intro">
        <p className="eyebrow">Mobile bracket view</p>
        <p>Tap a team to force a result. Each pod shows a compact knockout path.</p>
      </div>

      <div className="mobile-quarter-pod-list">
        {pods.quarterPods.map((pod) => (
          <section
            className="mobile-bracket-pod"
            key={pod.pod_id}
            aria-labelledby={`${pod.pod_id}-title`}
          >
            <header className="mobile-pod-header">
              <h3 id={`${pod.pod_id}-title`}>{pod.title}</h3>
              <span>R32 to QF</span>
            </header>
            <div className="mobile-pod-grid">
              <MobileStage title="R32" matches={pod.r32Matches} teamsById={teamsById} onWinnerOverride={onWinnerOverride} />
              <MobileStage title="R16" matches={pod.r16Matches} teamsById={teamsById} onWinnerOverride={onWinnerOverride} />
              <MobileStage title="QF" matches={[pod.qfMatch]} teamsById={teamsById} onWinnerOverride={onWinnerOverride} />
            </div>
          </section>
        ))}
      </div>

      <section className="mobile-bracket-pod mobile-finals-pod" aria-labelledby="mobile-finals-title">
        <header className="mobile-pod-header">
          <h3 id="mobile-finals-title">Final path</h3>
          <span>Quarter winners converge</span>
        </header>
        <div className="mobile-finals-grid">
          <MobileStage title="SF" matches={pods.finalsPod.sfMatches} teamsById={teamsById} onWinnerOverride={onWinnerOverride} />
          <MobileStage title="Final" matches={[pods.finalsPod.finalMatch]} teamsById={teamsById} onWinnerOverride={onWinnerOverride} />
          <ChampionNode match={pods.finalsPod.finalMatch} teamsById={teamsById} />
        </div>
      </section>
    </div>
  );
}

interface MobileStageProps {
  title: string;
  matches: RuntimeMatch[];
  teamsById: Map<string, Team>;
  onWinnerOverride: (matchId: string, winnerTeamId: string) => void;
}

function MobileStage({
  title,
  matches,
  teamsById,
  onWinnerOverride,
}: MobileStageProps) {
  return (
    <div className="mobile-stage">
      <span className="mobile-stage-label">{title}</span>
      <div className="mobile-stage-match-list">
        {matches.map((match) => (
          <MobileMatchNode
            key={match.match_id}
            match={match}
            teamsById={teamsById}
            onWinnerOverride={onWinnerOverride}
          />
        ))}
      </div>
    </div>
  );
}

interface MobileMatchNodeProps {
  match: RuntimeMatch;
  teamsById: Map<string, Team>;
  onWinnerOverride: (matchId: string, winnerTeamId: string) => void;
}

function MobileMatchNode({
  match,
  teamsById,
  onWinnerOverride,
}: MobileMatchNodeProps) {
  const teamA = match.team_a_id ? teamsById.get(match.team_a_id) ?? null : null;
  const teamB = match.team_b_id ? teamsById.get(match.team_b_id) ?? null : null;

  return (
    <article
      className={`mobile-match-node mobile-match-${match.round_id.toLowerCase()} ${
        match.is_overridden ? "mobile-match-overridden" : ""
      }`}
      aria-label={`${match.match_id} mobile match`}
    >
      <header className="mobile-match-header">
        <span>{match.match_id}</span>
        <span>{selectionLabel(match.selection_source)}</span>
      </header>
      <MobileTeamPill
        matchId={match.match_id}
        team={teamA}
        probability={match.probability_a}
        isWinner={match.winner_team_id === teamA?.team_id}
        isLoser={Boolean(match.winner_team_id && teamA && match.winner_team_id !== teamA.team_id)}
        onWinnerOverride={onWinnerOverride}
      />
      <MobileTeamPill
        matchId={match.match_id}
        team={teamB}
        probability={match.probability_b}
        isWinner={match.winner_team_id === teamB?.team_id}
        isLoser={Boolean(match.winner_team_id && teamB && match.winner_team_id !== teamB.team_id)}
        onWinnerOverride={onWinnerOverride}
      />
    </article>
  );
}

interface MobileTeamPillProps {
  matchId: string;
  team: Team | null;
  probability: number | null;
  isWinner: boolean;
  isLoser: boolean;
  onWinnerOverride: (matchId: string, winnerTeamId: string) => void;
}

function MobileTeamPill({
  matchId,
  team,
  probability,
  isWinner,
  isLoser,
  onWinnerOverride,
}: MobileTeamPillProps) {
  if (!team) {
    return (
      <div className="mobile-team-pill mobile-team-pill-empty">
        <span>Pending</span>
        <span>-</span>
      </div>
    );
  }

  return (
    <button
      type="button"
      className={`mobile-team-pill ${isWinner ? "mobile-team-pill-winner" : ""} ${
        isLoser ? "mobile-team-pill-loser" : ""
      }`}
      onClick={() => onWinnerOverride(matchId, team.team_id)}
      aria-pressed={isWinner}
      aria-label={`Select ${team.display_name} as winner of ${matchId}`}
      title={`${team.display_name} ${formatPercent(probability)}`}
    >
      <span className="mobile-team-identity">
        <TeamFlag team={team} />
        <span>{getCompactTeamLabel(team)}</span>
      </span>
      <span className="mobile-probability">{formatPercent(probability)}</span>
    </button>
  );
}

function ChampionNode({
  match,
  teamsById,
}: {
  match: RuntimeMatch;
  teamsById: Map<string, Team>;
}) {
  const champion = match.winner_team_id ? teamsById.get(match.winner_team_id) ?? null : null;

  return (
    <div className="mobile-champion-node" aria-label="Projected champion">
      <span className="mobile-stage-label">Champion</span>
      <div className="mobile-champion-card">
        {champion ? (
          <>
            <TeamFlag team={champion} />
            <strong>{getCompactTeamLabel(champion)}</strong>
            <span>{champion.display_name}</span>
          </>
        ) : (
          <span>Pending</span>
        )}
      </div>
    </div>
  );
}

function selectionLabel(selectionSource: RuntimeMatch["selection_source"]) {
  if (selectionSource === "user_override") {
    return "User";
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
