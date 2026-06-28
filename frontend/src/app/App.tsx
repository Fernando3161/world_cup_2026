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
            Use the bracket to test tournament paths. Each selection is local
            to your browser and recalculates future matchups plus the title
            probability table.
          </p>
          <aside className="data-note" aria-label="Forecast data note">
            <span className="note-label">Data status</span>
            <strong>Pre-knockout snapshot</strong>
            <span>
              Fixtures are loaded from a local Wikipedia knockout-stage
              snapshot. Ratings are a local FootballRatings.org snapshot dated
              2026-06-28.
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
            This project is a static public forecast interface for exploring a
            32-team World Cup knockout bracket. It is built as a browser-side
            data product: the deployed site ships static JSON and runs the
            bracket calculations locally.
          </p>
          <p>
            The emphasis is transparent scenario analysis. A user can change
            any match winner, see that team advance through the correct path,
            and inspect how title probabilities respond without a backend,
            account system, or live data feed.
          </p>
          <p>
            The current deployment uses a local Round-of-32 fixture snapshot
            and a local pre-knockout rating snapshot. Future updates should
            follow the same reviewed local validation and static build
            pipeline.
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
            <h3>Rating-difference probability</h3>
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
            <h3>Exact bracket propagation</h3>
            <p>
              The bracket is resolved from the static tournament structure. In
              each match, the selected winner feeds into the documented
              downstream match and slot. Champion probabilities are propagated
              through the bracket exactly from pairwise match probabilities.
            </p>
          </section>
          <section>
            <h3>Baseline vs current scenario</h3>
            <p>
              The baseline forecast is the model-only path with no user picks.
              The current scenario applies your selected winners where valid,
              clears impossible downstream picks, and recalculates the affected
              matchups and title probabilities.
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
              <li>The model treats advancement as a single match outcome.</li>
              <li>No player, injury, venue, travel, or lineup adjustments are included.</li>
              <li>No live data is fetched during user interaction.</li>
              <li>The current public build uses static snapshots, not live feeds.</li>
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
            The public app reads generated static JSON. Source files are
            prepared locally, validated in Python, and packaged into the Vite
            build so the deployed site stays fully static.
          </p>
          <section>
            <h3>Current snapshot status</h3>
            <p>
              The current bracket is parsed from a locally saved Wikipedia
              knockout-stage page. Ratings are parsed from a locally saved
              FootballRatings.org page dated 2026-06-28, then stored as a CSV
              snapshot before frontend generation.
            </p>
          </section>
          <section>
            <h3>Future rating snapshots</h3>
            <p>
              Updated forecast builds should use reviewed local rating
              snapshots from an Elo-style national-team source, with the
              source name, snapshot date, retrieval date, and URL preserved
              before frontend generation.
            </p>
          </section>
          <section>
            <h3>Reproducible local pipeline</h3>
            <p>
              The pipeline is source CSV/JSON to Python validation to generated
              frontend JSON to static React build. The browser does not scrape
              ratings, query a database, or call a model server at runtime.
            </p>
          </section>
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
              <dt>Flag assets</dt>
              <dd>
                <a
                  href="https://github.com/lipis/flag-icons"
                  target="_blank"
                  rel="noreferrer"
                >
                  flag-icons
                </a>
                <span>
                  Selected MIT-licensed SVG files are committed locally under
                  frontend/public/flags and served as static assets.
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
