(function () {
    const activePageIntervals = new Set();
    const activePageTimeouts = new Set();
    const activePageListeners = [];
    const nativeSetInterval = window.setInterval.bind(window);
    const nativeClearInterval = window.clearInterval.bind(window);
    const nativeSetTimeout = window.setTimeout.bind(window);
    const nativeClearTimeout = window.clearTimeout.bind(window);
    const nativeDocumentAdd = document.addEventListener.bind(document);
    const nativeWindowAdd = window.addEventListener.bind(window);
    let runningPageScripts = true;
    let navigationRequest = null;
    let activeForm = null;

    window.setInterval = function (callback, delay, ...args) {
        const timer = nativeSetInterval(callback, delay, ...args);
        if (runningPageScripts) activePageIntervals.add(timer);
        return timer;
    };
    window.clearInterval = function (timer) {
        activePageIntervals.delete(timer);
        nativeClearInterval(timer);
    };
    window.setTimeout = function (callback, delay, ...args) {
        if (!runningPageScripts) return nativeSetTimeout(callback, delay, ...args);
        let timer;
        timer = nativeSetTimeout(() => {
            activePageTimeouts.delete(timer);
            callback(...args);
        }, delay);
        activePageTimeouts.add(timer);
        return timer;
    };
    window.clearTimeout = function (timer) {
        activePageTimeouts.delete(timer);
        nativeClearTimeout(timer);
    };

    document.addEventListener = function (type, listener, options) {
        if (runningPageScripts) activePageListeners.push([document, type, listener, options]);
        nativeDocumentAdd(type, listener, options);
    };
    window.addEventListener = function (type, listener, options) {
        if (runningPageScripts) activePageListeners.push([window, type, listener, options]);
        nativeWindowAdd(type, listener, options);
    };

    function findMarker(root, markerText) {
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_COMMENT);
        let node;
        while ((node = walker.nextNode())) {
            if (node.data.trim() === markerText) return node;
        }
        return null;
    }

    function nodesBetween(start, end) {
        const nodes = [];
        for (let node = start && start.nextSibling; node && node !== end; node = node.nextSibling) {
            nodes.push(node);
        }
        return nodes;
    }

    function replaceMarkedNodes(currentDocument, nextDocument, startText, endText, insertNodes = true) {
        const currentStart = findMarker(currentDocument, startText);
        const currentEnd = findMarker(currentDocument, endText);
        const nextStart = findMarker(nextDocument, startText);
        const nextEnd = findMarker(nextDocument, endText);
        if (!currentStart || !currentEnd || !nextStart || !nextEnd) return [];

        nodesBetween(currentStart, currentEnd).forEach((node) => node.remove());
        const nextNodes = nodesBetween(nextStart, nextEnd);
        if (insertNodes) {
            nextNodes.forEach((node) => currentEnd.parentNode.insertBefore(node.cloneNode(true), currentEnd));
        }
        return nextNodes;
    }

    function stopCurrentPageWork() {
        activePageIntervals.forEach(nativeClearInterval);
        activePageIntervals.clear();
        activePageTimeouts.forEach(nativeClearTimeout);
        activePageTimeouts.clear();
        activePageListeners.forEach(([target, type, listener, options]) => {
            if (target === document) {
                document.removeEventListener(type, listener, options);
            } else {
                window.removeEventListener(type, listener, options);
            }
        });
        activePageListeners.length = 0;
        if (window.Chart && Chart.instances) {
            Object.values(Chart.instances).forEach((chart) => chart.destroy());
        }
    }

    function runPageScripts(scriptNodes) {
        runningPageScripts = true;
        try {
            scriptNodes
                .filter((node) => node.nodeName === 'SCRIPT' && !node.src && node.textContent.trim())
                .forEach((script) => {
                    const functionNames = [...script.textContent.matchAll(/\bfunction\s+([A-Za-z_$][\w$]*)\s*\(/g)]
                        .map((match) => match[1]);
                    const exportFunctions = [...new Set(functionNames)]
                        .map((name) => `try { window[${JSON.stringify(name)}] = eval(${JSON.stringify(name)}); } catch (_) {}`)
                        .join('\n');
                    const execute = new Function(
                        'window',
                        'document',
                        `${script.textContent}\n${exportFunctions}`,
                    );
                    execute.call(window, window, document);
                });
        } finally {
            runningPageScripts = false;
        }
        document.dispatchEvent(new Event('DOMContentLoaded', { bubbles: true }));
        document.dispatchEvent(new CustomEvent('zenalyze:page:loaded'));
    }

    function syncMessages(nextDocument) {
        const currentMessages = document.getElementById('pageMessages');
        const nextMessages = nextDocument.getElementById('pageMessages');
        if (currentMessages && nextMessages) currentMessages.innerHTML = nextMessages.innerHTML;
    }

    function showRequestError(message) {
        let notice = document.getElementById('softNavigationError');
        if (!notice) {
            notice = document.createElement('div');
            notice.id = 'softNavigationError';
            notice.className = 'alert alert-warning shadow-sm position-fixed top-0 start-50 translate-middle-x mt-3';
            notice.setAttribute('role', 'alert');
            notice.style.zIndex = '2000';
            document.body.appendChild(notice);
        }
        notice.textContent = message;
        nativeSetTimeout(() => notice.remove(), 6000);
    }

    function applyPage(nextDocument, nextUrl, historyMode) {
        const currentWrapper = document.querySelector('.dashboard-wrapper');
        const nextWrapper = nextDocument.querySelector('.dashboard-wrapper');
        const currentSidebar = currentWrapper && currentWrapper.querySelector('.sidebar');
        const nextSidebar = nextWrapper && nextWrapper.querySelector('.sidebar');
        const currentMain = currentWrapper && currentWrapper.querySelector('.main-content');
        const nextMain = nextWrapper && nextWrapper.querySelector('.main-content');
        if (!currentSidebar || !nextSidebar || !currentMain || !nextMain) return false;

        stopCurrentPageWork();
        replaceMarkedNodes(
            document,
            nextDocument,
            'dashboard-page-styles:start',
            'dashboard-page-styles:end',
        );
        const nextScripts = replaceMarkedNodes(
            document,
            nextDocument,
            'dashboard-page-scripts:start',
            'dashboard-page-scripts:end',
            false,
        );

        currentSidebar.replaceWith(nextSidebar.cloneNode(true));
        currentMain.replaceWith(nextMain.cloneNode(true));
        document.title = nextDocument.title;
        document.documentElement.dataset.theme = nextDocument.documentElement.dataset.theme || 'light';
        syncMessages(nextDocument);

        if (historyMode === 'push') {
            window.history.pushState({}, '', nextUrl);
        } else if (historyMode === 'replace') {
            window.history.replaceState({}, '', nextUrl);
        }

        document.body.style.overflow = '';
        runPageScripts(nextScripts);
        window.scrollTo(0, 0);
        return true;
    }

    async function fetchPage(url, historyMode = 'push', options = {}) {
        if (navigationRequest) navigationRequest.abort();
        navigationRequest = new AbortController();
        const request = navigationRequest;

        try {
            const response = await fetch(url, {
                ...options,
                credentials: 'same-origin',
                cache: 'no-store',
                signal: request.signal,
                headers: {
                    Accept: 'text/html',
                    'X-Requested-With': 'XMLHttpRequest',
                    ...(options.headers || {}),
                },
            });
            const html = await response.text();
            const nextDocument = new DOMParser().parseFromString(html, 'text/html');
            if (!response.ok || !applyPage(nextDocument, response.url, historyMode)) {
                if (options.form) {
                    showRequestError('The update could not be completed. Your current page has been kept.');
                } else {
                    window.location.assign(response.url);
                }
            }
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Background page update failed.', error);
                showRequestError('Could not update this page. Check your connection and try again.');
            }
        } finally {
            if (navigationRequest === request) navigationRequest = null;
            if (options.form && activeForm === options.form) {
                activeForm.removeAttribute('aria-busy');
                activeForm = null;
            }
        }
    }

    nativeDocumentAdd('click', (event) => {
        if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        const clickTarget = event.target instanceof Element ? event.target : event.target.parentElement;
        const link = clickTarget && clickTarget.closest('a[href]');
        if (!link || link.target || link.hasAttribute('download') || link.rel === 'external' || link.dataset.noSoftNavigation !== undefined) return;

        const url = new URL(link.href, window.location.href);
        if (url.origin !== window.location.origin || url.pathname === window.location.pathname && url.hash) return;
        if (!/^https?:$/.test(url.protocol)) return;

        event.preventDefault();
        fetchPage(url.href);
    });

    nativeDocumentAdd('submit', (event) => {
        const form = event.target;
        if (!(form instanceof HTMLFormElement) || !form.hasAttribute('data-background-update')) return;
        if (event.defaultPrevented || activeForm) return;

        event.preventDefault();
        activeForm = form;
        form.setAttribute('aria-busy', 'true');
        const method = (form.method || 'GET').toUpperCase();
        const action = new URL(form.action || window.location.href, window.location.href);
        const options = { method, form };
        if (method === 'GET') {
            new FormData(form).forEach((value, key) => {
                if (typeof value === 'string') action.searchParams.set(key, value);
            });
            options.method = 'GET';
        } else {
            options.body = new FormData(form);
        }
        fetchPage(action.href, 'replace', options);
    });

    nativeWindowAdd('popstate', () => fetchPage(window.location.href, 'none'));
    nativeSetTimeout(() => { runningPageScripts = false; }, 0);
})();
