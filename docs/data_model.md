# data_model.md

# World Cup Knockout Forecast Website — Data Model

## 1. Purpose

This document defines the data model for the World Cup knockout forecast website.

The goal is to make the bracket, team data, rating data, historical result data, user overrides, official locked results, model selection, and forecast history explicit and testable.

The data model must support:

- A static 32-team knockout bracket
- Team names and flags
- Local current Elo rating snapshots
- Historical match result snapshots
- Locally reconstructed historical Elo data
- Simple Elo probability model
- Future historically informed Elo probability model
- Browser-side probability calculation
- Baseline forecast
- Current scenario forecast with user overrides
- Future official result locking
- Future forecast history
- Future shareable scenario URLs

The MVP must avoid data structures that require a runtime backend or database.

---

## 2. Core Data Principles

The project must follow these principles:

1. **Stable IDs are mandatory.**  
   Teams, matches, rounds, models, and snapshots must use stable IDs. Do not rely on display names as identifiers.

2. **Display names are not IDs.**  
   Team names may change, contain accents, or vary between sources. Logic must use stable IDs.

3. **Runtime data must be static.**  
   The public website consumes generated JSON files. It must not depend on live data fetching during user interaction.

4. **Raw data and frontend data are separate.**  
   CSV files are acceptable for input and snapshots. The React frontend should consume validated JSON generated from those files.

5. **User overrides are local state.**  
   In the MVP, manual user selections exist only in the browser. They do not modify source files.

6. **Official locked results are source data.**  
   In a future version, official match results are stored in a static results file and redeployed with the site.

7. **Derived values should be recalculable.**  
   Probabilities, winners, and champion chances should be computed from source data rather than manually duplicated.

8. **Model selection is explicit.**  
   The selected model must be represented by a stable model ID, not by UI text.

---

## 3. Main Data Layers

The project has four data layers.

```text
Raw data
  ↓
Validated project data
  ↓
Generated frontend data
  ↓
Browser runtime state
```

### 3.1 Raw Data

Raw data includes manually prepared or downloaded files.

Examples:

- Current Elo rating CSV
- Initial bracket CSV or JSON
- Team metadata file
- Historical match results
- Historical penalty shootout results
- Optional official results file

### 3.2 Validated Project Data

Python scripts validate the raw data and convert it into consistent internal structures.

Validation should check:

- Required columns exist
- Team IDs are unique
- Match IDs are unique
- Ratings exist for all teams
- Bracket references are valid
- No impossible match references exist
- Historical match team names can be mapped
- Historical result rows have valid scores
- Official result locks refer to valid matches and teams

### 3.3 Generated Frontend Data

Python scripts generate static JSON consumed by React.

This JSON should be placed in a frontend-accessible location, for example:

```text
frontend/public/data/tournament.json
```

### 3.4 Browser Runtime State

The React app loads the static JSON and creates runtime state for:

- Selected forecast mode
- Selected probability model
- User overrides
- Locally persisted user selections, if implemented
- Derived bracket state
- Derived probabilities
- Derived champion probabilities

Browser runtime state must not be treated as authoritative source data.

---

## 4. Source Catalog Model

The project should keep explicit metadata about external data sources.

Recommended source catalog file:

```text
data/manual/source_catalog.json
```

Each source entry should include:

| Field | Type | Required | Description |
|---|---:|---:|---|
| `source_id` | string | yes | Stable source ID |
| `display_name` | string | yes | Human-readable name |
| `source_type` | string | yes | `current_elo`, `historical_results`, `mirror`, `flags`, etc. |
| `url` | string | yes | Source URL |
| `license_note` | string | optional | License or usage note |
| `retrieval_method` | string | optional | Manual download, Python fetch, scraper, API, etc. |
| `notes` | string | optional | Project-specific notes |

Recommended source IDs:

```text
world_football_elo
footballratings_mirror
martj42_international_results
martj42_kaggle_mirror
openfootball_internationals_mirror
```

---

## 5. Team Model

A team represents one national team in the knockout bracket.

### 5.1 Required Fields

Each team must have:

| Field | Type | Required | Description |
|---|---:|---:|---|
| `team_id` | string | yes | Internal stable identifier |
| `display_name` | string | yes | Name shown in the UI |
| `short_name` | string | yes | Shorter name for compact bracket display |
| `rating` | number | yes | Rating used by the probability model |
| `rating_source` | string | yes | Source of the rating |
| `flag_mode` | string | yes | How the flag is represented |
| `flag_value` | string | yes | Emoji, asset path, or other flag reference |

