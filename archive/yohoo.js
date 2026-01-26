// Yohoo JavaScript
// localStorage key
const STORAGE_KEY = 'yohoo-custom-layout';

// State
let draggedElement = null;
let draggedSubcategory = null;
let customSubcategories = [];
let subcategoryOrder = [];
let deletedLinks = [];

// Debug logging
const debugLog = [];
function log(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const entry = `[${timestamp}] ${message}`;
    debugLog.push({ message: entry, type });
    console.log(entry);

    const debugLogEl = document.getElementById('debugLog');
    if (debugLogEl && debugLogEl.parentElement.parentElement.style.display !== 'none') {
        const entryDiv = document.createElement('div');
        entryDiv.className = `debug-entry ${type}`;
        entryDiv.textContent = entry;
        debugLogEl.appendChild(entryDiv);
        debugLogEl.scrollTop = debugLogEl.scrollHeight;
    }
}

function updateDebugStorage() {
    const debugStorageEl = document.getElementById('debugStorage');
    if (debugStorageEl) {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            try {
                const data = JSON.parse(stored);
                debugStorageEl.innerHTML = `
                    <div>Subcategories: ${data.customSubcategories?.length || 0}</div>
                    <div>Link Assignments: ${Object.keys(data.linkAssignments || {}).length}</div>
                    <div>Custom Links: ${data.customLinks?.length || 0}</div>
                    <div>Deleted Links: ${data.deletedLinks?.length || 0}</div>
                    <details style="margin-top: 5px;">
                        <summary>Raw Data</summary>
                        <pre style="font-size: 8px; overflow-x: auto;">${JSON.stringify(data, null, 2)}</pre>
                    </details>
                `;
            } catch (e) {
                debugStorageEl.textContent = 'Error parsing: ' + e.message;
            }
        } else {
            debugStorageEl.textContent = 'No data stored';
        }
    }
}

// Debug toggle
document.addEventListener('DOMContentLoaded', () => {
    const debugToggle = document.getElementById('debugToggle');
    const debugPanel = document.getElementById('debugPanel');

    debugToggle.addEventListener('click', () => {
        if (debugPanel.style.display === 'none') {
            debugPanel.style.display = 'block';
            updateDebugStorage();
        } else {
            debugPanel.style.display = 'none';
        }
    });
});

// Update time display
function updateTime() {
    const now = new Date();
    const options = {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    document.getElementById('currentTime').textContent = now.toLocaleDateString('en-US', options);
}

updateTime();
setInterval(updateTime, 60000);

// Search functionality
const searchBox = document.getElementById('searchBox');

searchBox.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase().trim();

    if (searchTerm === '') {
        document.querySelectorAll('.subcategory').forEach(cat => cat.classList.remove('hidden'));
        document.querySelectorAll('.link-item').forEach(link => link.classList.remove('hidden'));
        return;
    }

    // Filter links
    document.querySelectorAll('.link-item').forEach(link => {
        const text = link.querySelector('.link-text').textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            link.classList.remove('hidden');
        } else {
            link.classList.add('hidden');
        }
    });

    // Hide subcategories with no visible links
    document.querySelectorAll('.subcategory').forEach(subcategory => {
        const visibleLinks = subcategory.querySelectorAll('.link-item:not(.hidden)');
        if (visibleLinks.length === 0) {
            subcategory.classList.add('hidden');
        } else {
            subcategory.classList.remove('hidden');
        }
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement !== searchBox) {
        e.preventDefault();
        searchBox.focus();
    }

    if (e.key === 'Escape' && document.activeElement === searchBox) {
        searchBox.value = '';
        searchBox.dispatchEvent(new Event('input'));
        searchBox.blur();
    }
});

// Save/Load functions
function saveSubcategoryOrder() {
    const order = [];
    document.querySelectorAll('.subcategory').forEach(subcat => {
        order.push(subcat.dataset.subcategory);
    });
    subcategoryOrder = order;
    log(`Saved subcategory order: ${order.join(', ')}`);
    saveCustomLayout();
}

