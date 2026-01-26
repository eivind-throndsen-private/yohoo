#!/usr/bin/env python3
"""
Chrome History Analyzer for Yohoo Start Page
Analyzes Chrome browsing history and surfaces frequently visited URLs
"""

import sqlite3
import shutil
import os
from datetime import datetime, timedelta
from urllib.parse import urlparse
from collections import defaultdict
from typing import List, Dict, Any, Optional
import json
import tempfile
import math
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.logging_config import setup_logging, add_logging_arguments
from scripts.parse_bookmarks import CATEGORY_KEYWORDS


# URLs to exclude (low-value patterns)
EXCLUDE_PATTERNS = [
    'google.com/search',
    'localhost',
    '127.0.0.1',
    'chrome://',
    'chrome-extension://',
    'about:',
    'file:///',
    'accounts.google.com/signin',
    'accounts.google.com/ServiceLogin',
]


def get_chrome_history_path(logger=None) -> str:
    """Get the path to Chrome history database based on OS"""
    import platform

    system = platform.system()
    home = os.path.expanduser("~")

    if system == "Darwin":  # macOS
        # Try Profile 1 first, then Default
        profile1_path = os.path.join(home, "Library", "Application Support", "Google", "Chrome", "Profile 1", "History")
        default_path = os.path.join(home, "Library", "Application Support", "Google", "Chrome", "Default", "History")

        if os.path.exists(profile1_path):
            if logger:
                logger.debug(f"Found Chrome history at: {profile1_path}")
            return profile1_path
        elif os.path.exists(default_path):
            if logger:
                logger.debug(f"Found Chrome history at: {default_path}")
            return default_path
        else:
            raise FileNotFoundError(f"Chrome history not found. Tried:\n  {profile1_path}\n  {default_path}")
    elif system == "Linux":
        return os.path.join(home, ".config", "google-chrome", "Default", "History")
    elif system == "Windows":
        return os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data", "Default", "History")
    else:
        raise Exception(f"Unsupported operating system: {system}")


