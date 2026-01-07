# Yohoo! - Personal Start Page

A smart, customizable, editable browser start page with powerful settings and customization options.

## Features

- ⚙️ **Settings Modal** - Centralized configuration for all customizations
- 🎨 **Custom Background Colors** - Choose from presets or pick any color
- 🔍 **Fast Search** - Press `/` to quickly search your links
- 🎯 **Smart Categorization** - Automatically organizes links into categories
- 📊 **Usage Analytics** - Analyzes Chrome history to prioritize frequently visited sites
- 🎭 **Drag & Drop** - Reorganize links and sections with ease
- 🗑️ **Trash System** - Soft-delete with restore and empty trash options
- 💾 **Data Management** - Export and import your complete configuration
- 💾 **Local Storage** - All customizations saved in your browser

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
- **Settings**: Click ⚙️ Settings in the header to access configuration
- **Reorganize**: Drag and drop links between sections
- **Delete Links**: Hover over a link and click the 🗑️ icon
- **Restore Links**: Expand the Trash section and click "Restore"
- **Empty Trash**: Open Settings → Trash Management → Empty Trash (permanent)
- **Add Sections**: Click "+ Add Section" to create new categories
- **Drop URLs**: Drag external URLs into sections to add them
- **Customize Colors**: Settings → Appearance → Background Color
- **Export/Import**: Settings → Data Management → Export/Import Data

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

### Using the Proxy Server for Title Fetching

The proxy server allows you to automatically fetch and update page titles for your links, bypassing CORS restrictions.

#### Starting the Proxy

```bash
make proxy
```

The server will start on `http://localhost:3001` and display:
```
✅ Starting Yohoo Proxy Server on http://127.0.0.1:3001
📝 Logging to: logs/proxy_server.log
⏹️  Press CTRL+C to quit
```

#### Using the Fetch Title Feature

1. **Start the proxy server** in a terminal: `make proxy`
2. **Open yohoo.html** in your browser
3. **Hover over any link** to reveal the action buttons
4. **Click the 🔄 button** to fetch the page title

The title will be automatically updated and saved. If the proxy is not running, you'll get a helpful error message with instructions.

#### Proxy Features

- ✅ **CORS-Free Fetching** - Works with any website, including local files
- ✅ **Smart Title Extraction** - Tries `<title>`, `og:title`, and `twitter:title` tags
- ✅ **Multiple URL Schemes** - Supports `http://`, `https://`, and `file://` URLs
- ✅ **Port Conflict Detection** - Clear error if port 3001 is already in use
- ✅ **Detailed Logging** - All requests logged to `logs/proxy_server.log`
- ✅ **Security** - Localhost-only binding, no external access
- ✅ **Timeout Protection** - 10-second timeout for unresponsive sites

#### Stopping the Proxy

Press `Ctrl+C` in the terminal where the proxy is running.

#### Troubleshooting the Proxy

**Port already in use:**
```bash
# Find what's using port 3001
lsof -i :3001

# Kill the process or change PORT in proxy_server.py
```

**Proxy not responding:**
- Check that you ran `make install` to install Flask and dependencies
- Verify the proxy is running with: `curl http://localhost:3001/health`
- Check logs in `logs/proxy_server.log`

**Title fetch fails:**
- Some sites block requests from unknown user agents
- Timeout after 10 seconds for slow-loading pages
- Use the edit button (✏️) to manually set titles for problematic sites

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
make proxy     # Start local proxy server for title fetching
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

### Settings Modal

Access the Settings modal by clicking the ⚙️ button in the header. Features include:

#### Appearance
- **Background Color**: Choose from 5 presets or pick any custom color
  - Light Cream (default)
  - Soft Blue
  - Mint Green
  - Soft Pink
  - Dark Mode
- **Font Size**: Adjust text size with slider (1.1x - 2.4x)

#### Data Management
- **Export Data**: Download complete backup as timestamped JSON file
- **Import Data**: Restore from previous backup (auto-backup created before import)

#### Trash Management
- **Empty Trash**: Permanently delete all items in trash (with confirmation)
- Shows trash item count

#### Developer Tools
- **Debug Console**: Toggle visibility of debug console with timestamped logs

### Debug Mode
Enable the debug console in Settings → Developer Tools to view:
- Event log with timestamps
- Drag-and-drop operations
- localStorage operations
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

**Version**: 1.2
**Last Updated**: January 2026
**Author**: Eivind Throndsen

### Changelog

#### v1.2 (January 2026)
- ✨ Added Settings Modal with centralized configuration
- 🎨 Added background color customization with 5 presets + custom color picker
- 🗑️ Added Empty Trash feature for permanent deletion
- 💾 Moved Export/Import to Settings for better organization
- 🐛 Moved Debug console toggle to Settings
- 🔧 Improved initialization with DOMContentLoaded wrapper
- ✨ Added ESC key priority handling (modal first, then search)
- 🎯 Added font slider synchronization between settings and main UI
- ♿ Added ARIA labels for better accessibility

#### v1.0 (December 2025)
- Initial release with core functionality
