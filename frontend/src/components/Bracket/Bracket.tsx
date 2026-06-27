import { MatchCard } from "../MatchCard/MatchCard";
import type { Round, RuntimeMatch, Team } from "../../domain/types";

interface BracketProps {
  matches: RuntimeMatch[];
  rounds: Round[];
  teamsById: Map<string, Team>;
  onWinnerOverride: (matchId: string, winnerTeamId: string) => void;
}

export function Bracket({
  matches,
  rounds,
  teamsById,
  onWinnerOverride,
}: BracketProps) {
  const matchesByRound = new Map<string, RuntimeMatch[]>();
  for (const match of matches) {
    const roundMatches = matchesByRound.get(match.round_id) ?? [];
    roundMatches.push(match);
    matchesByRound.set(match.round_id, roundMatches);
  }

  return (
    <section className="section-block bracket-section" aria-labelledby="bracket-title">
      <div className="section-heading">
        <p className="eyebrow">Interactive bracket</p>
        <h2 id="bracket-title">Knockout path</h2>
      </div>
      <div className="bracket-grid" role="list" aria-label="Knockout bracket rounds">
        {rounds.map((round) => (
          <section className="round-column" key={round.round_id} aria-labelledby={`${round.round_id}-title`}>
            <h3 id={`${round.round_id}-title`} className="round-title">
              {round.display_name}
            </h3>
            <div className="round-match-list">
              {[...(matchesByRound.get(round.round_id) ?? [])]
                .sort((left, right) => left.match_id.localeCompare(right.match_id))
                .map((match) => (
                  <MatchCard
                    key={match.match_id}
                    match={match}
                    teamsById={teamsById}
                    onWinnerOverride={onWinnerOverride}
                  />
                ))}
            </div>
          </section>
        ))}
      </div>
    </section>
  );
}

