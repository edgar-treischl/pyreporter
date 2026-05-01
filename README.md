# PyReporter

A survey-report pipeline for automated school evaluation reports. PyReporter connects to LimeSurvey, processes survey responses, generates visualizations, and produces comprehensive PDF reports using Quarto.

## Features

- 🔗 **LimeSurvey Integration**: Automatic survey discovery and data export via JSON-RPC API
- 📊 **Data Processing**: Transforms survey responses into normalized long-format DataFrames
- 📈 **Visualization**: Creates publication-ready plots using plotnine
- 📄 **PDF Generation**: Assembles reports with Quarto using customizable templates
- 🎯 **Metadata-Driven**: CSV-based configuration for templates, labels, and report structure

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

## Documentation

Visit the [full documentation](https://your-docs-url.here) for:
- Installation guide
- Getting started tutorial
- API reference
- Configuration options


