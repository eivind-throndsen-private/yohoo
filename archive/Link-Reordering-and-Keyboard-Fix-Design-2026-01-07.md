# Link Re-ordering and Keyboard Shortcut Fix Design
**Date:** 2026-01-07
**Author:** Eivind Throndsen
**Status:** Design Proposal

## Executive Summary

This document identifies root causes and proposes solutions for two usability issues in Yohoo:

1. **Link re-ordering within sections is unreliable** - Links can only be moved between sections, not reordered within the same section
2. **Search shortcut (/) interrupts link editing** - Typing "/" while renaming a link triggers the search function instead of inserting the character

## Issue 1: Link Re-ordering Within Sections

### Problem Statement

Users cannot reliably re-order links within a section. While drag-and-drop works for moving links **between** sections, attempting to reorder links **within the same section** always places the dragged link at the end of the list, regardless of where the user drops it.

### Root Cause Analysis

**Location:** `yohoo.html:1830-1858` (`handleLinkDrop` function)

The link drop handler contains logic for moving links between sections but lacks position-aware insertion:

```javascript
function handleLinkDrop(e) {
    // ... validation code ...

    if (draggedType === 'link' && draggedItem) {
        const sourceSection = appState.sections.find(s => s.id === draggedItem.sectionId);
        const targetSection = appState.sections.find(s => s.id === targetSectionId);

        const linkIndex = sourceSection.links.findIndex(l => l.id === draggedItem.id);
        if (linkIndex > -1) {
            const [link] = sourceSection.links.splice(linkIndex, 1);
            link.sectionId = targetSectionId;
            targetSection.links.push(link);  // ← PROBLEM: Always appends to end
            saveState();
            render();
        }
    }
}
```

**Key Issues:**

1. **No insertion position calculation** - The handler uses `push()` which always appends to the array end
2. **No drop target detection** - Unlike section drag (which uses placeholders), link drag doesn't detect where in the list the drop occurred
3. **Missing visual feedback** - No placeholder shows where the link will be inserted

### Current Section Drag Implementation (Reference)

The section drag system (`yohoo.html:1684-1705`) demonstrates a working approach:

```javascript
function handleSectionPointerMove(e) {
    // Find insertion point based on mouse Y position
    const sections = Array.from(targetColumn.querySelectorAll('.section')).filter(
        s => s !== dragState.draggedEl
    );

    let insertBefore = null;
    for (const section of sections) {
        const rect = section.getBoundingClientRect();
        const middle = rect.top + rect.height / 2;

        if (e.clientY < middle) {
            insertBefore = section;
            break;
        }
    }

    // Move placeholder to calculated position
    if (insertBefore) {
        targetColumn.insertBefore(dragState.placeholderEl, insertBefore);
    } else {
        targetColumn.appendChild(dragState.placeholderEl);
    }
}
```

This approach:
- Calculates midpoint of each potential drop target
- Determines insertion position based on mouse Y coordinate
- Provides visual feedback via placeholder element

### Proposed Solution

**Approach:** Adapt the section drag placeholder logic for link re-ordering

#### Implementation Strategy

1. **Add placeholder element for link drags**
   - Create a `.link-placeholder` element (similar to `.section-placeholder`)
   - Show it during drag operations to indicate insertion point
   - Style it to match link item dimensions

2. **Enhance `handleLinkDragOver` to calculate insertion position**
   - Currently only adds `.drag-over` class to the entire list
   - Should iterate through existing links to find insertion point
   - Calculate midpoint of each link using `getBoundingClientRect()`
   - Position placeholder before/after based on mouse Y coordinate

3. **Update `handleLinkDrop` to use insertion position**
   - Read placeholder position to determine index
   - Use `Array.splice()` to insert at specific index instead of `push()`
   - Handle same-section moves differently from cross-section moves

#### Detailed Code Changes

**Location:** `yohoo.html:1812-1820` (`handleLinkDragOver`)

```javascript
function handleLinkDragOver(e) {
    // Don't handle section drags
    if (draggedType === 'section') return;

    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = 'move';

    // NEW: Calculate insertion position
    const linkList = this;  // .link-list element
    const links = Array.from(linkList.querySelectorAll('.link-item')).filter(
        li => li !== draggedItem?.element
    );

    let insertBefore = null;
    for (const link of links) {
        const rect = link.getBoundingClientRect();
        const middle = rect.top + rect.height / 2;

        if (e.clientY < middle) {
            insertBefore = link;
            break;
        }
    }

    // Get or create placeholder
    let placeholder = linkList.querySelector('.link-placeholder');
    if (!placeholder) {
        placeholder = document.createElement('li');
        placeholder.className = 'link-placeholder';
        placeholder.style.height = '2.5rem';  // Match link-item height
        placeholder.style.border = '2px dashed var(--mauve-400)';
        placeholder.style.borderRadius = '0.375rem';
        placeholder.style.margin = '0.25rem 0';
        placeholder.style.opacity = '0.6';
    }

    // Position placeholder
    if (insertBefore) {
        linkList.insertBefore(placeholder, insertBefore);
    } else {
        linkList.appendChild(placeholder);
    }
}
```