### 5.2 Recommended Optional Fields

| Field | Type | Description |
|---|---:|---|
| `fifa_code` | string | FIFA-style three-letter code, if available |
| `iso_alpha2` | string | ISO alpha-2 country code, if available |
| `iso_alpha3` | string | ISO alpha-3 country code, if available |
| `confederation` | string | UEFA, CONMEBOL, CAF, AFC, CONCACAF, OFC |
| `seed` | number | Optional tournament seed |
| `group` | string | Original group-stage group, if useful |
| `notes` | string | Human-readable notes |

### 5.3 Team ID Rule

`team_id` must be stable and must not depend on display formatting.

Recommended format:

```text
arg
fra
bra
esp
eng
ger
```

For most teams, use a lowercase three-letter football code.

Do not use full names such as:

```text
Argentina
France
Brazil
```

as internal IDs.

### 5.4 Team Alias Model

Historical result datasets may use different names for the same team.

The project should maintain:

```text
data/manual/team_aliases.csv
```

Recommended columns:

| Column | Required | Description |
|---|---:|---|
| `source_name` | yes | Team name as it appears in a source |
| `team_id` | yes | Project stable team ID |
| `source_id` | optional | Source where this alias appears |
| `valid_from` | optional | Start date for alias validity |
| `valid_to` | optional | End date for alias validity |
| `notes` | optional | Explanation |

This file is important for historical results and historical Elo reconstruction.

### 5.5 Flag Representation

The MVP may use emoji flags.

Example:

```text
flag_mode = "emoji"
flag_value = "🇦🇷"
```

Later versions may use local static assets.

Example:

```text
flag_mode = "asset"
flag_value = "/flags/arg.svg"
```

The frontend must not assume that all teams can be represented only by ISO country flags. Some football associations may not map cleanly to independent ISO countries.

---

## 6. Current Rating Snapshot Model

A rating snapshot records the rating values used for a particular forecast build.

Ratings should be stored locally before generating frontend data.

### 6.1 Current Rating CSV

Recommended file:

```text
data/snapshots/ratings.csv
```

Recommended columns:

| Column | Required | Description |
|---|---:|---|
| `team_id` | yes | Stable team ID |
| `display_name` | yes | Team name at rating source |
| `rating` | yes | Numeric Elo/rating value |
| `rating_source` | yes | Source name |
| `source_id` | yes | Stable source ID from source catalog |
| `rating_snapshot_kind` | yes | `pre_tournament`, `pre_knockout`, `manual`, etc. |
| `rating_date` | yes | Date the rating was published or intended to represent |
| `retrieved_at` | yes | Date/time this project retrieved or created the snapshot |
| `source_url` | optional | URL or identifier for source |
| `fifa_code` | optional | FIFA code |
| `iso_alpha2` | optional | ISO alpha-2 code |
| `iso_alpha3` | optional | ISO alpha-3 code |
| `notes` | optional | Human-readable notes |

### 6.2 Rating Snapshot Kinds

Recommended values:

| Value | Meaning |
|---|---|
| `pre_tournament` | Frozen before the World Cup starts |
| `pre_knockout` | Frozen after the knockout bracket is known |
| `manual` | Manually prepared rating snapshot |
| `test_fixture` | Artificial data for tests |

For a pre-WC2026 forecast, use `pre_tournament`.

For a post-group-stage knockout forecast, use `pre_knockout`.

The frontend must display enough metadata for users to know which kind of forecast they are seeing.

### 6.3 Rating Rules

- Every bracket team must have exactly one rating.
- Ratings must be numeric.
- Missing ratings must fail validation.
- Duplicate ratings for the same `team_id` must fail validation unless explicitly resolved before frontend generation.
- The rating date must be preserved for transparency.
- The source must be preserved for transparency.

---

## 7. Historical Result Snapshot Model

The historically informed model requires a local historical result snapshot.

Recommended raw files:

```text
data/raw/results/results.csv
data/raw/results/shootouts.csv
data/raw/results/former_names.csv
```

Recommended normalized output:

```text
data/processed/historical_results_normalized.csv
```

### 7.1 Historical Results Fields

Recommended normalized columns:

| Column | Required | Description |
|---|---:|---|
| `match_date` | yes | Match date |
| `home_team_id` | yes | Project team ID for home team |
| `away_team_id` | yes | Project team ID for away team |
| `home_team_source_name` | yes | Original source home team name |
| `away_team_source_name` | yes | Original source away team name |
| `home_score` | yes | Full-time score including extra time, if source defines it that way |
| `away_score` | yes | Full-time score including extra time, if source defines it that way |
| `tournament` | yes | Tournament or match category |
| `city` | optional | Match city |
| `country` | optional | Host country |
| `neutral` | yes | Whether source marks match as neutral |
| `shootout_winner_team_id` | optional | Winner of shootout, if match decided by penalties |
| `source_id` | yes | Historical source ID |
| `source_row_hash` | optional | Hash for traceability |

### 7.2 Historical Results Rules

- Every historical team name must map to a `team_id` or be explicitly excluded.
- Rows with unmapped teams must be reported.
- Match dates must be valid.
- Scores must be numeric.
- Historical data cleaning must be reproducible.
- Exclusions must be documented.

---

## 8. Historical Elo Reconstruction Model

The historically informed model should use locally reconstructed Elo features.

Recommended output:

```text
data/processed/historical_elo_timeseries.csv
```

Recommended columns:

| Column | Required | Description |
|---|---:|---|
| `match_date` | yes | Match date |
| `match_index` | yes | Chronological index |
| `team_id` | yes | Team ID |
| `pre_match_elo` | yes | Team Elo before match |
| `post_match_elo` | yes | Team Elo after match |
| `opponent_team_id` | yes | Opponent team ID |
| `tournament` | yes | Tournament name/category |
| `neutral` | yes | Neutral venue flag |
| `elo_formula_version` | yes | Formula version used |
| `source_id` | yes | Historical result source |

### 8.1 Historical Match Features

Recommended output:

```text
data/processed/historical_match_features.csv
```

Recommended columns:

| Column | Required | Description |
|---|---:|---|
| `match_date` | yes | Match date |
| `home_team_id` | yes | Home team ID |
| `away_team_id` | yes | Away team ID |
| `home_pre_elo` | yes | Home team Elo before match |
| `away_pre_elo` | yes | Away team Elo before match |
| `elo_diff_home_minus_away` | yes | Home pre-match Elo minus away pre-match Elo |
| `abs_elo_diff` | yes | Absolute rating difference |
| `higher_rated_team_id` | yes | Team with higher pre-match Elo |
| `winner_team_id` | optional | Winner after match if any |
| `advancing_team_id` | optional | Winner including shootout if applicable |
| `higher_rated_team_won` | yes | Boolean or 0/1 target |
| `match_outcome` | yes | `home_win`, `away_win`, `draw`, `shootout_home`, `shootout_away` |
| `tournament` | yes | Tournament |
| `neutral` | yes | Neutral venue flag |
| `source_id` | yes | Data source |

This table is the main training data for the historically informed Elo calibration.

---

## 9. Model Metadata

The frontend data must include explicit model metadata.

Recommended model IDs:

| Model ID | Meaning | MVP? |
|---|---|---:|
| `simple_elo` | Direct Elo/rating-difference probability model | yes |
| `historical_elo` | Rating-difference model calibrated on historical results | future |

Recommended top-level model structure:

```json
{
  "default_model_id": "simple_elo",
  "available_models": [
    {
      "model_id": "simple_elo",
      "display_name": "Simple Elo",
      "model_version": "1.0.0",
      "probability_method": "rating_difference_logistic",
      "is_available": true
    },
    {
      "model_id": "historical_elo",
      "display_name": "Historically informed Elo",
      "model_version": "0.1.0",
      "probability_method": "historical_rating_difference_calibration",
      "is_available": false
    }
  ]
}
```

The frontend should only show a model as selectable when `is_available = true`.

---

## 10. Round Model

Rounds must use stable IDs.

Recommended round IDs:

| Round ID | Display Name | Number of Matches |
|---|---|---:|
| `R32` | Round of 32 | 16 |
| `R16` | Round of 16 | 8 |
| `QF` | Quarter-final | 4 |
| `SF` | Semi-final | 2 |
| `F` | Final | 1 |

The MVP does not include the third-place match.

Rounds must be ordered explicitly.

Recommended order:

```text
R32 → R16 → QF → SF → F
```

