import { describe, expect, it } from "vitest";

import tournamentDataJson from "../../frontend/public/data/tournament.json";
import {
  clearAllOverrides,
  getRuntimeMatch,
  resolveBaselineForecast,
  resolveCurrentScenarioForecast,
} from "../../frontend/src/domain/bracket/resolveBracket";
import type { TournamentData, UserOverride } from "../../frontend/src/domain/types";

const tournamentData = tournamentDataJson as TournamentData;

describe("user overrides", () => {
  it("changes downstream matches when an upstream winner is overridden", () => {
    const forecast = resolveCurrentScenarioForecast(tournamentData, [
      { match_id: "R32-01", winner_team_id: "t01" },
    ]);

    expect(getRuntimeMatch(forecast, "R32-01").winner_team_id).toBe("t01");
    expect(getRuntimeMatch(forecast, "R32-01").selection_source).toBe("user_override");
    expect(getRuntimeMatch(forecast, "R16-01").team_a_id).toBe("t01");
    expect(getRuntimeMatch(forecast, "R16-01").team_b_id).toBe("t04");
  });

  it("ignores invalid downstream overrides after upstream recalculation", () => {
    const overrides: UserOverride[] = [
      { match_id: "R32-01", winner_team_id: "t01" },
      { match_id: "R16-01", winner_team_id: "t02" },
    ];

    const forecast = resolveCurrentScenarioForecast(tournamentData, overrides);

    expect(getRuntimeMatch(forecast, "R16-01").team_a_id).toBe("t01");
    expect(getRuntimeMatch(forecast, "R16-01").team_b_id).toBe("t04");
    expect(getRuntimeMatch(forecast, "R16-01").selection_source).toBe("model");
    expect(forecast.ignoredOverrides).toContainEqual({ match_id: "R16-01", winner_team_id: "t02" });
  });

  it("resetting overrides returns the forecast to baseline", () => {
    const baseline = resolveBaselineForecast(tournamentData);
    const reset = resolveCurrentScenarioForecast(tournamentData, clearAllOverrides());

    expect(reset.matches.map((match) => match.winner_team_id)).toEqual(
      baseline.matches.map((match) => match.winner_team_id),
    );
    expect(reset.appliedOverrides).toEqual([]);
    expect(reset.ignoredOverrides).toEqual([]);
  });
});

