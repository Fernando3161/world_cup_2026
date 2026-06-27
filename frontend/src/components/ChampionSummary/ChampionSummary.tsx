import type { ChampionProbability, Team } from "../../domain/types";
import { TeamFlag } from "../TeamFlag/TeamFlag";

interface ChampionSummaryProps {
  championProbabilities: ChampionProbability[];
  teamsById: Map<string, Team>;
}

export function ChampionSummary({
  championProbabilities,
  teamsById,
}: ChampionSummaryProps) {
  const leaderProbability = championProbabilities[0]?.champion_probability ?? 1;

  return (
    <section className="section-block champion-summary" aria-labelledby="champion-summary-title">
      <div className="section-heading">
        <p className="eyebrow">Current scenario</p>
        <h2 id="champion-summary-title">Most likely champions</h2>
      </div>
      <ol className="champion-list">
        {championProbabilities.map((teamProbability, index) => {
          const team = teamsById.get(teamProbability.team_id);
          return (
            <li className="champion-row" key={teamProbability.team_id}>
              <span className="rank">{index + 1}</span>
              <span className="team-identity">
                {team ? (
                  <TeamFlag team={team} />
                ) : (
                  <span className="team-flag team-flag--fallback" aria-hidden="true">
                    {teamProbability.team_id}
                  </span>
                )}
                <span className="team-name">
                  {team?.display_name ?? teamProbability.team_id}
                </span>
              </span>
              <span className="champion-probability">
                {formatPercent(teamProbability.champion_probability)}
              </span>
              <span className="probability-bar" aria-hidden="true">
                <span
                  style={{
                    width: `${Math.max(
                      4,
                      (teamProbability.champion_probability / leaderProbability) * 100,
                    )}%`,
                  }}
                />
              </span>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

function formatPercent(value: number) {
  return new Intl.NumberFormat("en", {
    style: "percent",
    maximumFractionDigits: 1,
  }).format(value);
}
