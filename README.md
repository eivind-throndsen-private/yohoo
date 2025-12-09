# Yohoo! - Personal Start Page

A smart, customizable browser start page that combines your bookmarks with browser history analysis to surface your most frequently visited links.

## Features

- 🎨 **Modern Dark Theme** - Clean, easy-on-the-eyes interface
- 🔍 **Fast Search** - Press `/` to quickly search your links
- 🎯 **Smart Categorization** - Automatically organizes links into categories
- 📊 **Usage Analytics** - Analyzes Chrome history to prioritize frequently visited sites
- 🎭 **Drag & Drop** - Reorganize links and sections with ease
- 🗑️ **Trash System** - Soft-delete links with undo capability
- 💾 **Local Storage** - All customizations saved in your browser
- 🔄 **Auto-generation** - Python scripts to refresh from bookmarks + history

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Chrome (for history analysis)
- macOS, Linux, or Windows

### Installation

1. **Clone or download the project**

2. **Install dependencies**
   ```bash
   make install
   ```

3. **Set up configuration (optional)**
   ```bash
   cp .env.example .env
   # Edit .env with your preferences
   ```

4. **Open the start page**
   ```bash
   make run
   ```

That's it! The page will open in your default browser.

## Usage

### Using the Start Page

- **Search**: Press `/` or click the search box to filter links
- **Reorganize**: Drag and drop links between sections
- **Delete Links**: Hover over a link and click the 🗑️ icon
- **Restore Links**: Expand the Trash section and click "Restore"
- **Add Sections**: Click "+ Add Section" to create new categories
- **Drop URLs**: Drag external URLs into sections to add them

### Generating from Bookmarks & History

1. **Export Chrome bookmarks** to `input/` directory

2. **Parse bookmarks**
   ```bash
   make parse
   ```

3. **Generate HTML** (combines bookmarks + history data)
   ```bash
   make generate
   ```

4. **Refresh all** (full workflow)
   ```bash
   make parse && make generate
   ```

## Project Structure

```
yohoo/
├── yohoo.html          # Main start page (generated or manual)
├── yohoo.js            # Client-side JavaScript
├── Makefile            # Build and run commands
├── requirements.txt    # Python dependencies
├── SPECIFICATIONS.md   # Functional specification
├── TODO.md            # Development roadmap
├── input/             # Input files (bookmarks)
├── output/            # Generated files
├── logs/              # Application logs
├── temp/              # Temporary/interim work
├── data/              # Processed data files
│   ├── bookmarks.json
│   ├── history.json
│   └── categories/
├── scripts/           # Python scripts
│   ├── parse_bookmarks.py
│   ├── analyze_history.py
│   ├── generate_html.py
│   └── utils.py
└── tests/             # Test files
```

## Available Commands

```bash
make help      # Show available commands
make install   # Create virtual environment and install dependencies
make run       # Open yohoo.html in browser
make parse     # Parse bookmarks file
make generate  # Generate HTML from data
make test      # Run tests
make format    # Format Python code
make clean     # Remove generated files and caches
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

- `CHROME_HISTORY_PATH` - Path to Chrome history database
- `BOOKMARKS_FILE` - Input bookmarks HTML file
- `HISTORY_DAYS` - Days of history to analyze (default: 90)
- `MIN_VISITS` - Minimum visits to include a site (default: 3)
- `LOG_LEVEL` - Logging verbosity (DEBUG, INFO, WARNING, ERROR)

## Scripts

### parse_bookmarks.py

Parses Chrome/Firefox HTML bookmarks and categorizes them.

```bash
python scripts/parse_bookmarks.py input/bookmarks.html -o data/bookmarks.json
python scripts/parse_bookmarks.py --verbose    # With detailed logging
python scripts/parse_bookmarks.py --debug      # Debug mode
```

### analyze_history.py

Analyzes Chrome browsing history and scores URLs by frequency.

```bash
python scripts/analyze_history.py --days 90 -o data/history.json
python scripts/analyze_history.py --verbose
```

### generate_html.py

Generates the start page HTML from bookmark and history data.

```bash
python scripts/generate_html.py -b data/bookmarks.json -o yohoo.html
```

### utils.py

Utility functions for merging and exporting data.

```bash
python scripts/utils.py merge data/bookmarks.json data/history.json -o data/merged.json
```

## Setting as Browser Home Page

### Chrome
1. Open Chrome Settings
2. Navigate to "On startup"
3. Select "Open a specific page or set of pages"
4. Click "Add a new page"
5. Enter: `file:///path/to/yohoo/yohoo.html`

### Firefox
1. Open Firefox Settings
2. Navigate to "Home"
3. Under "Homepage and new windows", select "Custom URLs"
4. Enter: `file:///path/to/yohoo/yohoo.html`

### Safari
1. Open Safari Preferences
2. Navigate to "General"
3. Set Homepage to: `file:///path/to/yohoo/yohoo.html`

## Customization

### Adding Categories

Edit the `CATEGORY_KEYWORDS` dictionary in `scripts/parse_bookmarks.py`:

```python
CATEGORY_KEYWORDS = {
    "My Category": ["keyword1", "keyword2"],
    # ...
}
```

### Styling

Edit the `<style>` section in `yohoo.html` to customize colors, fonts, and layout.

### Icons

Change section icons by editing the emoji in the subcategory headers:

```html
<span class="subcategory-icon">🚀</span>
```

## Troubleshooting

### Virtual environment not activating
```bash
make clean
make install
```

### Missing Python dependencies
```bash
. .venv/bin/activate
pip install -r requirements.txt
```

### Links not appearing
1. Check that bookmarks are in `input/` directory
2. Run `make parse` to regenerate bookmarks.json
3. Check logs in `logs/` directory

### Debug mode
Press the "Debug" button in the bottom-right corner to view:
- Event log
- localStorage contents
- Error messages

## Development

### Running Tests
```bash
make test
```

### Code Formatting
```bash
make format
```

### Logging Levels

All scripts support logging options:
- `--verbose` - INFO level logging
- `--debug` - DEBUG level logging
- `--quiet` - ERROR level only

## Contributing

1. Check `TODO.md` for planned features
2. Review `SPECIFICATIONS.md` for functional requirements
3. Follow Python coding standards (see `.flake8`, use `black` formatter)
4. Add tests for new functionality
5. Update documentation as needed

## License

Personal project - use as you wish!

## Acknowledgments

- Inspired by browser start pages like Momentum and Tabliss
- Uses HTML5 drag-and-drop API
- Built with vanilla JavaScript (no frameworks)

---

**Version**: 1.0  
**Last Updated**: December 2025  
**Author**: Eivind Throndsen
