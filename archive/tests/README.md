# Yohoo Test Suite

Comprehensive automated tests to ensure drag-and-drop and reset functionality never breaks.

## Quick Start

```bash
# Install dependencies (first time only)
make -C archive install

# Install Playwright browsers for browser tests (first time only)
make -C archive install-browsers

# Run all tests
make -C archive test

# Run only fast unit tests (no browser required)
make -C archive test-unit

# Run only browser tests
make -C archive test-browser

# Run only regression tests (for drag-drop and reset bugs)
make -C archive test-regression
```

---

## Test Files

### 1. `test_drag_drop_reset.py` - Unit Tests
**Purpose:** Test HTML generation correctness
**Speed:** Fast (~1-2 seconds)
**Requirements:** Python, pytest

**What it tests:**
- ✅ CSS fix for drag-and-drop is present (`pointer-events: none`)
- ✅ `DEFAULT_DATA` constant is embedded in HTML
- ✅ `resetToDefaults()` function exists and is complete
- ✅ Reset button calls `resetToDefaults()` (not `location.reload()`)
- ✅ All draggable links have required attributes
- ✅ All drag handlers are defined
- ✅ Embedded data matches source `default_links.json`
- ✅ Delete icons have onclick handlers

**Test classes:**
- `TestHTMLGeneration` - Verify generated HTML structure
- `TestDefaultLinksData` - Verify default_links.json integrity
- `TestRegressionPrevention` - Catch the specific bugs if they return

**Run individually:**
```bash
cd archive
. .venv/bin/activate
pytest tests/test_drag_drop_reset.py -v
```

---

### 2. `test_browser_functionality.py` - Browser Tests
**Purpose:** Test actual drag-and-drop and reset behavior in real browsers
**Speed:** Slower (~10-30 seconds)
**Requirements:** Python, pytest, playwright, chromium browser

**What it tests:**
- ✅ Links can be dragged between sections
- ✅ Sections can be reordered via drag-and-drop
- ✅ Drag operations persist in localStorage
- ✅ Reset button restores exact default state
- ✅ Reset clears all customizations (moved links, custom sections, deleted links)
- ✅ Reset clears trash
- ✅ Reset restores font size to 100%
- ✅ Links can be dragged even when grabbing text span (Chrome/Windows bug)
- ✅ Delete icons remain clickable despite pointer-events fix

**Test classes:**
- `TestDragAndDrop` - Drag-and-drop functionality
- `TestResetFunctionality` - Reset to defaults functionality
- `TestRegressionDetection` - Browser-level regression tests

**Run individually:**
```bash
cd archive
. .venv/bin/activate
pytest tests/test_browser_functionality.py -v --headed
```

**Options:**
- `--headed` - Show browser window during tests (useful for debugging)
- `--browser chromium` - Specify browser (chromium, firefox, webkit)
- `-s` - Show print output

---

## Regression Tests

Special tests designed to catch the exact bugs we fixed:

### Bug 1: Drag-and-Drop Broken on Chrome/Windows
**Root cause:** Child elements captured pointer events
**Test:** `test_link_children_have_pointer_events_none()`
**Checks:** `.link-item > *` has `pointer-events: none`
**Location:** `test_drag_drop_reset.py::TestRegressionPrevention`

### Bug 2: Reset Doesn't Restore Defaults
**Root cause:** Reset used `location.reload()` instead of rebuilding from data
**Test:** `test_no_location_reload_in_reset()`
**Checks:** Reset button calls `resetToDefaults()`, NOT `location.reload()`
**Location:** `test_drag_drop_reset.py::TestRegressionPrevention`

**Run regression tests only:**
```bash
make -C archive test-regression
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Yohoo

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd archive
          python -m venv .venv
          . .venv/bin/activate
          pip install -r requirements.txt

      - name: Install Playwright browsers
        run: |
          cd archive
          . .venv/bin/activate
          playwright install --with-deps chromium

      - name: Run unit tests
        run: |
          cd archive
          . .venv/bin/activate
          pytest tests/test_drag_drop_reset.py -v

      - name: Run browser tests
        run: |
          cd archive
          . .venv/bin/activate
          pytest tests/test_browser_functionality.py -v

      - name: Run regression tests
        run: |
          cd archive
          . .venv/bin/activate
          pytest tests/test_drag_drop_reset.py::TestRegressionPrevention -v
          pytest tests/test_browser_functionality.py::TestRegressionDetection -v
```

