# Add link and edit section features

Spec for changes made to `archive/yohoo.html` and `archive/scripts/generate_html.py`.  
Target: apply equivalent changes to the live `/yohoo.html`.

## 1. "+ Link" button in header controls

- New button in the top controls bar, next to "+ Section".  
- Opens the Add Link modal targeting a **Misc** section.  
- If no section with `data-section="misc"` exists, one is auto-created (emoji: 📌).  

## 2. Per-section "+" button

- Each section header gets a "+" button immediately after the section title.  
- Visible on hover (fades in, same pattern as the delete icon on links).  
- Clicking opens the Add Link modal pre-targeted to that section.  

## 3. Per-section "✎" edit button

- Each section header gets a pencil button after the "+" button.  
- Visible on hover, same reveal behavior.  
- Clicking replaces the section title with an inline text input.  
- Enter or blur saves the new name. Escape reverts.  

## 4. Section header layout

Order left to right:  

```
[icon] [title] [+ add] [✎ edit] ............. [collapse toggle]
```

- Title no longer has `flex: 1`. The collapse toggle uses `margin-left: auto` to push itself to the far right.  
- Action buttons use a shared `.section-action-btn` class (font-size 1.15rem, hover-reveal at 0.5 opacity, full opacity + accent color on direct hover).  

## 5. Add Link modal

- Fields: URL, Title (both text inputs).  
- Modal title dynamically shows the target: "Add link to {section name}".  
- Hidden input stores the target section ID.  
- Auto-prepends `https://` if no protocol given.  
- Derives display title from domain if title is left blank.  
- Enter in URL field moves focus to title field. Enter in title field submits.  
- New link is marked `data-custom="true"` so it persists via `saveState()`.  

## 6. Files changed

| File | What changed |  
| --- | --- |  
| `archive/yohoo.html` | CSS for `.section-action-btn`, modal HTML, JS functions (`openAddLinkModal`, `addLinkFromModal`, `ensureMiscSection`, `editSectionName`), event listeners, "+" and "✎" buttons in all section headers, `createSection()` updated |  
| `archive/scripts/generate_html.py` | Same changes mirrored in the Python template (CSS, HTML structure, JS functions and event listeners) |  
