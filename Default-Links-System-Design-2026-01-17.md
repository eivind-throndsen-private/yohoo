# Default Links System Design

**Date:** 2026-01-17
**Author:** Eivind Throndsen with Claude Code
**Purpose:** Enable customizable default links that can be updated without code changes

---

## 1. Overview

This design adds a configurable default links system to Yohoo that allows:
- Loading initial links from an external JSON file (`default-links.json`)
- Resetting to defaults at any time
- Updating the default link set by exporting and replacing the defaults file
- Zero code changes required to update the default links

**Critical Constraint:** All existing drag-and-drop and display logic MUST remain unchanged.

---

## 2. Current State Analysis

### 2.1 Current Default Links Behavior
**Location:** `yohoo.html` lines 897-909

```javascript
const defaultLinks = [
    { id: 'l1', title: 'Google', url: 'https://google.com', sectionId: 'productivity', date: Date.now() },
    { id: 'l2', title: 'GitHub', url: 'https://github.com', sectionId: 'development', date: Date.now() },
    { id: 'l3', title: 'Jira', url: 'https://jira.atlassian.com', sectionId: 'bob', date: Date.now() },
    { id: 'l4', title: 'YouTube', url: 'https://youtube.com', sectionId: 'media', date: Date.now() },
];

let appState = {
    sections: JSON.parse(JSON.stringify(defaultSections)),
    trash: [],
    layout: null
};
```

**Current initialization flow:**
1. Page loads
2. `loadState()` checks `localStorage.getItem(STORAGE_KEY)`
3. If found → load from localStorage
4. If NOT found → use hardcoded `appState` with `defaultSections` and `defaultLinks`

### 2.2 Export/Import Format
**Location:** `yohoo.html` lines 988-1009

Export format structure:
```json
{
  "version": "1.0.0",
  "exportDate": "2026-01-17T...",
  "exportedBy": "Yohoo Export Feature",
  "data": {
    "sections": [...],
    "trash": [],
    "layout": { "columns": [...] },
    "fontScale": 2.0
  },
  "metadata": {
    "sectionCount": 15,
    "linkCount": 120,
    "trashCount": 0,
    "columns": 4
  }
}
```

### 2.3 Backup Links Data Structure
**File:** `backup-links-2026-01-17.json`

Current structure (NOT compatible with export format):
```json
{
  "backup_date": "2026-01-17",
  "description": "Backup of yohoo.html links...",
  "links": [
    {"section": "Norwegian Essentials", "title": "Yr (Weather)", "url": "https://www.yr.no/en", "domain": "yr.no"},
    ...
  ]
}
```

**Problem:** This is a flat list with section names, not the nested structure used by Yohoo's appState.

---

## 3. Proposed Solution

### 3.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Page Load / Reset                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
           ┌─────────────────────┐
           │ localStorage empty? │
           └─────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         │ YES                   │ NO
         ▼                       ▼
   ┌──────────────┐      ┌─────────────────┐
   │ Fetch        │      │ Load from       │
   │ default-     │      │ localStorage    │
   │ links.json   │      └─────────────────┘
   └──────┬───────┘
          │
          ▼
   ┌──────────────────┐
   │ Transform to     │
   │ appState format  │
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ Render page      │
   └──────────────────┘
```

### 3.2 File Structure Changes

**New file:** `default-links.json`
- Same origin as `yohoo.html` (works locally and on GitHub Pages)
- Uses standard Yohoo export format
- Serves as the "factory defaults"

### 3.3 Code Changes Required

#### Change 1: Create `default-links.json`
Transform `backup-links-2026-01-17.json` into proper export format:
1. Group links by section
2. Generate section objects with IDs, titles, icons
3. Assign link IDs
4. Create layout structure
5. Wrap in export format envelope

#### Change 2: Modify `loadState()` function
**Location:** `yohoo.html` line 945

**Current:**
```javascript
function loadState() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
        appState = JSON.parse(stored);
        // Ensure layout exists (backwards compatibility)
        if (!appState.layout) {
            appState.layout = getDefaultLayout();
        }
    } else {
        // Uses hardcoded defaultSections
        appState.sections.forEach(section => {
            const sectionLinks = defaultLinks.filter(link => link.sectionId === section.id);
            section.links = sectionLinks;
        });
        appState.layout = getDefaultLayout();
        saveState();
    }
}
```

**Proposed:**
```javascript
async function loadState() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
        appState = JSON.parse(stored);
        if (!appState.layout) {
            appState.layout = getDefaultLayout();
        }
    } else {
        // Load from external default-links.json
        await loadDefaultLinks();
    }
}

