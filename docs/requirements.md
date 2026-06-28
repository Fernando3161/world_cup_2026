# requirements.md

# World Cup Knockout Forecast Website — Requirements

## 1. Purpose

This document defines the functional, non-functional, data, modeling, frontend, deployment, and testing requirements for the World Cup knockout forecast website.

The requirements are written for implementation by coding agents. They should be treated as a contract for the MVP unless explicitly marked as a later-phase requirement.

---

## 2. Requirement Levels

The following terms are used:

- **Must**: required for the MVP.
- **Should**: strongly recommended, but may be deferred if necessary.
- **May**: optional.
- **Future**: not part of the MVP, but the architecture should not block it.

---

## 3. Product Scope

### REQ-SCOPE-001 — Knockout-stage focus

The application must forecast the World Cup knockout stage starting from the Round of 32.

The MVP must not attempt to predict the group stage.

### REQ-SCOPE-002 — 32-team bracket

The application must support a 32-team single-elimination bracket.

The MVP bracket must contain:

- 16 Round-of-32 matches
- 8 Round-of-16 matches
- 4 quarter-final matches
- 2 semi-final matches
- 1 final match

### REQ-SCOPE-003 — Match prediction target

The prediction target must be:

> The probability that a team wins the knockout match and advances to the next round.

The MVP must not separately model regulation-time wins, draws, extra time, or penalties.

### REQ-SCOPE-004 — Public-facing website

The application must be designed as a public, accessible, polished website.

It must not be implemented only as a local notebook, script, or command-line tool.

---

## 4. Architecture Requirements

### REQ-ARCH-001 — Static deployment

The deployed website must be capable of running as a static site.

The public app must be deployable to GitHub Pages or an equivalent static hosting provider.

### REQ-ARCH-002 — No runtime backend

The MVP must not require a live backend server for normal user interaction.

The deployed app must not require:

- A running Python process
- A backend database
- Runtime authentication
- Server-side sessions
- Runtime scraping

### REQ-ARCH-003 — Python role

Python must be used only for build-time, setup-time, data preparation, data validation, model training, and model validation tasks.

Python may generate static JSON files for the frontend.

### REQ-ARCH-004 — Browser-side interaction

All user-facing interactive bracket recalculation must happen in the browser.

This includes:

- Manual winner overrides
- Downstream bracket recalculation
- Current scenario forecast updates
- Champion probability updates
- Model toggle updates, once multiple models are available

### REQ-ARCH-005 — Frontend stack

The frontend must use:

- React
- TypeScript
- Vite
- Custom CSS

The MVP must not introduce a heavy UI framework unless explicitly approved.

---

## 5. Data Source Requirements

### REQ-SOURCE-001 — Current Elo source

The preferred current Elo source must be World Football Elo Ratings:

```text
https://www.eloratings.net/
```

The project may use an accessible mirror or fallback only if source metadata clearly records that the underlying Elo data comes from World Football Elo Ratings.

### REQ-SOURCE-002 — No claim of official Elo

The project must not claim that World Football Elo is an official FIFA ranking.

If FIFA ranking points are used in any future model, they must be labeled separately from World Football Elo.

### REQ-SOURCE-003 — Pre-tournament snapshot

For a pre-WC2026 forecast, the project must use a frozen pre-tournament rating snapshot.

The snapshot should represent the latest available ratings before the first World Cup 2026 match.

The snapshot metadata must record:

- `rating_snapshot_kind = "pre_tournament"`
- `rating_date`
- `retrieved_at`
- `rating_source`
- `source_url`

### REQ-SOURCE-004 — Pre-knockout snapshot

For a forecast made after the Round of 32 is known, the project may use a pre-knockout rating snapshot.

The snapshot metadata must record:

- `rating_snapshot_kind = "pre_knockout"`
- `rating_date`
- `retrieved_at`
- `rating_source`
- `source_url`

### REQ-SOURCE-005 — No accidental data leakage across forecast types

A forecast labeled pre-tournament must not use ratings updated after tournament matches have already started.

A forecast labeled pre-knockout must not be presented as a pre-tournament forecast.

### REQ-SOURCE-006 — Historical result source

The preferred historical match result source must be Mart Jürisoo’s international football results dataset:

```text
https://github.com/martj42/international_results
```

The project should use at least:

- `results.csv`
- `shootouts.csv`

### REQ-SOURCE-007 — Historical result mirrors

The Kaggle mirror and OpenFootball mirror may be used for convenience or alternative formats, but the source metadata must record the actual source used.

### REQ-SOURCE-008 — Local source snapshots

All external source data must be copied into local project files before model building or frontend generation.

The deployed frontend must not fetch source data directly.

### REQ-SOURCE-009 — Source metadata

Generated frontend data must include enough source metadata to explain:

- Rating source
- Historical result source, once used
- Snapshot date
- Model version
- Data generation timestamp

---

## 6. Data Requirements

### REQ-DATA-001 — Static frontend data

The frontend must consume static generated JSON data.

The MVP should use a file such as:

```text
frontend/public/data/tournament.json
```

### REQ-DATA-002 — Local rating snapshot

The application must use a local rating snapshot.

The MVP must not depend on live online rating data during user interaction.

### REQ-DATA-003 — Missing rating data

If the required rating CSV or rating data is missing, the data preparation or build process must fail with a clear error message.

The application must not silently assign fake ratings.

### REQ-DATA-004 — Stable team IDs

Every team must have a stable `team_id`.

Display names must not be used as logic identifiers.

### REQ-DATA-005 — Stable match IDs

Every match must have a stable `match_id`.

Match IDs must not be randomly generated.

Recommended format:

```text
R32-01
R32-02
...
R16-01
...
QF-01
SF-01
F-01
```

### REQ-DATA-006 — Stable model IDs

Every probability model must have a stable `model_id`.

Recommended model IDs:

```text
simple_elo
historical_elo
```

### REQ-DATA-007 — Team data

Each team must include at least:

- `team_id`
- `display_name`
- `short_name`
- `rating`
- `rating_source`
- `flag_mode`
- `flag_value`

### REQ-DATA-008 — Flag representation

The public MVP must use local static flag assets for the main UI.

The data model must allow:

- `flag_mode = "asset"` with a local static path such as `/flags/arg.svg`
- `flag_mode = "emoji"` as a fallback or development representation

The deployed app must not depend on remote flag images at runtime.

When `flag_mode = "asset"`, the frontend must render an image from the local `flag_value` path. Asset paths must not be remote URLs and should start with `/flags/`.

When `flag_mode = "emoji"`, the frontend may render the actual emoji string stored in `flag_value`, but emoji flags must not be the primary public-MVP solution because some operating systems render them as regional letters. ISO or other text fallbacks may be used only when the intended flag value is missing, invalid, or fails to load.

### REQ-DATA-009 — Bracket data

The bracket data must define:

- Match ID
- Round ID
- Slot A
- Slot B
- Next match receiving the winner
- Next slot receiving the winner
- Display order

### REQ-DATA-010 — Round data

Rounds must be explicitly defined and ordered.

The frontend must not infer round order alphabetically.

### REQ-DATA-011 — Team alias data

The project should maintain team aliases for historical data normalization.

Historical team names must not be mapped by fragile ad-hoc string replacement inside model code.

### REQ-DATA-012 — Generated data validation

Before frontend data is generated, scripts must validate:

- Team IDs are unique
- Match IDs are unique
- Model IDs are unique
- Every bracket team has a rating
- Every referenced team exists
- Every referenced match exists
- The bracket has the correct number of matches per round
- Later-round references point to valid earlier matches
- The final has no downstream match

---

## 7. Probability Model Requirements

### REQ-MODEL-001 — Simple Elo model

The MVP must use a transparent simple Elo/rating-difference model.

For each match, the model must calculate the probability that each team advances based on the difference between their ratings.

### REQ-MODEL-002 — Deterministic output

For a given pair of teams, rating values, and selected model, the model must always return the same probabilities.

### REQ-MODEL-003 — Probability range

Each match probability must be between 0 and 1.

### REQ-MODEL-004 — Probability sum

For every resolved match, both team probabilities must sum to 1.0 within an acceptable floating-point tolerance.

### REQ-MODEL-005 — Equal ratings

If two teams have equal ratings, the simple Elo model should return equal advancement probabilities.

Recommended output:

```text
Team A: 0.5
Team B: 0.5
```

### REQ-MODEL-006 — Higher rating advantage

If Team A has a higher rating than Team B, Team A must receive a higher advancement probability than Team B in the simple Elo model.

### REQ-MODEL-007 — Transparency

The frontend should expose enough information for users to understand why one team is favored.

At minimum, it should show or make available:

- Team ratings
- Match probabilities
- Selected model name
- Model method summary

### REQ-MODEL-008 — Historically informed Elo model

The historically informed Elo model is implemented in Stage 7 as `historically_informed_elo`.

It must not be implemented before the simple Elo model, bracket propagation, overrides, and champion probability calculation are stable and tested.

The implemented Stage 7 model uses local historical result snapshots, reconstructed pre-match Elo features, and an offline calibrated logistic curve exported as compact static frontend data.

### REQ-MODEL-009 — Historical calibration input

Once implemented, the historically informed model must be trained or calibrated from historical match features built from:

- Historical match results
- Pre-match Elo estimates
- Rating differences
- Match outcomes

### REQ-MODEL-010 — Historical model export

The historically informed model must be trained/calibrated offline in Python and exported as static model parameters.

