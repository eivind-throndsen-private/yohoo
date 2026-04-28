(() => {
    const PAGE_SOURCE = 'yohoo-page';
    const EXTENSION_SOURCE = 'yohoo-title-extension';

    function pageTargetOrigin() {
        return window.location.protocol === 'file:' ? '*' : window.location.origin;
    }

    function postToPage(payload) {
        window.postMessage({
            source: EXTENSION_SOURCE,
            ...payload
        }, pageTargetOrigin());
    }

    window.addEventListener('message', event => {
        if (event.source !== window) return;

        const message = event.data;
        if (!message || message.source !== PAGE_SOURCE || message.type !== 'YOHOO_TITLE_REQUEST') {
            return;
        }

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
