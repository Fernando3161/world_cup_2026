import { describe, expect, it } from "vitest";

import tournamentDataJson from "../../frontend/public/data/tournament.json";
import { deriveMobileBracketPods } from "../../frontend/src/domain/bracket/mobilePods";
import { resolveBaselineForecast } from "../../frontend/src/domain/bracket/resolveBracket";
import type { TournamentData } from "../../frontend/src/domain/types";

const tournamentData = tournamentDataJson as TournamentData;

describe("mobile bracket pods", () => {
  it("derives four quarter pods with the expected round shape", () => {
    const forecast = resolveBaselineForecast(tournamentData);
    const pods = deriveMobileBracketPods(forecast.matches);

    expect(pods.quarterPods).toHaveLength(4);

    for (const pod of pods.quarterPods) {
      expect(pod.r32Matches).toHaveLength(4);
      expect(pod.r16Matches).toHaveLength(2);
      expect(pod.qfMatch.round_id).toBe("QF");
      expect(pod.r16Matches.every((match) => match.round_id === "R16")).toBe(true);
      expect(pod.r32Matches.every((match) => match.round_id === "R32")).toBe(true);
    }
  });

  it("derives the finals pod from two semi-finals and one final", () => {
    const forecast = resolveBaselineForecast(tournamentData);
    const pods = deriveMobileBracketPods(forecast.matches);

    expect(pods.finalsPod.sfMatches).toHaveLength(2);
    expect(pods.finalsPod.sfMatches.map((match) => match.round_id)).toEqual(["SF", "SF"]);
    expect(pods.finalsPod.finalMatch.round_id).toBe("F");
  });

  it("does not duplicate matches across the mobile pod layout", () => {
    const forecast = resolveBaselineForecast(tournamentData);
    const pods = deriveMobileBracketPods(forecast.matches);
    const podMatches = [
      ...pods.quarterPods.flatMap((pod) => [
        ...pod.r32Matches,
        ...pod.r16Matches,
        pod.qfMatch,
      ]),
      ...pods.finalsPod.sfMatches,
      pods.finalsPod.finalMatch,
    ];
    const matchIds = podMatches.map((match) => match.match_id);

    expect(matchIds).toHaveLength(31);
    expect(new Set(matchIds).size).toBe(31);
  });
});
