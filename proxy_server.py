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
    
    # Validate file:// URLs
    if parsed.scheme == 'file' and not parsed.path:
        return False, "Invalid file path"
    
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
        response = requests.get(
            url,
            timeout=TIMEOUT,
            allow_redirects=True,
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


@app.route('/fetch-title', methods=['GET'])
def fetch_title_endpoint():
    """Fetch title from provided URL"""
    url = request.args.get('url')
    
    # Validate URL
    is_valid, error = validate_url(url)
    if not is_valid:
        logging.warning(f"Invalid URL: {url} - {error}")
        response = jsonify({
            'title': None,
            'url': url,
            'error': error
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 400
    
    # Fetch title
    logging.info(f"Fetching title for: {url}")
    title, error = fetch_page_title(url)
    
    if error:
        logging.warning(f"Failed to fetch title for {url}: {error}")
        response = jsonify({
            'title': None,
            'url': url,
            'error': error
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500
    
    logging.info(f"Successfully fetched title for {url} → \"{title}\"")
    response = jsonify({
        'title': title,
        'url': url,
        'error': None
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    response = jsonify({
        'status': 'ok',
        'service': 'yohoo-proxy',
        'version': '1.0'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


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
