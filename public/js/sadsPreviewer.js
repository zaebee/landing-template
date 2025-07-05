document.addEventListener('DOMContentLoaded', () => {
    const componentSelector = document.getElementById('component-selector');
    const componentRenderTarget = document.getElementById('component-render-target');
    const attributesDisplay = document.getElementById('attributes-display');

    // Check if SADS specific globals are available
    if (typeof SADSEngine === 'undefined' || typeof sadsManager === 'undefined' || typeof SADS_DEFAULT_THEME === 'undefined') {
        console.error('SADS Engine, Manager, or Default Theme not loaded. Previewer may not function correctly.');
        componentRenderTarget.innerHTML = '<p style="color: red;">Error: SADS scripts not loaded. Previewer functionality is limited.</p>';
        // return; // Decide if we should halt completely
    } else {
        // Initialize SADS engine for the page.
        // sadsManager.initSadsEngine() should be called to process any static SADS components
        // on the previewer page itself (if any) and prepare the engine.
        // If components are loaded dynamically, reapplySadsStyles will be key.
        sadsManager.initSadsEngine().then(() => {
            console.log("SADS Engine initialized by previewer.");
        }).catch(error => {
            console.error("Error initializing SADS Engine in previewer:", error);
        });
    }

    // 1. Fetch Component List
    fetch('/api/sads/components')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(components => {
            componentSelector.innerHTML = '<option value="">-- Select a Component --</option>'; // Clear loading message
            components.forEach(componentName => {
                const option = document.createElement('option');
                option.value = componentName;
                option.textContent = componentName.charAt(0).toUpperCase() + componentName.slice(1); // Capitalize
                componentSelector.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching component list:', error);
            componentSelector.innerHTML = '<option value="">-- Error Loading --</option>';
            attributesDisplay.textContent = `Error loading components: ${error.message}`;
        });

    // 2. Load Component when selected
    componentSelector.addEventListener('change', (event) => {
        const componentName = event.target.value;
        if (!componentName) {
            componentRenderTarget.innerHTML = ''; // Clear preview area
            attributesDisplay.textContent = 'No element selected.';
            return;
        }

        componentRenderTarget.innerHTML = `<p>Loading ${componentName}...</p>`;
        attributesDisplay.textContent = 'Loading component...';

        fetch(`/api/sads/component/${componentName}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status} for ${componentName}`);
                }
                return response.text(); // Rendered HTML
            })
            .then(htmlContent => {
                componentRenderTarget.innerHTML = htmlContent;

                // 3. Re-apply SADS styles to the newly added content
                // sadsManager.reapplySadsStyles() is the critical function here.
                if (sadsManager && typeof sadsManager.reapplySadsStyles === 'function') {
                    sadsManager.reapplySadsStyles().then(() => {
                        console.log(`SADS styles reapplied for ${componentName}`);
                    }).catch(error => {
                        console.error(`Error reapplying SADS styles for ${componentName}:`, error);
                    });
                } else {
                    console.warn('sadsManager.reapplySadsStyles() is not available. SADS styles might not be applied to dynamic content.');
                }
                attributesDisplay.textContent = 'Click on an element in the preview to see its SADS attributes.';
            })
            .catch(error => {
                console.error(`Error fetching component ${componentName}:`, error);
                componentRenderTarget.innerHTML = `<p style="color: red;">Error loading component ${componentName}: ${error.message}</p>`;
                attributesDisplay.textContent = `Error loading component: ${error.message}`;
            });
    });

    // 4. Display SADS Attributes on click
    componentRenderTarget.addEventListener('click', (event) => {
        const targetElement = event.target.closest('[data-sads-component], [data-sads-element], [data-sads-padding]'); // Try to get a relevant SADS element

        if (!targetElement || !componentRenderTarget.contains(targetElement)) {
            attributesDisplay.textContent = 'Clicked outside a recognized SADS element or component not fully loaded.';
            return;
        }

        const sadsAttributes = {};
        let hasSadsAttributes = false;
        for (const attr of targetElement.attributes) {
            if (attr.name.startsWith('data-sads-')) {
                sadsAttributes[attr.name] = attr.value;
                hasSadsAttributes = true;
            }
        }

        if (hasSadsAttributes) {
            let displayText = `Element: <${targetElement.tagName.toLowerCase()}>\n\n`;
            displayText += JSON.stringify(sadsAttributes, null, 2);
            attributesDisplay.textContent = displayText;
        } else {
            attributesDisplay.textContent = `Element: <${targetElement.tagName.toLowerCase()}>\n\nNo data-sads-* attributes found on this specific element. Try its parent or children.`;
        }
    });

});
