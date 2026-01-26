#!/usr/bin/env python3
"""
Utility functions for Yohoo scripts
"""

import json
import csv
import os
import sys
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.logging_config import setup_logging, add_logging_arguments


def merge_bookmarks_and_history(bookmarks_file: str, history_file: str, output_file: str, logger=None) -> None:
    """
    Merge bookmarks and history data, removing duplicates

    Args:
        bookmarks_file: Path to bookmarks JSON file
        history_file: Path to history JSON file
        output_file: Path to output merged JSON file
        logger: Logger instance (optional)
    """
    if logger:
        logger.info(f"Merging {bookmarks_file} and {history_file}")
    
    # Load bookmarks
    try:
        with open(bookmarks_file, 'r', encoding='utf-8') as f:
            bookmarks = json.load(f)
        if logger:
            logger.debug(f"Loaded {len(bookmarks)} bookmarks")
    except FileNotFoundError:
        if logger:
            logger.error(f"Bookmarks file not found: {bookmarks_file}")
        raise
    except Exception as e:
        if logger:
            logger.error(f"Error loading bookmarks: {e}")
        raise

    # Load history
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        if logger:
            logger.debug(f"Loaded {len(history)} history items")
    except FileNotFoundError:
        if logger:
            logger.error(f"History file not found: {history_file}")
        raise
    except Exception as e:
        if logger:
            logger.error(f"Error loading history: {e}")
        raise

    # Create set of bookmark URLs for deduplication
    bookmark_urls = {b['url'] for b in bookmarks}

    # Merge data
    merged = list(bookmarks)  # Start with all bookmarks

    # Add history items that aren't already bookmarks
    for hist_item in history:
        if hist_item['url'] not in bookmark_urls:
            # Convert history format to bookmark format
            bookmark_item = {
                'title': hist_item['title'],
                'url': hist_item['url'],
                'domain': hist_item['domain'],
                'category': hist_item.get('category', 'misc'),
                'source': 'history',
                'visit_count': hist_item['visit_count'],
                'score': hist_item['combined_score']
            }
            merged.append(bookmark_item)

    # Sort by score (if available) or by title
    merged.sort(key=lambda x: x.get('score', 0), reverse=True)

    # Export
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
    except Exception as e:
        if logger:
            logger.error(f"Error saving merged data: {e}")
        raise

    summary = []
    summary.append("\n=== Merge Summary ===")
    summary.append(f"Bookmarks: {len(bookmarks)}")
    summary.append(f"History items: {len(history)}")
    summary.append(f"Merged items: {len(merged)}")
    summary.append(f"Duplicates removed: {len(bookmarks) + len(history) - len(merged)}")
    summary.append(f"\nSaved to: {output_file}")
    
    summary_text = '\n'.join(summary)
    if logger:
        logger.info(summary_text)
    else:
        print(summary_text)


def generate_html_snippet(data_file: str, category: Optional[str] = None, logger=None) -> str:
    """
    Generate HTML snippet for links that can be inserted into yohoo.html

    Args:
        data_file: Path to JSON data file
        category: Optional category to filter by
        logger: Logger instance (optional)
    
    Returns:
        HTML snippet as string
    """
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            items = json.load(f)
        if logger:
            logger.debug(f"Loaded {len(items)} items from {data_file}")
    except FileNotFoundError:
        if logger:
            logger.error(f"Data file not found: {data_file}")
        raise
    except Exception as e:
        if logger:
            logger.error(f"Error loading data: {e}")
        raise

    if category:
        items = [item for item in items if item.get('category') == category]
        if logger:
            logger.debug(f"Filtered to {len(items)} items in category '{category}'")

    html = []
    for item in items:
        title = item['title']
        url = item['url']
        favicon = item.get('favicon', f"https://{item['domain']}/favicon.ico")

        html.append(f'''<a href="{url}" class="link-card">
    <div class="link-icon">
        <img src="{favicon}" alt="{title}">
    </div>
    <div class="link-content">
        <div class="link-title">{title}</div>
        <div class="link-url">{item['domain']}</div>
    </div>
</a>''')

    return '\n'.join(html)


def export_by_category(data_file: str, output_dir: str, logger=None) -> None:
    """
    Export data to separate files by category

    Args:
        data_file: Path to JSON data file
        output_dir: Directory to save category files
        logger: Logger instance (optional)
    """
    from collections import defaultdict

    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            items = json.load(f)
        if logger:
            logger.debug(f"Loaded {len(items)} items from {data_file}")
    except FileNotFoundError:
        if logger:
            logger.error(f"Data file not found: {data_file}")
        raise
    except Exception as e:
        if logger:
            logger.error(f"Error loading data: {e}")
        raise

    # Group by category
    by_category = defaultdict(list)
    for item in items:
        category = item.get('category', 'misc')
        by_category[category].append(item)

    # Create output directory if it doesn't exist
    try:
        os.makedirs(output_dir, exist_ok=True)
        if logger:
            logger.debug(f"Output directory: {output_dir}")
    except Exception as e:
        if logger:
            logger.error(f"Failed to create output directory: {e}")
        raise

    # Export each category
    for category, category_items in by_category.items():
        output_file = os.path.join(output_dir, f'{category}.json')
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(category_items, f, indent=2, ensure_ascii=False)
            msg = f"Exported {len(category_items)} items to {output_file}"
            if logger:
                logger.info(msg)
            else:
                print(msg)
        except Exception as e:
            if logger:
                logger.error(f"Failed to export {category}: {e}")
            raise


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description='Yohoo utility functions')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge bookmarks and history')
    merge_parser.add_argument('bookmarks', help='Path to bookmarks JSON file')
    merge_parser.add_argument('history', help='Path to history JSON file')
    merge_parser.add_argument('--output', '-o', default='data/merged_links.json',
                             help='Output file path')
    add_logging_arguments(merge_parser)

    # HTML snippet command
    html_parser = subparsers.add_parser('html', help='Generate HTML snippet')
    html_parser.add_argument('data_file', help='Path to JSON data file')
    html_parser.add_argument('--category', '-c', help='Filter by category')
    add_logging_arguments(html_parser)

    # Export by category command
    export_parser = subparsers.add_parser('export-categories',
                                          help='Export data by category')
    export_parser.add_argument('data_file', help='Path to JSON data file')
    export_parser.add_argument('--output-dir', '-o', default='data/categories',
                              help='Output directory')
    add_logging_arguments(export_parser)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Setup logging
    logger = setup_logging('utils', args.log_level)

    try:
        if args.command == 'merge':
            merge_bookmarks_and_history(args.bookmarks, args.history, args.output, logger)

        elif args.command == 'html':
            html = generate_html_snippet(args.data_file, args.category, logger)
            print(html)

        elif args.command == 'export-categories':
            export_by_category(args.data_file, args.output_dir, logger)
        
        logger.info("Operation completed successfully")
    
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
