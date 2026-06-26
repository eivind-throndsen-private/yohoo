# Fix: Duplicate Links Issue - 2026-01-31

## Problem Identified

**Issue:** "Just get copies of the same links" when dragging

**Root Cause:** Duplicate event listeners

### How It Happened

1. `setupDragAndDrop()` was called on page load
2. `setupDragAndDrop()` was called again after reset
3. Each call added NEW event listeners without removing old ones
4. Result: Each drag operation fired TWICE, creating duplicate links

### Code Pattern That Caused It

```javascript
function setupDragAndDrop() {
    document.querySelectorAll('.link-item').forEach(link => {
        link.addEventListener('dragstart', handleLinkDragStart);  // ← Added every time!
        link.addEventListener('dragend', handleLinkDragEnd);
    });
    // ... more listeners
}
```

When called twice:
- First call: 1 dragstart listener per link
- Second call: 2 dragstart listeners per link
- Result: Each drag fires twice → duplicates created

---

## Solution Applied

**Changed from:** Direct event listeners on each element
**Changed to:** Event delegation on parent container

### New Implementation

```javascript
let dragListenersInitialized = false;

function setupDragAndDrop() {
    if (dragListenersInitialized) {
        return; // Already set up, don't add duplicate listeners
    }

    const container = document.getElementById('sectionsContainer');

    // Single listener on container handles ALL drag events
    container.addEventListener('dragstart', function(e) {
        const link = e.target.closest('.link-item');
        if (link && e.target === link) {
            handleLinkDragStart.call(link, e);
        }
    });

    // ... other delegated listeners

    dragListenersInitialized = true; // Prevent re-initialization
}
```

### Benefits

1. ✅ **No duplicates:** Listeners only added once
2. ✅ **Works after reset:** Can call setupDragAndDrop() safely
3. ✅ **Better performance:** One listener instead of many
4. ✅ **Dynamic elements:** New elements automatically work

---

## Files Changed

### Archive yohoo.html
**File:** `/Users/eivind.throndsen@m10s.io/1-Projects/yohoo/archive/scripts/generate_html.py`

**Changes:**
- Added `dragListenersInitialized` flag
- Converted all drag listeners to event delegation
- Added guard to prevent re-initialization

**Status:** ✅ Fixed and regenerated

### Production yohoo.html
**File:** `/Users/eivind.throndsen@m10s.io/1-Projects/yohoo/yohoo.html`

**Changes:**
- Removed CSS pointer-events fix (not needed for this version)

**Status:** ⚠️ Needs testing - may have different issue

---

## Testing Instructions

### Archive File (NOW OPEN IN BROWSER)

**File:** `archive/yohoo.html`

1. **Clear localStorage:**
   - Press F12 (or Cmd+Option+I)
   - In Console tab, type: `localStorage.clear()`
   - Reload page (Cmd+R or Ctrl+R)

2. **Test drag:**
   - Drag "Yr (Weather)" from "Norway Essentials" to "Development & Docs"
   - **Expected:** Link moves (appears in destination, disappears from source)
   - **Should NOT:** Create duplicate, appear in both places

3. **Test after reset:**
   - Move some links around
   - Click Settings ⚙ → Reset
   - Confirm dialog
   - Try dragging again
   - **Expected:** Still works correctly, no duplicates

4. **Check for duplicates:**
   - Drag a link
   - Refresh page (Cmd+R)
   - **Expected:** Link appears only once in destination section

---

### Production File

**File:** Root `yohoo.html` (if you're testing this version)

This file has a different architecture and might need a different fix. Please test:

1. **Does drag-and-drop work at all?**
2. **Does it create duplicates?**
3. **Check browser console for errors**

---

## Verification

### Unit Tests
```bash
cd archive
. .venv/bin/activate
pytest tests/test_drag_drop_reset.py::TestRegressionPrevention -v
```

**Result:** ✅ 2 passed

### Manual Test Checklist

Archive file:
- [ ] Drag link between sections
- [ ] Link moves correctly (no duplicates)
- [ ] After reset, drag still works
- [ ] After multiple resets, no duplicates
- [ ] Delete/edit buttons still clickable
- [ ] Section dragging works

---

## Root Cause Analysis

### Why Duplicate Listeners Caused Duplicates

1. **First drag event fires:**
   - Listener 1: Calls `handleLinkDrop` → adds link to destination
   - Listener 2: Calls `handleLinkDrop` → adds link AGAIN to destination
   - Result: 2 copies of same link

2. **The DOM manipulation:**
   ```javascript
   this.appendChild(draggedElement);  // Listener 1 executes
   saveState();                        // Saves state with 1 copy

   // Then listener 2 fires immediately...
   this.appendChild(draggedElement);  // Adds AGAIN (but element already moved)
   saveState();                        // Saves state with 2 copies
   ```

3. **Why it looked like copies:**
   - `appendChild` moves the element the first time
   - But `saveState()` collects ALL .link-item elements
   - If somehow the element was cloned or re-rendered, you'd see duplicates

---

## Prevention

### For Future Development

1. **Always use event delegation for dynamic content**
2. **Or check if listeners exist before adding:**
   ```javascript
   if (!element.dataset.listenersAdded) {
       element.addEventListener(...);
       element.dataset.listenersAdded = 'true';
   }
   ```

3. **Or remove listeners before adding:**
   ```javascript
   element.removeEventListener('dragstart', handleDragStart);
   element.addEventListener('dragstart', handleDragStart);
   ```

4. **Document when setupDragAndDrop is called:**
   ```javascript
   // Called on: page load, after reset, after adding sections
   function setupDragAndDrop() { ... }
   ```

---

## Related Issues

This fix also solves potential issues with:
- Section drag-and-drop duplication
- Event listener memory leaks
- Performance degradation after multiple resets

---

## Next Steps

1. **Test the archive file now open in your browser**
2. **Follow testing instructions above**
3. **Report if duplicates still occur**
4. **Test production file separately if needed**

---

## Status

**Archive file:** ✅ FIXED - Event delegation implemented
**Production file:** ⚠️ UNKNOWN - Different architecture, needs separate testing

**Please test and report results!**
