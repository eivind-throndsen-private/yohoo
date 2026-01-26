# DESIGN_PROXY.md

## Yohoo Local Proxy Server for Title Fetching

**Version:** 1.0  
**Date:** 2025-01-10  
**Purpose:** Enable CORS-free page title fetching for yohoo.html

---

## 1. Architecture Overview

### System Components

```
┌─────────────────┐         HTTP GET          ┌──────────────────┐
│  yohoo.html     │ ───────────────────────>  │  Proxy Server    │
│  (Browser)      │                            │  (localhost:3001)│
│                 │ <─────────────────────────│                  │
│  fetchTitle()   │     JSON Response          │  Flask + Requests│
└─────────────────┘                            └──────────────────┘
                                                        │
                                                        │ HTTP GET / File Read
                                                        ↓
                                                ┌──────────────────┐
                                                │  Target Resource │
                                                │  - Websites      │
                                                │  - Local Files   │
                                                └──────────────────┘
```

### Technology Stack

- **Server Framework:** Flask (lightweight Python web framework)
- **HTTP Client:** requests library (reliable, handles redirects/SSL)
- **HTML Parsing:** BeautifulSoup4 (robust title extraction)
- **Logging:** Python logging module
- **Runtime:** Python 3.x

---

## 2. API Specification

### Endpoint: Fetch Title

**Request:**
```
GET /fetch-title?url=<encoded_url>
Host: localhost:3001
```

**Parameters:**
- `url` (required): URL-encoded target resource address
  - Must start with `http://`, `https://`, or `file://`
  - Example: `?url=https%3A%2F%2Fgithub.com`
  - Example: `?url=file%3A%2F%2F%2FUsers%2Fname%2FDocuments%2Fpage.html`

**Success Response (200 OK):**
```json
{
  "title": "GitHub: Let's build from here",
  "url": "https://github.com",
  "error": null
}
```

**Error Response (400 Bad Request):**
```json
{
  "title": null,
  "url": "invalid-url",
  "error": "Invalid URL format. Must start with http://, https://, or file://"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "title": null,
  "url": "https://example.com",
  "error": "Timeout: Request took longer than 10 seconds"
}
```

### Endpoint: Health Check

**Request:**
```
GET /health
Host: localhost:3001
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "service": "yohoo-proxy",
  "version": "1.0"
}
```

---

## 3. Security Considerations

### Localhost-Only Binding
- Server binds to `127.0.0.1:3001` exclusively
- NOT accessible from network (no `0.0.0.0` binding)
- Prevents external access to proxy service

### Port Availability Check
- Verify port 3001 is available before starting
- Abort with clear error if port is already in use
- Provide actionable error message to user

### URL Validation
```python
ALLOWED_SCHEMES = ['http', 'https', 'file']
MAX_URL_LENGTH = 2048

def validate_url(url):
    - Check URL length (< 2048 chars)
    - Validate scheme (http/https/file only)
    - Parse with urllib.parse
    - For file://, validate path exists
```

### Request Limits
- **Timeout:** 10 seconds per HTTP request
- **Max Redirects:** 5
- **User-Agent:** Custom UA to identify proxy (`YohooProxy/1.0`)
- **No Authentication:** Service is local-only

### Data Privacy
- **Full URL logging:** Logs include complete URLs (acceptable for localhost)
- **No caching:** Each request fetches fresh
- **No persistence:** No database or file storage
- **No content logging:** Only log URLs and titles, not page content

---

## 4. Implementation Details

### 4.1 Server Structure

**File:** `proxy_server.py`

```python
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
import logging
import socket
import sys
from urllib.parse import urlparse, unquote

app = Flask(__name__)

# Configuration (hardcoded)
PORT = 3001
HOST = '127.0.0.1'
TIMEOUT = 10
MAX_REDIRECTS = 5
ALLOWED_SCHEMES = ['http', 'https', 'file']
MAX_URL_LENGTH = 2048
USER_AGENT = 'YohooProxy/1.0'
```

### 4.2 Core Functions

**1. Port Availability Check**
```python
def check_port_available(port: int) -> bool:
    """
    Check if port is available for binding
    Returns: True if available, False if in use
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', port))
        sock.close()
        return True
    except OSError:
        return False
```