function restoreSubcategoryOrder() {
    if (!subcategoryOrder || subcategoryOrder.length === 0) return;

    log(`Restoring subcategory order: ${subcategoryOrder.join(', ')}`);

    const container = document.getElementById('subcategoriesContainer');
    const subcategories = Array.from(document.querySelectorAll('.subcategory'));

    subcategoryOrder.forEach(subcatId => {
        const subcategory = subcategories.find(subcat => subcat.dataset.subcategory === subcatId);
        if (subcategory) {
            container.appendChild(subcategory);
        }
    });

    log('Subcategory order restored', 'success');
}

function saveCustomLayout() {
    log('Saving custom layout to localStorage');

    const linkAssignments = {};
    const customLinks = [];

    document.querySelectorAll('.link-item').forEach(link => {
        const url = link.dataset.url;
        const subcategory = link.closest('.subcategory');

        if (subcategory) {
            linkAssignments[url] = subcategory.dataset.subcategory;
        }

        if (!link.hasAttribute('data-original')) {
            customLinks.push({
                url: url,
                title: link.dataset.title || link.textContent,
                domain: link.dataset.domain || ''
            });
        }
    });

    const data = {
        customSubcategories: customSubcategories,
        linkAssignments: linkAssignments,
        customLinks: customLinks,
        subcategoryOrder: subcategoryOrder,
        deletedLinks: deletedLinks
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    log(`Saved: ${Object.keys(linkAssignments).length} assignments, ${customLinks.length} custom links, ${subcategoryOrder.length} subcategory order, ${deletedLinks.length} deleted`, 'success');
    updateDebugStorage();
}

function applyLinkAssignments(assignments) {
    let movedCount = 0;
    let notFoundCount = 0;

    Object.entries(assignments).forEach(([url, targetId]) => {
        const links = document.querySelectorAll('.link-item');
        const link = Array.from(links).find(l => l.dataset.url === url);

        if (!link) {
            notFoundCount++;
            return;
        }

        const targetContainer = document.querySelector(`[data-subcategory="${targetId}"] .links-list`);

        if (!targetContainer) {
            log(`Target subcategory not found: ${targetId}`, 'error');
            return;
        }

        if (link.parentElement !== targetContainer) {
            const linkTitle = link.dataset.title || link.textContent;
            log(`Moving "${linkTitle.substring(0, 30)}" to ${targetId}`);
            targetContainer.appendChild(link);
            movedCount++;
        }
    });

    log(`Applied assignments: ${movedCount} moved, ${notFoundCount} not found`, movedCount > 0 ? 'success' : 'info');
}

function restoreCustomLinks(customLinks, assignments) {
    customLinks.forEach(linkData => {
        const newLink = document.createElement('a');
        newLink.href = linkData.url;
        newLink.className = 'link-item';
        newLink.draggable = true;
        newLink.dataset.url = linkData.url;
        newLink.dataset.title = linkData.title;
        newLink.dataset.domain = linkData.domain;

        newLink.innerHTML = `
            <span class="link-text">${linkData.title}</span>
            <span class="delete-icon" onclick="event.preventDefault(); deleteLink(this.parentElement);">🗑️</span>
        `;

        // Add event listeners
        newLink.addEventListener('mousedown', handleMouseDown);
        newLink.addEventListener('dragstart', handleDragStart);
        newLink.addEventListener('dragend', handleDragEnd);
        newLink.addEventListener('click', handleLinkClick);

        // Find target container
        const targetId = assignments[linkData.url];
        if (targetId) {
            const targetContainer = document.querySelector(`[data-subcategory="${targetId}"] .links-list`);
            if (targetContainer) {
                targetContainer.appendChild(newLink);
            }
        }
    });
}

function loadCustomLayout() {
    log('Loading custom layout from localStorage');

    const originalCount = document.querySelectorAll('.link-item').length;
    document.querySelectorAll('.link-item').forEach(link => {
        link.setAttribute('data-original', 'true');
    });
    log(`Marked ${originalCount} original links`);

    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
        try {
            const data = JSON.parse(stored);
            log(`Loaded data: ${Object.keys(data.linkAssignments || {}).length} assignments, ${data.customLinks?.length || 0} custom links, ${data.subcategoryOrder?.length || 0} subcategory order, ${data.deletedLinks?.length || 0} deleted`);

            if (data.customSubcategories) {
                customSubcategories = data.customSubcategories;
                // TODO: Render custom subcategories
            }
            if (data.subcategoryOrder) {
                subcategoryOrder = data.subcategoryOrder;
            }
            if (data.deletedLinks) {
                deletedLinks = data.deletedLinks;
                log(`Restored ${deletedLinks.length} deleted links`);
                updateTrashDisplay();
            }
            if (data.customLinks) {
                log(`Restoring ${data.customLinks.length} custom links`);
                restoreCustomLinks(data.customLinks, data.linkAssignments);
            }
            if (data.linkAssignments) {
                log(`Applying ${Object.keys(data.linkAssignments).length} link assignments`);
                applyLinkAssignments(data.linkAssignments);
            }
            if (data.subcategoryOrder) {
                restoreSubcategoryOrder();
            }
            log('Custom layout loaded successfully', 'success');
        } catch (e) {
            log('Error loading custom layout: ' + e.message, 'error');
            console.error('Error loading custom layout:', e);
        }
    } else {
        log('No saved layout found');
    }
}

