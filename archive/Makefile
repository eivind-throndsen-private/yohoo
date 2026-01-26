# Yohoo Project Makefile

.PHONY: help install run generate parse test format clean proxy

# Default target
help:
	@echo "Yohoo Project - Available commands:"
	@echo "  make install   - Create virtual environment and install dependencies"
	@echo "  make run       - Open yohoo.html in browser"
	@echo "  make proxy     - Start local proxy server for title fetching"
	@echo "  make generate  - Generate HTML from merged data"
	@echo "  make parse     - Parse bookmarks file"
	@echo "  make test      - Run tests"
	@echo "  make format    - Format Python code with black and isort"
	@echo "  make clean     - Remove generated files and caches"

# Create virtual environment
.venv:
	python3 -m venv .venv
	@echo "Virtual environment created at .venv"

# Install dependencies
install: .venv
	. ./.venv/bin/activate && pip install --upgrade pip
	. ./.venv/bin/activate && pip install -r requirements.txt
	@echo "Dependencies installed successfully"

# Open yohoo.html in default browser
run:
	@echo "Opening yohoo.html in browser..."
	open yohoo.html

# Generate HTML from merged data
generate:
	@echo "Generating HTML..."
	. ./.venv/bin/activate && python scripts/generate_html.py

# Parse bookmarks file
parse:
	@echo "Parsing bookmarks..."
	. ./.venv/bin/activate && python scripts/parse_bookmarks.py input/bookmarks_08.12.2025.html -o data/bookmarks.json

# Start proxy server
proxy: .venv
	@echo "Starting Yohoo Proxy Server..."
	. ./.venv/bin/activate && python proxy_server.py

# Run tests
test:
	@echo "Running tests..."
	. ./.venv/bin/activate && pytest tests/ -v

# Format Python code
format:
	@echo "Formatting Python code..."
	. ./.venv/bin/activate && black scripts/ tests/
	. ./.venv/bin/activate && isort scripts/ tests/

# Clean generated files
clean:
	@echo "Cleaning up..."
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -f logs/*.log 2>/dev/null || true
	@echo "Cleanup complete"