The browser must be able to use the historical model without calling a Python backend.

---

## 8. Model Toggle Requirements

### REQ-TOGGLE-001 — Model selector

Once more than one model is available, the frontend must provide a model selector or toggle.

At minimum, it must support:

- Simple Elo
- Historically informed Elo

### REQ-TOGGLE-002 — Disabled future model

Before or whenever the historically informed model artifact is unavailable, the frontend may hide it or show it as disabled.

The app must not expose a non-working model toggle.

### REQ-TOGGLE-003 — Recalculate on model change

Changing the selected model must recompute:

- Match probabilities
- Model-selected winners
- Downstream bracket propagation
- Champion probabilities
- Top four champion summary

### REQ-TOGGLE-004 — Overrides remain stable across model changes

User overrides should remain in place when the selected model changes, as long as the overridden winner is still valid for that match.

### REQ-TOGGLE-005 — Model-specific explanation

The UI should show a short explanation of the selected model.

For `simple_elo`, explain that the model uses rating difference directly.

For `historical_elo`, explain that the model adjusts rating-difference probabilities using historical match outcomes.

---

## 9. Bracket Logic Requirements

### REQ-BRACKET-001 — First-round teams

Round-of-32 matches must contain fixed team slots.

### REQ-BRACKET-002 — Later-round teams

Later-round matches must receive teams from the winners of previous matches.

### REQ-BRACKET-003 — Winner propagation

When a winner is selected in a match, that team must advance to the correct downstream match and slot.

### REQ-BRACKET-004 — Baseline winner selection

In the baseline forecast, the selected model must automatically select the team with the higher advancement probability as the predicted winner.

### REQ-BRACKET-005 — Unresolved match handling

If a match does not yet have two valid teams, it must be marked as unresolved.

The app must not calculate misleading probabilities for unresolved matches.

### REQ-BRACKET-006 — Final winner

The final match winner must be displayed as the predicted champion in the bracket path.

### REQ-BRACKET-007 — No hard-coded UI logic

Bracket logic must not be hard-coded directly inside React display components.

The bracket calculation should be implemented in reusable functions that can be tested separately.

---

## 10. Forecast Mode Requirements

### REQ-MODE-001 — Baseline forecast

The app must provide a baseline forecast.

The baseline forecast must use:

- Initial bracket
- Team ratings
- Selected probability model
- Official locked results, if present in a future version
- No user overrides

### REQ-MODE-002 — Current scenario forecast

The app must provide a current scenario forecast.

The current scenario forecast must use:

- Initial bracket
- Team ratings
- Selected probability model
- User overrides
- Official locked results, if present in a future version

### REQ-MODE-003 — Mode distinction

The UI must clearly distinguish between the baseline forecast and the current scenario forecast.

### REQ-MODE-004 — Recalculation

When the user changes a match winner, the current scenario forecast must update.

Affected downstream matches and champion probabilities must be recalculated.

---

## 11. Manual Override Requirements

### REQ-OVERRIDE-001 — User can override winners

Users must be able to manually select the winner of a match.

### REQ-OVERRIDE-002 — Override validity

A user override is valid only if the selected winner is one of the two teams currently assigned to that match.

### REQ-OVERRIDE-003 — Downstream recalculation

When a user override changes an advancing team, all dependent downstream matches must be recalculated.

### REQ-OVERRIDE-004 — Invalid downstream overrides

If an upstream override changes the teams in a downstream match, and a previous downstream override no longer refers to a team in that match, the invalid downstream override must be cleared or ignored.

The app must not keep impossible bracket states.

### REQ-OVERRIDE-005 — Visual marking

User-overridden matches must be visually marked.

The user must be able to tell when a winner was selected manually rather than by the model.

### REQ-OVERRIDE-006 — Reset overrides

The app must provide a way to reset user overrides.

After reset, the current scenario forecast should match the baseline forecast for the selected model.

### REQ-OVERRIDE-007 — Local-only overrides

In the MVP, user overrides must remain local to the browser.

They must not be written to source files or uploaded to a server.

---

## 12. Champion Probability Requirements

### REQ-CHAMP-001 — Champion probabilities

The app must calculate each team’s probability of winning the tournament.

### REQ-CHAMP-002 — Exact propagation preferred

The MVP must use exact probability propagation where practical.

The deployed app must not require Monte Carlo simulation for every user interaction.

### REQ-CHAMP-003 — Probability sum

The sum of champion probabilities across all teams must be 1.0 within an acceptable floating-point tolerance.

### REQ-CHAMP-004 — Top four summary

The app must show the four most likely World Cup champions and their probabilities.

### REQ-CHAMP-005 — Current scenario update

Champion probabilities must update when user overrides change the current scenario forecast.

### REQ-CHAMP-006 — Baseline versus scenario probabilities

