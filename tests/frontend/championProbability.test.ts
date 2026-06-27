import { describe, expect, it } from "vitest";

import tournamentDataJson from "../../frontend/public/data/tournament.json";
import { resolveBaselineForecast } from "../../frontend/src/domain/bracket/resolveBracket";
import {
  calculateChampionProbabilities,
  deriveTopFourChampions,
} from "../../frontend/src/domain/forecast";
import type { TournamentData } from "../../frontend/src/domain/types";

const tournamentData = tournamentDataJson as TournamentData;

describe("champion probability propagation", () => {
  it("calculates champion probabilities that sum to 1", () => {
    const forecast = resolveBaselineForecast(tournamentData);
    const championProbabilities = calculateChampionProbabilities(tournamentData, forecast);

    const total = championProbabilities.reduce(
      (sum, teamProbability) => sum + teamProbability.champion_probability,
      0,
    );

    expect(total).toBeCloseTo(1, 12);
  });

  it("derives the top four champion summary from the full probability table", () => {
    const forecast = resolveBaselineForecast(tournamentData);
    const championProbabilities = calculateChampionProbabilities(tournamentData, forecast);
    const topFour = deriveTopFourChampions(championProbabilities);

    expect(topFour).toHaveLength(4);
    expect(topFour[0].champion_probability).toBeGreaterThanOrEqual(topFour[1].champion_probability);
    expect(topFour[1].champion_probability).toBeGreaterThanOrEqual(topFour[2].champion_probability);
    expect(topFour[2].champion_probability).toBeGreaterThanOrEqual(topFour[3].champion_probability);
  });
});

