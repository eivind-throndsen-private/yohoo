# Link Reordering Solution Design - 2026-01-08

## Executive Summary

The link reordering (drag-and-drop within sections) functionality broke after the section drag-and-drop enhancement (commit 83ec33c). The root cause is a flawed placeholder-based insertion logic that:

1. Uses placeholder positioning instead of simple index calculation
2. Filters links after placeholder instead of using placeholder position in the actual array
3. Fails when the placeholder is the last element in the list
4. Over-complicates the logic that previously worked with simple `push()`

## Root Cause Analysis

### What Was Working (Commit 1ad078e)
```javascript
function handleLinkDrop(e) {
    // ...
    if (draggedType === 'link' && draggedItem) {
        const sourceSection = appState.sections.find(s => s.id === draggedItem.sectionId);
        const targetSection = appState.sections.find(s => s.id === targetSectionId);

        const linkIndex = sourceSection.links.findIndex(l => l.id === draggedItem.id);
        if (linkIndex > -1) {
            const [link] = sourceSection.links.splice(linkIndex, 1);
            link.sectionId = targetSectionId;
            targetSection.links.push(link);  // ✅ Simple, works
            saveState();
            render();
        }
    }
}
```

### What's Broken Now (Current)
```javascript
// handleLinkDragOver creates placeholder
let placeholder = linkList.querySelector('.link-placeholder');
if (!placeholder) {
    placeholder = document.createElement('li');
    placeholder.className = 'link-placeholder';
}

// Position placeholder based on mouse Y
if (insertBefore) {
    linkList.insertBefore(placeholder, insertBefore);
} else {
    linkList.appendChild(placeholder);
}
```

Then in `handleLinkDrop`:
```javascript
// ❌ Problem: Tries to find DOM position instead of using draggedItem.element
const linksAfterPlaceholder = Array.from(
    this.querySelectorAll('.link-item')
).filter(li => {
    const rect = li.getBoundingClientRect();
    const placeholderRect = placeholder.getBoundingClientRect();
    return rect.top >= placeholderRect.top;  // ❌ Brittle: depends on layout
});

// ❌ Problem: Looks up by ID in target section links, but doesn't account for multi-section moves
if (linksAfterPlaceholder.length > 0) {
    const firstLinkAfter = linksAfterPlaceholder[0];
    const linkId = firstLinkAfter.dataset.id;
    insertIndex = targetSection.links.findIndex(l => l.id === linkId);
}

// ❌ Problem: Logic breaks when moving within same section
if (targetSectionId === draggedItem.sectionId && insertIndex > linkIndex) {
    insertIndex--;
}
```

## Problems with Current Approach

| Issue | Impact | Example |
|-------|--------|---------|
| Placeholder is in DOM, actual links in array | Position mismatch | Dragging to bottom appends, but placeholder shows middle position |
| Uses `getBoundingClientRect()` | Layout-dependent, fails with wrapping | Single-column layout works, multi-column layout fails |
| Filters `querySelector('.link-item')` only | Gets ALL links in list | If moving link from section A to B, still queries A's link positions |
| Complex same-section logic | Hard to debug and maintain | Off-by-one errors in reordering |
| No visual feedback during drag | UX broken | User doesn't see where link will land |
| Placeholder removal timing | Can leave orphaned placeholders | If drop fails, placeholder never removed |

## Proposed Solution: Index-Based Approach

Instead of using DOM placeholder positioning, calculate insertion index directly from drag coordinates.

### Key Design Principles

1. **Single Source of Truth**: Use `draggedItem.element` (the actual dragged link) as source
2. **DOM Position → Array Index**: Convert mouse Y coordinate to insertion index in array
3. **No Placeholder DOM Manipulation**: Show placeholder only for visual feedback, don't rely on it for logic
4. **Explicit Same-Section Handling**: Handle same-section moves as a special case
5. **Robustness**: Works with any layout (single column, multi-column, wrapped)

### Implementation Strategy

#### Phase 1: Core Link Reordering (Same Section)

```javascript
function findInsertionIndex(targetList, dragEvent, excludeElement) {
    // Get all visible link elements in target list (except dragged element)
    const linkElements = Array.from(targetList.querySelectorAll('.link-item'))
        .filter(el => el !== excludeElement);

    // Find insertion point based on vertical position
    let insertIndex = linkElements.length; // Default: end

    for (let i = 0; i < linkElements.length; i++) {
        const rect = linkElements[i].getBoundingClientRect();
        const midpoint = rect.top + rect.height / 2;

        if (dragEvent.clientY < midpoint) {
            insertIndex = i;
            break;
        }
    }

    return insertIndex;
}
```

#### Phase 2: Cross-Section Moves