**Location:** `yohoo.html:1830-1858` (`handleLinkDrop`)

```javascript
function handleLinkDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.remove('drag-over');

    // Remove placeholder
    const placeholder = this.querySelector('.link-placeholder');

    if (draggedType === 'link' && draggedItem) {
        const targetSectionId = this.dataset.sectionId;
        const sourceSection = appState.sections.find(s => s.id === draggedItem.sectionId);
        const targetSection = appState.sections.find(s => s.id === targetSectionId);

        if (!sourceSection || !targetSection) {
            if (placeholder) placeholder.remove();
            return;
        }

        // Remove from source
        const linkIndex = sourceSection.links.findIndex(l => l.id === draggedItem.id);
        if (linkIndex === -1) {
            if (placeholder) placeholder.remove();
            return;
        }
        const [link] = sourceSection.links.splice(linkIndex, 1);

        // NEW: Calculate insertion index from placeholder position
        let insertIndex = targetSection.links.length;  // Default: end of list

        if (placeholder) {
            const linksAfterPlaceholder = Array.from(
                this.querySelectorAll('.link-item')
            ).filter(li => {
                const rect = li.getBoundingClientRect();
                const placeholderRect = placeholder.getBoundingClientRect();
                return rect.top >= placeholderRect.top;
            });

            if (linksAfterPlaceholder.length > 0) {
                const firstLinkAfter = linksAfterPlaceholder[0];
                const linkId = firstLinkAfter.dataset.id;
                insertIndex = targetSection.links.findIndex(l => l.id === linkId);

                // Adjust index if moving within same section and moving down
                if (targetSectionId === draggedItem.sectionId && insertIndex > linkIndex) {
                    insertIndex--;
                }
            }

            placeholder.remove();
        }

        // Insert at calculated position
        link.sectionId = targetSectionId;
        targetSection.links.splice(insertIndex, 0, link);

        saveState();
        render();
        debugLog('Link moved', {
            from: sourceSection.id,
            to: targetSection.id,
            insertIndex
        });
    }
    // ... external drop handling ...
}
```

**Location:** `yohoo.html:1798-1810` (`handleDragEnd`)

```javascript
function handleDragEnd(e) {
    if (draggedType === 'link') {
        // Clean up
        draggedItem = null;
        draggedType = null;

        document.querySelectorAll('.link-item.dragging').forEach(el =>
            el.classList.remove('dragging')
        );
        document.querySelectorAll('.drag-over').forEach(el =>
            el.classList.remove('drag-over')
        );

        // NEW: Remove any remaining placeholders
        document.querySelectorAll('.link-placeholder').forEach(el =>
            el.remove()
        );
    }
}
```

#### CSS Additions

```css
.link-placeholder {
    height: 2.5rem;
    border: 2px dashed var(--mauve-400);
    border-radius: 0.375rem;
    margin: 0.25rem 0;
    opacity: 0.6;
    background: transparent;
    list-style: none;
    pointer-events: none;
}
```

### Benefits

- **Predictable behavior** - Links land exactly where users drop them
- **Visual feedback** - Placeholder shows insertion point during drag
- **Consistent UX** - Matches section drag-and-drop behavior
- **Same-section reordering** - Finally enables sorting within a section

### Edge Cases to Handle

1. **Dropping on self** - Ignore if drop position === current position
2. **Empty sections** - Placeholder should appear in empty lists
3. **Same-section moves** - Adjust indices when moving down (offset by 1)
4. **Rapid drags** - Clean up stale placeholders in `handleDragEnd`

---

## Issue 2: Search Shortcut Interrupts Link Editing

### Problem Statement

When renaming a link or section, typing the "/" character moves focus to the search bar instead of inserting the character into the input field. This breaks workflows for users trying to enter URLs or paths containing slashes.

### Root Cause Analysis

**Location:** `yohoo.html:2035-2038` (global keyboard handler)

```javascript
document.addEventListener('keydown', (e) => {
    // ... ESC handler ...

    // Keyboard Shortcut "/" - Focus search
    if (e.key === '/' && document.activeElement !== searchInput) {
        e.preventDefault();
        searchInput.focus();
    }
});
```

**The Problem:**