async function loadDefaultLinks() {
    try {
        const response = await fetch('./default-links.json');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const defaultData = await response.json();

        // Validate and apply
        const validation = validateImportData(defaultData);
        if (validation.valid) {
            appState.sections = JSON.parse(JSON.stringify(defaultData.data.sections));
            appState.trash = defaultData.data.trash || [];
            appState.layout = defaultData.data.layout || getDefaultLayout();

            // Apply font scale if present
            if (defaultData.data.fontScale) {
                saveFontScale(defaultData.data.fontScale.toString());
                loadFontScale();
            }

            saveState();
            debugLog('Loaded default links from default-links.json');
        } else {
            throw new Error('Invalid default-links.json format: ' + validation.errors.join(', '));
        }
    } catch (error) {
        console.error('Failed to load default-links.json:', error);
        // Fallback to hardcoded defaults
        loadHardcodedDefaults();
    }
}

function loadHardcodedDefaults() {
    // Keep current hardcoded defaults as ultimate fallback
    appState.sections.forEach(section => {
        const sectionLinks = defaultLinks.filter(link => link.sectionId === section.id);
        section.links = sectionLinks;
    });
    appState.layout = getDefaultLayout();
    saveState();
    debugLog('Loaded hardcoded fallback defaults');
}
```

#### Change 3: Add "Reset to Defaults" button
**Location:** Settings Modal → Data Management section

**HTML Addition:**
```html
<!-- After Export/Import control -->
<div class="settings-control">
    <label class="settings-control-label">
        Reset to Defaults
    </label>
    <div class="settings-control-description">
        Reset all links, sections, and layout to the default configuration from default-links.json.
        Your current data will be automatically backed up before resetting.
    </div>
    <button id="resetToDefaultsBtn" class="secondary-btn" title="Reset to default links">
        🔄 Reset to Defaults
    </button>