Do not infer round order alphabetically.

---

## 11. Match Model

A match represents one bracket fixture.

Each match must have:

| Field | Type | Required | Description |
|---|---:|---:|---|
| `match_id` | string | yes | Stable match identifier |
| `round_id` | string | yes | Round ID |
| `slot_a` | Slot | yes | First team slot |
| `slot_b` | Slot | yes | Second team slot |
| `feeds_to_match_id` | string or null | yes | Next match receiving the winner |
| `feeds_to_slot` | string or null | yes | Whether the winner feeds into slot A or B |
| `display_order` | number | yes | Order in bracket display |

### 11.1 Match ID Rule

Match IDs must be stable.

Recommended IDs:

```text
R32-01
R32-02
...
R32-16
R16-01
...
R16-08
QF-01
...
QF-04
SF-01
SF-02
F-01
```

Do not generate random match IDs.

Do not change match IDs after user-facing deployment, because match IDs are needed for:

- User overrides
- Official result locks
- Forecast snapshots
- Future shareable scenario URLs
- Automated tests

---

## 12. Slot Model

A slot defines where a team in a match comes from.

A slot can be one of three types:

1. Fixed team
2. Winner of previous match
3. Empty or unresolved placeholder

### 12.1 Slot Fields

| Field | Type | Required | Description |
|---|---:|---:|---|
| `slot_type` | string | yes | `team`, `winner_of`, or `empty` |
| `team_id` | string or null | conditional | Required when `slot_type = team` |
| `source_match_id` | string or null | conditional | Required when `slot_type = winner_of` |
| `label` | string or null | optional | Human-readable placeholder |

---

## 13. Selection Source Model

Every resolved match winner should have a selection source.

Recommended selection sources:

| Value | Meaning |
|---|---|
| `model` | Winner selected by the probability model |
| `user_override` | Winner manually selected by the user |
| `official_lock` | Winner is an official real-world completed result |
| `unresolved` | Winner cannot yet be resolved |

### 13.1 Selection Priority

When determining a match winner, use this priority:

```text
official_lock > user_override > model > unresolved
```

User overrides must not be allowed to override official locked results.

---

## 14. User Override Model

In the MVP, user overrides exist only in browser state.

A user override records:

| Field | Type | Required | Description |
|---|---:|---:|---|
| `match_id` | string | yes | Match being overridden |
| `winner_team_id` | string | yes | User-selected winner |
| `created_at` | string | optional | Browser timestamp |
| `updated_at` | string | optional | Browser timestamp |

### 14.1 Override Rules

- The selected winner must be one of the two teams currently assigned to the match.
- If upstream overrides change the teams in a downstream match, invalid downstream overrides must be cleared or ignored.
- User overrides must not alter ratings.
- User overrides must not alter official locked results.
- User overrides must be visually marked in the UI.

### 14.2 Local Persistence

If local browser persistence is implemented, the stored override data should contain only stable IDs.

Recommended local storage shape:

```json
{
  "schema_version": "1",
  "selected_model_id": "simple_elo",
  "overrides": [
    {
      "match_id": "R32-01",
      "winner_team_id": "arg"
    }
  ]
}
```

The app must be able to reset all user overrides.

---

## 15. Official Result Lock Model

Official result locking is a future feature.

Official locked results are controlled by the project administrator through a static data file.

Recommended file:

```text
data/snapshots/official_results.json
```

An official result should contain:

| Field | Type | Required | Description |
|---|---:|---:|---|
| `match_id` | string | yes | Completed match |
| `winner_team_id` | string | yes | Official advancing team |
| `team_a_score` | number or null | optional | Score for team A |
| `team_b_score` | number or null | optional | Score for team B |
| `decided_by` | string | optional | `regular_time`, `extra_time`, `penalties`, or `unknown` |
| `played_at` | string | optional | Match date/time |
| `locked_at` | string | yes | Date/time result was locked in this project |
| `source` | string | optional | Source of official result |
| `notes` | string | optional | Human-readable notes |

---

## 16. Forecast Mode Model

The app supports two forecast modes.

### 16.1 Baseline Forecast

The baseline forecast uses:

- Initial bracket
- Team ratings
- Selected probability model
- Official locked results, if present in future versions
- No user overrides

### 16.2 Current Scenario Forecast

The current scenario forecast uses:

