#!/usr/bin/env python3
"""
Transform backup-links-2026-01-17.json to default-links.json format.

Converts flat link structure with section names to nested Yohoo export format
with 3-column layout.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


# Section configuration: maps section names to IDs and icons
SECTION_CONFIG = {
    "Norwegian Essentials": {"icon": "🇳🇴", "id": "norwegian-essentials"},
    "Transport & Travel": {"icon": "🚆", "id": "transport-travel"},
    "Norwegian News": {"icon": "📰", "id": "norwegian-news"},
    "International News": {"icon": "🌍", "id": "international-news"},
    "Norwegian Streaming": {"icon": "📺", "id": "norwegian-streaming"},
    "Global Streaming": {"icon": "🎬", "id": "global-streaming"},
    "Events & Culture": {"icon": "🎭", "id": "events-culture"},
    "Government & Official": {"icon": "🏛️", "id": "government-official"},
    "Banking": {"icon": "🏦", "id": "banking"},
    "Development": {"icon": "💻", "id": "development"},
    "Productivity & Tools": {"icon": "🛠️", "id": "productivity-tools"},
    "AI & Research": {"icon": "🤖", "id": "ai-research"},
    "Learn Norwegian": {"icon": "📚", "id": "learn-norwegian"},
    "Online Learning": {"icon": "🎓", "id": "online-learning"},
    "Outdoors & Activities": {"icon": "⛰️", "id": "outdoors-activities"},
    "Food & Groceries": {"icon": "🍽️", "id": "food-groceries"},
    "Interesting & Fun": {"icon": "🎨", "id": "interesting-fun"}
}


def generate_link_id(index: int) -> str:
    """Generate unique link ID."""
    return f"link-{index:04d}"


def transform_backup_to_defaults(backup_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform backup links format to Yohoo export format.

    Args:
        backup_data: Backup data with flat links array

    Returns:
        Yohoo export format data structure
    """
    # Group links by section
    sections_dict: Dict[str, List[Dict[str, Any]]] = {}

    for idx, link in enumerate(backup_data.get("links", [])):
        section_name = link["section"]

        # Initialize section if not exists
        if section_name not in sections_dict:
            sections_dict[section_name] = []

        # Create link object in Yohoo format
        link_obj = {
            "id": generate_link_id(idx),
            "title": link["title"],
            "url": link["url"],
            "date": int(datetime.now().timestamp() * 1000)  # Current timestamp in ms
        }

        sections_dict[section_name].append(link_obj)

    # Build sections array
    sections = []
    section_ids = []

    for section_name, links in sections_dict.items():
        if section_name not in SECTION_CONFIG:
            print(f"Warning: Unknown section '{section_name}' - skipping", file=sys.stderr)
            continue

        config = SECTION_CONFIG[section_name]
        section_id = config["id"]

        section_obj = {
            "id": section_id,
            "title": section_name,
            "icon": config["icon"],
            "links": links
        }

        sections.append(section_obj)
        section_ids.append(section_id)

    # Build 3-column layout (distribute sections evenly)
    num_columns = 3
    layout = {
        "columns": [
            {"id": "col-1", "sections": []},
            {"id": "col-2", "sections": []},
            {"id": "col-3", "sections": []}
        ]
    }

    for idx, section_id in enumerate(section_ids):
        col_index = idx % num_columns
        layout["columns"][col_index]["sections"].append(section_id)

    # Calculate metadata
    total_links = sum(len(s["links"]) for s in sections)

    # Build export structure
    export_data = {
        "version": "1.0.0",
        "exportDate": datetime.now().isoformat(),
        "exportedBy": "Yohoo Transform Script",
        "data": {
            "sections": sections,
            "trash": [],
            "layout": layout,
            "fontScale": 2.0
        },
        "metadata": {
            "sectionCount": len(sections),
            "linkCount": total_links,
            "trashCount": 0,
            "columns": num_columns
        }
    }

    return export_data


def main():
    """Main transformation function."""
    # Paths
    project_root = Path(__file__).parent.parent
    backup_file = project_root / "backup-links-2026-01-17.json"
    output_file = project_root / "default-links.json"

    # Read backup data
    print(f"Reading backup from: {backup_file}")

    if not backup_file.exists():
        print(f"Error: Backup file not found: {backup_file}", file=sys.stderr)
        sys.exit(1)

    with open(backup_file, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)

    # Transform
    print("Transforming data...")
    export_data = transform_backup_to_defaults(backup_data)

    # Write output
    print(f"Writing default-links.json to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    # Summary
    print("\n✅ Transformation complete!")
    print(f"   Sections: {export_data['metadata']['sectionCount']}")
    print(f"   Links: {export_data['metadata']['linkCount']}")
    print(f"   Columns: {export_data['metadata']['columns']}")
    print(f"\nOutput: {output_file}")


if __name__ == "__main__":
    main()