</div>
```

**JavaScript Handler:**
```javascript
async function resetToDefaults() {
    const confirmed = confirm(
        '🚨 RESET TO DEFAULTS\n\n' +
        'This will replace all your current sections, links, and layout with the default configuration.\n\n' +
        '✅ Your current data will be automatically backed up before resetting.\n\n' +
        'Continue with reset?'
    );

    if (!confirmed) {
        debugLog('Reset to defaults cancelled by user');
        return;
    }

    // Create automatic backup
    const backupData = {
        version: '1.0.0',
        exportDate: new Date().toISOString(),
        exportedBy: 'Yohoo Auto-Backup (Before Reset)',
        data: {
            sections: JSON.parse(JSON.stringify(appState.sections)),
            trash: JSON.parse(JSON.stringify(appState.trash)),
            layout: JSON.parse(JSON.stringify(appState.layout)),
            fontScale: parseFloat(localStorage.getItem('yohoo_font_scale') || '2.0')
        }
    };

    // Download backup
    const dataStr = JSON.stringify(backupData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const timestamp = new Date().toISOString().replace(/:/g, '-').replace(/\..+/, '');
    const link = document.createElement('a');
    link.href = url;
    link.download = `yohoo-backup-before-reset-${timestamp}.json`;
    link.click();
    URL.revokeObjectURL(url);

    debugLog('Backup created before reset');

    // Clear localStorage and reload defaults
    localStorage.removeItem(STORAGE_KEY);
    await loadDefaultLinks();

    // Re-render
    render();

    alert('✅ Reset complete! Your previous data has been saved to your downloads folder.');
    debugLog('Reset to defaults completed');
}

// Initialize button in initSettingsModal()
document.getElementById('resetToDefaultsBtn')?.addEventListener('click', resetToDefaults);
```

#### Change 4: Add "Save Current as Default" button
**Location:** Settings Modal → Data Management section

**HTML Addition:**
```html
<div class="settings-control">
    <label class="settings-control-label">
        Save as Default Template
    </label>
    <div class="settings-control-description">
        Export your current link set in the default-links.json format.
        Save the downloaded file as "default-links.json" in the same folder as yohoo.html
        to make it the new default configuration (works locally, read-only on GitHub Pages).
    </div>
    <button id="saveAsDefaultBtn" class="secondary-btn" title="Export as default template">
        💾 Save Current as Default Template
    </button>
</div>
```

**JavaScript Handler:**
```javascript
function saveCurrentAsDefault() {
    const fontScale = localStorage.getItem('yohoo_font_scale') || '2.0';

    const defaultTemplate = {
        version: '1.0.0',
        exportDate: new Date().toISOString(),
        exportedBy: 'Yohoo - Save as Default Template',
        data: {
            sections: JSON.parse(JSON.stringify(appState.sections)),
            trash: [], // Empty trash for clean defaults
            layout: JSON.parse(JSON.stringify(appState.layout)),
            fontScale: parseFloat(fontScale)
        },
        metadata: {
            sectionCount: appState.sections.length,
            linkCount: appState.sections.reduce((sum, s) => sum + s.links.length, 0),
            trashCount: 0,
            columns: appState.layout.columns.length
        }
    };

    // Create download with specific filename
    const dataStr = JSON.stringify(defaultTemplate, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'default-links.json';
    link.click();
    URL.revokeObjectURL(url);

    alert(
        '💾 Default template saved!\n\n' +
        'To use this as your new defaults:\n' +
        '1. Save the downloaded "default-links.json" file\n' +
        '2. Place it in the same folder as yohoo.html\n' +
        '3. Replace the existing default-links.json file\n\n' +
        'Note: This works when running locally. On GitHub Pages, you\'ll need to commit the file to your repository.'
    );

    debugLog('Saved current state as default template');
}

// Initialize button in initSettingsModal()
document.getElementById('saveAsDefaultBtn')?.addEventListener('click', saveCurrentAsDefault);
```

#### Change 5: Update `init()` to be async
**Location:** `yohoo.html` line ~2840

**Current:**
```javascript
function init() {
    loadState();
    loadFontScale();
    loadBackgroundColor();
    render();
    setupEventListeners();
    initSettingsModal();
    debugLog('Yohoo initialized');
}
```

**Proposed:**
```javascript
async function init() {
    await loadState(); // Now async
    loadFontScale();
    loadBackgroundColor();
    render();
    setupEventListeners();
    initSettingsModal();
    debugLog('Yohoo initialized');
}
```

---

## 4. Data Transformation: Backup to Default Links

### 4.1 Transformation Script

Need to create a script or manually transform `backup-links-2026-01-17.json` to the proper format:

**Input:** Flat array of links with section names
**Output:** Nested sections with embedded links

**Section mapping:**
```javascript
const sectionConfig = {
    "Norwegian Essentials": { icon: "🇳🇴", id: "norwegian-essentials" },
    "Transport & Travel": { icon: "🚆", id: "transport-travel" },
    "Norwegian News": { icon: "📰", id: "norwegian-news" },
    "International News": { icon: "🌍", id: "international-news" },
    "Norwegian Streaming": { icon: "📺", id: "norwegian-streaming" },
    "Global Streaming": { icon: "🎬", id: "global-streaming" },
    "Events & Culture": { icon: "🎭", id: "events-culture" },
    "Government & Official": { icon: "🏛️", id: "government-official" },
    "Banking": { icon: "🏦", id: "banking" },
    "Development": { icon: "💻", id: "development" },
    "Productivity & Tools": { icon: "🛠️", id: "productivity-tools" },
    "AI & Research": { icon: "🤖", id: "ai-research" },
    "Learn Norwegian": { icon: "📚", id: "learn-norwegian" },
    "Online Learning": { icon: "🎓", id: "online-learning" },
    "Outdoors & Activities": { icon: "⛰️", id: "outdoors-activities" },
    "Food & Groceries": { icon: "🍽️", id: "food-groceries" },
    "Interesting & Fun": { icon: "🎨", id: "interesting-fun" }
};
```

### 4.2 Layout Configuration

Default layout: 4 columns, distribute sections evenly
```javascript
{
    "columns": [
        ["norwegian-essentials", "transport-travel", "norwegian-news", "international-news"],
        ["norwegian-streaming", "global-streaming", "events-culture", "government-official"],
        ["banking", "development", "productivity-tools", "ai-research"],
        ["learn-norwegian", "online-learning", "outdoors-activities", "food-groceries", "interesting-fun"]
    ]
}
```

---

## 5. Implementation Checklist

- [ ] Create transformation script for backup-links to default-links format
- [ ] Generate `default-links.json` from `backup-links-2026-01-17.json`
- [ ] Add `loadDefaultLinks()` async function
- [ ] Add `loadHardcodedDefaults()` fallback function
- [ ] Modify `loadState()` to call `loadDefaultLinks()` when localStorage empty
- [ ] Make `init()` async to support await loadState()
- [ ] Add "Reset to Defaults" button HTML to settings modal
- [ ] Add `resetToDefaults()` function
- [ ] Add "Save Current as Default Template" button HTML to settings modal
- [ ] Add `saveCurrentAsDefault()` function
- [ ] Wire up event handlers in `initSettingsModal()`
- [ ] Test: Fresh page load (no localStorage) should load from default-links.json
- [ ] Test: Reset to defaults should backup current state and reload defaults
- [ ] Test: Save as default template should export with correct filename
- [ ] Test: Fallback to hardcoded defaults if default-links.json fails
- [ ] Verify: All existing drag-and-drop functionality unchanged
- [ ] Verify: All existing display logic unchanged

---

## 6. Testing Scenarios

### 6.1 First-Time User Experience
1. User opens yohoo.html for first time
2. localStorage is empty
3. Page fetches `./default-links.json`
4. Displays all 17 sections with ~120 links
5. Layout: 4 columns as configured

### 6.2 Reset to Defaults
1. User has customized their links
2. Clicks Settings → "Reset to Defaults"
3. Sees confirmation dialog
4. Downloads automatic backup file
5. Page reloads default-links.json
6. All customizations replaced with defaults

### 6.3 Save Custom Defaults
1. User customizes their perfect link set
2. Clicks Settings → "Save Current as Default Template"
3. Downloads `default-links.json`
4. User replaces original default-links.json with downloaded file
5. New users (or after reset) see the custom defaults

### 6.4 Fallback Behavior
1. default-links.json is missing or invalid
2. Page catches error
3. Falls back to hardcoded defaults
4. Logs error to console
5. Page still functional

### 6.5 GitHub Pages Deployment
1. default-links.json committed to repository
2. Hosted on GitHub Pages
3. First-time visitors fetch from GitHub Pages origin
4. "Save as default" exports file (user must commit to repo manually)

---

## 7. Benefits

✅ **No code changes to update defaults** - Just replace default-links.json
✅ **Works locally and on GitHub Pages** - Same-origin fetch
✅ **Safe with automatic backups** - Before every reset
✅ **Graceful degradation** - Falls back to hardcoded if file missing
✅ **Uses existing export/import format** - No new data structures
✅ **Preserves all drag-and-drop logic** - No changes to core functionality

---

## 8. Potential Issues & Mitigations

| Issue | Mitigation |
|-------|-----------|
| default-links.json not found | Fallback to hardcoded defaults |
| Invalid JSON in default-links.json | Try-catch + validation, fallback to hardcoded |
| Fetch blocked by CORS (if served from different origin) | Document requirement: same origin as HTML file |
| User expects "Save as default" to immediately update page | Add clear instructions in alert that file must be manually replaced |
| Async init() breaks existing code | Only loadState() is awaited; rest of init is synchronous |

---

## 9. Documentation Updates Needed

- **README.md**: Explain default-links.json system
- **CLAUDE.md**: Update architecture section
- **User guide** (if exists): How to customize defaults

---

## 10. Future Enhancements (Out of Scope)

- Cloud sync for defaults (would require backend)
- Multiple default templates (e.g., "Work", "Personal", "Norwegian Focus")
- Scheduled automatic backups
- Default link set versioning
