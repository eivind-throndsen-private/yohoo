# Yohoo Scripts

Python scripts for analyzing bookmarks and browsing history to populate your personal start page.

## Scripts

### 1. parse_bookmarks.py

Parses HTML bookmark exports and extracts links less than 1 year old.

**Usage:**
```bash
# Parse bookmarks and show summary
python3 scripts/parse_bookmarks.py bookmarks_08.12.2025.html

# Export to JSON
python3 scripts/parse_bookmarks.py bookmarks_08.12.2025.html \
    --output data/bookmarks.json --format json

# Export to CSV
python3 scripts/parse_bookmarks.py bookmarks_08.12.2025.html \
    --output data/bookmarks.csv --format csv

# Only include bookmarks from last 180 days
python3 scripts/parse_bookmarks.py bookmarks_08.12.2025.html \
    --max-age 180 --output data/bookmarks_recent.json
```

**Options:**
- `--output, -o`: Output file path
- `--format, -f`: Output format (`json` or `csv`)
- `--max-age, -m`: Maximum age in days (default: 365)

**Features:**
- Filters bookmarks by age
- Auto-categorizes into 7 categories
- Extracts favicons
- Deduplicates by URL

---

### 2. analyze_history.py

Analyzes Chrome browsing history and surfaces frequently visited URLs.

**Usage:**
```bash
# Analyze last 90 days with minimum 5 visits
python3 scripts/analyze_history.py --days 90 --min-visits 5

# Export to JSON
python3 scripts/analyze_history.py --days 90 --min-visits 3 \
    --output data/history.json

# Use custom Chrome profile
python3 scripts/analyze_history.py \
    --history-path "/path/to/Chrome/Profile/History" \
    --output data/history.json
```

**Options:**
- `--history-path, -p`: Path to Chrome History database (auto-detected if not provided)
- `--output, -o`: Output file path
- `--format, -f`: Output format (`json` or `csv`)
- `--days, -d`: Number of days to analyze (default: 90)
- `--min-visits, -m`: Minimum visit count (default: 3)
- `--top, -t`: Number of top URLs to display (default: 20)

**Features:**
- Analyzes visit frequency and recency
- Calculates combined score (60% frequency, 40% recency)
- Excludes low-value URLs (Google searches, localhost, etc.)
- Auto-categorizes URLs

**Scoring Algorithm:**
```
recency_score = e^(-0.1 × days_ago)
normalized_frequency = min(visit_count / 50, 1.0)
combined_score = (normalized_frequency × 0.6) + (recency_score × 0.4)
```

---

### 3. utils.py

Utility functions for merging data and generating HTML.

**Commands:**

#### Merge bookmarks and history
```bash
python3 scripts/utils.py merge \
    data/bookmarks.json \
    data/history.json \
    --output data/merged_links.json
```

#### Generate HTML snippet
```bash
# Generate HTML for all links
python3 scripts/utils.py html data/bookmarks.json

# Generate HTML for specific category
python3 scripts/utils.py html data/bookmarks.json \
    --category work-productivity
```

#### Export by category
```bash
python3 scripts/utils.py export-categories data/bookmarks.json \
    --output-dir data/categories
```

---

## Categories

The scripts automatically categorize URLs into these categories:

1. **work-productivity** - Gmail, Calendar, Notion, Drive, Docs, Trello, Asana
2. **development** - GitHub, Stack Overflow, MDN, Python Docs, AWS, npm
3. **communication** - Slack, Teams, Discord, Zoom, Meet
4. **media-entertainment** - YouTube, Netflix, Spotify, Reddit, Twitter
5. **research-learning** - Wikipedia, arXiv, Coursera, Medium, Scholar
6. **personal** - Amazon, Maps, Weather, Banking, Shopping
7. **tools-utilities** - ChatGPT, Translate, Canva, Figma, Miro, Analytics

Uncategorized items are marked as `uncategorized`.

---

## Data Files

After running the scripts, you'll have:

```
data/
├── bookmarks.json       # Parsed bookmarks
├── bookmarks.csv        # Bookmarks in CSV format
├── history.json         # Analyzed Chrome history
├── merged_links.json    # Combined bookmarks + history
└── categories/          # Links split by category
    ├── work-productivity.json
    ├── development.json
    └── ...
```

---

## Dependencies

Install required Python packages:

```bash
pip install beautifulsoup4
```

Or create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install beautifulsoup4
```

---

## Chrome History Location

The script auto-detects Chrome history location:

- **macOS**: `~/Library/Application Support/Google/Chrome/Default/History`
- **Linux**: `~/.config/google-chrome/Default/History`
- **Windows**: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\History`

If you use a different profile, use `--history-path` to specify the location.

---

## Example Workflow

```bash
# 1. Export your bookmarks from Chrome
# Chrome → Bookmarks → Bookmark Manager → ⋮ → Export bookmarks

# 2. Parse bookmarks
python3 scripts/parse_bookmarks.py bookmarks_08.12.2025.html \
    --output data/bookmarks.json

# 3. Analyze Chrome history
python3 scripts/analyze_history.py --days 90 --min-visits 5 \
    --output data/history.json

# 4. Merge both sources
python3 scripts/utils.py merge \
    data/bookmarks.json \
    data/history.json \
    --output data/merged_links.json

# 5. Export by category for easier integration
python3 scripts/utils.py export-categories data/merged_links.json \
    --output-dir data/categories
```

---

## Notes

- The Chrome history analyzer creates a temporary copy of the database (Chrome locks the original)
- Temporary files are automatically cleaned up
- URLs longer than 200 characters are excluded
- Google search URLs and localhost URLs are automatically filtered out
- The scripts use UTF-8 encoding to handle international characters
