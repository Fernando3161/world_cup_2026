import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import tournamentDataJson from "../../../public/data/tournament.json";
import { resolveBaselineForecast } from "../../domain/bracket/resolveBracket";
import type { RuntimeMatch, TournamentData } from "../../domain/types";
import { MobileBracket } from "./MobileBracket";

const tournamentData = tournamentDataJson as TournamentData;

describe("MobileBracket", () => {
  it("renders pending slots without crashing and keeps selectable team buttons", () => {
    const forecast = resolveBaselineForecast(tournamentData);
    const teamsById = new Map(tournamentData.teams.map((team) => [team.team_id, team]));
    const pendingMatches: RuntimeMatch[] = forecast.matches.map((match) =>
      match.match_id === "F-01"
        ? {
            ...match,
            team_a_id: null,
            probability_a: null,
            winner_team_id: null,
            selection_source: "unresolved",
          }
        : match,
    );

    const markup = renderToStaticMarkup(
      <MobileBracket
        matches={pendingMatches}
        teamsById={teamsById}
        onWinnerOverride={() => undefined}
      />,
    );

    expect(markup).toContain("Pending");
    expect(markup).toContain("Select ");
    expect(markup).toContain("mobile-bracket-pods");
  });
});
