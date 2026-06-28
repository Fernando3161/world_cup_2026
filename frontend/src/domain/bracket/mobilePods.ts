import type { RuntimeMatch } from "../types";

export interface QuarterBracketPod {
  pod_id: string;
  title: string;
  qfMatch: RuntimeMatch;
  r16Matches: [RuntimeMatch, RuntimeMatch];
  r32Matches: [RuntimeMatch, RuntimeMatch, RuntimeMatch, RuntimeMatch];
}

export interface FinalsBracketPod {
  sfMatches: [RuntimeMatch, RuntimeMatch];
  finalMatch: RuntimeMatch;
}

export interface MobileBracketPods {
  quarterPods: QuarterBracketPod[];
  finalsPod: FinalsBracketPod;
}

export function deriveMobileBracketPods(matches: RuntimeMatch[]): MobileBracketPods {
  const matchesById = new Map(matches.map((match) => [match.match_id, match]));
  const quarterPods: QuarterBracketPod[] = [];

  for (let quarterIndex = 1; quarterIndex <= 4; quarterIndex += 1) {
    const qfMatch = requireMatch(matchesById, `QF-${formatOrder(quarterIndex)}`);
    const r16Start = (quarterIndex - 1) * 2 + 1;
    const r32Start = (quarterIndex - 1) * 4 + 1;

    quarterPods.push({
      pod_id: `quarter-${quarterIndex}`,
      title: `Quarter ${quarterIndex}`,
      qfMatch,
      r16Matches: [
        requireMatch(matchesById, `R16-${formatOrder(r16Start)}`),
        requireMatch(matchesById, `R16-${formatOrder(r16Start + 1)}`),
      ],
      r32Matches: [
        requireMatch(matchesById, `R32-${formatOrder(r32Start)}`),
        requireMatch(matchesById, `R32-${formatOrder(r32Start + 1)}`),
        requireMatch(matchesById, `R32-${formatOrder(r32Start + 2)}`),
        requireMatch(matchesById, `R32-${formatOrder(r32Start + 3)}`),
      ],
    });
  }

  return {
    quarterPods,
    finalsPod: {
      sfMatches: [requireMatch(matchesById, "SF-01"), requireMatch(matchesById, "SF-02")],
      finalMatch: requireMatch(matchesById, "F-01"),
    },
  };
}

function requireMatch(matchesById: Map<string, RuntimeMatch>, matchId: string) {
  const match = matchesById.get(matchId);
  if (!match) {
    throw new Error(`Cannot derive mobile bracket pods: missing match '${matchId}'.`);
  }
  return match;
}

function formatOrder(value: number) {
  return value.toString().padStart(2, "0");
}
