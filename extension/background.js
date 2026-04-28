const MAX_TITLE_HTML_BYTES = 256 * 1024;
const FETCH_TIMEOUT_MS = 5000;
const HELPER_TIMEOUT_MS = 1500;
const LOCAL_HELPER_ENDPOINTS = [
    'http://127.0.0.1:3001/fetch-title',
    'http://localhost:3001/fetch-title'
];

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message?.type !== 'YOHOO_FETCH_TITLE') return false;

    resolveTitle(message.url)
        .then(result => sendResponse({
            requestId: message.requestId,
            ...result
        }))
        .catch(error => sendResponse({
            requestId: message.requestId,
            title: null,
            provider: null,
            error: error.message
        }));

    return true;
});

async function resolveTitle(rawUrl) {
    const url = normalizeUrl(rawUrl);
    if (!url || !/^https?:\/\//.test(url)) {
        return { title: null, provider: null, error: 'Unsupported URL' };
    }

    const tabTitle = await findOpenTabTitle(url);
    if (tabTitle) return { title: tabTitle, provider: 'open-tab', error: null };

    const fetchedTitle = await fetchTitleFromPage(url);
    if (fetchedTitle) return { title: fetchedTitle, provider: 'extension-fetch', error: null };

    const helperTitle = await fetchTitleFromLocalHelper(url);
    if (helperTitle) return { title: helperTitle, provider: 'local-helper', error: null };

    return { title: null, provider: null, error: null };
}

function normalizeUrl(rawUrl) {
    const trimmed = (rawUrl || '').trim();
    if (!trimmed) return null;
    if (trimmed.startsWith('www.')) return `https://${trimmed}`;
    return trimmed;
}

async function findOpenTabTitle(url) {
    const target = canonicalUrl(url);
    if (!target) return null;

    const tabs = await chrome.tabs.query({});
    for (const tab of tabs) {
        if (!tab.url || !tab.title) continue;

        if (urlsReferToSamePage(target, canonicalUrl(tab.url))) {
            const title = cleanTitle(tab.title);
            if (isUsefulTitle(title, url)) return title;
        }
    }

    return null;
}

function canonicalUrl(rawUrl) {
    try {
        const url = new URL(rawUrl);
        url.hash = '';
        return url.href.replace(/\/$/, '');
    } catch (_error) {
        return null;
    }
}

function urlsReferToSamePage(target, candidate) {
    if (!target || !candidate) return false;
    if (target === candidate) return true;

    try {
        const targetUrl = new URL(target);
        const candidateUrl = new URL(candidate);
        if (targetUrl.origin !== candidateUrl.origin) return false;

        const targetDoc = documentIdentity(targetUrl);
        const candidateDoc = documentIdentity(candidateUrl);
        return Boolean(targetDoc && targetDoc === candidateDoc);
    } catch (_error) {
        return false;
    }
}

