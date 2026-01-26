# Design Document: Personal Start Page (Yohoo)
**Project**: Yohoo - Yahoo-like Personal Start Page
**Author**: Eivind Throndsen
**Date**: 2025-12-08
**Status**: Design Review

---

## 1. Executive Summary

This document outlines the design for a personal, customizable start page inspired by Yahoo's portal design. The application will aggregate frequently-used links, organize them thematically, and provide intelligent bookmark management based on browsing history and recency.

---

## 2. Project Goals

- Create a fast, clean start page displaying frequently-used links organized by category
- Support manual updates and reorganization of links
- Automatically suggest links based on Chrome browsing history
- Filter and display bookmarks less than one year old
- Provide a useful category scaffold for organizing bookmarks thematically

---

## 3. System Architecture

### 3.1 High-Level Components

```
┌─────────────────────────────────────────┐
│         Frontend (Web Interface)        │
│  - Link Display Grid/Cards              │
│  - Category Navigation                  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Backend/Data Layer              │
│  - Link Storage (static HTML)           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Data Collection Scripts            │
│  - Chrome History Parser                │
│  - Bookmark Parser                      │
│  - Usage Frequency Analyzer             │
└─────────────────────────────────────────┘
```

### 3.2 Technology Stack Recommendations

**Frontend:**
- HTML5/CSS3 for structure and styling
- Vanilla JavaScript or lightweight framework (Alpine.js/Petite-Vue)
- Responsive grid layout for link organization

**Backend:**
- CSV file or similar, being used to generate static HTML 
  

**Scripts:**
- Python scripts for Chrome history analysis
- Chrome History location: `~/Library/Application Support/Google/Chrome/Default/History` (macOS)
- Chrome Bookmarks location: `~/Library/Application Support/Google/Chrome/Default/Bookmarks`

---

## 4. Data Models

### 4.1 Link/Bookmark Structure

```json
{
  "id": "unique-id",
  "title": "Link Title",
  "url": "https://example.com",
  "category": "category-slug",
  "favicon": "url-to-favicon",
  "addedDate": "2025-12-08T10:00:00Z",
  "lastVisited": "2025-12-08T10:00:00Z",
  "visitCount": 42,
  "isActive": true,
  "source": "manual|history|bookmark"
}
```

### 4.2 Category Structure

```json
{
  "id": "category-slug",
  "name": "Category Name",
  "icon": "icon-name",
  "order": 1,
  "color": "#hexcolor"
}
```

---

## 5. Proposed Category Scaffold

Based on common personal usage patterns, suggest the following initial categories:

1. **Work & Productivity**
   - Project management tools
   - Communication platforms
   - Documentation/wikis

2. **Development**
   - GitHub, GitLab
   - Stack Overflow
   - Dev tools and documentation

3. **Communication**
   - Email clients
   - Slack, Teams, Discord
   - Calendar apps

4. **Media & Entertainment**
   - YouTube, Netflix, Spotify
   - News sites
   - Social media

5. **Research & Learning**
   - Online courses
   - Documentation sites
   - Technical blogs

6. **Personal**
   - Health/fitness
   - Personal projects
   - Utilities

7. **Tools & Utilities**
   - File conversion
   - Design tools
   - Online calculators

---

## 6. Chrome History Analysis Script

### 6.1 Functionality

The script will:
- Copy Chrome History database to avoid locking issues
- Query visit counts and last visit timestamps
- Filter by minimum visit count threshold (e.g., 5+ visits)
- Filter by date range (e.g., last 90 days)
- Exclude common low-value URLs (google.com searches, localhost, etc.)
- Score and rank URLs by frequency and recency
- Output candidate links for manual review

### 6.2 Key Metrics

```python
score = (visit_count * 0.6) + (recency_score * 0.4)
```

- **visit_count**: Number of times URL was visited
- **recency_score**: Weighted score based on how recently visited (exponential decay)

---

## 7. Bookmark Parser Script

### 7.1 Functionality

The script will:
- Parse Chrome Bookmarks JSON file
- Extract all bookmarks with metadata
- Filter bookmarks added within last 365 days
- Map to suggested categories using keyword matching
- Detect duplicates with existing links
- Output organized bookmark list to CSV for import

