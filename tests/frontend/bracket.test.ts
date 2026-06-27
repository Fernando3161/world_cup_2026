import { describe, expect, it } from "vitest";

import tournamentDataJson from "../../frontend/public/data/tournament.json";
import {
  getRuntimeMatch,
  resolveBaselineForecast,
} from "../../frontend/src/domain/bracket/resolveBracket";
import type { TournamentData } from "../../frontend/src/domain/types";

const tournamentData = tournamentDataJson as TournamentData;

describe("baseline bracket resolution", () => {
  it("propagates model winners to the correct downstream match slots", () => {
    const forecast = resolveBaselineForecast(tournamentData);

    expect(getRuntimeMatch(forecast, "R32-01").winner_team_id).toBe("t02");
    expect(getRuntimeMatch(forecast, "R32-02").winner_team_id).toBe("t04");

    const roundOf16Match = getRuntimeMatch(forecast, "R16-01");
    expect(roundOf16Match.team_a_id).toBe("t02");
    expect(roundOf16Match.team_b_id).toBe("t04");
    expect(roundOf16Match.winner_team_id).toBe("t04");
    expect(roundOf16Match.selection_source).toBe("model");
  });
});

