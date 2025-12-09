# Yohoo - Personal Start Page Specification

**Project**: Yohoo - Yahoo-like Personal Start Page
**Version**: 1.1
**Last Updated**: 2025-12-09
**Status**: Active Development

---

## 1. Overview

Yohoo is a personal, customizable start page inspired by Yahoo's classic portal design. The application aggregates frequently-used links, organizes them thematically, and provides intelligent bookmark management based on browsing history and link recency.

### 1.1 Goals

1. Create a fast, clean start page displaying frequently-used links organized by category
2. Support manual updates and reorganization of links via drag-and-drop
3. Automatically suggest links based on Chrome browsing history
4. Filter and display bookmarks less than one year old
5. Provide a useful category scaffold for organizing bookmarks thematically
6. Persist customizations locally without requiring a backend

### 1.2 Non-Goals

- Cloud sync (local-first design)
- Multi-user support
- Backend server (static HTML only)
- Analytics or tracking

---

## 2. System Architecture

### 2.1 High-Level Components

```
┌─────────────────────────────────────────┐
│         Frontend (Web Interface)        │
│  - yohoo.html: Main start page          │
│    (JavaScript embedded inline)         │
└─────────────────┬───────────────────────┘
                  │ localStorage
┌─────────────────▼───────────────────────┐
│         Data Layer (Static)             │
│  - data/bookmarks.json                  │
│  - data/history.json                    │
│  - data/categories/*.json               │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Data Collection Scripts            │
│  - parse_bookmarks.py                   │
│  - analyze_history.py                   │
│  - utils.py                             │
│  - generate_html.py                     │
└─────────────────────────────────────────┘
```

### 2.2 Technology Stack

**Frontend:**
- HTML5/CSS3 (single self-contained file)
- Vanilla JavaScript (no frameworks, embedded inline)
- Three-column grid layout (responsive)
- Light cream theme (originally dark mauve, now updated)

**Data Storage:**
- JSON files for structured data
- CSV for spreadsheet compatibility
- localStorage for user customizations

**Scripts:**
- Python 3.8+
- BeautifulSoup4 for HTML parsing
- SQLite3 for Chrome history (built-in)
- Logging framework with configurable levels

---

## 3. Data Models

### 3.1 Link/Bookmark Structure

```json
{
  "title": "Link Title",
  "url": "https://example.com",
  "domain": "example.com",
  "category": "category-slug",
  "added_date": "2025-12-08T10:00:00",
  "favicon": "url-to-favicon",
  "source": "bookmark|history",
  "visit_count": 42,
  "score": 0.85
}
```

### 3.2 Category Structure

The application uses a two-level hierarchy:
- **Sections/Subcategories**: Top-level groupings displayed as cards
- **Links**: Individual bookmarks within each section

Standard categories (from parse_bookmarks.py):
| Category ID | Display Name | Icon | Keywords |
|-------------|--------------|------|----------|
| work-productivity | Work & Productivity | 💼 | mail.google, calendar.google, notion, drive.google, trello, asana |
| development | Development | ⚡ | github, gitlab, stackoverflow, developer.mozilla, docker, kubernetes |
| communication | Communication | 💬 | slack, teams.microsoft, discord, zoom, meet.google |
| media-entertainment | Media & Entertainment | 🎬 | youtube, netflix, spotify, reddit, twitter |
| research-learning | Research & Learning | 📚 | wikipedia, arxiv, coursera, udemy, medium |
| personal | Personal | 🏠 | amazon, ebay, maps.google, weather, booking |
| tools-utilities | Tools & Utilities | 🔧 | chatgpt, chat.openai, translate.google, canva, figma |
| misc | Miscellaneous | 📌 | (uncategorized links) |

### 3.3 localStorage Schema

```json
{
  "customSubcategories": [],
  "linkAssignments": {
    "url": "section-id"
  },
  "customLinks": [
    { "url": "...", "title": "...", "domain": "..." }
  ],
  "subcategoryOrder": ["bob", "dai", ...],
  "deletedLinks": [
    { "url": "...", "title": "...", "categoryId": "...", "isOriginal": true }
  ]
}
```

---

## 4. Functional Requirements

