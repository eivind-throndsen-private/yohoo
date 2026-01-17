# Testing Instructions for Default Links System

## Test 1: Fresh Page Load (First-Time User)

**Goal:** Verify that default-links.json is loaded on first page load.

**Steps:**
1. Open browser DevTools (F12 or Cmd+Option+I)
2. Go to Application tab → Local Storage
3. Delete all `yohoo_*` entries
4. Refresh the page (F5)
5. **Expected:** Page should load with 17 sections and ~100 Norwegian/International links
6. Check Console for: "Loaded defaults from default-links.json"

**Verification:**
- Sections visible: Norwegian Essentials, Transport & Travel, Norwegian News, etc.
- Links include: Yr, Finn.no, Entur, NRK, etc.
- No errors in console

---

## Test 2: Reset to Defaults

**Goal:** Verify reset functionality creates backup and reloads defaults.

**Steps:**
1. Make some changes (add a link, delete a section, etc.)
2. Open Settings (⚙️ button)
3. Scroll to "Data Management" section
4. Click "🔄 Reset to Defaults"
5. Confirm the dialog
6. **Expected:**
   - Automatic backup downloads: `yohoo-backup-before-reset-YYYY-MM-DD-HHMMSS.json`
   - Page reloads with default configuration
   - Success alert appears

**Verification:**
- Backup file downloaded
- All custom changes reverted
- Links match default-links.json

---

## Test 3: Save Current as Default Template

**Goal:** Verify exporting current state as default template.

**Steps:**
1. Customize your links (add/remove/reorder)
2. Open Settings
3. Scroll to "Data Management"
4. Click "💾 Save Current as Default Template"
5. **Expected:**
   - File downloads with exact name: `default-links.json`
   - Alert with instructions appears

**Verification:**
- File named exactly `default-links.json` (not with timestamp)
- File contains your current sections and links
- trash array is empty (even if you had items in trash)

**To apply as new defaults:**
1. Save the downloaded file
2. Replace the existing `default-links.json` in your project folder
3. Clear localStorage and refresh (Test 1) to verify new defaults load

---

## Test 4: Fallback to Hardcoded Defaults

**Goal:** Verify graceful degradation when default-links.json is missing.

**Steps:**
1. Rename `default-links.json` to `default-links.json.backup`
2. Clear localStorage (Application tab → Local Storage → Delete all)
3. Refresh page
4. **Expected:**
   - Console error: "Failed to load default-links.json"
   - Console log: "Falling back to hardcoded defaults"
   - Page loads with minimal example links (ChatGPT, GitHub, Jira, YouTube)

**Verification:**
- No crashes or blank page
- Example links visible
- App fully functional

**Cleanup:**
- Rename `default-links.json.backup` back to `default-links.json`

---

## Test 5: Existing Drag-and-Drop Functionality

**Goal:** Verify all drag-and-drop still works perfectly.

**Steps:**
1. Load page with defaults
2. Test dragging links:
   - Within a section (reorder)
   - Between sections
   - To a different column
3. Test dragging sections:
   - Within a column (reorder)
   - Between columns
4. Refresh page
5. **Expected:** All changes persist

**Verification:**
- Smooth drag behavior
- Drop zones highlight correctly
- Changes saved to localStorage
- No console errors

---

## Test 6: Settings Modal Integration

**Goal:** Verify new buttons work correctly in settings.

**Steps:**
1. Open Settings (⚙️)
2. **Expected UI changes:**
   - "Export & Import" section still present
   - NEW: "Reset to Defaults" section below it
   - NEW: "Save as Default Template" section below that
3. All buttons should be clickable and functional

**Verification:**
- Settings modal looks clean and organized
- No layout issues
- All buttons respond on click

---

## Quick Console Commands for Testing

Open browser console and run these to help with testing:

```javascript
// Clear localStorage completely
localStorage.clear();
location.reload();

// Check what's in localStorage
Object.keys(localStorage).filter(k => k.startsWith('yohoo')).forEach(k => {
    console.log(k, localStorage.getItem(k).length, 'chars');
});

// View current appState
console.log(JSON.parse(localStorage.getItem('yohoo_v1_data')));

// View sections count
const state = JSON.parse(localStorage.getItem('yohoo_v1_data'));
console.log('Sections:', state.sections.length);
console.log('Total links:', state.sections.reduce((sum, s) => sum + s.links.length, 0));
```

---

## Known Issues to Watch For

- **CORS errors:** If testing via `file://` protocol, fetch may fail. Use local server or `open` command.
- **Async timing:** First load may take a moment to fetch default-links.json
- **Browser cache:** Hard refresh (Cmd+Shift+R) if changes don't appear

---

## Success Criteria

✅ All tests pass without errors
✅ Default links system works in fresh state
✅ Reset functionality preserves data via backup
✅ Save as template exports correctly
✅ Fallback works when default-links.json missing
✅ No changes to existing drag-and-drop behavior
✅ Settings UI clean and functional
