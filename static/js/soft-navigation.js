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
    let currentViewUrl = window.location.href;

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

    function applyPage(nextDocument, nextUrl, preservePosition) {
        const currentWrapper = document.querySelector('.dashboard-wrapper');
        const nextWrapper = nextDocument.querySelector('.dashboard-wrapper');
        const currentSidebar = currentWrapper && currentWrapper.querySelector('.sidebar');
        const nextSidebar = nextWrapper && nextWrapper.querySelector('.sidebar');
        const currentMain = currentWrapper && currentWrapper.querySelector('.main-content');
        const nextMain = nextWrapper && nextWrapper.querySelector('.main-content');
        if (!currentSidebar || !nextSidebar || !currentMain || !nextMain) return false;

        currentViewUrl = nextUrl;
        if (currentMain.innerHTML === nextMain.innerHTML && currentSidebar.innerHTML === nextSidebar.innerHTML) {
            return true;
        }

        const scrollPosition = window.scrollY;
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
        document.body.style.overflow = '';
        runPageScripts(nextScripts);
        window.scrollTo(0, preservePosition ? scrollPosition : 0);
        return true;
    }

    async function fetchPage(url, options = {}) {
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
            if (!response.ok) {
                showRequestError('The update could not be completed. Your current page has been kept.');
            } else if (!applyPage(nextDocument, response.url, options.preservePosition)) {
                if (options.form || options.silent) {
                    showRequestError('The update could not be completed. Your current page has been kept.');
                } else {
                    window.location.assign(response.url);
                }
            }
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Background page update failed.', error);
                if (!options.silent) {
                    showRequestError('Could not update this page. Check your connection and try again.');
                }
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

        const url = new URL(link.getAttribute('href'), currentViewUrl);
        const currentUrl = new URL(currentViewUrl);
        if (url.origin !== window.location.origin) return;
        if (url.pathname === currentUrl.pathname && url.hash) {
            event.preventDefault();
            let targetId;
            try {
                targetId = decodeURIComponent(url.hash.slice(1));
            } catch (_) {
                targetId = url.hash.slice(1);
            }
            const target = targetId ? document.getElementById(targetId) : null;
            if (target) target.scrollIntoView({ behavior: 'smooth' });
            else if (!targetId) window.scrollTo({ top: 0, behavior: 'smooth' });
            return;
        }
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
        const action = new URL(form.getAttribute('action') || currentViewUrl, currentViewUrl);
        const options = { method, form };
        if (method === 'GET') {
            new FormData(form).forEach((value, key) => {
                if (typeof value === 'string') action.searchParams.set(key, value);
            });
            options.method = 'GET';
        } else {
            options.body = new FormData(form);
        }
        fetchPage(action.href, options);
    });

    function canRefreshPage() {
        if (navigationRequest || activeForm) return false;
        const activeElement = document.activeElement;
        if (activeElement && activeElement.closest('.main-content') &&
            activeElement.matches('input, textarea, select, [contenteditable="true"]')) return false;
        if (document.querySelector('.modal.show')) return false;
        const hasUnsavedInput = [...document.querySelectorAll('.main-content input, .main-content textarea, .main-content select')]
            .some((control) => {
                if (control.type === 'checkbox' || control.type === 'radio') {
                    return control.checked !== control.defaultChecked;
                }
                if (control.tagName === 'SELECT') {
                    return [...control.options].some((option) => option.selected !== option.defaultSelected);
                }
                return control.type !== 'hidden' && control.type !== 'submit' &&
                    control.type !== 'button' && control.type !== 'reset' &&
                    control.value !== control.defaultValue;
            });
        if (hasUnsavedInput) return false;
        return ![...document.querySelectorAll('.main-content video, .main-content audio')]
            .some((player) => !player.paused && !player.ended || player.currentTime > 0 && !player.ended);
    }

    function refreshCurrentPage() {
        if (document.visibilityState !== 'visible' || !canRefreshPage()) return;
        fetchPage(currentViewUrl, { preservePosition: true, silent: true });
    }

    nativeSetInterval(refreshCurrentPage, 30000);
    nativeDocumentAdd('visibilitychange', () => {
        if (document.visibilityState === 'visible') refreshCurrentPage();
    });
    nativeSetTimeout(() => { runningPageScripts = false; }, 0);
})();
