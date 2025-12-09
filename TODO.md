# Yohoo Project - TODO List

**Last Updated**: 2025-12-09  
**Review By**: Architecture Code Review

---

## Priority Legend
- 🔴 **P0 - Critical**: Blocking issues or missing required infrastructure
- 🟠 **P1 - High**: Important improvements needed for production quality
- 🟡 **P2 - Medium**: Enhancements that improve quality/usability
- 🟢 **P3 - Low**: Nice-to-have features or minor improvements

---

## 🔴 P0 - Critical (Project Infrastructure)

### Project Setup (Required per Global Rules)

- [x] **Create Makefile** with standard commands:
  ```makefile
  # Required: run, test, clean, install, format
  .venv:
      python3 -m venv .venv
  
  install: .venv
      . ./.venv/bin/activate && pip install -r requirements.txt
  
  run:
      open yohoo.html
  
  generate:
      . ./.venv/bin/activate && python scripts/generate_html_v4.py
  
  parse:
      . ./.venv/bin/activate && python scripts/parse_bookmarks.py
  
  test:
      . ./.venv/bin/activate && pytest tests/
  
  format:
      . ./.venv/bin/activate && black scripts/ && isort scripts/
  
  clean:
      rm -rf .venv __pycache__ *.pyc logs/*.log
  ```

- [x] **Create .gitignore** with proper exclusions:
  ```
  .venv/
  __pycache__/
  *.pyc
  .env
  .DS_Store
  logs/*.log
  data/history.json
  *.db
  temp/
  ```

- [x] **Create .env.example** for configuration templates

- [x] **Create input/ directory** and move `bookmarks_08.12.2025.html` there

- [x] **Create logs/ directory** for script logs

- [x] **Create tests/ directory** with basic test structure

- [x] **Update README.md** with proper setup and usage instructions per global rules

---

## 🟠 P1 - High (Code Quality & Consistency)

### HTML/JS Consistency Issues

- [ ] **Reconcile yohoo.html and generate_html_v4.py structures**
  - Current yohoo.html uses flat subcategories grid
  - generate_html_v4.py creates categories with nested subcategories
  - These need to be aligned or one approach chosen
  - **Recommendation**: Adopt the flat subcategories approach from yohoo.html

- [x] **Consolidate generate_html versions**
  - Removed obsolete versions: `generate_html.py`, `generate_html_v2.py`, `generate_html_v3.py`
  - Renamed `generate_html_v4.py` to `generate_html.py`


### Python Script Improvements

- [x] **Add logging to all scripts** (required per global rules)
  - Created `logging_config.py` module with shared logging setup
  - All scripts now use consistent logging with file and console handlers
  - Log files saved to `logs/` directory with timestamps

- [x] **Add proper error handling** for missing files in all scripts
  - Added try/except blocks for file operations
  - Proper error logging with context

- [x] **Fix relative imports in analyze_history.py**
  - Fixed import: now uses `from scripts.parse_bookmarks import CATEGORY_KEYWORDS`
  - Added proper path handling for module imports

- [x] **Add type hints** to all Python functions (per Python rules)
  - All functions now have proper type hints
  - Used `typing` module for complex types (List, Dict, Optional, etc.)

- [x] **Add CLI logging options** to all scripts
  - `--verbose` / `-v`: INFO level logging
  - `--debug`: DEBUG level logging
  - `--quiet` / `-q`: ERROR level only

---

## 🟡 P2 - Medium (Feature Improvements)

### Frontend Enhancements

- [ ] **Complete "Add Section" functionality**
  - Button exists but modal in yohoo.html differs from generate_html_v4.py
  - Ensure consistent behavior

- [ ] **Add inline title editing**
  - Allow editing link titles by double-clicking
  - Save to localStorage

- [ ] **Add section renaming**
  - Allow renaming section titles
  - Persist to localStorage

- [ ] **Add section deletion**
  - Allow deleting empty sections
  - Move all links to Misc first if section has links

- [ ] **Improve external URL drop**
  - Currently shows hostname as title
  - Add background fetch for page title (already partially implemented)
  - Handle CORS failures gracefully

- [ ] **Add favicon display** for links
  - Data structure supports it
  - HTML generation includes it in some versions
  - Current yohoo.html doesn't show favicons

### Script Enhancements

- [ ] **Improve categorization accuracy**
  - Current: 37 uncategorized items out of 85
  - Add more keywords to CATEGORY_KEYWORDS
  - Consider ML-based categorization for Phase 3

- [ ] **Add subcategory detection in parse_bookmarks.py**
  - Currently only generate_html_v4.py handles subcategories
  - Move WORK_SUBCATEGORIES logic to parsing phase

- [ ] **Create refresh script** that combines all steps:
  ```bash
  # scripts/refresh_data.sh
  #!/bin/bash
  python scripts/parse_bookmarks.py input/bookmarks.html -o data/bookmarks.json
  python scripts/analyze_history.py --days 90 -o data/history.json
  python scripts/utils.py merge data/bookmarks.json data/history.json -o data/merged.json
  python scripts/generate_html.py -b data/merged.json -o yohoo.html
  ```

