# Repository Guidelines

## Project Structure & Module Organization
- Root UI: `yohoo.html`, `yohoo.js`, and `Yohoo.png` are the live start page assets.
- Tooling archive: `archive/` contains the data pipeline, tests, and historical assets.
  - Scripts: `archive/scripts/` (bookmark parsing, history analysis, HTML generation).
  - Data: `archive/data/` (generated JSON/CSV inputs/outputs).
  - Tests: `archive/tests/` (pytest + HTML harnesses).
  - Inputs: `archive/input/` (sample bookmarks exports).
  - Build tooling: `archive/Makefile`, `archive/requirements.txt`.
- Local proxy: `proxy_server.py` is used for title fetching in development.

## Build, Test, and Development Commands
- `make -C archive install`: create `.venv` and install Python deps.
- `make -C archive run`: open `archive/yohoo.html` in a browser.
- `make -C archive parse`: parse bookmarks into `archive/data/bookmarks.json`.
- `make -C archive generate`: regenerate `archive/yohoo.html` from data.
- `make -C archive test`: run pytest in `archive/tests/`.
- `make -C archive format`: run `black` + `isort` on Python code.
- `make -C archive proxy`: start the local title-fetch proxy.

## Coding Style & Naming Conventions
- JavaScript/HTML: 4-space indentation; prefer `const`/`let`; camelCase for variables and functions.
- Python: follow Black formatting and isort ordering; snake_case for functions/vars, CapWords for classes.
- File naming follows existing patterns (e.g., `test_*.py`, `generate_html.py`).

## Testing Guidelines
- Framework: pytest (`archive/tests/`).
- Naming: tests live in `test_*.py`; HTML harnesses are kept alongside.
- Run: `make -C archive test` before submitting UI or pipeline changes.

## Commit & Pull Request Guidelines
- Commit messages: short, imperative verb, sentence case (e.g., “Add configurable default links system”).
- PRs: include a concise summary, test command(s) run, and screenshots for UI changes.

## Configuration & Data Notes
- Optional env vars (via `.env`): `CHROME_HISTORY_PATH`, `BOOKMARKS_FILE`, `HISTORY_DAYS`, `MIN_VISITS`, `LOG_LEVEL`.
- The UI stores user edits in `localStorage` (custom sections, order, and deleted links).
