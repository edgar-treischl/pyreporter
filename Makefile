.PHONY: run clean

# --- Default values (can be overridden) ---
SNR ?= 0001
STYPE ?= gy
AUDIENCE ?= leh
UBB ?= False
GANZTAG ?= False
HAS_N ?= sus,leh
YEAR ?= 2025

run:
	SNR=$(SNR) STYPE=$(STYPE) AUDIENCE=$(AUDIENCE) \
	UBB=$(UBB) GANZTAG=$(GANZTAG) HAS_N=$(HAS_N) YEAR=$(YEAR) \
	poetry run python -m pyreporter.run

clean:
	@if [ -d res ]; then \
		echo "Cleaning res/ directory..."; \
		find res -mindepth 1 -exec rm -rf {} +; \
	else \
		echo "res/ directory does not exist."; \
	fi
help:
	@echo "Available commands:"
	@echo "  make run     Run the report pipeline"
	@echo "  make clean   Delete all files and subfolders under res/"