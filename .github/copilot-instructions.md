# Copilot Instructions

## Commands

```bash
# Run main pipeline
poetry run python -m pyreporter.run

# Run tests / scripts
poetry run python -m pyreporter.test        # meta data smoke test
poetry run python -m pyreporter.test.test   # inspect meta_sets
poetry run python -m pyreporter.test.test_plot  # visual plot test (renders a window)
poetry run python -m pyreporter.test.limer_test # live LimeSurvey API test (requires .env)
```

## Architecture

pyreporter is a **school evaluation report pipeline** that:
1. Fetches survey responses from a **LimeSurvey** instance via JSON-RPC API (`limer.py`)
2. Selects the correct report template using **CSV-based metadata** (`MetaRepository`, `pyreporter/data/`)
3. Processes raw response data into aggregated plot data (`utils.py`)
4. Renders **plotnine** (ggplot2-style) charts as PDFs (`plot.py`)
5. Assembles a final PDF report by rendering a **Quarto `.qmd` template** (`render_pdf.py`)

### Module responsibilities

| Module | Role |
|---|---|
| `limer.py` | LimeSurvey API: session management, survey listing, response export |
| `meta_repository.py` | Loads and validates all CSV metadata into a single `MetaRepository` object |
| `utils.py` | Data processing: `get_metadata`, `get_data`, `get_plotdata`, `get_sname`, `get_directory`, `match_meta_reports` |
| `plot.py` | Chart creation (`create_ggplot`) and export (`export_plot`) |
| `render_pdf.py` | Quarto subprocess invocation to render `.qmd` → PDF |

### Metadata CSVs (`pyreporter/data/`)

All domain configuration lives in CSVs, never hardcoded:
- `meta_templates.csv` — maps `(stype, type, ubb, ganztag)` to a `report_tmpl` name
- `meta_reports.csv` — maps report templates to plot names and survey variable codes
- `meta_sets.csv` — Likert scale label sets (codes, labels, colors, sort order)
- `meta_headers.csv` — header/section metadata per plot
- `meta_snames.csv` — school number (`SNR`) → school name mapping

### Output structure

```
pyreporter/res/{snr}_{year}/
    plots/          ← PDF charts, one per plot name (e.g. A12_plot.pdf)
    template.qmd    ← Quarto template (copied/placed manually)
    {snr}_results_{audience}.pdf  ← final rendered report
```

## Key Conventions

**LimeSurvey session lifecycle** — always acquire and release explicitly:
```python
limer_connect()
# ... limer_call / limer_responses / limer_n / limer_SIDs ...
limer_release()
```
`limer_connect()` populates a module-level `session_cache`; `limer_call()` reads from it.

**School number (`snr`)** is always a 4-digit zero-padded string (e.g. `"0001"`). `meta_snames.csv` is loaded with `dtype={"SNR": str}` to preserve leading zeros.

**Boolean columns in CSVs** are stored as `0`/`1` or `"true"`/`"false"` strings. Use `_as_bool()` from `utils.py` to normalize before filtering.

**Audience codes**: `"sus"` (students), `"elt"` (parents), `"leh"` (teachers), `"ubb"` (classroom observations), `"aus"` (trainers), `"all"` (combined).

**`ubb` flag** distinguishes classroom observation surveys — LimeSurvey survey titles containing the string `"ubb"` are treated as observation surveys; all others are standard surveys.

**Response data → long format**: `get_data()` pivots wide LimeSurvey CSVs (semicolon-delimited, base64-encoded) into a long DataFrame with columns `sid`, `surveyls_title`, `id`, `vars`, `vals`.

**Plot branching**: `create_ggplot(data, ubb, labels)` has two distinct code paths — `ubb=True` uses raw counts (`anz`); `ubb=False` uses percentages (`p`).

**Environment** — credentials are loaded from `.env` via `python-dotenv`. Required variables:
```
LIME_API_URL=
LIME_USERNAME=
LIME_PASSWORD=
```
