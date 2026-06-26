# Yohoo Project Makefile

.PHONY: help install install-browsers run generate parse test test-unit test-browser test-regression format clean proxy

# Default target
help:
	@echo "Yohoo Project - Available commands:"
	@echo "  make install          - Create virtual environment and install dependencies"
	@echo "  make install-browsers - Install Playwright browsers for testing"
	@echo "  make run              - Open yohoo.html in browser"
	@echo "  make proxy            - Start local proxy server for title fetching"
	@echo "  make generate         - Generate HTML from merged data"
	@echo "  make parse            - Parse bookmarks file"
	@echo "  make test             - Run all tests (unit + browser)"
	@echo "  make test-unit        - Run only unit tests (fast)"
	@echo "  make test-browser     - Run only browser tests (requires Playwright)"
	@echo "  make test-regression  - Run regression tests for drag-drop and reset bugs"
	@echo "  make format           - Format Python code with black and isort"
	@echo "  make clean            - Remove generated files and caches"

# Create virtual environment
.venv:
	python3 -m venv .venv
	@echo "Virtual environment created at .venv"

# Install dependencies
install: .venv
	. ./.venv/bin/activate && pip install --upgrade pip
	. ./.venv/bin/activate && pip install -r requirements.txt
	@echo "Dependencies installed successfully"
	@echo ""
	@echo "To run browser tests, also run: make install-browsers"

# Install Playwright browsers
install-browsers: .venv
	@echo "Installing Playwright browsers..."
	. ./.venv/bin/activate && playwright install chromium
	@echo "Playwright browsers installed successfully"

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

# Run all tests
test: test-unit test-browser

# Run only unit tests (fast, no browser required)
test-unit:
	@echo "Running unit tests..."
	. ./.venv/bin/activate && pytest tests/test_drag_drop_reset.py tests/test_url_validation.py -v

# Run only browser tests (requires Playwright browsers)
test-browser:
	@echo "Running browser tests..."
	@echo "Note: This requires Playwright browsers. Run 'make install-browsers' if not installed."
	. ./.venv/bin/activate && pytest tests/test_browser_functionality.py -v --headed

# Run regression tests specifically for drag-drop and reset bugs
test-regression:
	@echo "Running regression tests for drag-drop and reset bugs..."
	. ./.venv/bin/activate && pytest tests/test_drag_drop_reset.py::TestRegressionPrevention -v
	. ./.venv/bin/activate && pytest tests/test_browser_functionality.py::TestRegressionDetection -v --headed

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
