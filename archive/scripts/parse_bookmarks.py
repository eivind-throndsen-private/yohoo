#!/usr/bin/env python3
"""
Bookmark Parser for Yohoo Start Page
Parses HTML bookmark exports and extracts links less than 1 year old
"""

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urlparse
from typing import List, Dict, Any
import json
import re
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.logging_config import setup_logging, add_logging_arguments


# Category mapping based on URL patterns and keywords
CATEGORY_KEYWORDS = {
    'work-productivity': [
        'mail.google', 'calendar.google', 'notion', 'drive.google',
        'docs.google', 'sheets.google', 'slides.google', 'workspace',
        'trello', 'asana', 'monday', 'clickup'
    ],
    'development': [
        'github', 'gitlab', 'stackoverflow', 'developer.mozilla',
        'docs.python', 'npmjs', 'pypi', 'docker', 'kubernetes',
        'console.cloud.google', 'aws.amazon', 'vercel', 'netlify'
    ],
    'browser-settings': [
        'chrome://settings', 'chrome-settings',
        'chrome://extensions', 'chrome-extensions',
        'firefox:preferences', 'about:preferences',
        'about:addons', 'about:config',
        'edge://settings', 'edge-settings',
        'edge://extensions',
        'brave://settings', 'brave-settings',
        'brave://extensions'
    ],
    'communication': [
        'slack', 'teams.microsoft', 'discord', 'zoom', 'meet.google',
        'chat.', 'telegram', 'whatsapp'
    ],
    'media-entertainment': [
        'youtube', 'netflix', 'spotify', 'reddit', 'twitter', 'facebook',
        'instagram', 'tiktok', 'twitch', 'vimeo'
    ],
    'research-learning': [
        'wikipedia', 'arxiv', 'coursera', 'udemy', 'medium', 'substack',
        'scholar.google', 'researchgate', 'jstor'
    ],
    'personal': [
        'amazon', 'ebay', 'maps.google', 'weather', 'booking',
        'airbnb', 'paypal', 'bank', 'finn.no'
    ],
    'tools-utilities': [
        'chatgpt', 'chat.openai', 'translate.google', 'canva', 'figma',
        'miro', 'excalidraw', 'analytics', 'grafana'
    ]
}


def parse_bookmarks_html(filepath: str, max_age_days: int = 365, logger=None) -> List[Dict[str, Any]]:
    """
    Parse HTML bookmarks file and extract bookmarks

    Args:
        filepath: Path to HTML bookmarks file
        max_age_days: Maximum age of bookmarks to include (default 365 days)
        logger: Logger instance (optional)

    Returns:
        List of bookmark dictionaries
    """
    if logger:
        logger.info(f"Parsing bookmarks from: {filepath}")
        logger.info(f"Maximum age: {max_age_days} days")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        if logger:
            logger.error(f"File not found: {filepath}")
        raise
    except Exception as e:
        if logger:
            logger.error(f"Error reading file: {e}")
        raise

    soup = BeautifulSoup(content, 'html.parser')
    bookmarks = []

    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    cutoff_timestamp = int(cutoff_date.timestamp())
    
    if logger:
        logger.debug(f"Cutoff date: {cutoff_date.strftime('%Y-%m-%d')}")

    # Find all bookmark links
    for link in soup.find_all('a'):
        href = link.get('href')
        if not href:
            continue

        # Get add date (Unix timestamp)
        add_date_str = link.get('add_date')
        if not add_date_str:
            continue

        try:
            add_date = int(add_date_str)
        except ValueError:
            continue

        # Filter by age
        if add_date < cutoff_timestamp:
            continue

        # Extract bookmark data
        title = link.get_text().strip()
        icon = link.get('icon', '')

        # Parse URL
        parsed_url = urlparse(href)
        domain = parsed_url.netloc

        # Categorize
        category = categorize_url(href, title)

        bookmark = {
            'title': title,
            'url': href,
            'domain': domain,
            'category': category,
            'added_date': datetime.fromtimestamp(add_date).isoformat(),
            'favicon': icon if icon else f'https://{domain}/favicon.ico'
        }

        bookmarks.append(bookmark)
        
        if logger and len(bookmarks) % 100 == 0:
            logger.debug(f"Processed {len(bookmarks)} bookmarks...")

    if logger:
        logger.info(f"Found {len(bookmarks)} bookmarks within {max_age_days} days")
    
    return bookmarks


