import type { Team } from "../types";

export type TeamFlagDisplay =
  | {
      kind: "asset";
      src: string;
      alt: string;
      fallbackLabel: string;
    }
  | {
      kind: "text";
      label: string;
      className: "team-flag--emoji" | "team-flag--fallback";
    };

export function getCompactTeamLabel(team: Team) {
  return team.fifa_code || team.short_name || team.display_name || team.team_id;
}

export function getTeamFlagDisplay(team: Team): TeamFlagDisplay {
  const fallbackLabel = getCompactTeamLabel(team);

  if (team.flag_mode === "asset" && isLocalSvgFlagPath(team.flag_value)) {
    return {
      kind: "asset",
      src: team.flag_value,
      alt: `${team.display_name} flag`,
      fallbackLabel,
    };
  }

  if (team.flag_mode === "emoji" && hasDisplayValue(team.flag_value)) {
    return {
      kind: "text",
      label: team.flag_value,
      className: "team-flag--emoji",
    };
  }

  if (hasDisplayValue(team.flag_value) && team.flag_mode !== "asset") {
    return {
      kind: "text",
      label: team.flag_value,
      className: "team-flag--fallback",
    };
  }

  return {
    kind: "text",
    label: team.iso_alpha2 || fallbackLabel,
    className: "team-flag--fallback",
  };
}

function isLocalSvgFlagPath(value: string | undefined) {
  return Boolean(value && value.startsWith("/flags/") && value.endsWith(".svg"));
}

function hasDisplayValue(value: string | undefined) {
  return Boolean(value && value.trim().length > 0);
}
