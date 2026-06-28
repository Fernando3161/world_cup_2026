# World Cup 2026 Knockout Forecast

Static React + TypeScript forecast site for the World Cup 2026 knockout stage.

The MVP target is a GitHub Pages-compatible static site generated from local data snapshots. Python is used only for setup-time, build-time, data preparation, and validation tasks. The deployed app must not require a backend, database, live scraping, authentication, or runtime secrets.

## Project Structure

- `frontend/` - React, TypeScript, Vite, and custom CSS.
- `scripts/` - Python data preparation and validation entry points.
- `data/` - Local raw, manual, snapshot, processed, and generated data folders.
- `tests/` - Python and frontend test folders.
- `docs/` - Architecture, data model, requirements, visual design, and agent instructions.

## Setup

Use Python 3.11 or newer and Node.js 20 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

```powershell
cd frontend
npm install
```

## Data Preparation

The current repository data uses local build-time snapshots:

- Wikipedia knockout-stage HTML for the 2026 Round of 32 bracket.
- FootballRatings.org HTML for the current Elo-style rating table dated 2026-06-28.
- Mart Jurisoo's `international_results` CSV files for historical international match results and shootouts.

The frontend never fetches these sources at runtime. Refreshes should be done locally, reviewed, validated, and committed as static source files.

Required MVP source files:

- `data/manual/bracket.json`
- `data/manual/teams.csv`
- `data/manual/team_aliases.csv`
- `data/snapshots/ratings.csv`
- `data/manual/source_catalog.json`
- `frontend/public/flags/*.svg`
- `data/raw/wikipedia/2026_fifa_world_cup_knockout_stage.html`
- `data/raw/footballratings/footballratings_snapshot.html`
- `data/raw/international_results/results.csv`
- `data/raw/international_results/shootouts.csv`
- `data/raw/international_results/source_metadata.json`

Generated frontend data target:

- `frontend/public/data/tournament.json`

Validate source data:

```powershell
python scripts/validate_data.py
```

Refresh the bracket and rating source files from the committed raw HTML snapshots:

```powershell
python scripts/prepare_bracket.py
```

That script parses the local snapshots, writes `data/manual/teams.csv`, `data/manual/bracket.json`, `data/manual/team_aliases.csv`, and `data/snapshots/ratings.csv`, validates the result, and regenerates `frontend/public/data/tournament.json`.

To refresh the raw HTML snapshots first, run the same script with explicit setup-time fetching:

```powershell
python scripts/prepare_bracket.py --fetch-snapshots
```

Review the changed raw snapshots and normalized data before committing. Do not run live source fetching from the frontend or as a hidden runtime dependency.

Import a build-time current Elo snapshot from a manually prepared CSV:

```powershell
python scripts/fetch_current_elo.py import-csv `
  --input path\to\manual_ratings.csv `
  --rating-source "World Football Elo Ratings" `
  --source-id world_football_elo `
  --snapshot-kind pre_knockout `
  --rating-date 2026-07-01 `
  --source-url https://www.eloratings.net/
```

The manual CSV must contain at least `team_id` and `rating`. The script writes the normalized local snapshot to `data/snapshots/ratings.csv`, preserves rating source metadata, and validates that every bracket team has exactly one usable rating. If a source exposes a direct CSV URL, the build-time fetch path is:

```powershell
python scripts/fetch_current_elo.py fetch-csv `
  --url https://example.com/current-ratings.csv `
  --rating-source "World Football Elo Ratings" `
  --source-id world_football_elo `
  --snapshot-kind pre_knockout `
  --rating-date 2026-07-01
```

If the live source is unavailable or is not a CSV endpoint, use `import-csv` with a reviewed manual file. The frontend never fetches Elo data at runtime.

Generate frontend data:

```powershell
python scripts/fetch_historical_results.py validate-local
python scripts/prepare_historical_results.py
python scripts/build_historical_elo.py
python scripts/calibrate_historical_model.py
python scripts/validate_model.py
python scripts/generate_frontend_data.py
```

The generator also writes `data/frontend/tournament.json` as a build artifact copy. Source data remains authoritative; generated JSON should be reproducible from the committed source files and scripts.

To refresh the historical result snapshot manually:

```powershell
python scripts/fetch_historical_results.py fetch
```

Review and commit the resulting raw files and `source_metadata.json`. CI and deployment use `validate-local`; they do not fetch historical data from the network.

Historical model artifacts:

- `data/processed/historical_results_normalized.csv`
- `data/processed/historical_results_excluded.csv`
- `data/processed/historical_elo_timeseries.csv`
- `data/processed/historical_match_features.csv`
- `data/processed/calibrated_model.json`
- `data/processed/model_validation_report.json`

The historically informed Elo model reconstructs pre-match Elo features locally with initial rating `1500`, constant `K = 20`, no home-field adjustment, and no importance weighting. It fits a one-parameter logistic calibration to historical expected-score targets. Draws without shootouts are target `0.5`; shootout winners are target `1`. The frontend receives only compact calibration parameters, not raw historical match rows.

Limitations: the historical model does not include squads, injuries, tactics, venue effects, rest days, travel, weather, live odds, or betting-market information. It is a transparent historical calibration layer, not an official FIFA model, official historical Elo table, or betting advice.

Flag assets for the current MVP teams are local SVG files in `frontend/public/flags`. They are copied from the MIT-licensed [`flag-icons`](https://github.com/lipis/flag-icons) project and served statically by the frontend. The runtime app does not fetch remote flag images.

## Frontend Development

```powershell
cd frontend
npm run dev
npm run lint
npm run typecheck
npm run build
```

The Vite base path defaults to `/` for local development. For GitHub Pages project-site builds, set `VITE_BASE_PATH` explicitly, for example:

```powershell
$env:VITE_BASE_PATH="/world_cup_2026/"
npm run build
```

## Tests

Python:

```powershell
python -m pytest
```

Frontend:

```powershell
cd frontend
npm run lint
npm run typecheck
npm test
```

The frontend test suite covers the current domain logic for probability, bracket propagation, overrides, and champion probabilities.
It also covers the Simple Elo / Historically informed Elo model toggle and selected-model champion probability recalculation.

## GitHub Pages Deployment

The deployment target is GitHub Pages using static files from `frontend/dist`.

GitHub Actions workflows are defined in:

- `.github/workflows/ci.yml`
- `.github/workflows/deploy-pages.yml`

CI runs on pushes, pull requests, and manual dispatch. It validates source data, regenerates `frontend/public/data/tournament.json`, runs Python tests, installs frontend dependencies with `npm ci`, runs frontend lint/typecheck/tests, and builds the static site.

Production deployment runs only on pushes to `main` or manual dispatch. It repeats the validation and build steps, uploads only `frontend/dist` as the Pages artifact, and deploys with the official GitHub Pages Actions.

In the repository settings, configure GitHub Pages to use **GitHub Actions** as the source. For a project site, the deployed URL will be:

```text
https://<owner>.github.io/<repository-name>/
```

The deploy workflow sets `VITE_BASE_PATH` to `/<repository-name>/`, which matches GitHub Pages project-site deployment. For local builds the Vite base path defaults to `/`. For a custom domain or user site, update the workflow environment value to `/`.

The public build includes `.nojekyll` from `frontend/public/.nojekyll` and static data from `frontend/public/data/tournament.json`. No runtime backend, database, live data fetch, raw historical dataset deployment, or secret runtime configuration is introduced.
