# agents.md

# World Cup Knockout Forecast Website — Coding Agent Instructions

## 1. Purpose

This document defines the expected behavior, permissions, restrictions, and workflow for coding agents working on the World Cup knockout forecast website.

The coding agent must treat this file as the operational contract for implementation. The project must remain aligned with the documented architecture, data model, and requirements.

Relevant project documents:

```text
/docs/problem_statement.md
/docs/architecture_decisions.md
/docs/data_model.md
/docs/requirements.md
/docs/testing_strategy.md
/docs/agents.md
```

If a requested implementation conflicts with these documents, the agent must stop and report the conflict rather than silently changing the architecture.

---

## 2. Project Summary for Agents

The project is a public World Cup knockout-stage forecast website.

The app must:

- Display a 32-team knockout bracket starting at the Round of 32.
- Show match advancement probabilities.
- Use a rating-difference model for the MVP.
- Support manual user overrides.
- Recalculate downstream matches after overrides.
- Recalculate champion probabilities in the browser.
- Support a baseline forecast and a current scenario forecast.
- Be deployable as a static React + TypeScript website.

Python is used only for build-time, data preparation, data validation, and model validation.

The deployed app must not require a live backend.

---

## 3. Global Architecture Rule

The coding agent must preserve the following rule:

> The deployed public website must run as a static site. Do not introduce backend runtime dependencies unless the architecture document is explicitly revised.

This means the agent must not introduce:

- A live Python backend
- A Node/Express backend
- A database
- Runtime authentication
- Server-side sessions
- Runtime scraping
- Paid server infrastructure
- Secret API keys in frontend code

Normal user interaction must happen client-side in the browser.

---

## 4. Required Reading Before Implementation

Before making implementation changes, the coding agent must read:

1. `docs/architecture_decisions.md`
2. `docs/data_model.md`
3. `docs/requirements.md`
4. `docs/agents.md`

For changes involving statistical logic, the agent must also inspect relevant tests or create them before modifying behavior.

For changes involving data files, the agent must inspect the validation rules in `data_model.md` and `requirements.md`.

---

## 5. Allowed Agent Actions

The coding agent may:

- Create or modify React + TypeScript frontend code.
- Create or modify Python data preparation scripts.
- Create or modify static JSON data generation scripts.
- Create or modify tests.
- Create or modify project documentation when the implementation changes.
- Add small, justified dependencies.
- Refactor code while preserving documented behavior.
- Improve accessibility and responsiveness.
- Improve error messages.
- Improve test coverage.
- Add helper functions for bracket, probability, and forecast logic.
- Create or modify GitHub Actions workflows required for CI and GitHub Pages deployment.

The agent may also create sample data for testing, but sample data must be clearly marked as test/demo data and must not be presented as real ratings or real World Cup data.

---

## 6. Forbidden Agent Actions

The coding agent must not:

- Add a runtime backend to the MVP.
- Add a database to the MVP.
- Add login, accounts, or authentication to the MVP.
- Add betting odds or betting advice.
- Add player-level, injury, weather, or lineup modeling to the MVP.
- Add live scraping during user interaction.
- Fetch live rating data from the frontend.
- Silently invent missing ratings.
- Silently invent missing teams.
- Use display names as stable identifiers.
- Generate random team IDs or match IDs.
- Change existing stable IDs without explicit approval.
- Hard-code bracket propagation inside visual UI components.
- Store derived probabilities as authoritative source data.
- Allow user overrides to modify official locked results.
- Allow impossible bracket states to persist silently.
- Implement Phase 2 or Phase 3 features before the MVP is stable unless explicitly instructed.
- Replace GitHub Pages with another deployment target without explicit approval.
- Add Netlify, Vercel, Railway, Render, Fly.io, Heroku, or similar services to the MVP.
- Use third-party GitHub Pages deployment actions instead of official GitHub Pages Actions without explicit approval.
- Put secrets, tokens, or private API keys into frontend code or workflow files.
- Deploy pull requests to the production GitHub Pages site.

---

## 7. Changes Requiring Explicit Human Approval

The coding agent must request approval before:

- Changing the static-site architecture.
- Adding a backend service.
- Adding a database.
- Adding authentication.
- Adding paid third-party services.
- Adding dependencies with large bundle size or unclear maintenance status.
- Changing the rating source strategy.
- Changing the core probability formula.
- Changing stable `team_id` or `match_id` conventions.
- Changing the generated frontend data contract.
- Removing validation checks.
- Removing or weakening tests.
- Expanding scope into non-MVP features.
- Changing the GitHub Pages deployment strategy.
- Changing the branch that deploys to production.
- Enabling automatic external data refresh as part of normal deployment.

If approval is not available, the agent must choose the option that preserves the existing architecture and requirements.

---

## 8. Implementation Priority

The coding agent must prioritize implementation in this order:

1. Valid data model
2. Data validation
3. Probability calculation
4. Bracket propagation
5. Manual override behavior
6. Champion probability calculation
7. Baseline versus current scenario mode
8. Frontend display
9. Accessibility and responsiveness
10. Static deployment
11. Future enhancements

The agent must not prioritize visual polish over mathematical correctness.

The agent must not prioritize advanced football realism over a correct MVP.

---

## 9. Expected Repository Structure

The agent should preserve this general structure:


```text
world-cup-forecast/
├─ .github/
│  └─ workflows/
│     ├─ ci.yml
│     ├─ deploy-pages.yml
│     └─ refresh-data.yml        # optional/manual-only, not MVP deploy path
├─ frontend/
│  ├─ public/
│  │  ├─ data/
│  │  │  └─ tournament.json
│  │  └─ flags/
│  ├─ src/
│  │  ├─ app/
│  │  ├─ components/
│  │  │  ├─ Bracket/
│  │  │  ├─ MatchCard/
│  │  │  ├─ ChampionSummary/
│  │  │  ├─ ModelToggle/
│  │  │  └─ MethodNotes/
│  │  ├─ domain/
│  │  │  ├─ bracket/
│  │  │  ├─ probability/
│  │  │  ├─ forecast/
│  │  │  └─ validation/
│  │  ├─ hooks/
│  │  ├─ styles/
│  │  │  ├─ tokens.css
│  │  │  ├─ global.css
│  │  │  ├─ typography.css
│  │  │  ├─ layout.css
│  │  │  └─ components.css
│  │  ├─ types/
│  │  └─ main.tsx
│  ├─ package.json
│  ├─ tsconfig.json
│  └─ vite.config.ts
├─ scripts/
│  ├─ fetch_current_elo.py
│  ├─ fetch_historical_results.py
│  ├─ prepare_bracket.py
│  ├─ validate_data.py
│  ├─ build_historical_elo.py
│  ├─ calibrate_historical_model.py
│  ├─ validate_model.py
│  └─ generate_frontend_data.py
├─ data/
│  ├─ raw/
│  │  ├─ elo/
│  │  └─ results/
│  ├─ manual/
│  │  ├─ bracket.json
│  │  ├─ team_aliases.csv
│  │  └─ teams.csv
│  ├─ snapshots/
│  │  ├─ ratings.csv
│  │  ├─ official_results.json
│  │  └─ forecast_history.json
│  ├─ processed/
│  │  ├─ teams_normalized.csv
│  │  ├─ historical_results_normalized.csv
│  │  ├─ historical_elo_timeseries.csv
│  │  ├─ historical_match_features.csv
│  │  └─ calibrated_model.json
│  └─ frontend/
│     └─ tournament.json
├─ tests/
│  ├─ python/
│  │  ├─ test_data_validation.py
│  │  ├─ test_probability_model.py
│  │  ├─ test_historical_elo_builder.py
│  │  └─ test_calibration.py
│  └─ frontend/
│     ├─ bracket.test.ts
│     ├─ probability.test.ts
│     ├─ overrides.test.ts
│     └─ championProbability.test.ts
├─ docs/
│  ├─ problem_statement.md
│  ├─ architecture_decisions.md
│  ├─ data_model.md
│  ├─ requirements.md
│  ├─ visual_design.md
│  ├─ testing_strategy.md
│  └─ agents.md
├─ README.md
└─ pyproject.toml
```
---

## 9A. Visual Design Agent Rules

The coding agent must implement an FT-inspired editorial data-publication aesthetic.

This means:

- Warm paper-like background
- Restrained editorial palette
- Strong typographic hierarchy
- Fine rules and borders
- Compact data layout
- Calm interaction states
- Serious analytical tone

The agent must follow:

```text
docs/visual_design.md
```

### 9A.1 Allowed Visual Actions

The agent may:

- Create or modify custom CSS files.
- Add CSS design tokens.
- Use open-source or system fonts with documented licenses.
- Use serif headings and sans-serif UI text.
- Use tabular numeric formatting for probabilities.
- Improve layout, spacing, and visual hierarchy.
- Add responsive bracket layouts.
- Add accessible focus states.

### 9A.2 Forbidden Visual Actions

The agent must not:

- Use the FT logo.
- Name the product as if it were a Financial Times product.
- Use Financial Times trademarks as product branding.
- Commit proprietary FT font files.
- Import FT content, articles, headlines, or imagery.
- Copy the FT interface so closely that it implies affiliation.
- Add a heavy UI framework just for styling.
- Use betting-site visual language.
- Prioritize visual polish over mathematical correctness.

### 9A.3 Approval Required

The agent must ask for approval before:

- Adding any external font dependency.
- Adding any external image or icon package.
- Adding a UI framework.
- Changing the visual direction away from the editorial/FT-inspired style.
- Adding visual regression tooling that meaningfully changes CI runtime.

### 9A.4 CSS Rules

The agent should use:

```text
frontend/src/styles/tokens.css
frontend/src/styles/global.css
frontend/src/styles/typography.css
frontend/src/styles/layout.css
frontend/src/styles/components.css
```

The agent must avoid scattering one-off hard-coded colours and spacing values across React components.

The visual system should be token-based and maintainable.



Small deviations are allowed only when they improve clarity and do not violate the architecture.


---

## 10. CI/CD and GitHub Pages Rules

The agent must treat GitHub Pages deployment as part of the MVP contract.

### 10.1 Required Workflow Files

The agent should create and maintain:

```text
.github/workflows/ci.yml
.github/workflows/deploy-pages.yml
```

An optional future workflow may exist:

```text
.github/workflows/refresh-data.yml
```

The optional data refresh workflow must be manual-only unless the human explicitly approves otherwise.

### 10.2 CI Workflow Behavior

`ci.yml` must validate the project and must not deploy.

The CI workflow should run:

- Python dependency installation
- Data validation
- Frontend data generation
- Python tests
- `npm ci`
- Frontend linting
- TypeScript checking
- Frontend tests
- Frontend static build

The agent must not remove these checks to make CI pass.

If a check is temporarily unavailable because the command does not exist yet, the agent must either add the command or document the limitation clearly.

### 10.3 Deployment Workflow Behavior

`deploy-pages.yml` should deploy only from `main` or from manual dispatch.

Pull requests must not deploy to the production GitHub Pages site.

Deployment must happen only after validation, tests, and build pass.

The deployment workflow must upload only the static frontend build output, normally:

```text
frontend/dist
```

The deployment artifact must not be the full repository.

### 10.4 Official GitHub Pages Actions

The agent should use the official GitHub Pages Actions:

- `actions/configure-pages`
- `actions/upload-pages-artifact`
- `actions/deploy-pages`

Third-party deployment Actions require explicit human approval.

### 10.5 Minimal Permissions

The deployment workflow must use minimal permissions:

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

The agent must not broaden workflow permissions unless there is a clear documented reason.

### 10.6 Vite Base Path

The agent must configure Vite so the app works under a GitHub Pages project path.

For a project site, the base path is normally:

```text
/<repository-name>/
```

The agent must not assume root deployment unless a custom domain or user site is explicitly configured.

### 10.7 Static Data in Deployment

The agent must ensure `tournament.json` or the equivalent generated frontend data file is present before `npm run build`.

The deployed app must not rely on local-only files that are missing from the GitHub Pages artifact.

### 10.8 No Secrets

The agent must not add secrets to frontend code.

The agent must not require private API keys for GitHub Pages deployment.

The default GitHub Actions token should be sufficient for deployment.

### 10.9 No Runtime Backend by Workflow

The agent must not use CI/CD to hide a backend dependency.

A workflow may generate static files, but the deployed app must still be a static site.