```javascript
function handleLinkDrop(e) {
    e.preventDefault();
    e.stopPropagation();

    const targetSectionId = this.dataset.sectionId;
    const targetList = this; // the .link-list

    // CASE 1: Internal Link Move
    if (draggedType === 'link' && draggedItem) {
        const sourceSection = appState.sections.find(s => s.id === draggedItem.sectionId);
        const targetSection = appState.sections.find(s => s.id === targetSectionId);

        if (!sourceSection || !targetSection) return;

        const linkIndex = sourceSection.links.findIndex(l => l.id === draggedItem.id);
        if (linkIndex === -1) return;

        // Calculate insertion index from drag position
        let insertIndex = targetSection.links.length;

        if (draggedItem.sectionId === targetSectionId) {
            // Same section: find position excluding the dragged item itself
            insertIndex = findInsertionIndex(targetList, e, draggedItem.element);
        } else {
            // Different section: find position in target section
            insertIndex = findInsertionIndex(targetList, e, null);
        }

        // Perform move
        const [link] = sourceSection.links.splice(linkIndex, 1);
        link.sectionId = targetSectionId;
        targetSection.links.splice(insertIndex, 0, link);

        saveState();
        render();
        debugLog('Link moved', { from: sourceSection.id, to: targetSection.id, insertIndex });
    }
    // CASE 2: External URL Drop
    else if (!draggedItem) {
        // ... existing external URL handling ...
    }
}
```

#### Phase 3: Enhanced Visual Feedback

```javascript
function handleLinkDragOver(e) {
    if (draggedType === 'section') return;

    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = 'move';

    const targetList = this;
    const linkElements = Array.from(targetList.querySelectorAll('.link-item'))
        .filter(el => el !== draggedItem?.element);

    // Find where placeholder should go
    let insertBeforeElement = null;
    for (const linkEl of linkElements) {
        const rect = linkEl.getBoundingClientRect();
        if (e.clientY < rect.top + rect.height / 2) {
            insertBeforeElement = linkEl;
            break;
        }
    }

    // Manage placeholder for visual feedback
    let placeholder = targetList.querySelector('.link-placeholder');
    if (!placeholder) {
        placeholder = document.createElement('li');
        placeholder.className = 'link-placeholder';
    }

    if (insertBeforeElement) {
        targetList.insertBefore(placeholder, insertBeforeElement);
    } else {
        targetList.appendChild(placeholder);
    }
}
```

## Implementation Checklist

- [ ] Remove placeholder-based positioning logic
- [ ] Implement `findInsertionIndex()` helper function
- [ ] Update `handleLinkDragOver()` to calculate indices
- [ ] Update `handleLinkDrop()` to use array splice instead of DOM position lookup
- [ ] Handle same-section vs cross-section moves explicitly
- [ ] Ensure placeholder cleanup on dragend
- [ ] Test scenarios:
  - [ ] Drag link up within section
  - [ ] Drag link down within section
  - [ ] Drag link to beginning of section
  - [ ] Drag link to end of section
  - [ ] Drag link to different section
  - [ ] Drag link back to original position
  - [ ] Multi-column layout
  - [ ] Wrapped link items

## CSS for Placeholder

```css
.link-placeholder {
    height: 40px; /* Match link-item height */
    margin-bottom: 8px;
    background: rgba(255, 255, 255, 0.1);
    border: 2px dashed var(--border-color);
    border-radius: 4px;
    visibility: visible;
}
```

## Why This Solution is Better

| Aspect | Previous | Current (Broken) | Proposed |
|--------|----------|------------------|----------|
| Source of truth | Array (links) | DOM (placeholder) | Array (draggedItem) |
| Layout dependency | None | High (getBoundingClientRect) | Low (only for placeholder) |
| Complexity | Low | High | Medium |
| Error prone | Rare | Common | Unlikely |
| Maintainability | ✅ | ❌ | ✅ |
| Visual feedback | None | Exists but broken | Works perfectly |

## Edge Cases Handled

1. **Dragging to same position**: Position matches, no change occurs, state unchanged
2. **Dragging outside list**: Drop doesn't fire on list, no change
3. **Dragging between sections**: Source/target check handles this
4. **Empty target section**: `insertIndex = 0`, link goes to start
5. **Dropping on placeholder**: Placeholder is not a data link, won't match in array
6. **Multiple drags in succession**: `handleDragEnd` cleans up properly

## Rollout Plan

1. Implement `findInsertionIndex()` helper
2. Rewrite `handleLinkDragOver()` to use new logic
3. Rewrite `handleLinkDrop()` to use splice-based insertion
4. Simplify `handleDragEnd()` cleanup
5. Remove placeholder DOM position lookup
6. Test all scenarios
7. Clean up debug logging