**2. URL Validation**
```python
def validate_url(url: str) -> tuple[bool, str]:
    """
    Validate URL format and scheme
    Returns: (is_valid, error_message)
    """
    if not url:
        return False, "Missing url parameter"
    
    if len(url) > MAX_URL_LENGTH:
        return False, "URL too long (max 2048 characters)"
    
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL format"
    
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False, f"Invalid scheme. Use {', '.join(ALLOWED_SCHEMES)}"
    
    # Validate http/https URLs
    if parsed.scheme in ['http', 'https'] and not parsed.netloc:
        return False, "Invalid URL format"
    
    # Validate file:// URLs
    if parsed.scheme == 'file' and not parsed.path:
        return False, "Invalid file path"
    
    return True, None
```

**3. Title Extraction**
```python
def extract_title(html: str) -> str:
    """
    Extract <title> from HTML, with fallbacks
    Returns: title string or None
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Method 1: <title> tag
    title_tag = soup.find('title')
    if title_tag and title_tag.string:
        return title_tag.string.strip()
    
    # Method 2: meta og:title
    og_title = soup.find('meta', property='og:title')
    if og_title and og_title.get('content'):
        return og_title['content'].strip()
    
    # Method 3: meta twitter:title
    twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
    if twitter_title and twitter_title.get('content'):
        return twitter_title['content'].strip()
    
    return None
```

**4. File Handler**
```python
def fetch_file_title(url: str) -> tuple[str, str]:
    """
    Fetch title from local file:// URL
    Returns: (title, error)
    """
    try:
        parsed = urlparse(url)
        file_path = unquote(parsed.path)
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Extract title
        title = extract_title(html)
        if not title:
            return None, "No title found in file"
        
        return title, None
        
    except FileNotFoundError:
        return None, "File not found"
    except PermissionError:
        return None, "Permission denied to read file"
    except UnicodeDecodeError:
        return None, "File is not valid UTF-8 HTML"
    except Exception as e:
        return None, f"File error: {str(e)}"
```

**5. HTTP Handler**
```python
def fetch_http_title(url: str) -> tuple[str, str]:
    """
    Fetch title from http:// or https:// URL
    Returns: (title, error)
    """
    try:
        response = requests.get(
            url,
            timeout=TIMEOUT,
            allow_redirects=True,
            max_redirects=MAX_REDIRECTS,
            headers={'User-Agent': USER_AGENT}
        )
        response.raise_for_status()
        
        # Extract title
        title = extract_title(response.text)
        if not title:
            return None, "No title found in page"
        
        return title, None
        
    except requests.Timeout:
        return None, f"Timeout after {TIMEOUT} seconds"
    except requests.ConnectionError:
        return None, "Connection failed - check your internet connection"
    except requests.HTTPError as e:
        return None, f"HTTP {e.response.status_code}"
    except requests.TooManyRedirects:
        return None, "Too many redirects"
    except Exception as e:
        return None, f"Request error: {str(e)}"
```

**6. Main Fetch Function**
```python
def fetch_page_title(url: str) -> tuple[str, str]:
    """
    Main function to fetch title from any supported URL type
    Returns: (title, error)
    """
    parsed = urlparse(url)
    
    if parsed.scheme == 'file':
        return fetch_file_title(url)
    else:
        return fetch_http_title(url)
```

### 4.3 Flask Routes

```python
@app.route('/fetch-title', methods=['GET'])
def fetch_title_endpoint():
    """Fetch title from provided URL"""
    url = request.args.get('url')
    
    # Validate URL
    is_valid, error = validate_url(url)
    if not is_valid:
        logging.warning(f"Invalid URL: {url} - {error}")
        return jsonify({
            'title': None,
            'url': url,
            'error': error
        }), 400
    
    # Fetch title
    logging.info(f"Fetching title for: {url}")
    title, error = fetch_page_title(url)
    
    if error:
        logging.warning(f"Failed to fetch title for {url}: {error}")
        return jsonify({
            'title': None,
            'url': url,
            'error': error
        }), 500
    
    logging.info(f"Successfully fetched title for {url} → \"{title}\"")
    return jsonify({
        'title': title,
        'url': url,
        'error': None
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'yohoo-proxy',
        'version': '1.0'
    }), 200
```

