/**
 * Set of Marks (SoM) Injection Script
 * 
 * This script scans the DOM for interactive elements, filters out invisible ones,
 * and overlays a unique numeric ID on top of them.
 * 
 * Returns: A map of { ID: { tag, text, selector, coordinates } }
 */

(function () {
    // 1. Reset existing marks if any
    document.querySelectorAll('.som-marker').forEach(el => el.remove());
    window.somMap = {};

    // 2. Define interactive selectors
    const selectors = [
        'button',
        'a',
        'input',
        'textarea',
        'select',
        '[onclick]',
        '[role="button"]',
        '[role="link"]',
        '[role="checkbox"]',
        '[role="menuitem"]'
    ].join(',');

    const elements = document.querySelectorAll(selectors);
    let idCounter = 1;
    const items = [];

    // 3. Helper: Check visibility
    function isVisible(el) {
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);
        return (
            rect.width > 0 &&
            rect.height > 0 &&
            style.visibility !== 'hidden' &&
            style.display !== 'none' &&
            style.opacity !== '0'
        );
    }

    // 4. Helper: Generate unique selector (simple version)
    function getSelector(el) {
        if (el.id) return `#${el.id}`;
        if (el.name) return `[name="${el.name}"]`;
        // Fallback to a rough path - in production we'd want a more robust path generator
        let path = el.tagName.toLowerCase();
        if (el.className) path += `.${el.className.split(' ').join('.')}`;
        return path;
    }

    // 5. Iterate and Mark
    elements.forEach(el => {
        if (!isVisible(el)) return;

        const rect = el.getBoundingClientRect();

        // Create Marker
        const marker = document.createElement('div');
        marker.className = 'som-marker';
        marker.textContent = idCounter;
        marker.style.position = 'absolute';
        marker.style.left = `${window.scrollX + rect.left}px`;
        marker.style.top = `${window.scrollY + rect.top}px`;
        marker.style.backgroundColor = '#ff0000'; // High contrast red
        marker.style.color = 'white';
        marker.style.fontWeight = 'bold';
        marker.style.fontSize = '12px';
        marker.style.padding = '2px 4px';
        marker.style.zIndex = '999999';
        marker.style.border = '1px solid white';
        marker.style.borderRadius = '2px';
        marker.style.pointerEvents = 'none'; // Don't block clicks

        document.body.appendChild(marker);

        // Store Metadata
        items.push({
            id: idCounter,
            tag: el.tagName.toLowerCase(),
            text: el.innerText || el.value || el.placeholder || '',
            selector: getSelector(el),
            rect: {
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height
            }
        });

        idCounter++;
    });

    return items;
})();