### 4.1 Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| FR-001 | Display links organized by section in a responsive grid | ✅ Implemented |
| FR-002 | Search/filter links using "/" keyboard shortcut | ✅ Implemented |
| FR-003 | Drag-and-drop links between sections | ✅ Implemented |
| FR-004 | Drag-and-drop to reorder sections | ✅ Implemented |
| FR-005 | Delete links (move to trash) | ✅ Implemented |
| FR-006 | Restore deleted links from trash | ✅ Implemented |
| FR-007 | Persist customizations in localStorage | ✅ Implemented |
| FR-008 | Display current time | ✅ Implemented |
| FR-009 | Add new sections via modal | ⚠️ Partial (button exists) |
| FR-010 | Drop URLs from browser address bar | ✅ Implemented |

### 4.2 Script Features

| Feature | Description | Status |
|---------|-------------|--------|
| FR-101 | Parse HTML bookmark exports | ✅ Implemented |
| FR-102 | Filter bookmarks by age (configurable) | ✅ Implemented |
| FR-103 | Auto-categorize bookmarks by URL patterns | ✅ Implemented |
| FR-104 | Analyze Chrome browsing history | ✅ Implemented |
| FR-105 | Calculate frequency + recency score | ✅ Implemented |
| FR-106 | Merge bookmarks and history data | ✅ Implemented |
| FR-107 | Export by category | ✅ Implemented |
| FR-108 | Generate complete HTML from data | ✅ Implemented |

### 4.3 Future Features (Not Yet Implemented)

| Feature | Description | Priority |
|---------|-------------|----------|
| FF-001 | Dark/light mode toggle | Medium |
| FF-002 | Edit link titles inline | Medium |
| FF-003 | Custom themes/colors | Low |
| FF-004 | Weather widget | Low |
| FF-005 | Quick notes widget | Low |
| FF-006 | Multi-browser support (Firefox, Safari) | Medium |
| FF-007 | Import/export settings | Medium |

---

## 5. User Interface Specification

### 5.1 Layout

```
┌───────────────────────────────────────────────────┐
│  Yohoo!                                           │
│  Your Personal Start Page                         │
│  [Current Time]                                   │
├───────────────────────────────────────────────────┤
│  [ Search... ]  [+ Add Section]                   │
│  Press "/" to search | Drag sections and links    │
├───────────────────────────────────────────────────┤
│                                                   │
│  ┌─────────────────┐  ┌─────────────────┐        │
│  │ 🤖 Section 1    │  │ 🧠 Section 2    │        │
│  │ • Link 1       🗑│  │ • Link A       🗑│        │
│  │ • Link 2       🗑│  │ • Link B       🗑│        │
│  └─────────────────┘  └─────────────────┘        │
│                                                   │
│  ┌─────────────────┐  ┌─────────────────┐        │
│  │ 📊 Section 3    │  │ 💬 Section 4    │        │
│  │ • Link X       🗑│  │ • Link Y       🗑│        │
│  └─────────────────┘  └─────────────────┘        │
│                                                   │
├───────────────────────────────────────────────────┤
│  🗑️ Trash (N)  ▼                                  │
│  [Collapsed trash section]                        │
├───────────────────────────────────────────────────┤
│  © 2025 Yohoo                                     │
└───────────────────────────────────────────────────┘
```

### 5.2 Color Scheme (Light Cream Theme)

| Element | Color |
|---------|-------|
| Background | #FFEFCF |
| Section Background | #FFF8E7 |
| Border | #E6D5B0 |
| Logo/Headers | #6B4E3D |
| Links | #0066CC |
| Link Hover | #0052A3 |
| Muted Text | #8B7355 |
| Delete Icon | #D32F2F |
| Text Main | #2C2416 |

### 5.3 Responsive Breakpoints

- **Desktop**: Three-column fixed grid layout
- **Tablet** (≤992px): Two-column layout
- **Mobile** (≤768px): Single column layout

### 5.4 Interactive Features

- **Drag-and-drop**: Reorder sections and move links between sections
- **Search**: Press `/` to activate search, `Escape` to clear
- **Trash system**: Deleted links moved to collapsible trash section with restore capability
- **Debug console**: Toggle button in bottom-right corner for troubleshooting
- **External URL drop**: Drag URLs from browser address bar into sections

---

## 6. Scoring Algorithm

The Chrome history analyzer uses a combined scoring algorithm:

```python
recency_score = e^(-0.1 × days_ago)
normalized_frequency = min(visit_count / 50, 1.0)
combined_score = (normalized_frequency × 0.6) + (recency_score × 0.4)
```

- **Frequency weight**: 60%
- **Recency weight**: 40%
- **Decay factor**: 0.1 (exponential decay)
- **Max visits cap**: 50 visits

---

## 7. File Structure