The app should allow users to understand whether displayed champion probabilities correspond to:

- The baseline forecast, or
- The current user-modified scenario

### REQ-CHAMP-007 — Model-specific champion probabilities

Champion probabilities must be calculated using the selected model.

When the model toggle changes, champion probabilities must update.

### REQ-CHAMP-008 — Monte Carlo role

Monte Carlo simulation may be used as a Python-side validation or comparison tool.

Monte Carlo is not required for the deployed MVP.

---

## 13. User Interface Requirements

### REQ-UI-001 — Full bracket display

The UI must display the full knockout bracket from Round of 32 to final.

### REQ-UI-002 — Team display

Each team display should include:

- Flag
- Team name or short name
- Advancement probability, where applicable

### REQ-UI-003 — Match display

Each match display should include:

- Both teams
- Probability for each team
- Selected winner
- Selection source indicator, where appropriate

### REQ-UI-004 — Champion summary

The page must include a summary section showing the top four most likely champions.

### REQ-UI-005 — Method information

The page should include a short method explanation.

The user should be able to understand that the forecast is rating-based and probabilistic.

### REQ-UI-006 — Model toggle

Once more than one model is available, the UI must include a clear model toggle or selector.

### REQ-UI-007 — Responsive layout

The app must be usable on desktop and mobile.

The mobile layout does not need to show the bracket in the same shape as desktop, but it must remain readable and functional.

### REQ-UI-008 — Professional appearance

The app should look like a polished public website, not a debugging tool.

### REQ-UI-009 — No clutter

The bracket must avoid unnecessary visual clutter.

Probabilities, flags, names, and winners must be readable.


---

## 13A. Visual Design Requirements

### REQ-STYLE-001 — Visual Design v2 direction

The website must use Visual Design v2 as the controlling MVP visual direction.

Visual Design v2 is a premium football analytics dashboard with:

- Light outer page shell
- Dark bracket panel/canvas
- Bracket-first first viewport
- Stronger but controlled color system
- Polished knockout-tree presentation
- Professional analytical tone

Visual Design v1 was the previous Financial Times-inspired editorial aesthetic with warm paper background and restrained newspaper-like data-publication feel. V1 is now superseded because it was too restrained: the MVP was functionally good but visually too empty, quiet, and unattractive. The bracket is the product and must become the immediate visual hero.

### REQ-STYLE-002 — Original identity

The website must not present itself as a Financial Times product.

It must not use the FT logo, Financial Times trademarks, FT content, or proprietary FT fonts unless the project owner has a documented license.

### REQ-STYLE-003 — Bracket-first first viewport

On desktop, the bracket must be prominently visible in the first viewport.

The page must avoid large empty ceremonial whitespace before the bracket.

Navigation and title content must be compact enough that the large bracket panel is visible immediately on landing.

Stage 6.3 / Visual Design v2.1 requires this page hierarchy:

1. Title / nav row
2. Bracket
3. Model status, scenario controls, champion summary, and reset controls
4. Additional explanations
5. Footer

The bracket must appear immediately after the title/header area. Model controls, champion summary, and scenario panels must not push the bracket downward or make it visually subordinate.

### REQ-STYLE-004 — Dark bracket panel and controlled palette

The UI must use a light page shell around a dark bracket panel/canvas.

Recommended color roles:

- Light page shell
- Dark navy/charcoal bracket panel
- Off-white or deep slate match nodes
- Dark ink text
- Muted secondary text
- Muted slate connector lines
- Gold/amber for final or champion-path emphasis
- Teal/green for selected winners and user picks
- Grey/desaturated lower-opacity losing states

The UI must not use aggressive sportsbook colors, over-bright neon, excessive beige, pastel SaaS styling, or childish sports-broadcast graphics.

### REQ-STYLE-005 — Editorial typography

The interface must use an editorial typographic hierarchy.

Recommended approach:

- Serif or editorial-style typeface for major headings
- Sans-serif typeface for controls, labels, compact data, and match cards
- Tabular numbers for probabilities and rankings
- Clear line-height and spacing suitable for reading

Open or system fonts should be used unless licensed fonts are explicitly available.

### REQ-STYLE-006 — No proprietary font files

The repository must not include proprietary FT font files or any font file without a clear license.

If web fonts are used, their source and license must be documented.

### REQ-STYLE-007 — CSS design tokens

Visual constants must be expressed through reusable CSS tokens.

Recommended files:

```text
frontend/src/styles/tokens.css
frontend/src/styles/global.css
frontend/src/styles/typography.css
frontend/src/styles/layout.css
frontend/src/styles/components.css
```

React components should consume CSS classes or tokens rather than hard-coded inline styling.

### REQ-STYLE-008 — Knockout-tree bracket hierarchy

The bracket must be presented as a polished tournament-tree diagram:

- Left half of bracket
- Central final area
- Right half of bracket
- Visible connector lines
- Round labels that are present but not oversized
- Compact match nodes

The structure must be understandable at a glance and feel like a real knockout wall chart, not a generic list of cards.

Winner and loser states must be visual:

- Winners should be highlighted.
- Losers should be greyed out, desaturated, or lower opacity.
- Large textual `WIN` labels inside team names must not be used.

Country labels in bracket nodes must not wrap mid-word. If full country names do not fit, use FIFA-style three-letter codes in compact nodes. Full names may appear in accessible labels, title text, tooltips, or detail states.

If `flag_mode = "asset"`, the flag displayed in bracket nodes and summaries must be the local image from `flag_value`. The compact team label may use a FIFA-style code, but the flag itself must not be replaced by ISO alpha-2 text when a valid local asset is available.

If a local asset fails to load, the UI must fall back gracefully to a short text label such as the FIFA code or short name.

The UI should use:

- Fine rules
- Compact data rows
- Ranked lists
- Short captions
- Clear headings
- Minimal ornament

### REQ-STYLE-009 — Avoid betting-site language and visuals

The app must avoid betting-site language and visual patterns.

Avoid language such as:

```text
Best bets
Lock of the day
Guaranteed winner
```

Use language such as:

```text
Forecast probability
Title probability
Model estimate
Most likely champions
```

### REQ-STYLE-010 — Accessibility over aesthetics

The editorial aesthetic must not reduce accessibility.

Text contrast, focus states, keyboard navigation, and non-colour indicators remain mandatory.

### REQ-STYLE-011 — Visual design documentation

The implementation must follow:

```text
docs/visual_design.md
```

The implementation must follow the Visual Design v2 section in that document, not the superseded v1 FT-inspired direction.

unless that document is explicitly revised.

---

## 14. Accessibility Requirements

### REQ-A11Y-001 — Keyboard usability

Interactive elements should be usable by keyboard.

### REQ-A11Y-002 — Text contrast

Text should have sufficient contrast against its background.

### REQ-A11Y-003 — Non-color indicators

The UI must not rely only on color to communicate important states such as user override, selected model, or official lock.

### REQ-A11Y-004 — Semantic structure

The page should use appropriate headings, labels, and semantic structure.

### REQ-A11Y-005 — Screen-reader labels

Buttons or controls for selecting winners and model mode should have clear accessible labels.

---

## 15. Local Persistence Requirements

### REQ-PERSIST-001 — Optional browser persistence

The MVP may persist user overrides and selected model in local browser storage.

### REQ-PERSIST-002 — No accounts

The MVP must not include user accounts or login.

### REQ-PERSIST-003 — Reset local state

If local persistence is implemented, the user must be able to clear saved overrides.

### REQ-PERSIST-004 — Stable IDs only

Persisted local state must use stable match IDs, team IDs, and model IDs.

It must not rely on display names.

---

## 16. Deployment and CI/CD Requirements

### REQ-DEPLOY-001 — Static build

The project must be buildable into static frontend assets.

The production build output must not require a backend server.

### REQ-DEPLOY-002 — GitHub Pages target

The primary deployment target must be GitHub Pages.

The project must be compatible with GitHub Pages static hosting.

### REQ-DEPLOY-003 — GitHub Actions publishing source

GitHub Pages deployment must use GitHub Actions as the publishing source.

The project should not rely on manual copying of build files into a deployment branch for normal operation.

### REQ-DEPLOY-004 — Official Pages Actions

The deployment workflow should use the official GitHub Pages Actions:

- `actions/configure-pages`
- `actions/upload-pages-artifact`
- `actions/deploy-pages`

Third-party deployment actions must not be introduced for the MVP unless explicitly approved.

### REQ-DEPLOY-005 — Build artifact path

The deployment workflow must upload only the static frontend build output as the Pages artifact.

Recommended artifact path:

```text
frontend/dist
```

The workflow must not upload the whole repository as the deployed site.

### REQ-DEPLOY-006 — Vite build compatibility

The frontend must build successfully with Vite.

The Vite configuration must support deployment under a GitHub Pages project path.

If deployed at:

```text
https://<owner>.github.io/<repository-name>/
```

then the frontend must use the correct base path:

```text
/<repository-name>/
```

### REQ-DEPLOY-007 — Static data included in build

The generated frontend data file must be present in the static build before deployment.

The deployed app must be able to load the tournament data from the published GitHub Pages site.

### REQ-DEPLOY-008 — No secret runtime configuration

The deployed frontend must not require private API keys or secrets.

No secrets must be embedded in the frontend bundle.

### REQ-DEPLOY-009 — No runtime external data dependency

The deployed frontend must not fetch live Elo data, live match data, or historical result databases from external sources during user interaction.

All necessary runtime forecast data must be included as static files in the deployed site.