### 10.10 Deployment Failure Reporting

If a deployment-related task cannot be completed, the agent must report:

- Which workflow or command failed
- Whether the failure is in Python validation, frontend validation, build, artifact upload, or Pages deployment
- What was changed
- What remains unresolved


---

## 11. Data Handling Rules

The agent must treat data as part of the product contract.

### 10.1 Rating Data

The MVP uses a local rating snapshot.

The preferred current Elo source is World Football Elo / `eloratings.net`, with an accessible fallback or cross-check source such as Football Elo Ratings when appropriate.

The rating snapshot must distinguish:

- `pre_tournament`
- `pre_knockout`
- other explicitly named snapshot types, if needed

The frontend must not fetch current ratings directly.

### 10.2 Historical Results Data

The preferred historical international results source is Mart Jürisoo's `international_results` dataset, especially:

- `results.csv`
- `shootouts.csv`

The historically informed model should use historical results and reconstructed historical Elo features.

The agent must not assume direct head-to-head history is sufficient for calibration.

### 10.3 Missing Data

The agent must fail clearly when required data is missing.

The agent must not silently insert placeholder values into production data.

Allowed test placeholders must be located only in test/demo fixtures and clearly labeled.

---

## 12. Identifier Rules

Stable IDs are mandatory.

### 11.1 Team IDs

The agent must use stable `team_id` values for logic.

Allowed example:

```text
arg
fra
bra
esp
```

Forbidden for logic:

```text
Argentina
France
Brazil
Spain
```

Display names are for UI only.

### 11.2 Match IDs

The agent must use stable `match_id` values.

Recommended format:

```text
R32-01
R32-02
R16-01
QF-01
SF-01
F-01
```

The agent must not generate random match IDs.

The agent must not change stable IDs after they appear in data, tests, or documentation without explicit approval.

---

## 13. Model Implementation Rules

### 12.1 MVP Model

The MVP model is the simple Elo/rating-difference model.

It must:

- Use team ratings.
- Convert rating difference into advancement probability.
- Return probabilities between 0 and 1.
- Return probabilities that sum to 1.
- Be deterministic for a given input.
- Be covered by tests.

### 12.2 Historically Informed Model

The historically informed model is a later version.

When implemented, it must:

- Use historical rating-difference calibration.
- Be selectable by a frontend toggle.
- Recalculate match probabilities, bracket predictions, and champion probabilities when selected.
- Preserve the same bracket and override behavior.
- Be covered by tests.

### 12.3 Model Toggle

When both models exist, the frontend must provide a toggle between:

- Simple Elo
- Historically informed Elo

Changing the toggle must not reset user overrides unless explicitly designed and documented.

The selected model must be clearly shown in the UI.

The app must not mix model outputs without labeling them.

---

## 14. Bracket Logic Rules

Bracket logic must live in testable domain functions, not only in React visual components.

The agent should separate:

- Data loading
- Data validation
- Probability calculation
- Bracket resolution
- Override application
- Champion probability calculation
- UI rendering

The agent must ensure:

- First-round teams are fixed.
- Later-round teams are derived from previous winners.
- Manual overrides update downstream matches.
- Invalid downstream overrides are cleared or ignored.
- Official locked results, when implemented, override user overrides.
- The final resolves to a champion.

---

## 15. Champion Probability Rules

The deployed app should use exact probability propagation where practical.

Monte Carlo simulation may be used in Python for validation, but it is not required for the deployed MVP.

The agent must ensure:

- Champion probabilities sum to 1 within tolerance.
- Eliminated teams have zero champion probability under forced or locked paths.
- Scenario changes update champion probabilities.
- The top four champion list is derived from the full probability table.

The top four list must not be manually stored as source data.

---

## 16. Official Result Locking Rules

Official result locking is a future feature.

The agent must not implement a live admin dashboard for the MVP.

When official locking is implemented, it should work through static data updates and redeployment.

Official locks must:

- Use stable `match_id` values.
- Use stable `team_id` values.
- Override model predictions.
- Override user overrides.
- Be visually distinct in the UI.
- Trigger recalculation of downstream probabilities.

---

## 17. Forecast History Rules

Forecast history is a future feature.

The agent must not implement it before the MVP unless explicitly instructed.

