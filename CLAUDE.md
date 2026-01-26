# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Yohoo is a personal, customizable browser start page that combines bookmarks with Chrome browsing history analysis. It features a dark mauve theme with drag-and-drop organization, localStorage persistence, and automatic link categorization based on usage patterns.

## Development Commands

### Setup
```bash
make -C archive install          # Create .venv and install dependencies
```

### Running
```bash
make -C archive run              # Open archive/yohoo.html in browser (uses 'open' command)
```

### Data Pipeline
```bash
make -C archive parse            # Parse bookmarks HTML → archive/data/bookmarks.json
make -C archive generate         # Generate archive/yohoo.html from data
make -C archive parse && make -C archive generate  # Full refresh workflow
```

### Development
```bash
make -C archive test             # Run pytest tests
make -C archive format           # Format Python code with black and isort
make -C archive clean            # Remove .venv, __pycache__, and logs
```

### Running Scripts Directly
```bash
# Always activate virtual environment first
. archive/.venv/bin/activate

# Parse bookmarks with options
python archive/scripts/parse_bookmarks.py archive/input/bookmarks_08.12.2025.html -o archive/data/bookmarks.json
python archive/scripts/parse_bookmarks.py --verbose    # INFO logging
python archive/scripts/parse_bookmarks.py --debug      # DEBUG logging

# Analyze Chrome history
python archive/scripts/analyze_history.py --days 90 -o archive/data/history.json

# Generate HTML
python archive/scripts/generate_html.py -b archive/data/bookmarks.json -o archive/yohoo.html

# Merge data
python archive/scripts/utils.py merge archive/data/bookmarks.json archive/data/history.json -o archive/data/merged.json
```

## Architecture

### Data Flow
```
Chrome Bookmarks HTML → archive/scripts/parse_bookmarks.py → archive/data/bookmarks.json
                                                     ↓
Chrome History DB → archive/scripts/analyze_history.py → archive/data/history.json → archive/scripts/utils.py (merge) → archive/scripts/generate_html.py → archive/yohoo.html
                                                                                          ↓
                                                                                  Browser (localStorage)
```

### Key Scripts

**archive/scripts/parse_bookmarks.py**
Parses HTML bookmark exports (Chrome/Firefox format). Extracts links, filters by age (default: 365 days), auto-categorizes based on URL patterns in `CATEGORY_KEYWORDS` dict. Outputs to `data/bookmarks.json`.

**archive/scripts/analyze_history.py**
Analyzes Chrome's SQLite history database. Creates temporary copy (Chrome locks the original), calculates frequency + recency scores using exponential decay algorithm (60% frequency weight, 40% recency weight). Excludes low-value patterns (search results, localhost, etc.). Outputs to `data/history.json`.

**archive/scripts/utils.py**
Merges bookmarks and history data, deduplicates by URL, exports to JSON/CSV formats.

**archive/scripts/generate_html.py**
Generates self-contained archive/yohoo.html with embedded JavaScript for drag-and-drop, localStorage persistence, search (keyboard shortcut: `/`), and trash system.

**archive/scripts/logging_config.py**
Centralized logging setup. All scripts support `--verbose`, `--debug`, and `--quiet` flags.

### Frontend Architecture

**archive/yohoo.html**
Single-file start page with:
- Vanilla JavaScript (no frameworks)
- localStorage for customizations (link assignments, custom sections, deleted links, section order)
- HTML5 drag-and-drop API for reorganizing links and sections
- Search functionality (press `/` to activate)
- Trash system with soft-delete and restore

**Data stored in localStorage:**
- `customSubcategories`: User-created sections
- `linkAssignments`: URL → section mappings
- `customLinks`: User-added links
- `subcategoryOrder`: Section display order
- `deletedLinks`: Soft-deleted links (restorable)

### Category System

Categories are defined in `CATEGORY_KEYWORDS` dict in `archive/scripts/parse_bookmarks.py`:
- `work-productivity`: Google Workspace, Notion, Trello, etc.
- `development`: GitHub, Stack Overflow, AWS, Docker, etc.
- `communication`: Slack, Teams, Zoom, etc.
- `media-entertainment`: YouTube, Netflix, Reddit, etc.
- `research-learning`: Wikipedia, Coursera, Medium, etc.
- `personal`: Amazon, Maps, Banking, etc.
- `tools-utilities`: ChatGPT, Canva, Figma, etc.

Auto-categorization matches URL domain against keywords (case-insensitive).

### Scoring Algorithm

Chrome history scoring (in `analyze_history.py`):
```python
recency_score = e^(-0.1 × days_ago)
normalized_frequency = min(visit_count / 50, 1.0)
combined_score = (normalized_frequency × 0.6) + (recency_score × 0.4)
```

## Configuration

**Environment Variables** (optional `.env` file):
- `CHROME_HISTORY_PATH`: Override default Chrome history location
- `BOOKMARKS_FILE`: Input bookmarks HTML path
- `HISTORY_DAYS`: Days of history to analyze (default: 90)
- `MIN_VISITS`: Minimum visits to include a site (default: 3)
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

## Important Notes

- **Virtual environment**: Always use `.venv/bin/activate` before running Python scripts
- **Makefile note**: The `archive/Makefile` `generate` target references `generate_html_v4.py` but this file doesn't exist—likely should be `generate_html.py`
- **Chrome history**: Scripts auto-detect Chrome profile (tries Profile 1 first, then Default on macOS)
- **Browser compatibility**: Works in Chrome, Firefox, Safari, Edge (uses standard HTML5 APIs)
- **Tests**: `archive/tests/` includes a settings modal harness; run `make -C archive test` for pytest
- **Local-first**: No backend, cloud sync, or external dependencies—all data stays local

## Project Status

See `archive/SPECIFICATIONS.md` for detailed functional requirements and feature status. See `archive/PROJECT_STATUS.md` for development history.