### 4.4 Server Startup

```python
if __name__ == '__main__':
    # Setup logging
    import os
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('logs/proxy_server.log'),
            logging.StreamHandler()
        ]
    )
    
    # Check port availability
    if not check_port_available(PORT):
        print(f"\n❌ ERROR: Port {PORT} is already in use!\n")
        print("Either:")
        print(f"  1. Stop the process using port {PORT}")
        print(f"  2. Change PORT in proxy_server.py\n")
        sys.exit(1)
    
    # Start server
    print(f"\n✅ Starting Yohoo Proxy Server on http://{HOST}:{PORT}")
    print(f"📝 Logging to: logs/proxy_server.log")
    print("⏹️  Press CTRL+C to quit\n")
    
    app.run(host=HOST, port=PORT, debug=False)
```

### 4.5 Logging Strategy

**Log Levels:**
- **INFO:** Successful fetches, server start/stop
- **WARNING:** Validation failures, timeouts, missing titles
- **ERROR:** Unexpected server errors

**Log Format:**
```
[2025-01-10 14:05:23] INFO: Fetching title for: https://github.com/torvalds/linux
[2025-01-10 14:05:24] INFO: Successfully fetched title for https://github.com/torvalds/linux → "torvalds/linux: Linux kernel source tree"
[2025-01-10 14:05:28] WARNING: Failed to fetch title for https://slow-site.com: Timeout after 10 seconds
[2025-01-10 14:05:30] INFO: Fetching title for: file:///Users/name/Documents/index.html
[2025-01-10 14:05:30] INFO: Successfully fetched title for file:///Users/name/Documents/index.html → "My Homepage"
[2025-01-10 14:05:35] WARNING: Invalid URL: not-a-url - Invalid URL format
```

**Log File:** `logs/proxy_server.log` (auto-created on first run)

---

## 5. Error Handling

### Error Categories

| Error Type | HTTP Code | Response | Client Action |
|------------|-----------|----------|---------------|
| Missing URL param | 400 | `{"error": "Missing url parameter"}` | Show validation error |
| Invalid URL | 400 | `{"error": "Invalid URL format"}` | Show validation error |
| URL too long | 400 | `{"error": "URL too long"}` | Show validation error |
| Invalid scheme | 400 | `{"error": "Invalid scheme"}` | Show validation error |
| File not found | 500 | `{"error": "File not found"}` | Suggest checking path |
| Permission denied | 500 | `{"error": "Permission denied"}` | Suggest file permissions |
| Timeout | 500 | `{"error": "Timeout after 10s"}` | Suggest retry |
| Connection failed | 500 | `{"error": "Connection failed"}` | Suggest checking internet |
| HTTP error | 500 | `{"error": "HTTP 404"}` | Show HTTP status |
| No title found | 500 | `{"error": "No title found"}` | Suggest manual edit |

### Client-Side Handling (yohoo.html)

```javascript
async function fetchTitle(linkId, url, sectionId, buttonElement) {
    const PROXY_URL = 'http://localhost:3001/fetch-title';
    
    buttonElement.classList.add('fetching');
    buttonElement.disabled = true;
    
    try {
        // Call proxy
        const response = await fetch(
            `${PROXY_URL}?url=${encodeURIComponent(url)}`
        );
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Update title in appState
        const section = appState.sections.find(s => s.id === sectionId);
        const link = section.links.find(l => l.id === linkId);
        
        if (link) {
            const oldTitle = link.title;
            link.title = data.title;
            saveState();
            render();
            debugLog(`Fetched title: "${oldTitle}" → "${data.title}"`);
        }
        
    } catch (error) {
        debugLog('Fetch title error', { error: error.message });
        
        // Check if proxy is unreachable
        if (error.message === 'Failed to fetch') {
            alert('Proxy server not running.\n\nStart it with:\n  make proxy\n\nOr use the edit button (✏️) to set title manually.');
        } else {
            alert(`Could not fetch title:\n${error.message}\n\nUse the edit button (✏️) to set title manually.`);
        }
    } finally {
        buttonElement.classList.remove('fetching');
        buttonElement.disabled = false;
    }
}
```

