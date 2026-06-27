import { useMemo, useState } from "react";

import tournamentDataJson from "../../public/data/tournament.json";
import { Bracket } from "../components/Bracket/Bracket";
import { ChampionSummary } from "../components/ChampionSummary/ChampionSummary";
import { ForecastControls } from "../components/ForecastControls/ForecastControls";
import { HeaderNav } from "../components/HeaderNav/HeaderNav";
import { Modal } from "../components/Modal/Modal";
import { SiteFooter } from "../components/SiteFooter/SiteFooter";
import {
  clearAllOverrides,
  resolveBaselineForecast,
  resolveCurrentScenarioForecast,
} from "../domain/bracket/resolveBracket";
import {
  calculateChampionProbabilities,
  deriveTopFourChampions,
} from "../domain/forecast";
import type { TournamentData, UserOverride } from "../domain/types";

const tournamentData = tournamentDataJson as TournamentData;
const GITHUB_URL = "https://github.com/Fernando3161/world_cup_2026";

type ActiveModal = "about" | "model" | "sources" | null;

export function App() {
  const [overrides, setOverrides] = useState<UserOverride[]>([]);
  const [activeModal, setActiveModal] = useState<ActiveModal>(null);

  const baselineForecast = useMemo(
    () => resolveBaselineForecast(tournamentData),
    [],
  );
  const scenarioForecast = useMemo(
    () => resolveCurrentScenarioForecast(tournamentData, overrides),
    [overrides],
  );
  const baselineChampionProbabilities = useMemo(
    () => calculateChampionProbabilities(tournamentData, baselineForecast),
    [baselineForecast],
  );
  const scenarioChampionProbabilities = useMemo(
    () => calculateChampionProbabilities(tournamentData, scenarioForecast),
    [scenarioForecast],
  );
  const topScenarioChampions = useMemo(
    () => deriveTopFourChampions(scenarioChampionProbabilities),
    [scenarioChampionProbabilities],
  );
  const topBaselineChampions = useMemo(
    () => deriveTopFourChampions(baselineChampionProbabilities),
    [baselineChampionProbabilities],
  );
  const teamsById = useMemo(
    () => new Map(tournamentData.teams.map((team) => [team.team_id, team])),
    [],
  );

  const baselineChampion = topBaselineChampions[0];
  const scenarioChampion = topScenarioChampions[0];

  function handleWinnerOverride(matchId: string, winnerTeamId: string) {
    setOverrides((currentOverrides) => [
      ...currentOverrides.filter((override) => override.match_id !== matchId),
      { match_id: matchId, winner_team_id: winnerTeamId },
    ]);
  }

  function handleResetOverrides() {
    setOverrides(clearAllOverrides());
  }

  return (
    <>
      <HeaderNav
        githubUrl={GITHUB_URL}
        onOpenAbout={() => setActiveModal("about")}
        onOpenModel={() => setActiveModal("model")}
        onOpenSources={() => setActiveModal("sources")}
      />

      <main className="publication-shell" aria-labelledby="page-title">
        <Bracket
          matches={scenarioForecast.matches}
          tournamentMatches={tournamentData.matches}
          rounds={tournamentData.rounds}
          teamsById={teamsById}
          onWinnerOverride={handleWinnerOverride}
        />

        <section className="secondary-control-row" aria-label="Forecast controls and champion summary">
          <ForecastControls
            tournamentData={tournamentData}
            teamsById={teamsById}
            baselineChampion={baselineChampion}
            scenarioChampion={scenarioChampion}
            appliedOverrideCount={scenarioForecast.appliedOverrides.length}
            ignoredOverrideCount={scenarioForecast.ignoredOverrides.length}
            hasOverrides={overrides.length > 0}
            onResetOverrides={handleResetOverrides}
          />
          <ChampionSummary
            championProbabilities={topScenarioChampions}
            teamsById={teamsById}
          />
        </section>

        <section className="forecast-note-row" aria-label="Forecast summary">
          <p className="standfirst">
            A browser-side rating model for the knockout stage. Pick match
            winners to redraw the path to the final and update the title
            probabilities without any runtime server.
          </p>
          <aside className="data-note" aria-label="Forecast data note">
            <span className="note-label">Data status</span>
            <strong>Placeholder fixture data</strong>
            <span>
              Ratings and teams are test values for the MVP data contract, not
              real tournament data.
            </span>
          </aside>
        </section>
      </main>

      <SiteFooter tournamentData={tournamentData} />

      <Modal
        isOpen={activeModal === "about"}
        title="About Me"
        onClose={() => setActiveModal(null)}
      >
        <div className="modal-copy">
          <p>
            FPV is building this as a compact public forecasting project: part
            software exercise, part statistical explainer, and part editorial
            data interface.
          </p>
          <p>
            The goal is to keep the model transparent enough to inspect while
            making the bracket useful for scenario thinking. The current MVP is
            intentionally local and static, so every public interaction runs in
            the browser.
          </p>
        </div>
      </Modal>

      <Modal
        isOpen={activeModal === "model"}
        title="Model Notes"
        onClose={() => setActiveModal(null)}
      >
        <div className="modal-copy model-explainer">
          <section>
            <h3>Simple Elo model</h3>
            <p>
              For two teams A and B with ratings R_A and R_B, the MVP converts
              rating difference into an advancement probability using the
              standard logistic Elo shape:
            </p>
            <pre aria-label="Simple Elo probability equation">
{`P(A advances) = 1 / (1 + 10 ^ ((R_B - R_A) / 400))
P(B advances) = 1 - P(A advances)`}
            </pre>
            <p>
              The higher-rated team is favored, equal ratings produce a 50/50
              match, and probabilities are propagated exactly through the
              bracket rather than sampled with Monte Carlo.
            </p>
          </section>
          <section>
            <h3>Historically informed Elo</h3>
            <p>
              Not implemented yet. The reserved future model will calibrate the
              rating-difference curve against historical international match
              outcomes prepared offline, then export static parameters for the
              browser.
            </p>
          </section>
          <section>
            <h3>Assumptions and limits</h3>
            <ul>
              <li>No player, injury, venue, travel, or lineup adjustments.</li>
              <li>No live data fetches during user interaction.</li>
              <li>Current MVP data uses placeholder teams and ratings.</li>
            </ul>
          </section>
        </div>
      </Modal>

      <Modal
        isOpen={activeModal === "sources"}
        title="Data Sources"
        onClose={() => setActiveModal(null)}
      >
        <div className="modal-copy">
          <p>
            The public app reads generated static JSON. Source snapshots are
            prepared locally, validated in Python, and packaged into the Vite
            build.
          </p>
          <dl className="source-list">
            {tournamentData.sources.map((source) => (
              <div key={source.source_id}>
                <dt>{source.display_name}</dt>
                <dd>
                  <a href={source.url} target="_blank" rel="noreferrer">
                    {source.url}
                  </a>
                  {source.notes ? <span>{source.notes}</span> : null}
                </dd>
              </div>
            ))}
            <div>
              <dt>Historical results source for future calibration</dt>
              <dd>
                <a
                  href="https://github.com/martj42/international_results"
                  target="_blank"
                  rel="noreferrer"
                >
                  Mart Jurisoo international_results
                </a>
                <span>
                  Future offline calibration input; not part of the current
                  MVP forecast calculation.
                </span>
              </dd>
            </div>
            <div>
              <dt>Local project files</dt>
              <dd>
                <span>data/manual/teams.csv</span>
                <span>data/manual/bracket.json</span>
                <span>data/snapshots/ratings.csv</span>
              </dd>
            </div>
          </dl>
        </div>
      </Modal>
    </>
  );
}