---

## Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "Running regression tests before commit..."

cd archive

# Activate virtual environment
. .venv/bin/activate

# Run fast unit tests
pytest tests/test_drag_drop_reset.py::TestRegressionPrevention -v

if [ $? -ne 0 ]; then
    echo "❌ Regression tests failed! Commit aborted."
    echo "The drag-drop or reset bugs may have been reintroduced."
    exit 1
fi

echo "✅ Regression tests passed!"
exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Test Coverage

### What IS tested:
- ✅ HTML generation correctness
- ✅ CSS fixes present in output
- ✅ JavaScript functions exist and are wired correctly
- ✅ Drag-and-drop works in browser
- ✅ Reset restores exact defaults
- ✅ LocalStorage persistence
- ✅ Cross-browser compatibility (Chromium, Firefox, WebKit)

### What is NOT tested:
- ❌ Mobile touch-based drag-and-drop
- ❌ Accessibility features (keyboard navigation)
- ❌ Performance/load testing
- ❌ Edge cases with malformed data

---

## Troubleshooting

### "playwright not found"
```bash
cd archive
. .venv/bin/activate
pip install pytest-playwright playwright
playwright install chromium
```

### Browser tests fail with "Browser not found"
```bash
make -C archive install-browsers
```

### Tests pass but drag-and-drop still doesn't work
1. Check which browser you're using (tests run on Chromium by default)
2. Clear browser cache
3. Hard refresh (Cmd+Shift+R or Ctrl+Shift+F5)
4. Check browser console for JavaScript errors

### "No such file: yohoo.html"
```bash
make -C archive generate
```

---

## Adding New Tests

### Unit Test Template
```python
def test_new_feature(self, generated_html):
    """Test that new feature is in generated HTML"""
    assert 'expected-string' in generated_html, \
        "New feature not found in HTML"
```

### Browser Test Template
```python
def test_new_browser_feature(self, page_with_yohoo: Page):
    """Test new browser feature"""
    page = page_with_yohoo

    # Interact with page
    button = page.locator('#myButton')
    button.click()

    # Assert result
    result = page.locator('#result').inner_text()
    assert result == 'expected', f"Got {result}"
```

---

## Test Maintenance

### When to update tests:

1. **Adding new features:** Add corresponding tests
2. **Changing HTML structure:** Update selectors in browser tests
3. **Modifying default_links.json:** Unit tests will auto-detect mismatches
4. **Changing CSS:** Update CSS verification tests

### Red flags (failing tests indicate bugs):

- ❌ `test_no_location_reload_in_reset` fails → Reset bug has returned!
- ❌ `test_link_children_have_pointer_events_none` fails → Drag-drop bug has returned!
- ❌ `test_reset_restores_defaults` fails → Reset doesn't work correctly
- ❌ `test_drag_link_between_sections` fails → Drag-and-drop broken

---

## Performance

**Unit tests:** ~1-2 seconds (run these often)
**Browser tests:** ~10-30 seconds (run before commits)
**Full test suite:** ~30-45 seconds

**Optimization tips:**
- Run unit tests during development
- Run browser tests before commits
- Run full suite in CI/CD pipeline

---

## Related Documentation

- `archive/Bug-Fixes-Summary-2026-01-31.md` - Details of the bugs we're preventing
- `archive/Drag-Drop-Reset-Issues-Analysis-2026-01-31.md` - Technical analysis
- `archive/CLAUDE.md` - Project overview and architecture

---

## Support

If tests fail unexpectedly:

1. Check `archive/yohoo.html` exists (run `make -C archive generate`)
2. Verify Python environment (run `make -C archive install`)
3. Ensure Playwright browsers installed (run `make -C archive install-browsers`)
4. Check for JavaScript errors in browser console
5. Review recent changes to `generate_html.py`

**When in doubt, run:**
```bash
make -C archive clean
make -C archive install
make -C archive install-browsers
make -C archive generate
make -C archive test
```