function documentIdentity(url) {
    const googleDocMatch = url.pathname.match(/^\/(?:document|spreadsheets|presentation)\/d\/([^/]+)/);
    if (url.hostname === 'docs.google.com' && googleDocMatch) {
        return `google:${googleDocMatch[1]}`;
    }

    const vendWikiMatch = url.pathname.match(/^\/(?:wiki|w)\/([^/?#]+)/);
    if (vendWikiMatch) {
        return `${url.hostname}:vendwiki:${vendWikiMatch[1]}`;
    }

    return null;
}

async function fetchTitleFromPage(url) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

    try {
        const response = await fetch(url, {
            cache: 'no-store',
            credentials: 'include',
            redirect: 'follow',
            signal: controller.signal
        });
        if (!response.ok || !response.body) return null;

        const html = await readResponsePrefix(response);
        return extractTitle(html, url);
    } catch (_error) {
        return null;
    } finally {
        clearTimeout(timeoutId);
    }
}

async function readResponsePrefix(response) {
    const reader = response.body.getReader();
    const chunks = [];
    let size = 0;

    while (size < MAX_TITLE_HTML_BYTES) {
        const { done, value } = await reader.read();
        if (done) break;

        chunks.push(value);
        size += value.byteLength;
    }

    await reader.cancel().catch(() => {});
    const bytes = new Uint8Array(size);
    let offset = 0;
    for (const chunk of chunks) {
        bytes.set(chunk, offset);
        offset += chunk.byteLength;
    }

    return new TextDecoder().decode(bytes);
}

async function fetchTitleFromLocalHelper(url) {
    for (const endpoint of LOCAL_HELPER_ENDPOINTS) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), HELPER_TIMEOUT_MS);
        try {
            const response = await fetch(`${endpoint}?url=${encodeURIComponent(url)}`, {
                cache: 'no-store',
                signal: controller.signal
            });
            if (!response.ok) continue;
            const payload = await response.json();
            const title = cleanTitle(payload.title);
            if (isUsefulTitle(title, url)) return title;
        } catch (_error) {
            // Missing helper is expected on machines without the optional local app.
        } finally {
            clearTimeout(timeoutId);
        }
    }

    return null;
}

function extractTitle(html, url) {
    const metaTitle = extractMetaTitle(html);
    if (isUsefulTitle(metaTitle, url)) return metaTitle;

    const titleMatch = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
    if (!titleMatch) return null;

    const title = cleanTitle(decodeEntities(titleMatch[1]));
    return isUsefulTitle(title, url) ? title : null;
}

function extractMetaTitle(html) {
    const metaTags = html.match(/<meta\s+[^>]*>/gi) || [];
    for (const tag of metaTags) {
        const attrs = parseAttributes(tag);
        const name = (attrs.name || attrs.property || '').toLowerCase();
        if ((name === 'og:title' || name === 'twitter:title') && attrs.content) {
            return cleanTitle(decodeEntities(attrs.content));
        }
    }
    return null;
}

function parseAttributes(tag) {
    const attrs = {};
    const attrPattern = /([^\s="'<>/]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))/g;
    let match;

    while ((match = attrPattern.exec(tag)) !== null) {
        attrs[match[1].toLowerCase()] = match[2] || match[3] || match[4] || '';
    }

    return attrs;
}

function cleanTitle(value) {
    if (typeof value !== 'string') return null;
    const title = value.replace(/\s+/g, ' ').trim();
    return title || null;
}

function isUsefulTitle(title, rawUrl) {
    if (!title) return false;

    const lowerTitle = title.toLowerCase();
    const blockedTitles = new Set([
        'new tab',
        'untitled',
        'login',
        'log in',
        'sign in',
        'sign in - google accounts',
        'google accounts',
        'access denied',
        'unauthorized'
    ]);
    if (blockedTitles.has(lowerTitle)) return false;

    try {
        const url = new URL(normalizeUrl(rawUrl));
        const normalizedUrl = url.href.replace(/\/$/, '').toLowerCase();
        return lowerTitle !== normalizedUrl && lowerTitle !== url.hostname.toLowerCase();
    } catch (_error) {
        return true;
    }
}

function decodeEntities(value) {
    const entities = {
        amp: '&',
        lt: '<',
        gt: '>',
        quot: '"',
        apos: "'",
        '#39': "'"
    };

    return value.replace(/&([^;]+);/g, (match, entity) => {
        if (entities[entity]) return entities[entity];
        if (entity.startsWith('#x')) return decodeCodePoint(match, entity.slice(2), 16);
        if (entity.startsWith('#')) return decodeCodePoint(match, entity.slice(1), 10);
        return match;
    });
}

function decodeCodePoint(fallback, value, radix) {
    const codePoint = parseInt(value, radix);
    if (!Number.isFinite(codePoint)) return fallback;

    try {
        return String.fromCodePoint(codePoint);
    } catch (_error) {
        return fallback;
    }
}