---

## 8. User Interface Design

### 8.1 Main View

```
┌───────────────────────────────────────────────────┐
│  Yohoo                              [Edit] [+Add] │
├───────────────────────────────────────────────────┤
│                                                   │
│  ┌─ Work & Productivity ──────────────────────┐  │
│  │  [Icon] GitHub    [Icon] Gmail            │  │
│  │  [Icon] Slack     [Icon] Notion           │  │
│  └───────────────────────────────────────────┘  │
│                                                   │
│  ┌─ Development ────────────────────────────┐    │
│  │  [Icon] Stack Overflow  [Icon] MDN       │    │
│  │  [Icon] Python Docs     [Icon] AWS       │    │
│  └───────────────────────────────────────────┘  │
│                                                   │
│  ┌─ Media & Entertainment ──────────────────┐    │
│  │  [Icon] YouTube   [Icon] Netflix         │    │
│  └───────────────────────────────────────────┘  │
└───────────────────────────────────────────────────┘
```

### 8.2 Edit Mode

- Drag-and-drop to reorder links within categories
- Click to edit link details
- Delete/archive links
- Create new categories
- Bulk import from history/bookmarks

---

## 9. Features & Functionality

### 9.1 Phase 1 (MVP)

- Static HTML start page with hardcoded links
- Manual category organization
- Responsive grid layout
- Favicon display

### 9.2 Phase 2

- Chrome history analyzer script
- Bookmark parser script
- CSV-based link storage

### 9.3 Phase 3

- Backend API for CRUD operations
- Persistent storage (SQLite)
- Auto-refresh suggestions from history
- Search functionality
- Dark mode toggle

### 9.4 Future Enhancements

- Multi-browser support (Firefox, Safari)
- Cloud sync across devices
- Import/export functionality
- Custom themes
- Widget support (weather, time, quick notes)

---

## 10. File Structure

```
yohoo/
├── backend/
│   ├── models.py           # Data models
│   └── database.py         # DB connection/queries
├── scripts/
│   ├── analyze_history.py  # Chrome history analyzer
│   ├── parse_bookmarks.py  # Bookmark parser
│   └── utils.py            # Shared utilities
├── frontend/
│   ├── index.html          # Main start page
│   ├── styles.css          # Styling
├── data/
│   ├── links.json          # Link storage
│   └── categories.json     # Category definitions
├── venv/                   # Python virtual environment
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
└── SPECIFICATIONS.md       # Technical Project specification 

```

---

## 11. Security & Privacy Considerations

- **Local-first design**: All data stored locally, no cloud dependencies
- **Chrome history access**: Read-only access, copy database before reading
- **No external tracking**: No analytics or third-party services
- **Optional**: Password protection for edit mode

---

## 12. Development Approach

### 12.1 Incremental Development

1. Build static HTML prototype with sample links
2. Implement category scaffold manually
3. Develop Chrome history analyzer as standalone script
4. Develop bookmark parser as standalone script
5. Create JSON data structure and storage
6. Editing using text / JSON editor 

### 12.2 Testing Strategy

- Manual testing for UI/UX
- Unit tests for history/bookmark parsers
- Test with sample Chrome profiles
- Verify cross-browser compatibility

---

## 13. Open Questions for Review

1. **Hosting**: Local HTML file
2. **Edit workflow**: In-place editing
3. **Data format**: JSON files or CSV
4. **Automation**: History analysis run manually 
5. **Browser support**: Support multiple browsers (Plain HTML) 
6. **Visual design**: Minimalist interface
7. **Link suggestions**: Auto-add above threshold

---

## 14. Next Steps

After design review approval:

1. Create detailed technical specification document
2. Define API contracts and data schemas
3. Create mockups/wireframes for UI
4. Set up development environment
5. Begin Phase 1 MVP implementation

---

## 15. Success Metrics

- Start page loads in < 1 second
- Contains 50-100 frequently-used links
- Categories are logically organized and intuitive
- History analyzer surfaces 80%+ relevant suggestions
- Edit workflow takes < 30 seconds per link
- User visits start page as default browser home page

---

**End of Design Document**

*This document is ready for review. Please provide feedback on architecture decisions, proposed features, and open questions before proceeding to detailed specification.*
