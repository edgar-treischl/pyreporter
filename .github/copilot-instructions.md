# Copilot Instructions

## Commands

```bash
# Install dependencies
poetry install

# --- Modular Pipeline (with caching) ---

# Download raw survey data from LimeSurvey (cached in .cache/)
make fetch SNR=0001 UBB=False

# Prepare plot-ready data from raw data (cached in .cache/)
make prepare SNR=0001 AUDIENCE=sus

# Generate all plots for a report
make plot AUDIENCE=sus

# Generate a specific plot only
make plot PLOT=A12 AUDIENCE=sus

# Run full pipeline: fetch + prepare + generate plots + render PDF
make run SNR=0001 STYPE=gy AUDIENCE=sus UBB=False GANZTAG=False HAS_N=sus,leh YEAR=2025

# --- Direct Python execution (alternative) ---

# Run individual pipeline stages
poetry run python -m pyreporter.fetch
poetry run python -m pyreporter.prepare
poetry run python -m pyreporter.plot

# Run full pipeline
poetry run python -m pyreporter.run

# --- Cleaning ---

# Clean generated output (res/ directory)
make clean

# Clean cached data (.cache/ directory)
make clean-cache

# Clean everything (res/ + .cache/)
make clean-all

# --- Focused script-style checks (there is no pytest suite in this repo) ---
poetry run python -m pyreporter.test.test        # print meta_sets from MetaRepository
poetry run python -m pyreporter.test.test2       # exercise get_metadata() template selection
poetry run python -m pyreporter.test.test_render # render a PDF from existing local assets
poetry run python -m pyreporter.test.test_plot   # open a plotnine window for manual inspection
poetry run python -m pyreporter.test.limer_test  # live LimeSurvey API check; requires .env
```

`poetry run python -m pyreporter.test` is stale and does not work because `pyreporter.test` has no `__main__`; use one of the explicit modules above instead.

## Caching Behavior

The refactored pipeline uses aggressive caching to speed up development:

- **Raw data cache** (`.cache/raw_*.pkl`): Cached by `(snr, ubb)`. Avoids repeated LimeSurvey API calls.
- **Prepared data cache** (`.cache/prepared_*.pkl`): Cached by `(snr, stype, audience, ubb, ganztag, has_N)`. Avoids reprocessing survey responses.
- **Cache invalidation**: Delete `.cache/` to force fresh downloads, or use `NO_CACHE=true` environment variable.
- **Modular execution**: `make prepare` automatically uses cached raw data if available. `make plot` uses cached prepared data.

```bash
# Force cache bypass for all commands
NO_CACHE=true make fetch

# Or manually clear cache
make clean-cache
```

## Environment Setup

LimeSurvey credentials are required to run the pipeline:

```bash
# Copy example and configure
cp .env.example .env

# Required variables:
# LIME_API_URL=https://your-limesurvey.com/admin/remotecontrol
# LIME_USERNAME=your_username
# LIME_PASSWORD=your_password
```

## High-Level Architecture

`pyreporter` is a survey-report pipeline for school evaluations. The pipeline is modular and cacheable:

**Modular Pipeline Stages:**

1. **Fetch** (`pyreporter.fetch`): Downloads raw survey data from LimeSurvey via JSON-RPC. Caches results by `(snr, ubb)`.
2. **Prepare** (`pyreporter.prepare`): Transforms raw data into plot-ready format, joining with metadata CSVs. Caches results by `(snr, stype, audience, ubb, ganztag, has_N)`.
3. **Plot** (`pyreporter.plot`): Generates plotnine charts and exports PDFs to `res/{snr}_{syear}/plots/`.
4. **Render** (`pyreporter.render_pdf`): Assembles final PDF report using Quarto.

**End-to-End Flow:**

