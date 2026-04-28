"""
Yohoo Local Proxy Server for Title Fetching

Version: 1.0
Purpose: Enable CORS-free page title fetching for yohoo.html
"""

from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
import logging
import socket
import sys
import os
import ipaddress
from urllib.parse import urlparse, unquote, urljoin

app = Flask(__name__)

# Configuration (hardcoded)
PORT = 3001
HOST = '127.0.0.1'
TIMEOUT = 10
MAX_REDIRECTS = 5
ALLOWED_SCHEMES = ['http', 'https', 'file']
MAX_URL_LENGTH = 2048
MAX_RESPONSE_BYTES = 512 * 1024
USER_AGENT = 'YohooTitleHelper/1.1'
ALLOWED_ORIGINS = {
    'null',
    'http://localhost',
    'http://127.0.0.1',
    'https://eivind-throndsen-private.github.io',
}


def add_cors_headers(response):
    """Allow Yohoo pages to call the localhost helper from browser JavaScript."""
    origin = request.headers.get('Origin')
    if origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Vary'] = 'Origin'
    elif not origin:
        response.headers['Access-Control-Allow-Origin'] = '*'

    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    # Required by Chrome Private Network Access when a public HTTPS page calls 127.0.0.1.
    response.headers['Access-Control-Allow-Private-Network'] = 'true'
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.after_request
def after_request(response):
    return add_cors_headers(response)


def origin_allowed() -> bool:
    origin = request.headers.get('Origin')
    return not origin or origin in ALLOWED_ORIGINS


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


def validate_url(url: str) -> tuple:
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

    if parsed.scheme in ['http', 'https']:
        is_safe, error = validate_public_http_target(parsed.hostname)
        if not is_safe:
            return False, error
    
    # Validate file:// URLs
    if parsed.scheme == 'file' and not parsed.path:
        return False, "Invalid file path"
    
    return True, None


def validate_public_http_target(hostname: str) -> tuple:
    """Reject private network targets to keep the helper from becoming a local SSRF bridge."""
    if not hostname:
        return False, "Invalid URL host"

    try:
        addresses = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return False, "Could not resolve URL host"

    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if (
            ip.is_private or
            ip.is_loopback or
            ip.is_link_local or
            ip.is_multicast or
            ip.is_reserved or
            ip.is_unspecified
        ):
            return False, "Private or local network targets are not allowed"

    return True, None


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


def fetch_file_title(url: str) -> tuple:
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


def fetch_http_title(url: str) -> tuple:
    """
    Fetch title from http:// or https:// URL
    Returns: (title, error)
    """
    try:
        session = requests.Session()
        current_url = url
        response = None

        for _redirect_count in range(MAX_REDIRECTS + 1):
            is_valid, validation_error = validate_url(current_url)
            if not is_valid:
                return None, validation_error

            response = session.get(
                current_url,
                timeout=TIMEOUT,
                allow_redirects=False,
                headers={'User-Agent': USER_AGENT},
                stream=True
            )

            if response.is_redirect:
                location = response.headers.get('Location')
                if not location:
                    return None, "Redirect without Location header"
                current_url = urljoin(current_url, location)
                response.close()
                continue

            break
        else:
            return None, "Too many redirects"

        if response is None:
            return None, "Request failed"

        response.raise_for_status()

        chunks = []
        total_bytes = 0
        for chunk in response.iter_content(chunk_size=16384, decode_unicode=False):
            if not chunk:
                continue
            chunks.append(chunk)
            total_bytes += len(chunk)
            if total_bytes >= MAX_RESPONSE_BYTES:
                break

        # Extract title
        encoding = response.encoding or response.apparent_encoding or 'utf-8'
        title = extract_title(b''.join(chunks).decode(encoding, errors='replace'))
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


def fetch_page_title(url: str) -> tuple:
    """
    Main function to fetch title from any supported URL type
    Returns: (title, error)
    """
    parsed = urlparse(url)
    
    if parsed.scheme == 'file':
        return fetch_file_title(url)
    else:
        return fetch_http_title(url)


@app.route('/fetch-title', methods=['GET', 'OPTIONS'])
def fetch_title_endpoint():
    """Fetch title from provided URL"""
    if request.method == 'OPTIONS':
        return ('', 204)

    if not origin_allowed():
        origin = request.headers.get('Origin')
        logging.warning(f"Rejected request from disallowed origin: {origin}")
        return jsonify({
            'title': None,
            'url': None,
            'error': 'Origin not allowed'
        }), 403

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


@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint"""
    if request.method == 'OPTIONS':
        return ('', 204)

    return jsonify({
        'status': 'ok',
        'service': 'yohoo-proxy',
        'version': '1.1'
    }), 200


if __name__ == '__main__':
    # Setup logging
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