```
yohoo/
├── yohoo.html              # Main start page (JS embedded inline)
├── bookmarks_*.html        # Exported bookmarks (multiple versions)
├── CLAUDE.md               # Claude Code instructions
├── SPECIFICATIONS.md       # This file
├── README.md               # Project documentation
├── Makefile                # Build commands
├── requirements.txt        # Python dependencies
├── .env.example            # Environment configuration template
├── .gitignore              # Git ignore rules
│
├── scripts/
│   ├── parse_bookmarks.py  # Bookmark parser
│   ├── analyze_history.py  # Chrome history analyzer
│   ├── utils.py            # Utility functions
│   ├── generate_html.py    # HTML generator
│   ├── logging_config.py   # Centralized logging setup
│   └── README.md           # Script documentation
│
├── data/
│   ├── bookmarks.json      # Parsed bookmarks
│   ├── bookmarks.csv       # CSV format
│   ├── categorize.csv      # Categorization data
│   ├── history.json        # Chrome history analysis
│   └── categories/         # By-category exports
│       ├── work-productivity.json
│       ├── development.json
│       ├── communication.json
│       ├── media-entertainment.json
│       ├── tools-utilities.json
│       └── uncategorized.json
│
├── input/                  # Source data files
│   └── bookmarks_*.html    # Bookmark exports
│
├── archive/                # Historical files and documents
│   ├── PROJECT_STATUS.md
│   ├── Design-Document-*.md
│   └── older HTML versions
│
├── logs/                   # Log files (empty directory)
├── tests/                  # Test files (empty directory)
└── .venv/                  # Python virtual environment
```

---

## 8. Security & Privacy

- **Local-first**: All data stored locally, no cloud dependencies
- **Chrome history access**: Read-only, copy database before reading
- **No external tracking**: No analytics or third-party services
- **No credentials stored**: No authentication required

---

## 9. Performance Requirements

| Metric | Target |
|--------|--------|
| Page load time | < 1 second |
| Search response | < 100ms |
| Drag-drop feedback | < 50ms |
| localStorage save | < 100ms |

---

## 10. Browser Support

| Browser | Support Level |
|---------|---------------|
| Chrome | Full |
| Firefox | Full |
| Safari | Full |
| Edge | Full |
| Mobile browsers | Full (responsive) |

---

## 11. Dependencies

### Python Scripts
- beautifulsoup4 == 4.12.3
- Python 3.8+
- Virtual environment (.venv) managed via Makefile

### Frontend
- No external dependencies
- Vanilla JavaScript
- CSS3 (Grid, Flexbox, CSS Variables)

---

## 12. Usage Workflow

### Initial Setup
```bash
# 1. Install dependencies
make install

# 2. Export bookmarks from Chrome
# Chrome → Bookmarks → Bookmark Manager → ⋮ → Export bookmarks
# Save to input/ directory

# 3. Parse bookmarks
make parse

# 4. Generate HTML
make generate

# 5. Open start page
make run
```

### Refresh Data
```bash
# Full workflow
make parse && make generate

# Or run scripts individually with virtual environment activated
. .venv/bin/activate

# Analyze recent Chrome history
python scripts/analyze_history.py --days 90 -o data/history.json

# Merge with bookmarks
python scripts/utils.py merge data/bookmarks.json data/history.json -o data/merged.json

# Regenerate HTML
python scripts/generate_html.py -b data/merged.json -o yohoo.html
```

---

## 13. Known Issues and Notes

### Current Implementation Notes
- **Test directory**: Empty `tests/` directory exists but no tests implemented yet. `make test` will fail.
- **Logs directory**: Empty `logs/` directory exists for future logging output.
- **Theme change**: Originally specified dark mauve theme, but implementation uses light cream theme.
- **JavaScript**: All JavaScript is embedded inline in yohoo.html, not in external file.
- **Chrome profile detection**: Scripts auto-detect Chrome profile (tries Profile 1 first, then Default on macOS).

### Future Improvements
- Implement test suite
- Add logging output to logs/ directory
- Consider theme toggle for dark/light modes
- Add documentation for customizing categories
- Create pytest fixtures for testing bookmark parsing and history analysis

---

## 14. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2025-12-08 | Initial design document |
| 0.2 | 2025-12-08 | Phase 1 implementation (static HTML, scripts) |
| 0.3 | 2025-12-09 | Drag-drop, localStorage, trash functionality |
| 1.0 | 2025-12-09 | Specification document created |
| 1.1 | 2025-12-09 | Updated to reflect actual implementation (light theme, inline JS, correct file structure, known issues); Fixed Makefile to reference correct script name |

---

**End of Specification**
