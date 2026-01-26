## 1. Goal

Enable users to rearrange **sections** on a 3-column personal homepage via drag-and-drop, Trello-style, with:

* Obvious drag affordance
* Real-time visual preview of the new layout
* No external libraries (vanilla HTML/CSS/JS only)

“Sections” = the boxes like **Bob the Builder**, **Misc**, **Everyday AI**, etc. We only move whole sections, not individual bookmarks inside them.

---

## 2. UX & Behavior

### 2.1 What can be dragged

* Each section card is draggable.
* Drag is started by **grabbing the section header bar**:

  * Header includes the section title and an optional “grip” icon (≡) on the right.
  * Cursor changes to `grab`/`grabbing` over the header.

### 2.2 How reordering works

* The board is a 3-column layout.
* When user drags a section:

  * The original section becomes semi-transparent.
  * A **placeholder card** appears where it came from.
  * As the user moves the mouse, the placeholder moves into the position where the section would land **if they released now**.
* Sections reorder **both within a column and across columns**.

  * Dragging horizontally over another column will move the placeholder into that column.
* When user releases the mouse:

  * The section card “snaps” into the placeholder position.
  * The new order is persisted (e.g., to `localStorage` via the JS API described below).

### 2.3 Visual cues

* Drag state:

  * Dragged card: slightly scaled up, box shadow increased, `opacity: 0.9`.
  * Placeholder: same size as a section card, but:

    * dotted border
    * light background
    * “Drop here” text, or just an empty outline.
* Valid drop zones:

  * Entire area of each column.
  * If dropped outside any column, the card returns to its original position.

### 2.4 Keyboard & accessibility (nice-to-have but desirable)

* Sections are focusable (`tabindex="0"` on header).
* Press **Space/Enter** on a focused header to enter “reorder mode”:

  * Announce via ARIA (e.g., `aria-live`).
  * Use arrow keys to move the card up/down/left/right.
  * Press Space/Enter again to confirm new position; Esc cancels.
* Use ARIA roles:

  * Columns: `role="list"`.
  * Section cards: `role="listitem"`.
  * Use `aria-grabbed` on the card when it’s being dragged.

---

## 3. Data Model

Use a simple serialized representation so order can be persisted and restored.

```js
// Example in-memory model
const layout = {
  columns: [
    {
      id: 'col-1',
      sections: ['sec-bob', 'sec-misc', 'sec-everyday-ai']
    },
    {
      id: 'col-2',
      sections: ['sec-bob-ideas', 'sec-vend', 'sec-1-1-meetings']
    },
    {
      id: 'col-3',
      sections: ['sec-pm-days', 'sec-linker', 'sec-private', 'sec-vibe-projects']
    }
  ]
};
```

Persistence:

* On every successful drop:

  * Update `layout` to reflect the new order.
  * Save to `localStorage` under a key like `homepageLayout`.
* On load:

  * Read from `localStorage`; fall back to default layout if missing.

---

## 4. DOM Structure

### 4.1 Board and columns

```html
<div id="board">
  <div class="column" data-column-id="col-1" role="list" aria-label="Column 1"></div>
  <div class="column" data-column-id="col-2" role="list" aria-label="Column 2"></div>
  <div class="column" data-column-id="col-3" role="list" aria-label="Column 3"></div>
</div>
```

### 4.2 Section card

```html
<article
  class="section-card"
  data-section-id="sec-bob"
  role="listitem"
>
  <header class="section-header" tabindex="0">
    <span class="section-title">Bob the Builder</span>
    <button class="section-drag-handle" aria-label="Move section" tabindex="-1">
      &#9776; <!-- grip icon -->
    </button>
  </header>
  <div class="section-body">
    <!-- existing bookmark links go here -->
  </div>
</article>
```

### 4.3 Placeholder element

The placeholder can be a reusable element inserted into the DOM:

```html
<div class="section-placeholder" aria-hidden="true"></div>
```

JS will move this `<div>` around as needed, instead of creating multiple placeholders.

---

## 5. Layout & Styling (CSS)

Key points (exact values can be adjusted):