### REQ-DEPLOY-010 — Reproducible build

The build process must be reproducible from committed source files and local data snapshots.

The deployment workflow must be able to regenerate frontend data before building the React app.

### REQ-DEPLOY-011 — Clear setup failure

If required source data is missing, setup or build scripts must fail clearly and explain what file is missing.

### REQ-DEPLOY-012 — `.nojekyll` support

The build output should include `.nojekyll` if needed to prevent GitHub Pages from applying Jekyll processing to static assets.

### REQ-DEPLOY-013 — Routing compatibility

If client-side routing is introduced, it must be compatible with GitHub Pages.

Acceptable approaches are:

- No deep client-side routes in the MVP
- Hash-based routing
- A generated `404.html` fallback

The MVP should avoid unnecessary routing complexity.

### REQ-DEPLOY-014 — GitHub Pages limits

The deployed site must remain small enough for GitHub Pages.

The frontend bundle must not include raw historical databases unless they are explicitly needed by the UI.

Large historical inputs should remain in `data/raw` or `data/processed`, not in the deployed bundle.

---

## 17. CI Workflow Requirements

### REQ-CI-001 — CI workflow file

The repository must include a CI workflow:

```text
.github/workflows/ci.yml
```

### REQ-CI-002 — CI triggers

The CI workflow should run on:

- Pull requests
- Pushes to development branches
- Manual dispatch, if useful

### REQ-CI-003 — CI must not deploy

The CI workflow must validate the project but must not deploy to GitHub Pages.

### REQ-CI-004 — Python validation in CI

CI must run the Python-side validation and tests.

At minimum, CI should run:

- Python dependency installation
- Data validation
- Frontend data generation
- Python tests

### REQ-CI-005 — Frontend validation in CI

CI must run the frontend checks.

At minimum, CI should run:

```text
npm ci
npm run lint
npm run typecheck
npm test
npm run build
```

If a command is not yet available, the project must either add it or document why it is temporarily omitted.

### REQ-CI-006 — CI failure on invalid data

CI must fail if data validation fails.

CI must not allow missing ratings, invalid bracket references, duplicated IDs, or stale generated data to pass silently.

### REQ-CI-007 — CI failure on TypeScript errors

CI must fail if TypeScript checking fails.

### REQ-CI-008 — CI failure on test errors

CI must fail if Python or frontend tests fail.

### REQ-CI-009 — Dependency installation

Frontend dependencies must be installed with `npm ci` in CI.

This requires a committed lockfile.

### REQ-CI-010 — Generated frontend data policy

CI must either:

- Generate `frontend/public/data/tournament.json` before frontend tests and build, or
- Verify that the committed generated file is fresh and consistent with the source data.

The project should prefer generation during CI.

---

## 18. GitHub Pages Deployment Workflow Requirements

### REQ-PAGES-001 — Deployment workflow file

The repository must include a deployment workflow:

```text
.github/workflows/deploy-pages.yml
```

### REQ-PAGES-002 — Deployment triggers

The deployment workflow should run on:

- Pushes to `main`
- Manual dispatch

Pull requests must not deploy to the production GitHub Pages site.

### REQ-PAGES-003 — Deployment gate

Deployment must happen only after validation, tests, and the static build succeed.

### REQ-PAGES-004 — Minimal permissions

The deployment workflow must use minimal permissions:

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

### REQ-PAGES-005 — Pages environment

The deployment job should use the GitHub Pages environment.

Recommended environment name:

```text
github-pages
```

### REQ-PAGES-006 — Deployment concurrency

The deployment workflow should use a concurrency group for Pages deployments.

This prevents multiple deployments from racing.

### REQ-PAGES-007 — Pages artifact upload

The workflow must upload the built static site with `actions/upload-pages-artifact` or the official equivalent.

### REQ-PAGES-008 — Pages deployment action

The workflow must deploy the uploaded artifact with `actions/deploy-pages` or the official equivalent.

### REQ-PAGES-009 — No third-party deployment services

The MVP must not require Netlify, Vercel, Railway, Render, Fly.io, Heroku, or any other external deployment service.

### REQ-PAGES-010 — Production source

The production deployment should represent the `main` branch plus deterministic generated build artifacts.

### REQ-PAGES-011 — Deployment summary

The workflow should expose the deployed GitHub Pages URL in the Actions deployment summary when available.

---

## 19. Optional Data Refresh Workflow Requirements

### REQ-DATAREFRESH-001 — Manual-only data refresh

A future data refresh workflow may exist:

```text
.github/workflows/refresh-data.yml
```

This workflow must be manual-only unless explicitly approved.

### REQ-DATAREFRESH-002 — No silent production data changes

Data refresh must not silently change production forecasts without review.

Fetched Elo or historical data should produce local snapshots that can be reviewed before deployment.