// Drag and Drop for links
let isDragging = false;
let dragStartPos = null;

function setupDragAndDrop() {
    // Make all link items draggable
    document.querySelectorAll('.link-item').forEach(link => {
        link.addEventListener('mousedown', handleMouseDown);
        link.addEventListener('dragstart', handleDragStart);
        link.addEventListener('dragend', handleDragEnd);
        link.addEventListener('click', handleLinkClick);
    });

    // Make all link containers drop targets
    document.querySelectorAll('.links-list').forEach(container => {
        container.addEventListener('dragover', handleDragOver);
        container.addEventListener('drop', handleDrop);
        container.addEventListener('dragleave', handleDragLeave);
    });

    // Make subcategories draggable
    setupSubcategoryDragAndDrop();
}

function setupSubcategoryDragAndDrop() {
    document.querySelectorAll('.subcategory').forEach(subcategory => {
        // Make subcategory draggable, but only from the header
        subcategory.setAttribute('draggable', 'false'); // Not draggable by default
        
        const header = subcategory.querySelector('.subcategory-header');
        if (header) {
            // Make the header the drag handle
            header.style.cursor = 'grab';
            header.setAttribute('draggable', 'true');
            header.addEventListener('dragstart', handleSubcategoryDragStart);
            header.addEventListener('dragend', handleSubcategoryDragEnd);
        }
        
        subcategory.addEventListener('dragover', handleSubcategoryDragOver);
        subcategory.addEventListener('drop', handleSubcategoryDrop);
        subcategory.addEventListener('dragleave', handleSubcategoryDragLeave);
    });
}

function handleSubcategoryDragStart(e) {
    // Get the parent subcategory
    const subcategory = this.closest('.subcategory');
    if (!subcategory) return;
    
    e.stopPropagation(); // Prevent link drag events from interfering
    
    draggedSubcategory = subcategory;
    subcategory.classList.add('dragging-subcategory');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/x-yohoo-subcategory', subcategory.dataset.subcategory);
    
    this.style.cursor = 'grabbing';
    log(`SUBCATEGORY DRAG START: ${this.querySelector('.subcategory-title').textContent}`);
}

function handleSubcategoryDragEnd(e) {
    const subcategory = this.closest('.subcategory');
    if (subcategory) {
        subcategory.classList.remove('dragging-subcategory');
        subcategory.style.borderLeft = '';
        subcategory.style.borderRight = '';
    }
    this.style.cursor = 'grab';
    draggedSubcategory = null;
    
    // Clean up any lingering visual indicators
    document.querySelectorAll('.subcategory').forEach(s => {
        s.style.borderLeft = '';
        s.style.borderRight = '';
    });
}

function handleSubcategoryDragOver(e) {
    // Only handle subcategory-to-subcategory drags here
    if (!draggedSubcategory) return;
    if (draggedSubcategory === this) return;

    e.preventDefault();
    e.stopPropagation();

    const rect = this.getBoundingClientRect();
    const midpoint = rect.left + rect.width / 2;
    const insertBefore = e.clientX < midpoint;

    this.style.borderLeft = insertBefore ? '3px solid #c4a3ff' : '';
    this.style.borderRight = !insertBefore ? '3px solid #c4a3ff' : '';

    return false;
}

