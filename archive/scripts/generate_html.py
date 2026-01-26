#!/usr/bin/env python3
"""
Generate yohoo.html - A curated start page for Norway-based digital workers
Features: drag-and-drop, localStorage persistence, search, customizable sections
"""

import json
import os
from datetime import datetime

# Default paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DEFAULT_LINKS_FILE = os.path.join(PROJECT_DIR, 'data', 'default_links.json')


def load_default_links(filepath=DEFAULT_LINKS_FILE):
    """Load default links from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_link_html(link):
    """Generate HTML for a single link"""
    title = link['title'][:80]
    url = link['url']
    domain = link.get('domain', '')

    return f'''<a href="{url}" class="link-item" draggable="true" data-url="{url}" data-title="{title}" data-domain="{domain}">
                            <span class="link-text">{title}</span>
                            <span class="delete-icon" onclick="event.preventDefault(); event.stopPropagation(); deleteLink(this.parentElement);">×</span>
                        </a>'''


def generate_section_html(section, is_user_section=False):
    """Generate HTML for a section"""
    section_id = section['id']
    name = section['name']
    emoji = section['emoji']
    links = section.get('links', [])
    placeholder = section.get('placeholder', '')

    links_html = '\n                        '.join(generate_link_html(link) for link in links)

    placeholder_html = ''
    if is_user_section and placeholder and not links:
        placeholder_html = f'<div class="placeholder-text">{placeholder}</div>'

    return f'''
            <div class="section" data-section="{section_id}" draggable="true">
                <div class="section-header">
                    <span class="section-icon">{emoji}</span>
                    <h2 class="section-title">{name}</h2>
                    <span class="section-toggle">−</span>
                </div>
                <div class="links-list">
                    {placeholder_html}
                    {links_html}
                </div>
            </div>'''


def generate_html(output_file='yohoo.html', default_links_file=None):
    """Generate complete HTML file"""

    if default_links_file is None:
        default_links_file = DEFAULT_LINKS_FILE

    # Load default links
    data = load_default_links(default_links_file)
    sections = data.get('sections', [])
    user_sections = data.get('userSections', [])

    # Generate sections HTML
    sections_html = []
    for section in sections:
        sections_html.append(generate_section_html(section, is_user_section=False))

    for section in user_sections:
        sections_html.append(generate_section_html(section, is_user_section=True))

    all_sections_html = '\n'.join(sections_html)

    # Count total links
    total_links = sum(len(s.get('links', [])) for s in sections)

    # Generate the HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yohoo! - Your Personal Start Page</title>
    <style>
        :root {{
            /* Light Cream Theme */
            --bg-color: #FFEFCF;
            --section-bg: #FFF8E7;
            --section-bg-hover: #FFF5DC;
            --border-color: #E6D5B0;
            --header-color: #6B4E3D;
            --link-color: #0066CC;
            --link-hover: #0052A3;
            --text-muted: #8B7355;
            --delete-color: #C44;
            --text-main: #2C2416;
            --accent-norway: #BA0C2F;
            --accent-blue: #00205B;

            /* Spacing */
            --gap: 0.75rem;
            --radius: 6px;

            /* Font Scaling */
            --font-scale: 1.0;

            /* Hover Effects */
            --hover-bg: rgba(107, 78, 61, 0.06);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            padding: 1rem;
            font-size: calc(14px * var(--font-scale));
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        /* Header */
        header {{
            margin-bottom: 1.5rem;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 1rem;
        }}

        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        .logo-area {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .logo {{
            font-size: 2rem;
            font-weight: 800;
            color: var(--header-color);
            text-decoration: none;
        }}

        .tagline {{
            color: var(--text-muted);
            font-size: 0.85rem;
        }}

        .controls {{
            display: flex;
            gap: 0.75rem;
            align-items: center;
            flex-wrap: wrap;
        }}

        .search-container {{
            position: relative;
        }}

        #searchBox {{
            width: 280px;
            padding: 0.5rem 0.75rem;
            padding-right: 2rem;
            border-radius: var(--radius);
            border: 1px solid var(--border-color);
            background-color: var(--section-bg);
            color: var(--text-main);
            font-size: 0.9rem;
        }}

        #searchBox:focus {{
            outline: none;
            border-color: var(--header-color);
            box-shadow: 0 0 0 2px rgba(107, 78, 61, 0.1);
        }}

        .shortcut-hint {{
            position: absolute;
            right: 0.5rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            font-size: 0.7rem;
            padding: 2px 5px;
            border: 1px solid var(--border-color);
            border-radius: 3px;
            background: var(--bg-color);
        }}

        .btn {{
            padding: 0.5rem 1rem;
            border-radius: var(--radius);
            border: 1px solid var(--border-color);
            background-color: var(--section-bg);
            color: var(--header-color);
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.85rem;
        }}

        .btn:hover {{
            background-color: var(--header-color);
            color: var(--section-bg);
        }}

        .btn-settings {{
            font-size: 1.2rem;
            padding: 0.4rem 0.6rem;
        }}

        /* Sections Grid */
        .sections-container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1rem;
        }}

        .section {{
            background: var(--section-bg);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 0.75rem;
            transition: all 0.2s;
        }}

        .section:hover {{
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}

        .section.dragging {{
            opacity: 0.5;
            transform: rotate(2deg);
        }}

        .section.drag-over {{
            border-color: var(--header-color);
            box-shadow: 0 0 0 2px rgba(107, 78, 61, 0.2);
        }}

        .section-header {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 0.5rem;
            cursor: move;
        }}

        .section-icon {{
            font-size: 1.1rem;
        }}

        .section-title {{
            flex: 1;
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--header-color);
        }}

        .section-toggle {{
            color: var(--text-muted);
            cursor: pointer;
            font-weight: bold;
            padding: 0 0.25rem;
            user-select: none;
        }}

        .section.collapsed .links-list {{
            display: none;
        }}

        .section.collapsed .section-toggle {{
            transform: rotate(0);
        }}

        .section.collapsed .section-toggle::after {{
            content: '+';
        }}

        .section.collapsed .section-toggle {{
            font-size: 0;
        }}

        .section.collapsed .section-toggle::after {{
            font-size: 1rem;
        }}

        /* Links */
        .links-list {{
            display: flex;
            flex-direction: column;
            gap: 2px;
            min-height: 30px;
        }}

        .links-list.drag-over {{
            background: var(--hover-bg);
            border-radius: 4px;
        }}

        .placeholder-text {{
            color: var(--text-muted);
            font-size: 0.8rem;
            font-style: italic;
            padding: 0.5rem;
            text-align: center;
        }}

        .link-item {{
            display: flex;
            align-items: center;
            padding: 0.35rem 0.5rem;
            border-radius: 4px;
            text-decoration: none;
            color: var(--link-color);
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.15s;
        }}

        .link-item:hover {{
            background: var(--hover-bg);
            color: var(--link-hover);
        }}

        .link-item.dragging {{
            opacity: 0.4;
        }}

        .link-item.hidden {{
            display: none;
        }}

        .link-text {{
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .delete-icon {{
            opacity: 0;
            color: var(--delete-color);
            font-size: 1rem;
            font-weight: bold;
            padding: 0 0.25rem;
            cursor: pointer;
            transition: opacity 0.15s;
        }}

        .link-item:hover .delete-icon {{
            opacity: 0.6;
        }}

        .delete-icon:hover {{
            opacity: 1 !important;
        }}

        /* Trash Section */
        .trash-section {{
            margin-top: 2rem;
            padding: 1rem;
            background: rgba(0,0,0,0.03);
            border: 1px dashed var(--border-color);
            border-radius: var(--radius);
        }}

        .trash-header {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            cursor: pointer;
            padding: 0.25rem;
        }}

        .trash-header:hover {{
            background: var(--hover-bg);
            border-radius: 4px;
        }}

        .trash-title {{
            flex: 1;
            font-weight: 600;
            color: var(--text-muted);
            font-size: 0.9rem;
        }}

        .trash-count {{
            color: var(--text-muted);
            font-size: 0.8rem;
        }}

        .trash-content {{
            display: none;
            margin-top: 0.75rem;
        }}

        .trash-content.expanded {{
            display: block;
        }}

        .trash-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.35rem 0.5rem;
            background: var(--section-bg);
            border-radius: 4px;
            margin-bottom: 4px;
            font-size: 0.85rem;
        }}

        .trash-item-link {{
            flex: 1;
            color: var(--text-muted);
            text-decoration: line-through;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .restore-btn {{
            padding: 0.2rem 0.5rem;
            font-size: 0.75rem;
            background: var(--header-color);
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }}

        .restore-btn:hover {{
            opacity: 0.9;
        }}

        /* Footer */
        footer {{
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-color);
            text-align: center;
            font-size: 0.8rem;
            color: var(--text-muted);
        }}

        footer a {{
            color: var(--text-muted);
            text-decoration: none;
        }}

        footer a:hover {{
            text-decoration: underline;
        }}

        /* Modal */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }}

        .modal.show {{
            display: flex;
        }}

        .modal-content {{
            background: var(--section-bg);
            border-radius: var(--radius);
            padding: 1.5rem;
            max-width: 400px;
            width: 90%;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }}

        .modal-title {{
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--header-color);
            margin-bottom: 1rem;
        }}

        .modal-input {{
            width: 100%;
            padding: 0.5rem;
            margin-bottom: 0.75rem;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-size: 0.9rem;
        }}

        .modal-input:focus {{
            outline: none;
            border-color: var(--header-color);
        }}

        .modal-buttons {{
            display: flex;
            gap: 0.5rem;
            justify-content: flex-end;
            margin-top: 1rem;
        }}

        /* Settings Panel */
        .settings-panel {{
            padding: 1rem 0;
        }}

        .settings-row {{
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }}

        .settings-label {{
            flex: 1;
            font-weight: 500;
        }}

        input[type="range"] {{
            width: 120px;
            cursor: pointer;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .sections-container {{
                grid-template-columns: 1fr;
            }}

            .header-top {{
                flex-direction: column;
                align-items: flex-start;
            }}

            #searchBox {{
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-top">
                <div class="logo-area">
                    <span class="logo">Yohoo!</span>
                    <span class="tagline">Your Personal Start Page</span>
                </div>
                <div class="controls">
                    <div class="search-container">
                        <input type="text" id="searchBox" placeholder="Search links..." autocomplete="off">
                        <span class="shortcut-hint">/</span>
                    </div>
                    <button class="btn" id="addSectionBtn">+ Section</button>
                    <button class="btn btn-settings" id="settingsBtn" title="Settings">⚙</button>
                </div>
            </div>
        </header>

        <div class="sections-container" id="sectionsContainer">
{all_sections_html}
        </div>

        <!-- Trash Section -->
        <div class="trash-section">
            <div class="trash-header" id="trashHeader">
                <span>🗑️</span>
                <span class="trash-title">Trash</span>
                <span class="trash-count" id="trashCount">(0)</span>
                <span class="trash-toggle">▼</span>
            </div>
            <div class="trash-content" id="trashContent">
                <div id="trashLinks"></div>
            </div>
        </div>

        <footer>
            <p>Yohoo! v1.3 &mdash; Curated links for Norway-based digital workers</p>
            <p style="margin-top: 0.25rem;">Press <kbd>/</kbd> to search &bull; Drag to reorganize &bull; All data stored locally</p>
        </footer>
    </div>

    <!-- Add Section Modal -->
    <div class="modal" id="addSectionModal">
        <div class="modal-content">
            <div class="modal-title">Add New Section</div>
            <input type="text" class="modal-input" id="sectionNameInput" placeholder="Section name">
            <input type="text" class="modal-input" id="sectionIconInput" placeholder="Emoji icon" value="📁">
            <div class="modal-buttons">
                <button class="btn" id="modalCancelBtn">Cancel</button>
                <button class="btn" id="modalAddBtn" style="background: var(--header-color); color: white;">Add</button>
            </div>
        </div>
    </div>

    <!-- Settings Modal -->
    <div class="modal" id="settingsModal">
        <div class="modal-content">
            <div class="modal-title">Settings</div>
            <div class="settings-panel">
                <div class="settings-row">
                    <span class="settings-label">Font Size</span>
                    <input type="range" id="fontSizeSlider" min="0.8" max="1.4" step="0.1" value="1.0">
                    <span id="fontSizeValue">100%</span>
                </div>
                <div class="settings-row">
                    <span class="settings-label">Reset to defaults</span>
                    <button class="btn" id="resetBtn" style="background: var(--delete-color); color: white; border-color: var(--delete-color);">Reset</button>
                </div>
            </div>
            <div class="modal-buttons">
                <button class="btn" id="settingsCloseBtn">Close</button>
            </div>
        </div>
    </div>

    <script>
        // Storage key
        const STORAGE_KEY = 'yohoo-data-v2';

        // State
        let draggedElement = null;
        let draggedSection = null;
        let deletedLinks = [];
        let sectionOrder = [];
        let collapsedSections = [];
        let fontScale = 1.0;

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {{
            loadState();
            setupEventListeners();
            setupDragAndDrop();
            updateTrashDisplay();
        }});

        // Load state from localStorage
        function loadState() {{
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {{
                try {{
                    const data = JSON.parse(stored);

                    // Restore deleted links
                    if (data.deletedLinks) {{
                        deletedLinks = data.deletedLinks;
                    }}

                    // Restore section order
                    if (data.sectionOrder && data.sectionOrder.length > 0) {{
                        sectionOrder = data.sectionOrder;
                        restoreSectionOrder();
                    }}

                    // Restore collapsed sections
                    if (data.collapsedSections) {{
                        collapsedSections = data.collapsedSections;
                        collapsedSections.forEach(id => {{
                            const section = document.querySelector(`[data-section="${{id}}"]`);
                            if (section) section.classList.add('collapsed');
                        }});
                    }}

                    // Restore link assignments
                    if (data.linkAssignments) {{
                        applyLinkAssignments(data.linkAssignments);
                    }}

                    // Restore custom links
                    if (data.customLinks) {{
                        restoreCustomLinks(data.customLinks);
                    }}

                    // Restore custom sections
                    if (data.customSections) {{
                        data.customSections.forEach(section => {{
                            createSection(section.name, section.emoji, section.id);
                        }});
                    }}

                    // Restore font scale
                    if (data.fontScale) {{
                        fontScale = data.fontScale;
                        document.documentElement.style.setProperty('--font-scale', fontScale);
                        document.getElementById('fontSizeSlider').value = fontScale;
                        document.getElementById('fontSizeValue').textContent = Math.round(fontScale * 100) + '%';
                    }}

                    // Hide deleted links
                    deletedLinks.forEach(deleted => {{
                        const link = document.querySelector(`[data-url="${{CSS.escape(deleted.url)}}"]`);
                        if (link) link.remove();
                    }});

                }} catch (e) {{
                    console.error('Error loading state:', e);
                }}
            }}
        }}

        // Save state to localStorage
        function saveState() {{
            const linkAssignments = {{}};
            const customLinks = [];
            const customSections = [];

            // Collect link assignments
            document.querySelectorAll('.link-item').forEach(link => {{
                const section = link.closest('.section');
                if (section) {{
                    linkAssignments[link.dataset.url] = section.dataset.section;
                }}

                // Check for custom links (added by user)
                if (link.dataset.custom === 'true') {{
                    customLinks.push({{
                        url: link.dataset.url,
                        title: link.dataset.title,
                        domain: link.dataset.domain,
                        sectionId: section?.dataset.section
                    }});
                }}
            }});

            // Collect custom sections
            document.querySelectorAll('.section[data-custom="true"]').forEach(section => {{
                customSections.push({{
                    id: section.dataset.section,
                    name: section.querySelector('.section-title').textContent,
                    emoji: section.querySelector('.section-icon').textContent
                }});
            }});

            // Collect section order
            sectionOrder = [];
            document.querySelectorAll('.section').forEach(section => {{
                sectionOrder.push(section.dataset.section);
            }});

            // Collect collapsed sections
            collapsedSections = [];
            document.querySelectorAll('.section.collapsed').forEach(section => {{
                collapsedSections.push(section.dataset.section);
            }});

            const data = {{
                linkAssignments,
                customLinks,
                customSections,
                deletedLinks,
                sectionOrder,
                collapsedSections,
                fontScale
            }};

            localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        }}

        // Restore section order
        function restoreSectionOrder() {{
            const container = document.getElementById('sectionsContainer');
            sectionOrder.forEach(id => {{
                const section = document.querySelector(`[data-section="${{id}}"]`);
                if (section) {{
                    container.appendChild(section);
                }}
            }});
        }}

        // Apply link assignments
        function applyLinkAssignments(assignments) {{
            Object.entries(assignments).forEach(([url, sectionId]) => {{
                const link = document.querySelector(`[data-url="${{CSS.escape(url)}}"]`);
                const section = document.querySelector(`[data-section="${{sectionId}}"]`);

                if (link && section) {{
                    const linksList = section.querySelector('.links-list');
                    if (linksList && link.parentElement !== linksList) {{
                        // Remove placeholder if present
                        const placeholder = linksList.querySelector('.placeholder-text');
                        if (placeholder) placeholder.remove();

                        linksList.appendChild(link);
                    }}
                }}
            }});
        }}

        // Restore custom links
        function restoreCustomLinks(links) {{
            links.forEach(linkData => {{
                const section = document.querySelector(`[data-section="${{linkData.sectionId}}"]`);
                if (section) {{
                    const linksList = section.querySelector('.links-list');

                    // Check if link already exists
                    if (!document.querySelector(`[data-url="${{CSS.escape(linkData.url)}}"]`)) {{
                        const linkEl = createLinkElement(linkData.url, linkData.title, linkData.domain, true);

                        // Remove placeholder if present
                        const placeholder = linksList.querySelector('.placeholder-text');
                        if (placeholder) placeholder.remove();

                        linksList.appendChild(linkEl);
                    }}
                }}
            }});
        }}

        // Create link element
        function createLinkElement(url, title, domain, isCustom = false) {{
            const link = document.createElement('a');
            link.href = url;
            link.className = 'link-item';
            link.draggable = true;
            link.dataset.url = url;
            link.dataset.title = title;
            link.dataset.domain = domain || '';
            if (isCustom) link.dataset.custom = 'true';

            link.innerHTML = `
                <span class="link-text">${{title}}</span>
                <span class="delete-icon" onclick="event.preventDefault(); event.stopPropagation(); deleteLink(this.parentElement);">×</span>
            `;

            // Setup drag handlers
            link.addEventListener('dragstart', handleLinkDragStart);
            link.addEventListener('dragend', handleLinkDragEnd);

            return link;
        }}

        // Create section
        function createSection(name, emoji, customId = null) {{
            const container = document.getElementById('sectionsContainer');
            const id = customId || 'custom-' + Date.now();

            const section = document.createElement('div');
            section.className = 'section';
            section.dataset.section = id;
            section.dataset.custom = 'true';
            section.draggable = true;

            section.innerHTML = `
                <div class="section-header">
                    <span class="section-icon">${{emoji}}</span>
                    <h2 class="section-title">${{name}}</h2>
                    <span class="section-toggle">−</span>
                </div>
                <div class="links-list">
                    <div class="placeholder-text">Drag links here</div>
                </div>
            `;

            container.appendChild(section);
            setupSectionDragAndDrop(section);

            // Setup toggle
            section.querySelector('.section-toggle').addEventListener('click', (e) => {{
                e.stopPropagation();
                section.classList.toggle('collapsed');
                saveState();
            }});

            return section;
        }}

        // Setup event listeners
        function setupEventListeners() {{
            // Search
            const searchBox = document.getElementById('searchBox');
            searchBox.addEventListener('input', handleSearch);

            // Keyboard shortcuts
            document.addEventListener('keydown', (e) => {{
                if (e.key === '/' && document.activeElement !== searchBox) {{
                    e.preventDefault();
                    searchBox.focus();
                }}
                if (e.key === 'Escape') {{
                    searchBox.value = '';
                    handleSearch({{ target: searchBox }});
                    searchBox.blur();
                    closeAllModals();
                }}
            }});

            // Add Section Modal
            document.getElementById('addSectionBtn').addEventListener('click', () => {{
                document.getElementById('addSectionModal').classList.add('show');
                document.getElementById('sectionNameInput').focus();
            }});

            document.getElementById('modalCancelBtn').addEventListener('click', () => {{
                document.getElementById('addSectionModal').classList.remove('show');
            }});

            document.getElementById('modalAddBtn').addEventListener('click', () => {{
                const name = document.getElementById('sectionNameInput').value.trim();
                const emoji = document.getElementById('sectionIconInput').value.trim() || '📁';

                if (name) {{
                    createSection(name, emoji);
                    saveState();

                    document.getElementById('addSectionModal').classList.remove('show');
                    document.getElementById('sectionNameInput').value = '';
                    document.getElementById('sectionIconInput').value = '📁';
                }}
            }});

            // Settings Modal
            document.getElementById('settingsBtn').addEventListener('click', () => {{
                document.getElementById('settingsModal').classList.add('show');
            }});

            document.getElementById('settingsCloseBtn').addEventListener('click', () => {{
                document.getElementById('settingsModal').classList.remove('show');
            }});

            document.getElementById('fontSizeSlider').addEventListener('input', (e) => {{
                fontScale = parseFloat(e.target.value);
                document.documentElement.style.setProperty('--font-scale', fontScale);
                document.getElementById('fontSizeValue').textContent = Math.round(fontScale * 100) + '%';
                saveState();
            }});

            document.getElementById('resetBtn').addEventListener('click', () => {{
                if (confirm('Reset all customizations? This will restore the default layout.')) {{
                    localStorage.removeItem(STORAGE_KEY);
                    location.reload();
                }}
            }});

            // Trash toggle
            document.getElementById('trashHeader').addEventListener('click', () => {{
                const content = document.getElementById('trashContent');
                const toggle = document.querySelector('.trash-toggle');
                content.classList.toggle('expanded');
                toggle.textContent = content.classList.contains('expanded') ? '▲' : '▼';
            }});

            // Section toggles
            document.querySelectorAll('.section-toggle').forEach(toggle => {{
                toggle.addEventListener('click', (e) => {{
                    e.stopPropagation();
                    const section = toggle.closest('.section');
                    section.classList.toggle('collapsed');
                    saveState();
                }});
            }});

            // Modal close on background click
            document.querySelectorAll('.modal').forEach(modal => {{
                modal.addEventListener('click', (e) => {{
                    if (e.target === modal) {{
                        modal.classList.remove('show');
                    }}
                }});
            }});

            // Enter key in modal inputs
            document.getElementById('sectionNameInput').addEventListener('keydown', (e) => {{
                if (e.key === 'Enter') document.getElementById('modalAddBtn').click();
            }});
        }}

        // Search functionality
        function handleSearch(e) {{
            const term = e.target.value.toLowerCase().trim();

            document.querySelectorAll('.link-item').forEach(link => {{
                const text = (link.dataset.title || link.textContent).toLowerCase();
                link.classList.toggle('hidden', term && !text.includes(term));
            }});

            document.querySelectorAll('.section').forEach(section => {{
                const visibleLinks = section.querySelectorAll('.link-item:not(.hidden)');
                section.style.display = (term && visibleLinks.length === 0) ? 'none' : '';
            }});
        }}

        // Drag and Drop Setup
        function setupDragAndDrop() {{
            // Links
            document.querySelectorAll('.link-item').forEach(link => {{
                link.addEventListener('dragstart', handleLinkDragStart);
                link.addEventListener('dragend', handleLinkDragEnd);
            }});

            // Link containers
            document.querySelectorAll('.links-list').forEach(list => {{
                list.addEventListener('dragover', handleLinkDragOver);
                list.addEventListener('dragleave', handleLinkDragLeave);
                list.addEventListener('drop', handleLinkDrop);
            }});

            // Sections
            document.querySelectorAll('.section').forEach(section => {{
                setupSectionDragAndDrop(section);
            }});
        }}

        function setupSectionDragAndDrop(section) {{
            section.addEventListener('dragstart', handleSectionDragStart);
            section.addEventListener('dragend', handleSectionDragEnd);
            section.addEventListener('dragover', handleSectionDragOver);
            section.addEventListener('dragleave', handleSectionDragLeave);
            section.addEventListener('drop', handleSectionDrop);
        }}

        // Link drag handlers
        function handleLinkDragStart(e) {{
            draggedElement = this;
            this.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', this.dataset.url);
            e.stopPropagation();
        }}

        function handleLinkDragEnd(e) {{
            this.classList.remove('dragging');
            document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
            draggedElement = null;
        }}

        function handleLinkDragOver(e) {{
            if (!draggedElement) return;
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            this.classList.add('drag-over');
        }}

        function handleLinkDragLeave(e) {{
            if (e.target === this) {{
                this.classList.remove('drag-over');
            }}
        }}

        function handleLinkDrop(e) {{
            e.preventDefault();
            e.stopPropagation();
            this.classList.remove('drag-over');

            if (draggedElement && draggedElement.parentElement !== this) {{
                // Remove placeholder if present
                const placeholder = this.querySelector('.placeholder-text');
                if (placeholder) placeholder.remove();

                this.appendChild(draggedElement);
                saveState();
            }}
        }}

        // Section drag handlers
        function handleSectionDragStart(e) {{
            if (e.target.classList.contains('link-item')) return;
            draggedSection = this;
            this.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/x-section', this.dataset.section);
        }}

        function handleSectionDragEnd(e) {{
            this.classList.remove('dragging');
            document.querySelectorAll('.section').forEach(s => {{
                s.style.borderTop = '';
                s.style.borderBottom = '';
            }});
            draggedSection = null;
        }}

        function handleSectionDragOver(e) {{
            if (!draggedSection || draggedSection === this) return;
            if (draggedElement) return; // Don't handle if dragging a link

            e.preventDefault();
            e.stopPropagation();

            const rect = this.getBoundingClientRect();
            const midY = rect.top + rect.height / 2;

            document.querySelectorAll('.section').forEach(s => {{
                s.style.borderTop = '';
                s.style.borderBottom = '';
            }});

            if (e.clientY < midY) {{
                this.style.borderTop = '3px solid var(--header-color)';
            }} else {{
                this.style.borderBottom = '3px solid var(--header-color)';
            }}
        }}

        function handleSectionDragLeave(e) {{
            this.style.borderTop = '';
            this.style.borderBottom = '';
        }}

        function handleSectionDrop(e) {{
            if (!draggedSection || draggedSection === this) return;
            if (draggedElement) return;

            e.preventDefault();
            e.stopPropagation();

            const rect = this.getBoundingClientRect();
            const midY = rect.top + rect.height / 2;
            const container = this.parentElement;

            if (e.clientY < midY) {{
                container.insertBefore(draggedSection, this);
            }} else {{
                container.insertBefore(draggedSection, this.nextSibling);
            }}

            this.style.borderTop = '';
            this.style.borderBottom = '';

            saveState();
        }}

        // Delete link
        function deleteLink(linkElement) {{
            const linkData = {{
                url: linkElement.dataset.url,
                title: linkElement.dataset.title,
                domain: linkElement.dataset.domain,
                sectionId: linkElement.closest('.section')?.dataset.section,
                isCustom: linkElement.dataset.custom === 'true'
            }};

            deletedLinks.push(linkData);
            linkElement.remove();
            updateTrashDisplay();
            saveState();
        }}

        // Restore link
        function restoreLink(index) {{
            const linkData = deletedLinks[index];
            if (!linkData) return;

            const section = document.querySelector(`[data-section="${{linkData.sectionId}}"]`);
            if (section) {{
                const linksList = section.querySelector('.links-list');

                // Remove placeholder if present
                const placeholder = linksList.querySelector('.placeholder-text');
                if (placeholder) placeholder.remove();

                const linkEl = createLinkElement(linkData.url, linkData.title, linkData.domain, linkData.isCustom);
                linksList.appendChild(linkEl);
            }}

            deletedLinks.splice(index, 1);
            updateTrashDisplay();
            saveState();
        }}

        // Update trash display
        function updateTrashDisplay() {{
            document.getElementById('trashCount').textContent = `(${{deletedLinks.length}})`;

            const trashLinks = document.getElementById('trashLinks');
            if (deletedLinks.length === 0) {{
                trashLinks.innerHTML = '<div style="color: var(--text-muted); font-size: 0.85rem; padding: 0.5rem;">No deleted links</div>';
            }} else {{
                trashLinks.innerHTML = deletedLinks.map((link, i) => `
                    <div class="trash-item">
                        <span class="trash-item-link">${{link.title}}</span>
                        <button class="restore-btn" onclick="restoreLink(${{i}})">Restore</button>
                    </div>
                `).join('');
            }}
        }}

        // Close all modals
        function closeAllModals() {{
            document.querySelectorAll('.modal').forEach(modal => {{
                modal.classList.remove('show');
            }});
        }}
    </script>
</body>
</html>'''

    # Write to file
    output_path = os.path.join(PROJECT_DIR, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated {output_file} with {len(sections)} sections and {total_links} links")
    print(f"Plus {len(user_sections)} empty user sections ready for customization")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate yohoo.html start page')
    parser.add_argument('--defaults', '-d', default=None,
                       help=f'Path to default links JSON (default: {DEFAULT_LINKS_FILE})')
    parser.add_argument('--output', '-o', default='yohoo.html',
                       help='Output HTML file (default: yohoo.html)')

    args = parser.parse_args()

    generate_html(args.output, args.defaults)


if __name__ == '__main__':
    main()
