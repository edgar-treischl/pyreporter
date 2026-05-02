# PyReporter

A survey-report pipeline for automated school evaluation reports. PyReporter connects to LimeSurvey, processes survey responses, generates visualizations, and produces comprehensive PDF reports using Quarto.

## Features

- 🔗 **LimeSurvey Integration**: Automatic survey discovery and data export via JSON-RPC API
- 📊 **Data Processing**: Transforms survey responses into normalized long-format DataFrames
- 📈 **Visualization**: Creates publication-ready plots using plotnine
- 📄 **PDF Generation**: Assembles reports with Quarto using customizable templates
- 🎯 **Metadata-Driven**: CSV-based configuration for templates, labels, and report structure
- ⚡ **Modular & Cacheable**: Split pipeline into independent stages with intelligent caching
- 🌐 **REST API**: FastAPI service layer for programmatic access

## Quick Start

### CLI Usage

```bash
# Install dependencies
poetry install

# Configure LimeSurvey credentials
cp .env.example .env
# Edit .env with your credentials

# Run the full pipeline
make run SNR=0001 STYPE=gy AUDIENCE=sus YEAR=2025
```

### API Usage

```bash
# Start the API server
make api-dev

# Visit the interactive docs
open http://localhost:8000/docs
```

See [API_README.md](API_README.md) for complete API documentation.

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

### API Endpoints

```bash
# Start the API server (development mode with auto-reload)
make api-dev

# Or production mode
make api
```

The API provides RESTful endpoints for all pipeline stages:

1. **POST** `/api/v1/raw-data` - Fetch raw survey data
2. **POST** `/api/v1/prepared-data` - Prepare plot-ready data
3. **POST** `/api/v1/plot` - Generate a single plot
4. **POST** `/api/v1/report` - Create complete PDF report
5. **GET** `/api/v1/plots/list` - List available plots

See [API_README.md](API_README.md) for detailed endpoint documentation, request/response examples, and usage instructions.

### Benefits

- **⚡ Faster Iteration**: Skip expensive API calls with intelligent caching
- **🎯 Selective Execution**: Generate only the plots you need during development
- **🔍 Better Debugging**: Test each stage independently
- **🔄 Composability**: Mix cached and fresh data as needed
- **🌐 Programmatic Access**: Use the REST API from any language or platform

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

### Use the API Programmatically

```python
import requests

# Generate a report via API
response = requests.post(
    "http://localhost:8000/api/v1/report",
    json={
        "snr": "0001",
        "stype": "gy",
        "audience": "sus",
        "year": "2025"
    }
)

# Save the PDF
with open("report.pdf", "wb") as f:
    f.write(response.content)
```

See [example_api_client.py](example_api_client.py) for more examples.

### Clean Generated Files

```bash
make clean         # Delete generated reports (res/)
make clean-cache   # Delete cached data (.cache/)
make clean-all     # Delete everything
```

## Available Commands

```bash
make help          # Show all available commands

# Pipeline commands
make fetch         # Download raw data from LimeSurvey
make prepare       # Prepare plot-ready data
make plot          # Generate plots
make run           # Run full pipeline

# API commands
make api           # Start API server (production)
make api-dev       # Start API server (development)

# Cleaning
make clean         # Clean output files
make clean-cache   # Clean cache
make clean-all     # Clean everything
```

## Testing

```bash
# Test API setup
poetry run python test_api_setup.py

# Test API client examples
poetry run python example_api_client.py
```

## Documentation

Visit the [full documentation](https://your-docs-url.here) for:
- Installation guide
- Getting started tutorial
- API reference
- Configuration options