- [ ] **Add progress indicators** for long-running operations (>30 seconds)

### Data Quality

- [ ] **Create categorize.csv workflow**
  - File exists but appears unused
  - Document intended usage or remove

- [ ] **Implement deduplication** in bookmark parsing
  - Remove exact URL duplicates
  - Handle URL variants (http vs https, trailing slash)

- [ ] **Add bookmark validation**
  - Check for dead links
  - Flag links that return 404

---

## 🟢 P3 - Low (Nice-to-Have)

### UI Enhancements

- [ ] **Add dark/light mode toggle**
  - Store preference in localStorage
  - Add CSS variables for easy theming

- [ ] **Add custom theme support**
  - Allow users to customize colors
  - Preset theme options

- [ ] **Add weather widget**
  - Optional widget in header
  - Use free weather API

- [ ] **Add quick notes widget**
  - Small notepad area
  - Persist in localStorage

- [ ] **Add keyboard navigation**
  - Arrow keys to navigate between sections
  - Enter to open first link in section

### Script Enhancements

- [ ] **Add Firefox history support**
  - Firefox stores history in places.sqlite
  - Create parser similar to Chrome

- [ ] **Add Safari history support**
  - Safari history in History.db
  - macOS only

- [ ] **Add Edge history support**
  - Same format as Chrome (Chromium-based)
  - Just need different path detection

- [ ] **Create import/export functionality**
  - Export all settings and links to JSON
  - Import from JSON backup

### Testing

- [ ] **Add unit tests for parse_bookmarks.py**
  - Test HTML parsing
  - Test categorization
  - Test age filtering

- [ ] **Add unit tests for analyze_history.py**
  - Test scoring algorithm
  - Test URL filtering

- [ ] **Add integration tests**
  - Test end-to-end workflow
  - Test with sample data

### Documentation

- [ ] **Create user guide**
  - How to set as browser home page
  - How to export bookmarks
  - How to customize categories

- [ ] **Add JSDoc comments** to yohoo.js functions

- [ ] **Create architecture diagram**
  - Visual representation of data flow
  - Component relationships

---

## Completed Tasks ✅

- [x] Create initial HTML start page with dark theme
- [x] Implement search functionality with "/" shortcut
- [x] Implement drag-and-drop for links
- [x] Implement drag-and-drop for sections
- [x] Implement delete/undelete (trash) functionality
- [x] Implement localStorage persistence
- [x] Create bookmark parser script
- [x] Create Chrome history analyzer
- [x] Create utility functions (merge, export)
- [x] Create HTML generator script
- [x] Add debug panel
- [x] Create SPECIFICATIONS.md
- [x] Create TODO.md

---

## Technical Debt

### Issues to Address

1. **Multiple HTML generator versions**
   - 4 versions exist (v1, v2, v3, v4)
   - Creates confusion about which is canonical
   - Solution: Consolidate to single version

2. **Inconsistent category terminology**
   - Design doc: "categories" with "subcategories"
   - yohoo.html: flat "subcategories" only
   - generate_html_v4.py: nested "categories" > "subcategories"
   - Solution: Standardize on single approach

3. **Hardcoded work subcategories**
   - WORK_SUBCATEGORIES only in generate_html_v4.py
   - Not configurable via JSON/config file
   - Solution: Move to external config

4. **test_v3.html in project root**
   - Appears to be a test file
   - Should be moved to tests/ or removed

5. **JavaScript embedded vs external**
   - generate_html_v4.py embeds JS in HTML
   - yohoo.html references external yohoo.js
   - Solution: Choose one approach (recommend external)

---

## Next Sprint Recommendations

For immediate improvement, focus on:

1. **Create Makefile** (P0) - 15 minutes
2. **Create .gitignore** (P0) - 5 minutes
3. **Fix duplicate links** (P1) - 30 minutes
4. **Consolidate generate_html versions** (P1) - 30 minutes
5. **Add logging to scripts** (P1) - 1 hour

**Estimated time for P0+P1**: ~3-4 hours

---

## Notes from Code Review

### What's Working Well
- Clean, modern UI with good visual design
- Drag-and-drop implementation is smooth
- localStorage persistence works correctly
- Search functionality is responsive
- Python scripts are well-structured with CLI interfaces

### Areas for Improvement
- Project structure doesn't follow global rules
- Multiple versions of same functionality create confusion
- Data quality issues (duplicates, empty titles)
- Missing tests and logging
- Inconsistency between manual HTML and generated HTML

### Recommendations
1. Decide on one canonical approach (manual HTML vs generated)
2. If generated: improve generator to match current yohoo.html quality
3. If manual: document the update workflow for adding links
4. Add automated validation before regenerating HTML

---

**End of TODO List**