def copy_history_db(source_path: str, logger=None) -> str:
    """
    Copy Chrome history database to temp location
    (Chrome locks the database, so we need a copy)

    Args:
        source_path: Path to source history database
        logger: Logger instance (optional)

    Returns:
        Path to temporary copy
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Chrome history not found at: {source_path}")

    # Create temporary file
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"chrome_history_copy_{os.getpid()}.db")

    # Copy database
    shutil.copy2(source_path, temp_path)
    
    if logger:
        logger.debug(f"Created temporary copy at: {temp_path}")
    else:
        print(f"Created temporary copy at: {temp_path}")

    return temp_path


def should_exclude_url(url: str) -> bool:
    """Check if URL should be excluded based on patterns"""
    url_lower = url.lower()

    for pattern in EXCLUDE_PATTERNS:
        if pattern in url_lower:
            return True

    # Exclude very long URLs (likely contain session tokens, etc.)
    if len(url) > 200:
        return True

    return False


def calculate_recency_score(days_ago: int, decay_factor: float = 0.1) -> float:
    """
    Calculate recency score using exponential decay

    Args:
        days_ago: Number of days since visit
        decay_factor: How quickly score decays (default 0.1)

    Returns:
        Score between 0 and 1
    """
    return math.exp(-decay_factor * days_ago)


def analyze_history(history_db_path: str, days_back: int = 90, min_visit_count: int = 3, logger=None) -> List[Dict[str, Any]]:
    """
    Analyze Chrome history database

    Args:
        history_db_path: Path to Chrome History database
        days_back: Number of days to look back (default 90)
        min_visit_count: Minimum visit count to include (default 3)
        logger: Logger instance (optional)

    Returns:
        List of URL data dictionaries
    """
    if logger:
        logger.info(f"Analyzing history from: {history_db_path}")
        logger.info(f"Looking back {days_back} days, minimum {min_visit_count} visits")
    
    # Calculate cutoff time (Chrome stores microseconds since 1601-01-01)
    now = datetime.now()
    cutoff_date = now - timedelta(days=days_back)

    # Chrome's epoch is 1601-01-01, convert to Chrome timestamp
    chrome_epoch = datetime(1601, 1, 1)
    cutoff_timestamp = int((cutoff_date - chrome_epoch).total_seconds() * 1000000)

    # Connect to database
    try:
        conn = sqlite3.connect(history_db_path)
        cursor = conn.cursor()
    except Exception as e:
        if logger:
            logger.error(f"Failed to connect to database: {e}")
        raise

    # Query to get URLs with visit counts and last visit time
    query = """
    SELECT
        urls.url,
        urls.title,
        COUNT(visits.id) as visit_count,
        MAX(visits.visit_time) as last_visit_time,
        urls.visit_count as total_visit_count
    FROM urls
    LEFT JOIN visits ON urls.id = visits.url
    WHERE visits.visit_time > ?
    GROUP BY urls.url
    HAVING visit_count >= ?
    ORDER BY visit_count DESC
    """

    try:
        cursor.execute(query, (cutoff_timestamp, min_visit_count))
        results = cursor.fetchall()
    except Exception as e:
        if logger:
            logger.error(f"Database query failed: {e}")
        conn.close()
        raise
    
    if logger:
        logger.info(f"Found {len(results)} URLs matching criteria")

    # Process results
    url_data = []

    for url, title, visit_count, last_visit_time, total_visit_count in results:
        # Skip excluded URLs
        if should_exclude_url(url):
            continue

        # Parse URL
        parsed = urlparse(url)
        domain = parsed.netloc

        # Calculate days since last visit
        last_visit_dt = chrome_epoch + timedelta(microseconds=last_visit_time)
        days_ago = (now - last_visit_dt).days

        # Calculate scores
        recency_score = calculate_recency_score(days_ago)

        # Combined score (60% frequency, 40% recency)
        # Normalize visit_count to 0-1 range (cap at 50 visits)
        normalized_frequency = min(visit_count / 50.0, 1.0)
        combined_score = (normalized_frequency * 0.6) + (recency_score * 0.4)

        url_data.append({
            'url': url,
            'title': title or domain,
            'domain': domain,
            'visit_count': visit_count,
            'total_visit_count': total_visit_count,
            'last_visit': last_visit_dt.isoformat(),
            'days_since_visit': days_ago,
            'recency_score': round(recency_score, 3),
            'combined_score': round(combined_score, 3)
        })
        
        if logger and len(url_data) % 100 == 0:
            logger.debug(f"Processed {len(url_data)} URLs...")

    conn.close()

    # Sort by combined score
    url_data.sort(key=lambda x: x['combined_score'], reverse=True)
    
    if logger:
        logger.info(f"Analysis complete: {len(url_data)} URLs after filtering")

    return url_data


def categorize_url(url: str, title: str) -> str:
    """
    Categorize a URL based on domain and title.
    Uses CATEGORY_KEYWORDS imported from parse_bookmarks module.
    
    Args:
        url: The URL to categorize
        title: The page title
    
    Returns:
        Category string
    """
    url_lower = url.lower()
    title_lower = title.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in url_lower or keyword in title_lower:
                return category

    return 'misc'


def export_to_json(url_data: List[Dict[str, Any]], output_file: str, logger=None) -> None:
    """Export URL data to JSON"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(url_data, f, indent=2, ensure_ascii=False)
        if logger:
            logger.info(f"Exported {len(url_data)} URLs to {output_file}")
        else:
            print(f"Exported {len(url_data)} URLs to {output_file}")
    except Exception as e:
        if logger:
            logger.error(f"Error exporting to JSON: {e}")
        raise


def export_to_csv(url_data: List[Dict[str, Any]], output_file: str, logger=None) -> None:
    """Export URL data to CSV"""
    import csv

    if not url_data:
        msg = "No URLs to export"
        if logger:
            logger.warning(msg)
        else:
            print(msg)
        return

    fieldnames = ['title', 'url', 'domain', 'visit_count', 'total_visit_count',
                  'last_visit', 'days_since_visit', 'recency_score', 'combined_score']

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(url_data)

        if logger:
            logger.info(f"Exported {len(url_data)} URLs to {output_file}")
        else:
            print(f"Exported {len(url_data)} URLs to {output_file}")
    except Exception as e:
        if logger:
            logger.error(f"Error exporting to CSV: {e}")
        raise


