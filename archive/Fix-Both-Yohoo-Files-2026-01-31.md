# Fix Plan: Both Yohoo.html Files Need Drag-Drop Fix - 2026-01-31

## Situation Analysis

There are **TWO COMPLETELY DIFFERENT** Yohoo applications:

### 1. Root yohoo.html (PUBLISHED - PRODUCTION)
**Location:** `/Users/eivind.throndsen@m10s.io/1-Projects/yohoo/yohoo.html`
**Status:** This is the published, production version
**Size:** 3544 lines, 122K
**Features:**
- More sophisticated application
- 3-column layout system
- Loads data from external `default-links.json`
- Has backup/export functionality
- Different sections ("Bob the Builder", "Department of AI", etc.)
- Storage key: `yohoo_v1_data`

**Bug Status:**
- ❌ **MISSING:** `.link-item > *` CSS fix for drag-and-drop
- ✅ **HAS:** `resetToDefaults()` function (async, loads from external JSON)
- ✅ **HAS:** Proper reset implementation

**CRITICAL:** Drag-and-drop will be BROKEN on Chrome/Windows!

---

### 2. Archive yohoo.html (GENERATED - DEVELOPMENT)
**Location:** `/Users/eivind.throndsen@m10s.io/1-Projects/yohoo/archive/yohoo.html`
**Status:** Generated version for testing/development
**Size:** 2547 lines, 127K
**Features:**
- Simpler standalone application
- Grid layout
- Embedded default data
- Norway-focused content
- Storage key: `yohoo-data-v2`

**Bug Status:**
- ✅ **HAS:** `.link-item > *` CSS fix for drag-and-drop
- ✅ **HAS:** Embedded `DEFAULT_DATA`
- ✅ **HAS:** `resetToDefaults()` function
- ✅ **ALL TESTS PASS**

---

## Required Fixes

### CRITICAL: Fix Root yohoo.html (PRODUCTION)

The published version needs the drag-and-drop CSS fix immediately!

**CSS Fix to Add:**
```css
/* Fix drag and drop on Chrome/Windows - child elements should not capture pointer events */
.link-item > * {
    pointer-events: none;
}

.link-item .delete-btn,
.link-item .edit-btn {
    pointer-events: auto;  /* Re-enable for button clicks */
}
```

**Where to add:** In the `<style>` section, after the `.link-item` rules (around line 409-475)

---

## Fix Implementation

### Step 1: Add CSS Fix to Root File

```bash
# Location to edit
code /Users/eivind.throndsen@m10s.io/1-Projects/yohoo/yohoo.html
```

Find this section (around line 471-475):
```css
.link-item:hover .delete-btn,
.link-item:hover .edit-btn {
    opacity: 1;
    pointer-events: auto;
}
```

Add AFTER it:
```css
/* Fix drag and drop on Chrome/Windows */
.link-item > * {
    pointer-events: none;
}

.link-item .delete-btn,
.link-item .edit-btn {
    pointer-events: auto;
}
```

### Step 2: Verify Reset Functionality

The root file already has a good `resetToDefaults()` implementation that:
1. Creates backup
2. Clears localStorage
3. Loads from external `default-links.json`
4. Re-renders

This is BETTER than the archive version - no changes needed.

### Step 3: Test Both Files

Test root yohoo.html:
```bash
open /Users/eivind.throndsen@m10s.io/1-Projects/yohoo/yohoo.html
```

Test archive yohoo.html:
```bash
open /Users/eivind.throndsen@m10s.io/1-Projects/yohoo/archive/yohoo.html
```

### Step 4: Update Tests

Tests currently point to archive/yohoo.html. We need tests for BOTH versions:

```python
# In tests/test_browser_functionality.py
PRODUCTION_HTML = Path(__file__).parent.parent.parent / 'yohoo.html'
ARCHIVE_HTML = Path(__file__).parent.parent / 'yohoo.html'

# Add tests for both
```

---

## Verification Checklist

### Root yohoo.html (PRODUCTION)
- [ ] Add `.link-item > * { pointer-events: none; }`
- [ ] Add `.link-item .delete-btn, .link-item .edit-btn { pointer-events: auto; }`
- [ ] Test drag-and-drop on Chrome/Windows
- [ ] Test reset to defaults
- [ ] Verify delete/edit buttons still clickable

### Archive yohoo.html (DEVELOPMENT)
- [x] Has `.link-item > * { pointer-events: none; }`
- [x] Has `DEFAULT_DATA` embedded
- [x] Has `resetToDefaults()` function
- [x] All unit tests pass
- [ ] Browser tests pass (need Playwright)

---

## Long-term Recommendations

### 1. Clarify Documentation

Update `archive/CLAUDE.md` to explain:
- Root yohoo.html = Production version (manual)
- Archive yohoo.html = Development version (generated)

### 2. Separate Test Suites

Create:
- `tests/test_production_yohoo.py` - Tests for root version
- `tests/test_archive_yohoo.py` - Tests for archive version

### 3. Pre-deployment Checklist

Before deploying root yohoo.html:
- [ ] Test drag-and-drop on Chrome/Windows
- [ ] Test drag-and-drop on Safari/Mac
- [ ] Test reset to defaults
- [ ] Test all buttons clickable
- [ ] Check console for errors

### 4. Version Control

Consider:
- Adding version numbers to each file
- Documenting which version is which
- Creating separate README files

---

## Immediate Action Required

**DO THIS NOW:**

1. Edit `/Users/eivind.throndsen@m10s.io/1-Projects/yohoo/yohoo.html`
2. Add the CSS fix after line 475
3. Save
4. Test drag-and-drop
5. Deploy

**CSS to add:**
```css
/* Fix drag and drop on Chrome/Windows - prevents child elements from capturing pointer events */
.link-item > * {
    pointer-events: none;
}

/* Re-enable pointer events for interactive buttons */
.link-item .delete-btn,
.link-item .edit-btn {
    pointer-events: auto;
}
```

---

## Files Needing Updates

1. `/Users/eivind.throndsen@m10s.io/1-Projects/yohoo/yohoo.html` - Add CSS fix
2. `/Users/eivind.throndsen@m10s.io/1-Projects/yohoo/archive/CLAUDE.md` - Document two versions
3. `/Users/eivind.throndsen@m10s.io/1-Projects/yohoo/archive/tests/test_browser_functionality.py` - Test both versions
4. Create `/Users/eivind.throndsen@m10s.io/1-Projects/yohoo/README.md` - Explain file structure

---

## Risk Assessment

**PRODUCTION RISK:** HIGH
- Drag-and-drop broken on Chrome/Windows until fix applied
- Users cannot move links between sections
- Fix is simple (5 lines of CSS) but critical

**TESTING RISK:** MEDIUM
- Current tests only cover archive version
- Production version untested
- Need browser tests for both

**DEPLOYMENT RISK:** LOW
- CSS fix is non-breaking
- Only affects pointer event handling
- Easy to roll back if issues
