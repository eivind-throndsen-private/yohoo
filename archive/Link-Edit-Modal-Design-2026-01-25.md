# Link Edit Modal Design - 2026-01-25

## Overview

Replace the current inline link editing system (title-only) with a proper modal dialog that allows editing both URL and title.

## Current Implementation

**Location:** `yohoo.html:2691-2740`
**Function:** `enterEditMode(linkItem, link, sectionId)`
**Behavior:**
- Replaces link content with inline `<input>` for title only
- Saves on blur or Enter key
- Cancels on Escape
- Re-renders entire page to exit edit mode

**Limitations:**
- Cannot edit URL
- Inline editing disrupts visual layout
- No validation or preview

## Proposed Solution

### Modal Dialog Pattern

Follow the existing Settings Modal pattern:
- Overlay with semi-transparent background (`rgba(44, 36, 22, 0.7)`)
- Centered content box with border and shadow
- Header with title and close button
- Body with form inputs
- Footer with action buttons

### Modal Structure

```html
<div id="linkEditModal" class="link-edit-modal">
    <div class="link-edit-modal-content">
        <div class="link-edit-header">
            <h3>✏️ Edit Link</h3>
            <button class="link-edit-close-btn">✕</button>
        </div>
        <div class="link-edit-body">
            <div class="form-group">
                <label for="linkEditTitle">Title</label>
                <input type="text" id="linkEditTitle" placeholder="Link title">
            </div>
            <div class="form-group">
                <label for="linkEditUrl">URL</label>
                <input type="url" id="linkEditUrl" placeholder="https://example.com">
            </div>
            <div class="link-preview">
                <!-- Show favicon and preview -->
            </div>
        </div>
        <div class="link-edit-footer">
            <button class="secondary-btn" id="linkEditCancel">Cancel</button>
            <button class="primary-btn" id="linkEditSave">Save</button>
        </div>
    </div>
</div>
```

## Implementation Plan

### Phase 1: Core Function & Data Model (Scaffolding)

**Function:** `openLinkEditModal(link, sectionId)`
**Responsibilities:**
- Store current link data in temporary state
- Populate modal inputs with current values
- Show modal
- Return promise for async handling

**Function:** `saveLinkEdit()`
**Responsibilities:**
- Validate inputs (non-empty title, valid URL format)
- Update link in appState
- Save to localStorage
- Close modal
- Re-render affected section only (optimization)

**Function:** `closeLinkEditModal()`
**Responsibilities:**
- Clear form inputs
- Hide modal
- Reset temporary state

**Data Validation:**
- Title: Required, trim whitespace
- URL: Required, basic URL format check
- URL should start with http://, https://, chrome://, edge://, about:, or brave://

### Phase 2: CSS Styling

**Modal Overlay:**
- Fixed position, full viewport
- z-index: 10000 (same as settings modal)
- Background: `rgba(44, 36, 22, 0.7)`
- Flexbox centering

**Modal Content:**
- Max-width: 500px
- Background: `var(--section-bg)`
- Border: `2px solid var(--border-color)`
- Border-radius: 8px
- Box-shadow for depth

**Form Inputs:**
- Full-width inputs with padding
- Border styling consistent with theme
- Focus states
- Label styling

**Buttons:**
- Primary button (Save): Accent color
- Secondary button (Cancel): Muted color
- Close X button: Top-right corner

### Phase 3: HTML Integration

**Modal Placement:**
- Add modal HTML after settings modal (around line 3200+)
- Use same structure as settings modal
- Ensure proper aria attributes for accessibility

### Phase 4: Event Wiring

**Edit Button Click:**
- Modify existing edit button handler (line ~1595)
- Replace `enterEditMode()` call with `openLinkEditModal()`

**Modal Interactions:**
- Close button → `closeLinkEditModal()`
- Cancel button → `closeLinkEditModal()`
- Save button → `saveLinkEdit()`
- Escape key → `closeLinkEditModal()`
- Click outside modal → `closeLinkEditModal()`
- Enter key in inputs → Focus next input or save