function handleSubcategoryDragLeave(e) {
    // Only clear borders if we're leaving the subcategory entirely
    if (e.target === this && !this.contains(e.relatedTarget)) {
        this.style.borderLeft = '';
        this.style.borderRight = '';
    }
}

function handleSubcategoryDrop(e) {
    if (!draggedSubcategory || draggedSubcategory === this) {
        return;
    }

    e.preventDefault();
    e.stopPropagation();

    this.style.borderLeft = '';
    this.style.borderRight = '';

    const rect = this.getBoundingClientRect();
    const midpoint = rect.left + rect.width / 2;
    const insertBefore = e.clientX < midpoint;

    const container = this.parentElement;
    if (insertBefore) {
        container.insertBefore(draggedSubcategory, this);
    } else {
        container.insertBefore(draggedSubcategory, this.nextSibling);
    }

    log(`SUBCATEGORY MOVED: ${draggedSubcategory.querySelector('.subcategory-title').textContent} ${insertBefore ? 'before' : 'after'} ${this.querySelector('.subcategory-title').textContent}`);

    saveSubcategoryOrder();
}

function handleMouseDown(e) {
    dragStartPos = { x: e.clientX, y: e.clientY };
    isDragging = false;
}

function handleLinkClick(e) {
    if (isDragging) {
        e.preventDefault();
        isDragging = false;
    }
}

function handleDragStart(e) {
    // Don't allow drag if we're dragging a subcategory
    if (draggedSubcategory) {
        e.preventDefault();
        return;
    }
    
    // DON'T prevent default here - we need the drag to work!
    // e.preventDefault() would stop the drag operation
    
    isDragging = true;
    draggedElement = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/x-yohoo-link', this.dataset.url);
    
    // Set both for compatibility
    e.dataTransfer.setData('text/uri-list', this.dataset.url);
    e.dataTransfer.setData('text/plain', this.dataset.url);
    
    // Create custom drag image to make it clearer what's being dragged
    const dragImage = document.createElement('div');
    dragImage.style.position = 'absolute';
    dragImage.style.top = '-1000px';
    dragImage.style.background = '#3d2854';
    dragImage.style.border = '1px solid #9d7ee0';
    dragImage.style.borderRadius = '3px';
    dragImage.style.padding = '4px 8px';
    dragImage.style.color = '#7dd3fc';
    dragImage.style.fontSize = '11px';
    dragImage.style.whiteSpace = 'nowrap';
    dragImage.style.maxWidth = '300px';
    dragImage.style.overflow = 'hidden';
    dragImage.style.textOverflow = 'ellipsis';
    dragImage.textContent = this.querySelector('.link-text')?.textContent || this.dataset.title || 'Link';
    document.body.appendChild(dragImage);
    e.dataTransfer.setDragImage(dragImage, 0, 0);
    
    // Clean up the drag image after a short delay
    setTimeout(() => {
        document.body.removeChild(dragImage);
    }, 0);
    
    e.stopPropagation();
    
    log(`LINK DRAG START: ${this.dataset.title || this.textContent}`);
}

function handleDragEnd(e) {
    log(`LINK DRAG END: ${this.dataset.title || this.textContent}`, 'info');
    this.classList.remove('dragging');
    document.querySelectorAll('.drag-over').forEach(el => {
        el.classList.remove('drag-over');
    });
    draggedElement = null;
    isDragging = false;
}

function handleDragOver(e) {
    // Only handle link drops, not subcategory drops
    if (draggedSubcategory) {
        log('DragOver: Ignoring because subcategory is being dragged');
        return;
    }
    
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.stopPropagation();
    
    // Set dropEffect based on whether this is an internal or external drag
    e.dataTransfer.dropEffect = draggedElement ? 'move' : 'copy';
    this.classList.add('drag-over');
    
    const subcategory = this.closest('.subcategory');
    const subcatName = subcategory?.dataset.subcategory || 'unknown';
    log(`DragOver: ${subcatName} (draggedElement: ${draggedElement ? 'yes' : 'no'})`);
    
    return false;
}

function handleDragLeave(e) {
    if (e.target === this) {
        this.classList.remove('drag-over');
    }
}