---

## 6. Deployment

### 6.1 Installation

**Update `requirements.txt`:**
```
flask==3.0.0
requests==2.31.0
beautifulsoup4==4.12.2
```

**Install dependencies:**
```bash
make install
```

This will:
1. Create/activate virtual environment (`.venv`)
2. Install all dependencies including Flask, requests, BeautifulSoup4

### 6.2 Running the Proxy

**Update `Makefile`:**
```makefile
.PHONY: proxy
proxy: .venv
	@echo "Starting Yohoo Proxy Server..."
	. ./.venv/bin/activate && python proxy_server.py
```

**Start server:**
```bash
make proxy
```

**Expected output:**
```
Starting Yohoo Proxy Server...

✅ Starting Yohoo Proxy Server on http://127.0.0.1:3001
📝 Logging to: logs/proxy_server.log
⏹️  Press CTRL+C to quit

[2025-01-10 14:00:00] INFO: Starting server...
 * Serving Flask app 'proxy_server'
 * Running on http://127.0.0.1:3001
```

**Stop server:**
```
Ctrl+C
```

**Error if port in use:**
```
❌ ERROR: Port 3001 is already in use!

Either:
  1. Stop the process using port 3001
  2. Change PORT in proxy_server.py
```

### 6.3 Testing

**Test 1: Health check**
```bash
curl http://localhost:3001/health
```
Expected: `{"status":"ok","service":"yohoo-proxy","version":"1.0"}`

**Test 2: Fetch HTTP title**
```bash
curl "http://localhost:3001/fetch-title?url=https%3A%2F%2Fgithub.com"
```
Expected: `{"title":"GitHub: Let's build from here","url":"https://github.com","error":null}`

**Test 3: Fetch file title**
```bash
curl "http://localhost:3001/fetch-title?url=file%3A%2F%2F%2FUsers%2Fname%2Ftest.html"
```
Expected: `{"title":"Test Page","url":"file:///Users/name/test.html","error":null}`

**Test 4: Invalid URL**
```bash
curl "http://localhost:3001/fetch-title?url=invalid"
```
Expected: `{"title":null,"url":"invalid","error":"Invalid scheme. Use http, https, file"}`

**Test 5: From yohoo.html**
1. Start proxy: `make proxy`
2. Open yohoo.html in browser
3. Hover over any link
4. Click 🔄 button
5. Verify title updates
6. Check debug console for logs
7. Check `logs/proxy_server.log` for server logs

---

## 7. File Structure

```
yohoo/
├── proxy_server.py          # New: Flask proxy server
├── requirements.txt         # Updated: Add flask, requests, bs4
├── Makefile                 # Updated: Add 'make proxy' command
├── yohoo.html              # Updated: Use proxy in fetchTitle()
├── DESIGN_PROXY.md         # New: This document
├── logs/
│   └── proxy_server.log    # Auto-created: Server logs
└── .venv/                  # Python virtual environment
```

---

## 8. Summary

This design provides a **simple, secure, and focused** solution to the CORS problem:

✅ **Single Purpose:** Fetch page titles only  
✅ **Privacy First:** No data storage, localhost-only, full URL logging acceptable  
✅ **Multi-Source:** Supports http://, https://, and file:// URLs  
✅ **Port Safety:** Aborts with error if port 3001 is unavailable  
✅ **Easy Setup:** One command to start (`make proxy`)  
✅ **Graceful Errors:** Clear feedback for all failure modes  
✅ **Easy to Remove:** Self-contained, no dependencies on other code  
✅ **Hardcoded Config:** No config files, simple to understand and modify  

---

## 9. Implementation Checklist

- [ ] Create `proxy_server.py` with all functions
- [ ] Update `requirements.txt` with Flask, requests, BeautifulSoup4
- [ ] Update `Makefile` with `proxy` target
- [ ] Modify `fetchTitle()` in `yohoo.html` to use proxy
- [ ] Create `logs/` directory (auto-created by server)
- [ ] Test with http:// URLs
- [ ] Test with https:// URLs
- [ ] Test with file:// URLs
- [ ] Test port conflict handling
- [ ] Test error scenarios
- [ ] Update README.md with proxy usage instructions

---

**End of Design Document**