- Initial bracket
- Team ratings
- Selected probability model
- Official locked results, if present
- User overrides from browser state

---

## 17. Match Runtime State

The frontend should derive runtime match state from the static bracket data plus official locks, selected model, and user overrides.

A resolved runtime match should contain:

| Field | Type | Description |
|---|---:|---|
| `match_id` | string | Stable match ID |
| `round_id` | string | Round ID |
| `team_a_id` | string or null | Resolved team in slot A |
| `team_b_id` | string or null | Resolved team in slot B |
| `selected_model_id` | string | Model used for probability |
| `probability_a` | number or null | Probability team A advances |
| `probability_b` | number or null | Probability team B advances |
| `winner_team_id` | string or null | Selected advancing team |
| `selection_source` | string | `model`, `user_override`, `official_lock`, or `unresolved` |
| `is_locked` | boolean | Whether result is official |
| `is_overridden` | boolean | Whether result comes from user override |

This state is derived and should not be manually edited in source files.

---

## 18. Champion Probability Model

Champion probabilities should be computed from the bracket structure and pairwise match probabilities.

The output should contain:

| Field | Type | Description |
|---|---:|---|
| `team_id` | string | Team ID |
| `champion_probability` | number | Probability of winning tournament |
| `final_probability` | number | Probability of reaching final |
| `semifinal_probability` | number | Probability of reaching semi-final |
| `quarterfinal_probability` | number | Probability of reaching quarter-final |
| `round_of_16_probability` | number | Probability of reaching Round of 16 |
| `selected_model_id` | string | Model used to calculate probabilities |

The sum of all champion probabilities over all active teams should be 1.0, subject to acceptable floating-point tolerance.

### 18.1 Top Champions Summary

The frontend should derive the top champion summary from the full champion probability table.

The top four list should not be stored manually.

---

## 19. Frontend Tournament Data File

The generated frontend data should be a single static JSON file for the MVP.

Recommended file:

```text
frontend/public/data/tournament.json
```

Recommended top-level structure:

```json
{
  "schema_version": "1",
  "tournament": { },
  "sources": [ ],
  "models": { },
  "teams": [ ],
  "rounds": [ ],
  "matches": [ ],
  "official_results": [ ]
}
```

### 19.1 Tournament Metadata

Tournament metadata should include:

| Field | Type | Description |
|---|---:|---|
| `tournament_id` | string | Example: `fifa-world-cup-2026` |
| `display_name` | string | Example: `FIFA World Cup 2026` |
| `stage` | string | Example: `knockout` |
| `starts_at_round` | string | Example: `R32` |
| `generated_at` | string | Build timestamp |
| `data_version` | string | Project data version |

### 19.2 Model Metadata

Model metadata should include:

| Field | Type | Description |
|---|---:|---|
| `default_model_id` | string | Default selected model |
| `available_models` | array | List of model metadata |
| `rating_source` | string | Rating source used |
| `rating_snapshot_date` | string | Date of rating snapshot |
| `rating_snapshot_kind` | string | Pre-tournament, pre-knockout, etc. |

The frontend should show model metadata somewhere in an “About this forecast” or “Method” section.

---

## 20. Forecast Snapshot Model — Future Version

Forecast snapshots are a future feature for tracing how probabilities change through the tournament.

Recommended file:

```text
data/snapshots/forecast_history.json
```

A forecast snapshot should contain:

| Field | Type | Required | Description |
|---|---:|---:|---|
| `snapshot_id` | string | yes | Stable snapshot ID |
| `created_at` | string | yes | Snapshot timestamp |
| `reason` | string | yes | Why snapshot was created |
| `locked_matches` | array | yes | Match IDs locked at this point |
| `model_id` | string | yes | Model used |
| `model_version` | string | yes | Model version |
| `rating_snapshot_date` | string | yes | Rating snapshot used |
| `champion_probabilities` | array | yes | Champion probabilities for all teams |
| `top_four` | array | yes | Top four champion probabilities |

Forecast snapshots are not part of the MVP.

---

## 21. Shareable Scenario Model — Future Version

Shareable scenario URLs are a future feature.

A shareable scenario should encode user overrides and selected model using stable IDs.

Conceptually:

```json
{
  "selected_model_id": "historical_elo",
  "overrides": [
    { "match_id": "R32-01", "winner_team_id": "arg" },
    { "match_id": "R32-02", "winner_team_id": "fra" }
  ]
}
```