### REQ-DATAREFRESH-003 — Snapshot preservation

The data refresh process must preserve source metadata, retrieval date, snapshot kind, and model metadata.

### REQ-DATAREFRESH-004 — No runtime scraping substitute

A data refresh workflow must not replace the static-site rule.

The public website must still use static data.


---

## 20. Testing Requirements

### REQ-TEST-001 — Probability tests

Automated tests must cover probability calculations.

At minimum, tests must check:

- Equal ratings produce equal probabilities
- Higher rating produces higher probability
- Probabilities are between 0 and 1
- Probabilities sum to 1

### REQ-TEST-002 — Bracket propagation tests

Automated tests must cover bracket propagation.

At minimum, tests must check:

- First-round winners feed into correct later-round slots
- Final winner can be resolved
- Invalid references fail validation

### REQ-TEST-003 — Override tests

Automated tests must cover manual override behavior.

At minimum, tests must check:

- User override changes winner
- User override changes downstream match participants
- Invalid downstream overrides are cleared or ignored
- Reset restores baseline behavior

### REQ-TEST-004 — Champion probability tests

Automated tests must cover champion probability calculation.

At minimum, tests must check:

- Champion probabilities sum to 1
- Eliminated teams receive zero probability when applicable
- Forced scenario paths affect probabilities correctly
- Changing selected model changes probabilities when model outputs differ

### REQ-TEST-005 — Data validation tests

Automated tests must cover source data validation.

At minimum, tests must check:

- Missing rating fails validation
- Duplicate team ID fails validation
- Duplicate match ID fails validation
- Duplicate model ID fails validation
- Invalid match reference fails validation
- Invalid historical result row fails validation
- Invalid official lock fails validation, once official locks exist

### REQ-TEST-006 — Frontend logic tests

Frontend calculation logic should be testable independently from UI rendering.

Bracket logic must not exist only inside visual components.

### REQ-TEST-007 — Historical model tests

Once the historical model exists, automated tests must cover:

- Historical result normalization
- Team alias mapping
- Historical Elo reconstruction
- Historical feature generation
- Calibration output shape
- Historical model probability range
- Historical model probability sum
- Model toggle behavior

### REQ-TEST-008 — No visual-only testing

The project must not rely only on manual visual inspection.

The mathematical and bracket logic must have automated tests.


### REQ-TEST-STYLE-001 — Visual style regression discipline

The project should include at least lightweight protection against accidental visual drift.

Acceptable MVP checks include:

- CSS linting
- Typecheck and build validation
- Component-level smoke tests for the bracket, champion summary, and model toggle
- Manual screenshot review before major visual changes

Automated visual regression testing may be added later, but is not required for the MVP.

---

## 21. Performance Requirements

### REQ-PERF-001 — Fast interaction

Manual winner overrides should update the bracket without noticeable delay.

### REQ-PERF-002 — No heavy runtime simulation

The deployed app must not require large Monte Carlo simulations on every click.

### REQ-PERF-003 — Browser suitability

The calculation approach must be suitable for normal consumer browsers.

### REQ-PERF-004 — Static asset size

The generated frontend data should remain small enough for quick loading.

The MVP should avoid unnecessary large datasets in the public bundle.

Historical training data should not be bundled into the frontend unless explicitly needed.

---

## 22. Error Handling Requirements

### REQ-ERR-001 — Missing frontend data

If the frontend data file cannot be loaded, the app must show a clear error message.

### REQ-ERR-002 — Invalid bracket state

If the bracket cannot be resolved because of invalid data, the app must fail visibly rather than showing misleading predictions.

### REQ-ERR-003 — Missing team rating

A missing team rating must be treated as a data error.

The app must not silently assume a default rating.

### REQ-ERR-004 — Invalid user override

Invalid user overrides must be ignored or cleared.

The app must not display impossible matchups.

### REQ-ERR-005 — Unavailable selected model

If a persisted or URL-specified model ID is unavailable, the app must fall back to the default model and inform the user where appropriate.

---

## 23. Future Requirements: Historically Informed Elo

Historical calibration is not part of the MVP unless explicitly moved into MVP scope.

### REQ-FUTURE-HISTELO-001 — Historical result ingestion

A future version must ingest historical match result data from a local source snapshot.

### REQ-FUTURE-HISTELO-002 — Elo reconstruction

A future version should reconstruct historical pre-match Elo values locally from historical match results.

### REQ-FUTURE-HISTELO-003 — Calibration

A future version should calibrate the rating-difference probability model using historical outcomes.

### REQ-FUTURE-HISTELO-004 — Exported parameters

The historical model must export compact static parameters for frontend use.

### REQ-FUTURE-HISTELO-005 — User-facing toggle

The user must be able to switch between simple Elo and historically informed Elo once both models exist.

