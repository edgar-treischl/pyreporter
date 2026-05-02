# PyReporter

A survey-report pipeline for automated school evaluation reports. PyReporter connects to LimeSurvey, processes survey responses, generates visualizations, and produces comprehensive PDF reports using Quarto.

## Features

- 🔗 **LimeSurvey Integration**: Automatic survey discovery and data export via JSON-RPC API
- 📊 **Data Processing**: Transforms survey responses into normalized long-format DataFrames
- 📈 **Visualization**: Creates publication-ready plots using plotnine
- 📄 **PDF Generation**: Assembles reports with Quarto using customizable templates
- 🎯 **Metadata-Driven**: CSV-based configuration for templates, labels, and report structure
- ⚡ **Modular & Cacheable**: Split pipeline into independent stages with intelligent caching

## Quick Start

```bash
# Install dependencies
poetry install

# Configure LimeSurvey credentials
cp .env.example .env
# Edit .env with your credentials

# Run the full pipeline
make run SNR=0001 STYPE=gy AUDIENCE=sus YEAR=2025
```

## Modular Pipeline Architecture

The pipeline has been refactored from a monolithic `make run` command into modular, cacheable components for faster development and selective execution:

### Pipeline Stages

```bash
# 1. Fetch raw survey data from LimeSurvey (cached)
make fetch SNR=0001 UBB=False

# 2. Prepare plot-ready data (cached)
make prepare AUDIENCE=sus

# 3. Generate all plots
make plot

# 4. Generate a specific plot only
make plot PLOT=A12

# 5. Run the complete pipeline
make run SNR=0001 STYPE=gy AUDIENCE=sus
```

### Benefits

- **⚡ Faster Iteration**: Skip expensive API calls with intelligent caching
- **🎯 Selective Execution**: Generate only the plots you need during development
- **🔍 Better Debugging**: Test each stage independently
- **🔄 Composability**: Mix cached and fresh data as needed

### Caching Behavior

- **Raw data cache** (`.cache/raw_*.pkl`): Cached by `(snr, ubb)` - avoids repeated LimeSurvey API calls
- **Prepared data cache** (`.cache/prepared_*.pkl`): Cached by `(snr, stype, audience, ubb, ganztag, has_N)` - avoids reprocessing
- **Cache invalidation**: Use `make clean-cache` or set `NO_CACHE=true`

```bash
# Clear cache and force fresh download
make clean-cache
make fetch

# Or bypass cache for one command
NO_CACHE=true make fetch
```

## Common Workflows

### Develop a Single Plot

```bash
# Download data once
make fetch SNR=0001

# Iterate on plot code
# (edit pyreporter/plot.py or metadata CSVs)
make plot PLOT=A12
# Repeat as needed without re-downloading
```

### Test Multiple Audiences

```bash
# Download once
make fetch SNR=0001

# Test different audiences (reuses cached raw data)
make plot AUDIENCE=sus
make plot AUDIENCE=leh
make plot AUDIENCE=elt
```

### Clean Generated Files

```bash
make clean         # Delete generated reports (res/)
make clean-cache   # Delete cached data (.cache/)
make clean-all     # Delete everything
```

## Documentation

Visit the [full documentation](https://your-docs-url.here) for:
- Installation guide
- Getting started tutorial
- API reference
- Configuration options


