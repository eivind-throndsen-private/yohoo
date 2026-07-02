(() => {
    const PAGE_SOURCE = 'yohoo-page';
    const EXTENSION_SOURCE = 'yohoo-title-extension';
    const TRUSTED_HTTP_HOSTS = new Set([
        'static.m10s.io',
        'localhost',
        '127.0.0.1'
    ]);

    function pageTargetOrigin() {
        return window.location.protocol === 'file:' ? '*' : window.location.origin;
    }

    function postToPage(payload) {
        window.postMessage({
            source: EXTENSION_SOURCE,
            ...payload
        }, pageTargetOrigin());
    }

    function isTrustedYohooPage() {
        if (window.location.protocol === 'file:') {
            return window.location.pathname.endsWith('/yohoo.html');
        }

        return TRUSTED_HTTP_HOSTS.has(window.location.hostname);
    }

    window.addEventListener('message', event => {
        if (event.source !== window) return;
        if (!isTrustedYohooPage()) return;

        const message = event.data;
        if (!message || message.source !== PAGE_SOURCE) {
            return;
        }

        if (message.type === 'YOHOO_OPEN_LOCAL_FILE_REQUEST') {
            if (typeof message.url !== 'string' || !message.url.startsWith('file://')) {
                postToPage({
                    type: 'YOHOO_OPEN_LOCAL_FILE_RESPONSE',
                    requestId: message.requestId,
                    success: false,
                    error: 'Unsupported URL'
                });
                return;
            }

            chrome.runtime.sendMessage({
                type: 'YOHOO_OPEN_LOCAL_FILE',
                requestId: message.requestId,
                url: message.url
            }, response => {
                const runtimeError = chrome.runtime.lastError?.message;
                postToPage({
                    type: 'YOHOO_OPEN_LOCAL_FILE_RESPONSE',
                    requestId: message.requestId,
                    success: Boolean(response?.success),
                    error: response?.error || runtimeError || null
                });
            });
            return;
        }

        if (message.type !== 'YOHOO_TITLE_REQUEST') return;

        chrome.runtime.sendMessage({
            type: 'YOHOO_FETCH_TITLE',
            requestId: message.requestId,
            url: message.url
        }, response => {
            const runtimeError = chrome.runtime.lastError?.message;
            postToPage({
                type: 'YOHOO_TITLE_RESPONSE',
                requestId: message.requestId,
                title: response?.title || null,
                provider: response?.provider || null,
                error: response?.error || runtimeError || null
            });
        });
    });

    postToPage({ type: 'YOHOO_TITLE_READY' });
})();
