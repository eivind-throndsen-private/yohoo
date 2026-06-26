# Test Plan for Both Yohoo Files - 2026-01-31

## Summary of Fixes Applied

### ✅ PRODUCTION FILE (Root yohoo.html)
**File:** `/Users/eivind.throndsen@m10s.io/1-Projects/yohoo/yohoo.html`
**Fix Applied:** Drag-and-drop CSS fix
**Status:** Ready for testing

**Changes:**
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

**Reset Functionality:** Already working correctly (loads from external default-links.json)

---

### ✅ ARCHIVE FILE (archive/yohoo.html)
**File:** `/Users/eivind.throndsen@m10s.io/1-Projects/yohoo/archive/yohoo.html`
**Fixes Applied:** Both drag-and-drop CSS fix AND reset functionality fix
**Status:** Ready for testing, all unit tests pass

---

## Testing Instructions

### Test 1: Production File - Drag and Drop (Chrome/Windows)

**File:** Root yohoo.html (now open in your browser)

1. **Test link dragging:**
   - Try to drag a link from one section to another
   - Try grabbing the link by the text (not just the edges)
   - Try grabbing the link by the icon/button area
   - Verify the link moves smoothly

2. **Test section dragging:**
   - Try to drag entire sections to reorder them
   - Verify sections reorder correctly

3. **Test button functionality:**
   - Hover over links to see delete/edit buttons
   - Click delete button - verify it works
   - Click edit button - verify it works
   - These should NOT interfere with dragging

**Expected Result:**
- ✅ Links drag smoothly from any grab point
- ✅ Sections can be reordered
- ✅ Delete/edit buttons remain clickable

---

### Test 2: Production File - Reset to Defaults

1. **Make changes:**
   - Add some links
   - Move sections around
   - Delete some links
   - Change settings

2. **Test reset:**
   - Click Settings (⚙ icon)
   - Find "Reset to Defaults" button
   - Click it
   - Confirm the dialog

3. **Verify:**
   - Should create automatic backup file download
   - Should restore original default sections
   - Should restore original layout
   - Should clear all customizations

**Expected Result:**
- ✅ Backup file downloads automatically
- ✅ Page returns to exact default state
- ✅ All custom changes removed

---

### Test 3: Archive File - Drag and Drop

**File:** archive/yohoo.html

```bash
open /Users/eivind.throndsen@m10s.io/1-Projects/yohoo/archive/yohoo.html
```

1. **Test link dragging:**
   - Drag links between sections
   - Verify they move correctly
   - Refresh page - verify positions persist

2. **Test section dragging:**
   - Drag sections to reorder
   - Verify order persists after refresh

**Expected Result:**
- ✅ All drag operations work smoothly
- ✅ Changes persist in localStorage

---

### Test 4: Archive File - Reset to Defaults

1. **Make changes:**
   - Move links around
   - Create custom sections (click "+ Section")
   - Delete some links
   - Change font size

2. **Test reset:**
   - Click Settings (⚙)
   - Click "Reset" button
   - Confirm

3. **Verify:**
   - All 17 default sections restored
   - All 100 default links present
   - All 5 user sections empty
   - Font size back to 100%
   - Trash cleared

**Expected Result:**
- ✅ Exact original state restored
- ✅ No reload, just DOM rebuild
- ✅ All customizations removed

---

## Automated Tests

### Run Unit Tests (Fast)

```bash
cd archive
. .venv/bin/activate
pytest tests/test_drag_drop_reset.py -v
```

**Expected:** All 16 tests pass ✅

---

### Run Browser Tests (Requires Playwright)

**First time setup:**
```bash
cd archive
make install-browsers
```

**Run tests:**
```bash
cd archive
. .venv/bin/activate
pytest tests/test_browser_functionality.py -v --headed
```

**Note:** Currently tests only the archive version. Production version needs manual testing.

---

## Regression Tests

These specifically check for the bugs we fixed:

```bash
cd archive
. .venv/bin/activate
pytest tests/test_drag_drop_reset.py::TestRegressionPrevention -v
```

**What they check:**
- ✅ `.link-item > *` has `pointer-events: none`
- ✅ Reset button calls `resetToDefaults()` not `location.reload()`

---

## Browser Compatibility Testing

### Priority 1: Chrome on Windows
**Why:** This is where the bug was reported
**Test:** Drag links and sections, verify smooth operation

### Priority 2: Chrome on Mac
**Test:** Same as Windows

### Priority 3: Safari on Mac
**Test:** Drag and drop should also work

### Priority 4: Firefox
**Test:** Cross-browser verification

---

## Known Differences Between Files

### Production (root yohoo.html)
- 3-column layout
- External default-links.json
- More sophisticated features (backup, export)
- Different default sections
- Storage key: `yohoo_v1_data`

### Archive (archive/yohoo.html)
- Grid layout
- Embedded default data
- Simpler feature set
- Norway-focused content
- Storage key: `yohoo-data-v2`

**Both versions now have the drag-and-drop fix! ✅**

---

## If Tests Fail

### Drag and drop doesn't work:
1. Check browser console for errors
2. Verify CSS fix is present: Search for `.link-item > *`
3. Clear browser cache (Cmd+Shift+R or Ctrl+Shift+F5)
4. Try incognito/private mode

### Reset doesn't work (archive):
1. Check console for errors
2. Verify `DEFAULT_DATA` constant exists
3. Verify `resetToDefaults()` function exists
4. Check localStorage is allowed

### Reset doesn't work (production):
1. Verify `default-links.json` file exists in same directory
2. Check network tab for 404 errors
3. Verify `loadDefaultLinks()` function works

### Buttons not clickable:
1. Verify buttons have `pointer-events: auto`
2. Check for CSS conflicts
3. Test hover state works

---

## Success Criteria

### Production File ✅ When:
- [ ] Drag and drop works on Chrome/Windows
- [ ] Drag and drop works on Chrome/Mac
- [ ] Drag and drop works on Safari/Mac
- [ ] Delete/edit buttons still clickable
- [ ] Reset to defaults works (creates backup, restores state)

### Archive File ✅ When:
- [x] All 16 unit tests pass
- [ ] Browser tests pass (if Playwright installed)
- [ ] Drag and drop works in browser
- [ ] Reset completely restores defaults
- [ ] No console errors

---

## Documentation Created

1. `archive/tests/README.md` - Complete test suite documentation
2. `archive/tests/test_drag_drop_reset.py` - Unit tests (16 tests)
3. `archive/tests/test_browser_functionality.py` - Browser tests
4. `archive/Bug-Fixes-Summary-2026-01-31.md` - Detailed bug analysis
5. `archive/Drag-Drop-Reset-Issues-Analysis-2026-01-31.md` - Technical analysis
6. `Fix-Both-Yohoo-Files-2026-01-31.md` - Fix plan
7. `CRITICAL-Dual-File-Issue-2026-01-31.md` - Dual file situation
8. **This file** - Test plan

---

## Next Steps

1. **Test production file** (currently open in browser)
2. **Test archive file** (`open archive/yohoo.html`)
3. **Run automated tests** (`make -C archive test-unit`)
4. **If all pass:** Deploy production file
5. **If failures:** Check troubleshooting section above

---

## Contact

If tests fail or issues arise:
- Check `archive/tests/README.md` for troubleshooting
- Review console errors in browser
- Verify file paths are correct
- Ensure localStorage is enabled