def print_summary(url_data: List[Dict[str, Any]], top_n: int = 20, logger=None) -> None:
    """Print summary statistics and top URLs"""
    output = []
    output.append("\n=== Chrome History Analysis ===")
    output.append(f"Total URLs analyzed: {len(url_data)}")

    if not url_data:
        summary = '\n'.join(output)
        if logger:
            logger.info(summary)
        else:
            print(summary)
        return

    # Visit count stats
    total_visits = sum(u['visit_count'] for u in url_data)
    avg_visits = total_visits / len(url_data)

    output.append(f"Total visits: {total_visits}")
    output.append(f"Average visits per URL: {avg_visits:.1f}")

    # Categorize and count
    categories = defaultdict(int)
    for url_item in url_data:
        # Add category if not present
        if 'category' not in url_item:
            url_item['category'] = categorize_url(url_item['url'], url_item['title'])
        categories[url_item['category']] += 1

    output.append("\nURLs by category:")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        output.append(f"  {category}: {count}")

    # Top URLs
    output.append(f"\n=== Top {top_n} URLs by Combined Score ===")
    for i, url_item in enumerate(url_data[:top_n], 1):
        output.append(f"\n{i}. {url_item['title'][:60]}")
        output.append(f"   URL: {url_item['url'][:80]}")
        output.append(f"   Visits: {url_item['visit_count']} | Last: {url_item['days_since_visit']} days ago")
        output.append(f"   Score: {url_item['combined_score']} (recency: {url_item['recency_score']})")
        output.append(f"   Category: {url_item.get('category', 'misc')}")
    
    summary = '\n'.join(output)
    if logger:
        logger.info(summary)
    else:
        print(summary)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description='Analyze Chrome browsing history')
    parser.add_argument('--history-path', '-p',
                        help='Path to Chrome History database (auto-detected if not provided)')
    parser.add_argument('--output', '-o',
                        help='Output file path (JSON or CSV)')
    parser.add_argument('--format', '-f', choices=['json', 'csv'], default='json',
                        help='Output format (default: json)')
    parser.add_argument('--days', '-d', type=int, default=90,
                        help='Number of days to analyze (default: 90)')
    parser.add_argument('--min-visits', '-m', type=int, default=3,
                        help='Minimum visit count (default: 3)')
    parser.add_argument('--top', '-t', type=int, default=20,
                        help='Number of top URLs to display (default: 20)')
    
    # Add logging arguments
    add_logging_arguments(parser)

    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging('analyze_history', args.log_level)

    try:
        # Get Chrome history path
        if args.history_path:
            history_path = args.history_path
        else:
            try:
                history_path = get_chrome_history_path(logger)
                logger.info(f"Auto-detected Chrome history at: {history_path}")
            except Exception as e:
                logger.error(f"Error: {e}")
                sys.exit(1)

        # Copy database
        try:
            temp_db_path = copy_history_db(history_path, logger)
        except FileNotFoundError as e:
            logger.error(f"Error: {e}")
            sys.exit(1)

        try:
            # Analyze history
            url_data = analyze_history(temp_db_path,
                                       days_back=args.days,
                                       min_visit_count=args.min_visits,
                                       logger=logger)

            # Print summary
            print_summary(url_data, top_n=args.top, logger=logger)

            # Export if output specified
            if args.output:
                if args.format == 'json':
                    export_to_json(url_data, args.output, logger)
                else:
                    export_to_csv(url_data, args.output, logger)
            
            logger.info("Analysis completed successfully")

        finally:
            # Clean up temporary database
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
                logger.debug("Cleaned up temporary file")
    
    except Exception as e:
        logger.error(f"Failed to analyze history: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
