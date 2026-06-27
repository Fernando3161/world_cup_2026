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

The current repository data includes placeholder/test source data for validating the MVP data contract. These are not real teams, ratings, or Elo values.

Required MVP source files:

- `data/manual/bracket.json`
- `data/manual/teams.csv`
- `data/snapshots/ratings.csv`
- `data/manual/source_catalog.json`

Generated frontend data target:

- `frontend/public/data/tournament.json`

Validate source data:

```powershell
python scripts/validate_data.py
```

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
python scripts/generate_frontend_data.py
```

The generator also writes `data/frontend/tournament.json` as a build artifact copy. Source data remains authoritative; generated JSON should be reproducible from the committed source files and scripts.

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