function handleDrop(e) {
    log(`DROP EVENT TRIGGERED on ${this.closest('.subcategory')?.dataset.subcategory || 'unknown'}`, 'success');
    
    // Only handle link drops, not subcategory drops
    if (draggedSubcategory) {
        log('Drop: Ignoring because subcategory is being dragged');
        return;
    }
    
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    if (e.preventDefault) {
        e.preventDefault();
    }

    this.classList.remove('drag-over');

    if (draggedElement) {
        // Internal link drop - move link to new location
        if (draggedElement.parentElement !== this) {
            const linkTitle = draggedElement.dataset.title || draggedElement.textContent;
            const targetSubcat = this.closest('.subcategory');
            const targetName = targetSubcat?.dataset.subcategory || 'unknown';

            log(`DROP: Moving "${linkTitle.substring(0, 30)}" to ${targetName}`);
            this.appendChild(draggedElement);
            saveCustomLayout();
        }
    } else {
        // External drop from browser URL bar
        const urlData = e.dataTransfer.getData('text/uri-list') || 
                       e.dataTransfer.getData('text/plain') || 
                       e.dataTransfer.getData('URL');
        const htmlData = e.dataTransfer.getData('text/html');

        log(`External drop - URL: ${urlData?.substring(0, 50)}, HTML: ${htmlData ? 'present' : 'none'}`);

        if (urlData && urlData.startsWith('http')) {
            // Log all available data types for debugging
            log(`Drop data types: ${e.dataTransfer.types.join(', ')}`);
            log(`URL: ${urlData.substring(0, 100)}`);
            log(`HTML: ${htmlData ? htmlData.substring(0, 200) : 'none'}`);

            const newLink = document.createElement('a');
            newLink.href = urlData;
            newLink.className = 'link-item';
            newLink.draggable = true;
            newLink.dataset.url = urlData;

            // Try to extract title from HTML data (Chrome includes this when dragging from address bar)
            let title = null;
            if (htmlData) {
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = htmlData;
                const anchor = tempDiv.querySelector('a');
                if (anchor && anchor.textContent.trim()) {
                    title = anchor.textContent.trim();
                    log(`Extracted title from HTML: "${title}"`);
                } else {
                    log(`No anchor found in HTML data`);
                }
            } else {
                log(`No HTML data available in drag event`);
            }

            // If no title from HTML, try to fetch it from the page
            if (!title) {
                try {
                    const url = new URL(urlData);
                    newLink.dataset.domain = url.hostname;
                    newLink.dataset.title = url.hostname;
                    newLink.innerHTML = `
                        <span class="link-text">${url.hostname}</span>
                        <span class="delete-icon" onclick="event.preventDefault(); deleteLink(this.parentElement);">🗑️</span>
                    `;

                    // Fetch the actual page title asynchronously
                    fetch(urlData, { mode: 'cors' })
                        .then(response => response.text())
                        .then(html => {
                            const parser = new DOMParser();
                            const doc = parser.parseFromString(html, 'text/html');
                            const pageTitle = doc.querySelector('title')?.textContent;
                            if (pageTitle) {
                                newLink.dataset.title = pageTitle;
                                newLink.querySelector('.link-text').textContent = pageTitle;
                                log(`Fetched title: "${pageTitle}"`);
                                saveCustomLayout();
                            }
                        })
                        .catch(err => {
                            log(`Could not fetch title: ${err.message}`, 'error');
                        });
                } catch (err) {
                    newLink.dataset.title = urlData;
                    newLink.innerHTML = `
                        <span class="link-text">${urlData}</span>
                        <span class="delete-icon" onclick="event.preventDefault(); deleteLink(this.parentElement);">🗑️</span>
                    `;
                }
            } else {
                try {
                    const url = new URL(urlData);
                    newLink.dataset.domain = url.hostname;
                    newLink.dataset.title = title;
                    newLink.innerHTML = `
                        <span class="link-text">${title}</span>
                        <span class="delete-icon" onclick="event.preventDefault(); deleteLink(this.parentElement);">🗑️</span>
                    `;
                } catch (err) {
                    newLink.dataset.title = title;
                    newLink.innerHTML = `
                        <span class="link-text">${title}</span>
                        <span class="delete-icon" onclick="event.preventDefault(); deleteLink(this.parentElement);">🗑️</span>
                    `;
                }
            }

            newLink.addEventListener('mousedown', handleMouseDown);
            newLink.addEventListener('dragstart', handleDragStart);
            newLink.addEventListener('dragend', handleDragEnd);
            newLink.addEventListener('click', handleLinkClick);

            this.appendChild(newLink);
            log(`Added new link: "${newLink.dataset.title}"`);
            saveCustomLayout();
        }
    }

    return false;
}