**Initialization:**
- Add `initLinkEditModal()` to setup event listeners
- Call from main init function (around line 937)

### Phase 5: Enhancements

**URL Preview:**
- Show favicon for entered URL
- Validate URL format in real-time
- Show error message for invalid URLs

**Smart Defaults:**
- Auto-add https:// if protocol missing
- Detect internal URLs (chrome://, etc.)

**Keyboard Navigation:**
- Tab between inputs
- Enter to save (from either input)
- Escape to cancel

## Testing Strategy

**Manual Tests:**
1. Open modal from edit button
2. Edit title only → Save → Verify update
3. Edit URL only → Save → Verify update
4. Edit both → Save → Verify both update
5. Cancel without saving → Verify no changes
6. Escape key → Verify modal closes
7. Click outside → Verify modal closes
8. Invalid URL → Verify validation error
9. Empty title → Verify validation error
10. Empty URL → Verify validation error

**Edge Cases:**
- Very long titles/URLs
- Special characters in URLs
- Internal URLs (chrome://, etc.)
- URLs with authentication
- Unicode in titles

## File Changes

**File:** `yohoo.html`

### 1. CSS Section - Add after line 695

**Location:** After settings modal styles, before other styles
**Action:** Add new CSS classes for link edit modal

```css
/* Link Edit Modal */
.link-edit-modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(44, 36, 22, 0.7);
    z-index: 10000;
    justify-content: center;
    align-items: center;
}

.link-edit-modal.visible {
    display: flex;
}

.link-edit-modal-content {
    background-color: var(--section-bg);
    border: 2px solid var(--border-color);
    border-radius: 8px;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

/* Additional modal styles for header, body, footer, form groups, etc. */
```

### 2. Remove Old CSS - Lines 460-469

**Action:** Delete `.link-edit-input` class (no longer needed)

```css
/* DELETE THIS:
.link-edit-input {
    width: 100%;
    padding: 0.25rem;
    border: 1px solid var(--link-color);
    border-radius: 2px;
    background-color: var(--section-bg);
    color: var(--text-main);
    font-size: calc(0.5rem * var(--font-scale));
    outline: 2px solid var(--link-color);
}
*/
```

### 3. HTML Section - Add after line 3200

**Location:** After settings modal closing div
**Action:** Add complete modal markup

```html
<!-- Link Edit Modal -->
<div id="linkEditModal" class="link-edit-modal" role="dialog" aria-modal="true">
    <div class="link-edit-modal-content">
        <div class="link-edit-header">
            <h3>✏️ Edit Link</h3>
            <button class="link-edit-close-btn">✕</button>
        </div>
        <div class="link-edit-body">
            <div class="form-group">
                <label for="linkEditTitle">Title</label>
                <input type="text" id="linkEditTitle" placeholder="Link title">
            </div>
            <div class="form-group">
                <label for="linkEditUrl">URL</label>
                <input type="url" id="linkEditUrl" placeholder="https://example.com">
            </div>
        </div>
        <div class="link-edit-footer">
            <button class="secondary-btn" id="linkEditCancel">Cancel</button>
            <button class="primary-btn" id="linkEditSave">Save</button>
        </div>
    </div>
</div>
```

### 4. JavaScript Functions - Add after line 2740

**Location:** After `enterSectionEditMode()` function
**Action:** Add three new functions

```javascript
// --- Link Edit Modal Management ---

let currentEditingLink = null;  // Store reference to link being edited
let currentEditingSectionId = null;

function openLinkEditModal(link, sectionId) {
    // Implementation here
}

function saveLinkEdit() {
    // Validation and save logic
}

function closeLinkEditModal() {
    // Cleanup and close
}

function initLinkEditModal() {
    // Set up event listeners
}
```

### 5. Modify Event Handler - Line 1595

**Current code:**
```javascript
li.querySelector('.edit-btn').addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    enterEditMode(li, link, section.id);  // ← CHANGE THIS
});
```

**New code:**
```javascript
li.querySelector('.edit-btn').addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    openLinkEditModal(link, section.id);  // ← NEW FUNCTION
});
```

### 6. Modify Initialization - Line 937

**Current code:**
```javascript
async function init() {
    await loadState();
    loadFontScale();
    loadBackgroundColor();
    render();
    setupEventListeners();
    initSettingsModal();  // ← ADD AFTER THIS
}
```

**New code:**
```javascript
async function init() {
    await loadState();
    loadFontScale();
    loadBackgroundColor();
    render();
    setupEventListeners();
    initSettingsModal();
    initLinkEditModal();  // ← ADD THIS LINE
}
```

### 7. Delete Old Function - Lines 2691-2740

**Action:** Remove `enterEditMode()` function entirely (50 lines)

```javascript
/* DELETE THIS ENTIRE FUNCTION:
function enterEditMode(linkItem, link, sectionId) {
    // ... 50 lines of old inline editing code ...
}
*/
```

## Backward Compatibility

- Remove `enterEditMode()` function (no longer needed)
- Remove `.link-edit-input` CSS (inline editing styles)
- All existing localStorage data remains compatible
- No migration needed

## Success Criteria

### Functional Requirements
- [ ] Modal opens when clicking edit button (✏️)
- [ ] Modal displays current title in title input field
- [ ] Modal displays current URL in URL input field
- [ ] Title field accepts text input and can be edited
- [ ] URL field accepts text input and can be edited
- [ ] Save button validates both fields are non-empty
- [ ] Save button validates URL has valid protocol (http://, https://, chrome://, etc.)
- [ ] Save button updates link.title in appState
- [ ] Save button updates link.url in appState
- [ ] Changes are saved to localStorage
- [ ] Changes are immediately visible after save (re-render)
- [ ] Cancel button closes modal without saving
- [ ] Close X button closes modal without saving
- [ ] Escape key closes modal without saving
- [ ] Clicking outside modal closes it without saving
- [ ] No changes persist if modal closed without saving

### UI/UX Requirements
- [ ] Modal overlay dims background (rgba(44, 36, 22, 0.7))
- [ ] Modal is centered on screen
- [ ] Modal has proper z-index (10000) above all content
- [ ] Modal styling matches existing design system colors
- [ ] Form inputs are clearly labeled
- [ ] Form inputs have placeholder text
- [ ] Buttons are visually distinct (Primary vs Secondary)
- [ ] Modal has proper border and shadow for depth
- [ ] Modal is responsive (90% width, max 500px)

### Keyboard & Accessibility
- [ ] Tab key moves between inputs and buttons
- [ ] Enter key in title field moves to URL field
- [ ] Enter key in URL field triggers save
- [ ] Escape key closes modal (already tested above)
- [ ] Modal has role="dialog" and aria-modal="true"
- [ ] Form inputs have associated labels
- [ ] Focus is set to title field when modal opens
- [ ] Focus returns to page when modal closes

### Error Handling
- [ ] Empty title shows validation error
- [ ] Empty URL shows validation error
- [ ] Invalid URL format shows validation error
- [ ] Validation errors are user-friendly
- [ ] Validation doesn't close modal on error

### Edge Cases
- [ ] Very long titles (100+ characters) display correctly
- [ ] Very long URLs (200+ characters) display correctly
- [ ] Special characters in title (quotes, apostrophes, etc.)
- [ ] Special characters in URL (query params, anchors, etc.)
- [ ] Unicode characters in title (emoji, non-Latin scripts)
- [ ] Internal browser URLs (chrome://, edge://, about:, brave://)
- [ ] URLs with authentication (user:pass@domain)
- [ ] Opening modal for one link, closing, opening for another

### Code Quality
- [ ] No console errors when opening/closing modal
- [ ] Old enterEditMode() function removed
- [ ] Old .link-edit-input CSS removed
- [ ] Code follows existing patterns and style
- [ ] Debug logging added for key actions
- [ ] Functions have clear, single responsibilities