---

## 24. Future Requirements: Official Result Locking

Official result locking is not part of the MVP.

However, the MVP architecture must not block it.

### REQ-FUTURE-LOCK-001 — Static official results file

A future version should support official results stored in a static file.

Recommended file:

```text
data/snapshots/official_results.json
```

### REQ-FUTURE-LOCK-002 — Locked winner

A locked result should force the official winner to advance.

### REQ-FUTURE-LOCK-003 — Override priority

Official locked results must override user overrides.

### REQ-FUTURE-LOCK-004 — Visual distinction

Official locked results should be visually distinct from model predictions and user overrides.

### REQ-FUTURE-LOCK-005 — Static redeploy workflow

The official-lock feature should work through static data update and redeployment, not through a live admin panel in the MVP architecture.

---

## 25. Future Requirements: Forecast History

Forecast history is not part of the MVP.

However, the MVP architecture must not block it.

### REQ-FUTURE-HIST-001 — Forecast snapshots

A future version should support forecast snapshots after official results are locked.

### REQ-FUTURE-HIST-002 — Probability time series

A future version should show how each team’s champion probability changes over time.

### REQ-FUTURE-HIST-003 — Snapshot metadata

Each snapshot should include:

- Snapshot ID
- Timestamp
- Locked matches
- Rating snapshot
- Model version
- Champion probabilities
- Top four most likely champions

---

## 26. Future Requirements: Shareable Scenarios

Shareable scenarios are not part of the MVP.

However, the MVP architecture must not block them.

### REQ-FUTURE-SHARE-001 — URL-encoded scenario

A future version may encode user overrides and selected model in the URL.

### REQ-FUTURE-SHARE-002 — Stable IDs

Shareable scenarios must use stable match IDs, team IDs, and model IDs.

### REQ-FUTURE-SHARE-003 — No backend required

Shareable scenarios should not require user accounts or backend storage.

---

## 27. Explicit MVP Non-Requirements

The MVP must not include:

- Group-stage prediction
- Betting odds
- Live match updates
- Player-level modeling
- Injury modeling
- Lineup modeling
- Weather modeling
- User accounts
- Login
- Backend database
- Live admin dashboard
- Paid server infrastructure
- Runtime Python server
- Runtime data scraping
- Real-time rating updates during user interaction
- Historically informed Elo, unless explicitly promoted into MVP scope

---

## 28. Acceptance Criteria for MVP

The MVP is acceptable when all of the following are true:

1. A static React + TypeScript app builds successfully.
2. The app loads a generated static tournament JSON file.
3. The app displays a full 32-team knockout bracket.
4. Every resolved match shows both teams and advancement probabilities.
5. The baseline forecast automatically advances model-selected winners.
6. The user can manually override match winners.
7. Downstream matches update after overrides.
8. The current scenario forecast updates after overrides.
9. The app shows the top four most likely champions.
10. Champion probabilities are calculated without requiring a backend.
11. Probability and bracket logic are covered by automated tests.
12. Missing or invalid source data fails validation clearly.
13. The app can be deployed as a static website.
14. The UI is readable, accessible, and suitable for public viewing.
15. The UI follows the Visual Design v2/v2.1 bracket-first direction defined in `docs/visual_design.md`.
16. No FT logos, trademarks, proprietary fonts, or FT content are included without license.
15. Source metadata is visible or available in the generated frontend data.

---

## 29. Acceptance Criteria for Historically Informed Elo Version

The historically informed Elo version is acceptable when all of the following are true:

1. Historical results are ingested from a local snapshot.
2. Team aliases are resolved through a documented mapping.
3. Historical pre-match Elo features are generated reproducibly.
4. Calibration parameters are generated offline.
5. The frontend can switch between `simple_elo` and `historical_elo`.
6. Changing model selection updates probabilities and champion summary.
7. Historical model output is deterministic.
8. Historical model output probabilities are valid and sum to 1.
9. The selected model is clearly explained in the UI.
10. The deployed app still requires no backend.

---

## 30. Guidance for Coding Agents

Coding agents must implement the MVP requirements before attempting future features.

Do not add a backend, database, authentication system, or live admin panel unless the architecture document is explicitly revised.

Do not implement advanced football realism before the basic simple Elo model, bracket propagation, overrides, and champion probability calculation are working and tested.

Do not hard-code tournament logic into UI components.

Do not use display names as identifiers.

Do not silently invent missing ratings or missing teams.

Do not label post-tournament or in-tournament ratings as pre-tournament ratings.

The priority order is:

1. Valid data model
2. Correct simple Elo probability math
3. Correct bracket propagation
4. Correct override behavior
5. Correct champion probability calculation
6. Polished public UI
7. Static deployment
8. Historical Elo data pipeline
9. Historical calibration
10. Model toggle
11. Future enhancements
