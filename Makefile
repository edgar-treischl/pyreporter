.PHONY: run fetch prepare plot clean clean-cache api api-dev help

# --- Default values (can be overridden) ---
SNR ?= 0001
STYPE ?= gy
AUDIENCE ?= leh
UBB ?= False
GANZTAG ?= False
HAS_N ?= sus,leh
YEAR ?= 2025
PLOT ?=

# --- Environment setup ---
export SNR
export STYPE
export AUDIENCE
export UBB
export GANZTAG
export HAS_N
export YEAR
export PLOT

# --- Pipeline targets ---

fetch:
	@echo "📡 Fetching raw data from LimeSurvey..."
	poetry run python -m pyreporter.fetch

prepare: fetch
	@echo "🔧 Preparing data for plotting..."
	poetry run python -m pyreporter.prepare

plot: prepare
	@echo "📊 Generating plots..."
	poetry run python -m pyreporter.plot

run:
	@echo "🚀 Running full pipeline..."
	poetry run python -m pyreporter.run

# --- API targets ---

api:
	@echo "🌐 Starting API server..."
	poetry run uvicorn pyreporter.api:app --host 0.0.0.0 --port 8000

api-dev:
	@echo "🌐 Starting API server (development mode with auto-reload)..."
	poetry run uvicorn pyreporter.api:app --reload --host 0.0.0.0 --port 8000

# --- Cleaning targets ---

clean:
	@if [ -d res ]; then \
		echo "🗑️  Cleaning res/ directory..."; \
		find res -mindepth 1 -exec rm -rf {} +; \
	else \
		echo "res/ directory does not exist."; \
	fi

clean-cache:
	@if [ -d .cache ]; then \
		echo "🗑️  Cleaning .cache/ directory..."; \
		rm -rf .cache; \
	else \
		echo ".cache/ directory does not exist."; \
	fi

clean-all: clean clean-cache
	@echo "✅ All generated files and caches cleaned"

# --- Help ---

help:
	@echo "Available commands:"
	@echo ""
	@echo "Pipeline (modular with caching):"
	@echo "  make fetch        Download raw data from LimeSurvey (cached)"
	@echo "  make prepare      Prepare plot-ready data (cached)"
	@echo "  make plot         Generate all plots (or specify PLOT=name)"
	@echo "  make run          Run full pipeline (fetch + prepare + plots + PDF)"
	@echo ""
	@echo "API Server:"
	@echo "  make api          Start FastAPI server (production mode)"
	@echo "  make api-dev      Start FastAPI server (dev mode with auto-reload)"
	@echo "                    API docs at: http://localhost:8000/docs"
	@echo ""
	@echo "Examples:"
	@echo "  make fetch SNR=0001 UBB=True"
	@echo "  make plot PLOT=A12 AUDIENCE=sus"
	@echo "  make run SNR=0002 AUDIENCE=leh"
	@echo ""
	@echo "Cleaning:"
	@echo "  make clean        Delete generated reports (res/)"
	@echo "  make clean-cache  Delete cached data (.cache/)"
	@echo "  make clean-all    Delete everything (res/ + .cache/)"
	@echo ""
	@echo "Default parameters:"
	@echo "  SNR=$(SNR) STYPE=$(STYPE) AUDIENCE=$(AUDIENCE)"
	@echo "  UBB=$(UBB) GANZTAG=$(GANZTAG) HAS_N=$(HAS_N)"