The MVP does not need to implement shareable URLs, but the data model must not block them.

---

## 22. Data Validation Rules

The data preparation pipeline must validate the following before generating frontend data:

### 22.1 Team Validation

- Every `team_id` is unique.
- Every team has a display name.
- Every team has a numeric rating.
- Every team has a flag representation.
- Every team appearing in the bracket exists in the team list.

### 22.2 Rating Validation

- Every bracket team has exactly one rating.
- Ratings are numeric.
- Rating source is present.
- Source ID is present.
- Rating snapshot kind is present.
- Rating date is present.
- Missing ratings fail the build.

### 22.3 Historical Result Validation

- Every historical match has a valid date.
- Every historical match has mapped team IDs or is explicitly excluded.
- Every score is numeric.
- Shootout winners refer to one of the two teams in the match.
- Team aliases are sufficient to map the training dataset.
- Historical data source metadata is preserved.

### 22.4 Historical Elo Validation

- Historical Elo time series is chronological.
- Every match has pre-match Elo for both teams.
- Every match has post-match Elo for both teams.
- Elo formula version is recorded.
- Generated historical feature rows contain no missing rating differences.

### 22.5 Bracket Validation

- Every `match_id` is unique.
- Every `round_id` is valid.
- Every later-round `winner_of` reference points to an earlier match.
- Every `feeds_to_match_id` points to a valid later match or is null for the final.
- Every `feeds_to_slot` is either `A`, `B`, or null.
- Round-of-32 contains 16 matches.
- Round-of-16 contains 8 matches.
- Quarter-final contains 4 matches.
- Semi-final contains 2 matches.
- Final contains 1 match.

### 22.6 Model Validation

- Every available model has a stable `model_id`.
- `default_model_id` exists in `available_models`.
- Models marked `is_available = true` have all required parameters.
- Model output probabilities are between 0 and 1.
- Model output probabilities sum to 1 within tolerance.


---

## 23. CI/CD and Deployment Data Model

The data model must support GitHub Pages deployment through GitHub Actions.

The public site is built from committed source data plus generated frontend data. The deployment workflow must be able to regenerate the frontend data deterministically before building the React app.

### 23.1 Workflow Files

The repository should include the following workflow files:

```text
.github/workflows/ci.yml
.github/workflows/deploy-pages.yml
```

A future optional workflow may exist for manual data refresh:

```text
.github/workflows/refresh-data.yml
```

Workflow files are part of the project configuration and should be version-controlled.

### 23.2 Source Data Versus Generated Data

The authoritative source data is:

```text
data/manual/bracket.json
data/manual/teams.csv
data/snapshots/ratings.csv
```

Future authoritative source data may include:

```text
data/snapshots/official_results.json
data/snapshots/forecast_history.json
```

The generated frontend data is:

```text
frontend/public/data/tournament.json
```

or an equivalent generated path copied into the frontend public folder before build.

The generated frontend file is a build artifact. It must be reproducible from the source data and Python scripts.

### 23.3 Build Metadata

The generated frontend data should include build and source metadata so users and maintainers can understand what version of the forecast they are seeing.

Recommended metadata fields:

| Field | Type | Required | Description |
|---|---:|---:|---|
| `schema_version` | string | yes | Frontend data schema version |
| `generated_at` | string | yes | Timestamp of JSON generation |
| `git_commit` | string or null | optional | Git commit used for build |
| `data_version` | string | yes | Project data version |
| `rating_snapshot_date` | string | yes | Date of current Elo snapshot |
| `rating_snapshot_kind` | string | yes | `pre_tournament`, `pre_knockout`, or another explicit kind |
| `model_versions` | object | yes | Versions of available probability models |
| `deployment_target` | string | optional | Example: `github_pages` |

### 23.4 Data Validation in CI

CI must validate source data before generating frontend data.

The CI data validation step should fail if:

- Required source data files are missing
- Rating data is missing for any bracket team
- Team IDs are duplicated
- Match IDs are duplicated
- Bracket references are invalid
- Model metadata is missing
- The generated frontend data cannot be parsed
- The generated frontend data violates the expected schema

### 23.5 Generated Data Freshness Check

If `frontend/public/data/tournament.json` is committed to the repository, CI should regenerate it and fail if the committed file is stale.

If the repository chooses not to commit generated frontend JSON, CI must generate it before frontend tests and before deployment.

