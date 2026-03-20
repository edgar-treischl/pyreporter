.PHONY: run clean help

run:
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