1. `pyreporter.fetch` talks to LimeSurvey, discovers relevant surveys for a school, and exports raw responses.
2. `pyreporter.prepare` converts exported surveys from wide CSV into normalized long-format DataFrames (`sid`, `surveyls_title`, `id`, `vars`, `vals`).
3. `pyreporter.prepare` resolves the report template and joins survey responses with CSV metadata from `pyreporter/data/`.
4. `pyreporter.plot` turns prepared plot data into plotnine charts and writes PDFs.
5. `pyreporter.utils.create_directories()` prepares `res/{snr}_{syear}/` by copying the correct `.qmd` template and image assets from `pyreporter/templates/`.
6. `pyreporter.render_pdf` writes `params.yml` and runs `quarto render template.qmd --to pdf --execute-params params.yml`.

The metadata layer is central to the design. `MetaRepository` loads `meta_templates.csv`, `meta_reports.csv`, `meta_sets.csv`, `meta_headers.csv`, `meta_mastertotemplate.csv`, and `meta_snames.csv` from package resources, and the pipeline uses those CSVs to choose report templates, plot membership, label sets, header text, and school names. When behavior changes, the right fix is often in the CSV metadata rather than Python code.

## Key Conventions

### Data Types and Formats
- **School numbers must be zero-padded strings.** `meta_snames.csv` is loaded with `dtype={"SNR": str}` so leading zeros survive joins and lookups. Never convert SNR to int.
- **Normalize metadata booleans with `_as_bool()` before filtering.** `meta_templates["ubb"]` and `meta_templates["ganztag"]` are stored as string-like values in CSVs (e.g., "True", "1") and must be normalized.

### Domain-Specific Codes
- **Audience codes**: `sus` (students), `elt` (parents), `leh` (teachers), `ubb` (classroom observations), `aus` (trainers), `all` (all groups).
- **The `all` audience is special**: `get_metadata()` requires `data_avail` parameter, and `get_plotdata()` appends the audience `type` to `vars` for labeling.
- **School types** (`stype`): `gy` (Gymnasium), etc. These determine which report template is selected.

### Pipeline Behavior
- **`ubb` changes behavior throughout**: Survey discovery checks for `"ubb"` in `surveyls_title`, and plotting switches from percentage-based bars (`p`) to raw-count bars (`anz`) when `ubb=True`.
- **`get_data()` performs critical reshaping**: Strips dots from variable names, splits at first `X`, removes first 3 characters, trims whitespace, and drops blank answers. This normalized long format (`sid`, `surveyls_title`, `id`, `vars`, `vals`) is expected everywhere downstream.
- **Report year comes from survey titles, not environment**: `run.py` extracts `syear` from the LimeSurvey `surveyls_title` field (second underscore-delimited segment, first 4 chars), not from the `YEAR` environment variable.

### File System and Templates
- **Use `create_directories()` and `get_directory()` as the source of truth** for output paths. All generated content goes under `res/{snr}_{syear}/`.
- **`render_pdf()` assumes directory structure is ready**: It expects `template.qmd`, header graphics (`graphic_title_ubb.png` or `graphic-title_bfr.png`, `header_isb.png`), and `plots/` subdirectory to already exist.
- **Template selection is metadata-driven**: `create_directories()` copies either `template_ubb.qmd` or `template_bfr.qmd` from `pyreporter/templates/` based on the `ubb` flag.

### API and Session Management
- **LimeSurvey session is module-level cached** in `limer.py` via `SessionCache`. Always use the `limer_connect()` → `limer_call()` → `limer_release()` pattern. Never manually store session keys.
- **Environment variables**: `.env` must contain `LIME_API_URL`, `LIME_USERNAME`, `LIME_PASSWORD`. The `load_dotenv()` call happens at module import in `limer.py`.

### Metadata Validation
- **`match_meta_reports()` performs critical pre-render validation**: It joins `meta_reports` with `meta_headers` to build the `header_report` DataFrame. If a plot exists in a report but not in `meta_headers`, rendering will fail before Quarto runs.
- **Metadata CSVs drive everything**: When behavior needs to change (new labels, plot membership, header text), edit the CSVs in `pyreporter/data/`, not Python code.

### Quarto Integration
- **PDF rendering uses subprocess**: `render_pdf()` writes `params.yml` and calls `quarto render template.qmd --to pdf --execute-params params.yml` via `subprocess.run()`.
- **Quarto must be installed** on the system and available in PATH. This is not a Python dependency but an external tool requirement.
