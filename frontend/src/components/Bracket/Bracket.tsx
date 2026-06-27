import type { CSSProperties } from "react";

import { MatchCard } from "../MatchCard/MatchCard";
import type { Match, Round, RuntimeMatch, Team } from "../../domain/types";

interface BracketProps {
  matches: RuntimeMatch[];
  tournamentMatches: Match[];
  rounds: Round[];
  teamsById: Map<string, Team>;
  onWinnerOverride: (matchId: string, winnerTeamId: string) => void;
}

interface NodePosition {
  x: number;
  y: number;
  side: "left" | "center" | "right";
}

type PositionedStyle = CSSProperties & {
  "--node-x": string;
  "--node-y": string;
};

type LabelStyle = CSSProperties & {
  "--label-x": string;
};

const ROUND_LABELS = [
  { label: "Round of 32", x: 6 },
  { label: "Round of 16", x: 17 },
  { label: "Quarter-finals", x: 28.5 },
  { label: "Semi-finals", x: 39.5 },
  { label: "Final", x: 50 },
  { label: "Semi-finals", x: 60.5 },
  { label: "Quarter-finals", x: 71.5 },
  { label: "Round of 16", x: 83 },
  { label: "Round of 32", x: 94 },
];

export function Bracket({
  matches,
  tournamentMatches,
  rounds,
  teamsById,
  onWinnerOverride,
}: BracketProps) {
  const positions = new Map<string, NodePosition>();
  for (const match of matches) {
    positions.set(match.match_id, getNodePosition(match.match_id, match.round_id));
  }

  const matchesByRound = new Map<string, RuntimeMatch[]>();
  for (const match of matches) {
    const roundMatches = matchesByRound.get(match.round_id) ?? [];
    roundMatches.push(match);
    matchesByRound.set(match.round_id, roundMatches);
  }

  return (
    <section className="bracket-section" aria-labelledby="bracket-title">
      <div className="section-heading">
        <p className="eyebrow">Interactive bracket</p>
        <h2 id="bracket-title">Knockout tree</h2>
        <p>
          Select any team to force a result. The current scenario then
          recalculates every dependent match and the title probabilities.
        </p>
      </div>

      <div className="bracket-diagram" aria-label="World Cup knockout bracket diagram">
        <div className="bracket-round-labels" aria-hidden="true">
          {ROUND_LABELS.map((roundLabel) => {
            const labelStyle: LabelStyle = { "--label-x": `${roundLabel.x}%` };
            return (
              <span key={`${roundLabel.label}-${roundLabel.x}`} style={labelStyle}>
                {roundLabel.label}
              </span>
            );
          })}
        </div>
        <svg
          className="bracket-connectors"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          aria-hidden="true"
          focusable="false"
        >
          {tournamentMatches
            .filter((match) => match.feeds_to_match_id)
            .map((match) => {
              const source = positions.get(match.match_id);
              const target = positions.get(match.feeds_to_match_id ?? "");
              if (!source || !target) {
                return null;
              }

              return (
                <path
                  key={`${match.match_id}-${match.feeds_to_match_id}`}
                  className={target.side === "center" ? "connector-final" : ""}
                  d={connectorPath(source, target)}
                />
              );
            })}
        </svg>

        {matches.map((match) => {
          const position = positions.get(match.match_id);
          if (!position) {
            return null;
          }

          const nodeStyle: PositionedStyle = {
            "--node-x": `${position.x}%`,
            "--node-y": `${position.y}%`,
          };

          return (
            <div
              className={`bracket-node-position bracket-node-${position.side}`}
              key={match.match_id}
              style={nodeStyle}
            >
              <MatchCard
                match={match}
                teamsById={teamsById}
                onWinnerOverride={onWinnerOverride}
              />
            </div>
          );
        })}
      </div>

      <div className="mobile-bracket-list" aria-label="World Cup knockout bracket by round">
        {rounds.map((round) => (
          <section
            className="round-column"
            key={round.round_id}
            aria-labelledby={`${round.round_id}-title`}
          >
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

function getNodePosition(matchId: string, roundId: RuntimeMatch["round_id"]): NodePosition {
  const order = matchOrder(matchId);

  if (roundId === "F") {
    return { x: 50, y: 50, side: "center" };
  }

  if (roundId === "SF") {
    return order === 1
      ? { x: 39.5, y: 50, side: "left" }
      : { x: 60.5, y: 50, side: "right" };
  }

  if (roundId === "QF") {
    if (order <= 2) {
      return { x: 28.5, y: yForIndex(order - 1, 2), side: "left" };
    }
    return { x: 71.5, y: yForIndex(order - 3, 2), side: "right" };
  }

  if (roundId === "R16") {
    if (order <= 4) {
      return { x: 17, y: yForIndex(order - 1, 4), side: "left" };
    }
    return { x: 83, y: yForIndex(order - 5, 4), side: "right" };
  }

  if (order <= 8) {
    return { x: 6, y: yForIndex(order - 1, 8), side: "left" };
  }
  return { x: 94, y: yForIndex(order - 9, 8), side: "right" };
}

function matchOrder(matchId: string) {
  const suffix = matchId.split("-")[1];
  return Number.parseInt(suffix ?? "1", 10);
}

function yForIndex(index: number, count: number) {
  return ((index + 0.5) / count) * 100;
}

function connectorPath(source: NodePosition, target: NodePosition) {
  const direction = target.x > source.x ? 1 : -1;
  const sourceX = source.x + direction * 4.15;
  const targetX = target.x - direction * 4.15;
  const midX = (sourceX + targetX) / 2;

  return `M ${sourceX} ${source.y} H ${midX} V ${target.y} H ${targetX}`;
}