```css
#board {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  align-items: flex-start;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Sections */
.section-card {
  background: #fdf7e3;      /* similar to your current style */
  border-radius: 4px;
  padding: 8px 10px 10px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

/* Header & handle */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: grab;
  font-weight: 600;
  margin-bottom: 6px;
}

.section-header:active {
  cursor: grabbing;
}

.section-drag-handle {
  background: none;
  border: none;
  cursor: grab;
}

/* Dragging state */
.section-card.dragging {
  opacity: 0.8;
  z-index: 1000;
  position: absolute; /* for ghost */
  pointer-events: none;
}

/* Placeholder */
.section-placeholder {
  border: 2px dashed rgba(0,0,0,0.2);
  border-radius: 4px;
  height: 80px;       /* will be overridden to match dragged card’s height */
}
```

Responsiveness (optional):

* On narrow screens, switch to 1 or 2 columns with `@media` queries.

---

## 6. Drag & Drop Logic (JS)

**Implementation approach:** use Pointer / Mouse events (more controllable than native HTML5 DnD).

### 6.1 State variables

```js
let dragState = {
  isDragging: false,
  draggedEl: null,        // the section-card element
  startColumnEl: null,    // original column
  placeholderEl: null,
  startX: 0,
  startY: 0,
  offsetX: 0,
  offsetY: 0
};
```

### 6.2 Event flow

#### 6.2.1 Start drag

Attach to `.section-header` and `.section-drag-handle`:

1. `pointerdown` / `mousedown`:

   * Set `dragState.draggedEl` to the parent `.section-card`.
   * Record initial mouse position and element’s bounding rect.
   * Compute `offsetX`, `offsetY` = pointer position − element top/left.
   * Insert `placeholderEl` **immediately after** the dragged element in its column.
   * Set explicit width/height of placeholder to match the dragged card.
   * Set `position: absolute` and `dragging` class on the dragged card.
   * Append the dragged card to `document.body` (so it can move freely).
   * `isDragging = true`.
   * Add `pointermove` and `pointerup` listeners on `window`.

#### 6.2.2 Move

On `pointermove`:

1. If `!isDragging`, return.
2. Update `draggedEl.style.left` / `.top` using `event.clientX - offsetX`, `event.clientY - offsetY`.
3. Determine **current best drop position**:

   * Get all `.column` elements.
   * Find the column whose bounding box horizontally contains `clientX`. If none, keep placeholder in original column.
   * Within that column:

     * Get all `.section-card` elements except the dragged one.
     * For each card, compare `clientY` to its vertical center:

       * If `clientY` < card center → placeholder should be inserted **before** this card.
     * If no such card, append placeholder at the end of the column.
4. Move the `placeholderEl` to that position using `insertBefore` / `appendChild`.

This gives a live preview identical to Trello’s behavior.

#### 6.2.3 Drop

On `pointerup`:

1. If `!isDragging`, return.
2. Set `isDragging = false`.
3. Remove global event listeners.
4. Insert `draggedEl` in the DOM exactly where `placeholderEl` is.
5. Remove `dragging` class and inline `style` (left/top/position).
6. Remove `placeholderEl` from DOM.
7. Rebuild the `layout` structure based on DOM order:

   * For each `.column` (in index order):

     * Read `data-column-id`.
     * Collect `data-section-id` for child `.section-card`s in order.
   * Update `layout.columns` accordingly.
8. Persist `layout` to `localStorage`.

#### 6.2.4 Cancel conditions

* If user presses **Escape** while dragging:

  * Return the card to the placeholder’s original start position.
  * Remove placeholder and reset state; do **not** update layout / storage.
* If pointer leaves window and `pointerup` never fires (edge case):

  * Add `pointercancel` handler that behaves like cancel.

---

## 7. Initialization

On page load:

1. Load `layout` from `localStorage` (if present).
2. Render columns and section cards in the correct order using that layout.
3. Attach drag handlers to each section’s header and handle.
4. Create a single global `placeholderEl` and reuse it for all drags.

---

## 8. Edge Cases & Constraints

* **Empty column**: if a column has no sections and card is dragged into its horizontal area, insert placeholder at the top of that column.
* **Scrolling**: if the board can scroll vertically:

  * Optionally auto-scroll when the pointer is near top/bottom of the viewport during drag.
* **Selection**:

  * Prevent text selection during drag (`event.preventDefault()` on `pointerdown` when starting drag).

