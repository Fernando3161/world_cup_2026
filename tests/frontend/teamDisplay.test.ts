import { describe, expect, it } from "vitest";

import {
  getCompactTeamLabel,
  getTeamFlagDisplay,
} from "../../frontend/src/domain/display/teamDisplay";
import type { Team } from "../../frontend/src/domain/types";
import tournamentDataJson from "../../frontend/public/data/tournament.json";
import type { TournamentData } from "../../frontend/src/domain/types";

const argentinaFlag = "\u{1F1E6}\u{1F1F7}";
const tournamentData = tournamentDataJson as TournamentData;

describe("team display helpers", () => {
  it("describes local asset flags for image rendering", () => {
    const team = buildTeam({
      flag_mode: "asset",
      flag_value: "/flags/arg.svg",
      fifa_code: "ARG",
      iso_alpha2: "AR",
    });

    expect(getTeamFlagDisplay(team)).toEqual({
      kind: "asset",
      src: "/flags/arg.svg",
      alt: "Argentina flag",
      fallbackLabel: "ARG",
    });
  });

  it("renders emoji flag values before ISO fallbacks", () => {
    const team = buildTeam({
      flag_mode: "emoji",
      flag_value: argentinaFlag,
      fifa_code: "ARG",
      iso_alpha2: "AR",
    });

    expect(getTeamFlagDisplay(team)).toEqual({
      kind: "text",
      label: argentinaFlag,
      className: "team-flag--emoji",
    });
  });

  it("uses ISO fallback only when an emoji value is missing", () => {
    const team = buildTeam({
      flag_mode: "emoji",
      flag_value: "",
      fifa_code: "ARG",
      iso_alpha2: "AR",
    });

    expect(getTeamFlagDisplay(team)).toEqual({
      kind: "text",
      label: "AR",
      className: "team-flag--fallback",
    });
  });

  it("falls back to a compact label for invalid asset paths", () => {
    const team = buildTeam({
      flag_mode: "asset",
      flag_value: "https://example.com/arg.svg",
      fifa_code: "ARG",
      iso_alpha2: "AR",
    });

    expect(getTeamFlagDisplay(team)).toEqual({
      kind: "text",
      label: "AR",
      className: "team-flag--fallback",
    });
  });

  it("falls back to provided text for unknown flag modes", () => {
    const team = buildTeam({
      flag_mode: "custom",
      flag_value: "ARG",
      fifa_code: "ARG",
    });

    expect(getTeamFlagDisplay(team)).toEqual({
      kind: "text",
      label: "ARG",
      className: "team-flag--fallback",
    });
  });

  it("uses FIFA codes for compact team labels", () => {
    const team = buildTeam({
      display_name: "Argentina",
      short_name: "Argentina",
      fifa_code: "ARG",
    });

    expect(getCompactTeamLabel(team)).toBe("ARG");
  });

  it("uses local SVG assets for the current tournament teams", () => {
    expect(tournamentData.teams).toHaveLength(32);
    for (const team of tournamentData.teams) {
      const flag = getTeamFlagDisplay(team);

      expect(team.flag_mode).toBe("asset");
      expect(team.flag_value).toMatch(/^\/flags\/[a-z]+\.svg$/);
      expect(flag.kind).toBe("asset");
    }
  });
});

function buildTeam(overrides: Partial<Team>): Team {
  return {
    team_id: "arg",
    display_name: "Argentina",
    short_name: "Argentina",
    rating: 2100,
    rating_source: "test",
    flag_mode: "emoji",
    flag_value: argentinaFlag,
    ...overrides,
  };
}