// Delete/Undelete functionality
function deleteLink(linkElement) {
    const url = linkElement.dataset.url;
    const title = linkElement.dataset.title || linkElement.querySelector('.link-text')?.textContent || 'Unknown';
    const domain = linkElement.dataset.domain || '';

    const subcategory = linkElement.closest('.subcategory');
    const subcategoryId = subcategory?.dataset.subcategory;

    log(`DELETE: "${title.substring(0, 30)}" from ${subcategoryId}`);

    deletedLinks.push({
        url: url,
        title: title,
        domain: domain,
        subcategoryId: subcategoryId,
        href: linkElement.href,
        isOriginal: linkElement.hasAttribute('data-original')
    });

    linkElement.remove();
    updateTrashDisplay();
    saveCustomLayout();
}

function undeleteLink(index) {
    const linkData = deletedLinks[index];
    if (!linkData) return;

    log(`UNDELETE: "${linkData.title.substring(0, 30)}" to ${linkData.subcategoryId}`);

    let targetContainer = document.querySelector(`[data-subcategory="${linkData.subcategoryId}"] .links-list`);

    if (!targetContainer) {
        log(`Could not find subcategory ${linkData.subcategoryId}, placing in Misc`, 'error');
        targetContainer = document.querySelector(`[data-subcategory="misc"] .links-list`);
    }

    if (targetContainer) {
        const newLink = document.createElement('a');
        newLink.href = linkData.href;
        newLink.className = 'link-item';
        newLink.draggable = true;
        newLink.dataset.url = linkData.url;
        newLink.dataset.title = linkData.title;
        newLink.dataset.domain = linkData.domain;
        if (linkData.isOriginal) {
            newLink.setAttribute('data-original', 'true');
        }

        newLink.innerHTML = `
            <span class="link-text">${linkData.title}</span>
            <span class="delete-icon" onclick="event.preventDefault(); deleteLink(this.parentElement);">🗑️</span>
        `;

        newLink.addEventListener('mousedown', handleMouseDown);
        newLink.addEventListener('dragstart', handleDragStart);
        newLink.addEventListener('dragend', handleDragEnd);
        newLink.addEventListener('click', handleLinkClick);

        targetContainer.appendChild(newLink);
    }

    deletedLinks.splice(index, 1);
    updateTrashDisplay();
    saveCustomLayout();
}

function updateTrashDisplay() {
    const trashLinks = document.getElementById('trashLinks');
    const trashCount = document.getElementById('trashCount');

    trashCount.textContent = `(${deletedLinks.length})`;

    if (deletedLinks.length === 0) {
        trashLinks.innerHTML = '<div style="color: #8e72b8; font-size: 11px; padding: 8px;">No deleted links</div>';
    } else {
        trashLinks.innerHTML = deletedLinks.map((link, index) => `
            <div class="trash-item">
                <span class="trash-item-link">${link.title}</span>
                <button class="undelete-btn" onclick="undeleteLink(${index})">Restore</button>
            </div>
        `).join('');
    }
}

// Trash toggle
document.getElementById('trashHeader').addEventListener('click', () => {
    const content = document.getElementById('trashContent');
    const toggle = document.querySelector('.trash-toggle');
    content.classList.toggle('expanded');
    toggle.textContent = content.classList.contains('expanded') ? '▲' : '▼';
});

// Prevent default drag/drop behavior on the entire document
document.addEventListener('dragover', (e) => {
    e.preventDefault();
});

document.addEventListener('drop', (e) => {
    e.preventDefault();
});

// Initialize
loadCustomLayout();
setupDragAndDrop();
updateTrashDisplay();