The condition `document.activeElement !== searchInput` only checks if the user is NOT in the search input, but doesn't check if they're in OTHER input fields (like edit inputs).

When editing a link:
- `enterEditMode()` creates an `<input class="link-edit-input">` (line 2335)
- `enterSectionEditMode()` creates an `<input class="section-title-input">` (line 2391)
- Both inputs receive focus, but the global "/" handler still triggers
- `e.preventDefault()` blocks "/" from being typed, and focus shifts to search

### Proposed Solution

**Approach:** Check if ANY input/textarea/contenteditable element has focus before triggering the search shortcut

#### Implementation

**Location:** `yohoo.html:2034-2038`

```javascript
// Keyboard Shortcut "/" - Focus search
if (e.key === '/') {
    const activeEl = document.activeElement;
    const isEditingText = (
        activeEl.tagName === 'INPUT' ||
        activeEl.tagName === 'TEXTAREA' ||
        activeEl.isContentEditable ||
        activeEl.classList.contains('link-edit-input') ||
        activeEl.classList.contains('section-title-input')
    );

    if (!isEditingText) {
        e.preventDefault();
        searchInput.focus();
    }
}
```

**Alternative (more concise):**

```javascript
// Keyboard Shortcut "/" - Focus search (only when not editing)
if (e.key === '/' && !isEditingText(document.activeElement)) {
    e.preventDefault();
    searchInput.focus();
}

// Helper function (add at top of script)
function isEditingText(element) {
    return (
        element.tagName === 'INPUT' ||
        element.tagName === 'TEXTAREA' ||
        element.isContentEditable === true
    );
}
```

### Benefits

- **Predictable behavior** - "/" works normally in all edit contexts
- **No breaking changes** - Still triggers search when not editing
- **Future-proof** - Covers any new input fields automatically
- **Standard pattern** - Common approach used by keyboard-driven apps (Slack, Notion, etc.)

### Testing Scenarios

1. ✅ **Typing "/" in search bar** - Should insert "/" character
2. ✅ **Typing "/" while editing link title** - Should insert "/" character
3. ✅ **Typing "/" while editing section name** - Should insert "/" character
4. ✅ **Typing "/" anywhere else** - Should focus search bar
5. ✅ **Typing "/" in future textarea** - Should insert "/" character

---

## Implementation Priority

### Phase 1: Keyboard Shortcut Fix (Low Risk, High Impact)
**Effort:** 5 minutes
**Risk:** Very low - simple conditional change
**Impact:** Immediate usability improvement

### Phase 2: Link Re-ordering (Medium Risk, High Impact)
**Effort:** 1-2 hours
**Risk:** Medium - requires careful index calculations
**Impact:** Major UX improvement, enables core workflow

---

## Testing Plan

### Manual Testing

**Link Re-ordering:**
1. Drag link within same section to different positions (top, middle, bottom)
2. Drag link from one section to another at specific positions
3. Drag link in empty section
4. Drag link in section with 1 item
5. Verify placeholder appearance and position during drag
6. Test rapid drag/cancel operations

**Keyboard Shortcut:**
1. Edit link title, type "/" - verify it's inserted
2. Edit section name, type "/" - verify it's inserted
3. Press "/" from homepage - verify search focuses
4. Press "/" while search already focused - verify it's inserted
5. Press "/" after closing edit mode - verify search focuses

### Browser Compatibility

Test in:
- ✅ Chrome (primary target)
- ✅ Firefox
- ✅ Safari
- ✅ Edge

---

## Migration Notes

No data migration required - both fixes are purely UI/behavior changes.

---

## Future Enhancements

1. **Keyboard shortcuts for link re-ordering**
   - Arrow keys to move links up/down within section
   - Ctrl/Cmd + Arrow to move between sections

2. **Multi-select drag**
   - Select multiple links and drag together
   - Shift+click to select range

3. **Undo/redo for drag operations**
   - Ctrl+Z to undo last move
   - Maintain operation history in localStorage

---

## Questions & Decisions

**Q: Should we add animation to the placeholder movement?**
A: Start without animation for simplicity. Can add CSS transitions in future iteration if desired.

**Q: Should links snap to grid positions or allow free placement?**
A: Continue using list-based approach (not free placement). Placeholder indicates exact insertion point.

**Q: Should we prevent "/" from triggering in readonly inputs?**
A: Current solution handles readonly via `isEditingText()` check - readonly inputs won't be contentEditable or standard input types.

---

## References

- **Section Drag Implementation:** `yohoo.html:1616-1750`
- **Link Drag Handlers:** `yohoo.html:1779-1858`
- **Edit Mode Functions:** `yohoo.html:2323-2427`
- **Keyboard Handlers:** `yohoo.html:2014-2039`
