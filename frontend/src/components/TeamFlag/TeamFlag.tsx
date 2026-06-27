import { useEffect, useState } from "react";

import { getTeamFlagDisplay } from "../../domain/display/teamDisplay";
import type { Team } from "../../domain/types";

interface TeamFlagProps {
  team: Team;
}

export function TeamFlag({ team }: TeamFlagProps) {
  const [assetFailed, setAssetFailed] = useState(false);
  const flag = getTeamFlagDisplay(team);

  useEffect(() => {
    setAssetFailed(false);
  }, [team.team_id, team.flag_value]);

  if (flag.kind === "asset" && !assetFailed) {
    return (
      <span className="team-flag team-flag--asset">
        <img
          src={flag.src}
          alt={flag.alt}
          width="24"
          height="18"
          loading="lazy"
          decoding="async"
          onError={() => setAssetFailed(true)}
        />
      </span>
    );
  }

  const fallbackLabel = flag.kind === "asset" ? flag.fallbackLabel : flag.label;
  const fallbackClassName = flag.kind === "asset" ? "team-flag--fallback" : flag.className;

  return (
    <span className={`team-flag ${fallbackClassName}`} aria-hidden="true">
      {fallbackLabel}
    </span>
  );
}