When implemented, forecast history should use static forecast snapshots.

A snapshot should record:

- Snapshot ID
- Timestamp
- Reason
- Locked matches
- Rating snapshot
- Model version
- Champion probabilities
- Top four champion probabilities

The agent must not require a database for forecast history unless the architecture is explicitly revised.

---

## 18. Testing Behavior

The agent must create or update tests when changing logic.

### 17.1 Required Test Areas

Tests must cover:

- Data validation
- Probability calculation
- Equal-rating behavior
- Higher-rating behavior
- Probability sum tolerance
- Bracket propagation
- Manual overrides
- Invalid downstream overrides
- Champion probability calculation
- Model toggle behavior, once historical model exists
- Missing data failures

### 17.2 Test Before Refactor

Before refactoring core logic, the agent should ensure tests exist for the behavior being preserved.

### 17.3 Do Not Weaken Tests

The agent must not delete, skip, or weaken tests to make a build pass unless explicitly instructed and documented.

If a test is wrong, the agent must explain why and replace it with a better test.

---

## 19. Frontend Behavior Rules

The frontend must:

- Use React + TypeScript.
- Keep domain logic outside visual components where practical.
- Display the full bracket.
- Display team names and flags.
- Display match probabilities.
- Display selected winners.
- Visually mark user overrides.
- Visually mark official locks when implemented.
- Show top four champion probabilities.
- Show which model is active.
- Remain usable on desktop and mobile.
- Avoid unnecessary clutter.

The frontend must not:

- Fetch live ratings.
- Depend on backend computation.
- Contain secret keys.
- Hide model uncertainty.
- Present forecasts as certainties.

---

## 20. Accessibility Rules

The agent should preserve accessibility as a core requirement.

Interactive controls must be keyboard usable.

Important visual states must not rely only on color.

Buttons and toggles must have accessible labels.

Text contrast should be sufficient.

The page should use meaningful headings and semantic structure.

---

## 21. Dependency Rules

The agent may add small, well-maintained dependencies when useful.

The agent should avoid:

- Large UI frameworks in the MVP
- Heavy charting libraries unless clearly needed
- Dependencies with unclear maintenance status
- Dependencies that require a backend
- Dependencies that require private runtime keys

If a dependency is added, the agent should document why it is needed.

---

## 22. Documentation Rules

When implementation changes affect behavior, the agent must update documentation.

Examples:

- If the data contract changes, update `data_model.md`.
- If architecture changes, update `architecture_decisions.md`.
- If requirements change, update `requirements.md`.
- If agent workflow changes, update `agents.md`.
- If setup changes, update `README.md`.

Documentation must not claim features exist before they are implemented unless clearly marked as future work.

---

## 23. Error Handling Rules

The agent must prefer clear failure over silent wrong behavior.

The app or scripts must fail clearly for:

- Missing rating data
- Missing bracket data
- Duplicate team IDs
- Duplicate match IDs
- Invalid match references
- Missing team ratings
- Invalid official locks, once implemented
- Invalid frontend data

The frontend should show user-friendly errors when static data cannot be loaded.

---

## 24. Completion Criteria for Agent Tasks

A task is complete only when:

1. The requested behavior is implemented.
2. Relevant tests pass.
3. New logic has test coverage where practical.
4. The app still respects the static-site architecture.
5. The data model remains valid.
6. Documentation is updated if behavior changed.
7. No unrelated scope expansion was introduced.
8. No production placeholder data was silently added.

The agent must summarize:

- What changed
- What tests were run
- What was not changed
- Any known limitations

---

## 25. Default Response Style for Coding Agent

When reporting back, the coding agent should be concise and concrete.

Recommended format:

```text
Implemented:
- ...

Tests:
- ...

Notes:
- ...
```

The agent should not provide long theoretical explanations unless requested.

The agent should not claim success if tests were not run.

If tests could not be run, the agent must say why.

---

## 26. MVP Guardrail

The agent must keep the MVP focused.

The MVP is not a full football analytics platform.

The MVP is:

> A static React + TypeScript knockout bracket forecast website using local rating data, browser-side bracket recalculation, manual overrides, and champion probability calculation.

All other features are future work unless explicitly requested.