The project should choose one policy and document it in the README.

Recommended policy:

- Commit source data snapshots.
- Generate frontend JSON in CI and during local setup.
- Do not treat generated JSON as authoritative source data.

### 23.6 Deployment Artifact Contents

The GitHub Pages artifact should include only static frontend build output.

It should include:

- Compiled HTML
- Compiled JavaScript
- Compiled CSS
- Static frontend data JSON
- Static flag assets, if used
- `.nojekyll`, if needed

It should not include:

- Raw historical result databases
- Python scripts
- Test files
- Development dependencies
- Private or temporary files
- Large data files not needed by the browser

### 23.7 Official Result Updates and Redeployment

In the future official-locking workflow, real results should be committed as static source data.

Recommended workflow:

```text
Update data/snapshots/official_results.json
↓
Run validation
↓
Regenerate frontend data
↓
Run tests
↓
Build React frontend
↓
Deploy to GitHub Pages
```

This preserves the no-backend architecture while allowing the public forecast to update as the tournament progresses.


---

## 24. MVP Required Data Files

The MVP should require the following source files:

```text
data/snapshots/ratings.csv
data/manual/bracket.json
data/manual/teams.csv
```

The MVP should generate:

```text
frontend/public/data/tournament.json
```

Optional later files:

```text
data/raw/results/results.csv
data/raw/results/shootouts.csv
data/raw/results/former_names.csv
data/processed/historical_results_normalized.csv
data/processed/historical_elo_timeseries.csv
data/processed/historical_match_features.csv
data/processed/calibrated_model.json
data/snapshots/official_results.json
data/snapshots/forecast_history.json
data/assets/flags/
```

---

## 25. Minimal MVP Data Contract

The minimum viable frontend data must contain:

- Tournament metadata
- Source metadata
- Model metadata
- 32 teams
- 31 knockout matches
- Round definitions
- Team ratings
- Flag representation
- Match slot definitions

The frontend must be able to calculate:

- Match probabilities
- Predicted winners
- User override effects
- Downstream bracket changes
- Champion probabilities
- Top four champion candidates

from this static data alone.


---

## 25.1 Visual Design Data Boundary

The Financial Times-inspired editorial style is a frontend presentation concern, not a forecasting data concern.

The core tournament data must not be polluted with one-off visual styling fields.

The frontend may maintain separate design tokens in CSS files, for example:

```text
frontend/src/styles/tokens.css
frontend/src/styles/global.css
frontend/src/styles/typography.css
frontend/src/styles/layout.css
frontend/src/styles/components.css
```

If a future version needs a small static UI configuration object, it should be kept separate from the mathematical forecast data.

Acceptable UI configuration examples:

- Product display title
- Method explanation copy
- Data-source explanation copy
- Feature flags for showing the model toggle

Unacceptable examples inside the forecast data contract:

- Per-match hand-coded colours
- Per-team decorative layout values
- Hard-coded component styling values
- Brand-specific fields that affect probability logic

The forecast data must remain model-first and reproducible. The visual style must be implemented through reusable frontend CSS tokens and components.

---

## 26. Design Warnings for Coding Agents

Coding agents must avoid the following mistakes:

1. Do not use team display names as IDs.
2. Do not hard-code bracket logic directly into UI components.
3. Do not make the frontend depend on a Python backend.
4. Do not fetch live rating data during normal user interaction.
5. Do not store derived probabilities as authoritative source data.
6. Do not allow user overrides to change official locked results.
7. Do not allow invalid downstream overrides to persist silently.
8. Do not change match IDs after deployment.
9. Do not assume all football teams map cleanly to ISO country flags.
10. Do not implement a database for the MVP.
11. Do not use post-tournament or in-tournament Elo data for a pre-tournament forecast unless the snapshot kind explicitly says so.
12. Do not make the model toggle depend on backend calls.
13. Do not store visual styling values as authoritative forecast data.
14. Do not use proprietary FT fonts, logos, trademarks, or content unless separately licensed.

---

## 27. Summary

The data model is built around stable team IDs, stable match IDs, stable model IDs, static generated frontend data, and derived browser-side forecast state.

The MVP requires only rating data, team data, bracket data, and generated JSON.

Future features such as historical calibration, model toggling, official result locking, forecast history, and shareable scenario URLs are supported by the same ID-based structure without requiring an architectural rewrite.