def categorize_url(url: str, title: str) -> str:
    """
    Categorize a URL based on domain and title

    Args:
        url: The URL to categorize
        title: The bookmark title

    Returns:
        Category string
    """
    url_lower = url.lower()
    title_lower = title.lower()

    # Check each category's keywords
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in url_lower or keyword in title_lower:
                return category

    return 'misc'


def export_to_json(bookmarks: List[Dict[str, Any]], output_file: str, logger=None) -> None:
    """Export bookmarks to JSON file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(bookmarks, f, indent=2, ensure_ascii=False)
        if logger:
            logger.info(f"Exported {len(bookmarks)} bookmarks to {output_file}")
        else:
            print(f"Exported {len(bookmarks)} bookmarks to {output_file}")
    except Exception as e:
        if logger:
            logger.error(f"Error exporting to JSON: {e}")
        raise


def export_to_csv(bookmarks: List[Dict[str, Any]], output_file: str, logger=None) -> None:
    """Export bookmarks to CSV file"""
    import csv

    if not bookmarks:
        msg = "No bookmarks to export"
        if logger:
            logger.warning(msg)
        else:
            print(msg)
        return

    fieldnames = ['title', 'url', 'domain', 'category', 'added_date', 'favicon']

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(bookmarks)

        if logger:
            logger.info(f"Exported {len(bookmarks)} bookmarks to {output_file}")
        else:
            print(f"Exported {len(bookmarks)} bookmarks to {output_file}")
    except Exception as e:
        if logger:
            logger.error(f"Error exporting to CSV: {e}")
        raise


def print_summary(bookmarks: List[Dict[str, Any]], logger=None) -> None:
    """Print summary statistics"""
    output = []
    output.append("\n=== Bookmark Summary ===")
    output.append(f"Total bookmarks: {len(bookmarks)}")

    # Count by category
    category_counts = {}
    for bookmark in bookmarks:
        category = bookmark['category']
        category_counts[category] = category_counts.get(category, 0) + 1

    output.append("\nBookmarks by category:")
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        output.append(f"  {category}: {count}")

    # Show date range
    if bookmarks:
        dates = [datetime.fromisoformat(b['added_date']) for b in bookmarks]
        oldest = min(dates)
        newest = max(dates)
        output.append("\nDate range:")
        output.append(f"  Oldest: {oldest.strftime('%Y-%m-%d')}")
        output.append(f"  Newest: {newest.strftime('%Y-%m-%d')}")
    
    summary = '\n'.join(output)
    if logger:
        logger.info(summary)
    else:
        print(summary)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description='Parse HTML bookmarks file')
    parser.add_argument('input_file', help='Path to HTML bookmarks file')
    parser.add_argument('--output', '-o', help='Output file path (JSON or CSV)')
    parser.add_argument('--format', '-f', choices=['json', 'csv'], default='json',
                        help='Output format (default: json)')
    parser.add_argument('--max-age', '-m', type=int, default=365,
                        help='Maximum age in days (default: 365)')
    
    # Add logging arguments
    add_logging_arguments(parser)

    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging('parse_bookmarks', args.log_level)

    try:
        # Parse bookmarks
        bookmarks = parse_bookmarks_html(args.input_file, args.max_age, logger)

        # Print summary
        print_summary(bookmarks, logger)

        # Export if output file specified
        if args.output:
            if args.format == 'json':
                export_to_json(bookmarks, args.output, logger)
            else:
                export_to_csv(bookmarks, args.output, logger)
        else:
            # Print first few bookmarks as example
            logger.info("\nFirst 5 bookmarks:")
            for bookmark in bookmarks[:5]:
                logger.info(f"\n  Title: {bookmark['title']}")
                logger.info(f"  URL: {bookmark['url']}")
                logger.info(f"  Category: {bookmark['category']}")
                logger.info(f"  Added: {bookmark['added_date']}")
        
        logger.info("Parse bookmarks completed successfully")
    except Exception as e:
        logger.error(f"Failed to parse bookmarks: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
