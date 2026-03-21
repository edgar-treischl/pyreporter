# Copilot Instructions

## Commands

```bash
# Install dependencies
poetry install

# Run the full pipeline directly
poetry run python -m pyreporter.run

# Run the full pipeline with repository defaults/overrides
make run SNR=0001 STYPE=gy AUDIENCE=sus UBB=False GANZTAG=False HAS_N=sus,leh YEAR=2025

# Clean generated output
make clean

# Focused script-style checks (there is no pytest suite in this repo)
poetry run python -m pyreporter.test.test        # print meta_sets from MetaRepository
poetry run python -m pyreporter.test.test2       # exercise get_metadata() template selection
poetry run python -m pyreporter.test.test_render # render a PDF from existing local assets
poetry run python -m pyreporter.test.test_plot   # open a plotnine window for manual inspection
poetry run python -m pyreporter.test.limer_test  # live LimeSurvey API check; requires .env
```

`poetry run python -m pyreporter.test` is stale and does not work because `pyreporter.test` has no `__main__`; use one of the explicit modules above instead.

## High-Level Architecture

`pyreporter` is a survey-report pipeline for school evaluations. The end-to-end flow crosses several modules:

1. `pyreporter.run` reads environment-driven inputs, loads metadata, and orchestrates the entire report generation.
2. `pyreporter.limer` talks to LimeSurvey over JSON-RPC, discovers the relevant surveys for a school, and exports raw responses.
3. `pyreporter.utils.get_data()` converts each exported survey from wide CSV into a normalized long-format DataFrame with `sid`, `surveyls_title`, `id`, `vars`, and `vals`.
4. `pyreporter.utils.get_metadata()` and `get_plotdata()` resolve the report template and join survey responses with CSV metadata from `pyreporter/data/`.
5. `pyreporter.plot` turns the prepared plot data into plotnine charts and writes PDFs under `res/{snr}_{syear}/plots/`.
6. `pyreporter.utils.create_directories()` prepares `res/{snr}_{syear}/` by copying the correct `.qmd` template and image assets from `pyreporter/templates/`.
7. `pyreporter.render_pdf` writes `params.yml` and runs `quarto render template.qmd --to pdf --execute-params params.yml` to assemble the final report PDF.

The metadata layer is central to the design. `MetaRepository` loads `meta_templates.csv`, `meta_reports.csv`, `meta_sets.csv`, `meta_headers.csv`, `meta_mastertotemplate.csv`, and `meta_snames.csv` from package resources, and the pipeline uses those CSVs to choose report templates, plot membership, label sets, header text, and school names. When behavior changes, the right fix is often in the CSV metadata rather than Python code.

## Key Conventions

- Treat school numbers as zero-padded strings. `meta_snames.csv` is loaded with `dtype={"SNR": str}` so leading zeros survive joins and lookups.
- Normalize metadata booleans with `_as_bool()` before filtering. `meta_templates["ubb"]` and `meta_templates["ganztag"]` are stored as string-like values in CSVs.
- Audience codes are domain-specific: `sus`, `elt`, `leh`, `ubb`, `aus`, and `all`. The `all` audience is special: `get_metadata()` needs `data_avail`, and `get_plotdata()` appends the audience `type` to `vars`.
- `ubb` changes behavior across the pipeline. Survey discovery checks whether `surveyls_title` contains `"ubb"`, and plotting switches from percentage-based bars (`p`) to raw-count bars (`anz`) when `ubb=True`.
- `get_data()` reshapes LimeSurvey exports into the long format expected everywhere else. It strips dots from variable names, splits at the first `X`, removes the first three characters, trims values, and drops blank answers before downstream joins.
- `run.py` derives the report year from the LimeSurvey survey title, not from the `YEAR` environment variable, before creating `res/{snr}_{syear}/`.
- Use `create_directories()` and `get_directory()` as the source of truth for output layout. `render_pdf()` expects `template.qmd`, header graphics, and `plots/` to already exist in that directory.
- LimeSurvey access depends on a module-level session cache in `limer.py`. Preserve the existing connect/call/release flow when changing API code, and keep `.env` variables `LIME_API_URL`, `LIME_USERNAME`, and `LIME_PASSWORD` in sync.
- `match_meta_reports()` joins `meta_reports` with `meta_headers` to build the `header_report` DataFrame required by `render_pdf()`. If a plot exists in a report but not in `meta_headers`, rendering will fail before Quarto runs.
