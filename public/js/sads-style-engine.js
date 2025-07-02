// SADS (Semantic Attribute-Driven Styling) Engine v0.1.1

class SADSEngine {
    constructor(themeConfig = {}) {
        this.theme = this._resolveTheme(themeConfig);
        this.dynamicStyleSheet = this._createDynamicStyleSheet();
        this.ruleCounter = 0;
        console.log("SADS Engine Initialized. Theme:", this.theme);
    }

    _resolveTheme(themeConfig) {
        const defaultConfig = {
            colors: {
                'surface': '#FFFFFF', 'surface-dark': '#2a2a2a', // Default surface, e.g. item bg for testimonials
                'surface-accent': '#f9f9f9', 'surface-accent-dark': '#1f1f1f', // Accented surface, e.g. section bg for testimonials
                // Generic names first
                // 'surface-dark': '#1f1f1f', 'surface-accent-dark': '#2a2a2a', // Original generic

                'text-primary': '#333333', 'text-primary-dark': '#e0e0e0',
                'text-accent': '#007bff', 'text-accent-dark': '#0af',
                'transparent': 'transparent',
                // Added for Testimonials and general use
                'text-secondary': '#555555', 'text-secondary-dark': '#bbbbbb',
                'border-accent': '#007bff', 'border-accent-dark': '#0af',

                // Blog specific BGs (can be aliased to more generic names if pattern emerges)
                'blog-section-bg': '#e9ecef', 'blog-section-bg-dark': '#2a2a2a',
                'blog-item-bg': '#ffffff', 'blog-item-bg-dark': '#1f1f1f',

                // Contact Form specific colors
                'contact-section-bg': '#e9ecef', 'contact-section-bg-dark': '#2a2a2a', // Same as blog section
                'contact-form-bg': '#ffffff', 'contact-form-bg-dark': '#1f1f1f',    // Same as blog item
                'input-border-color': '#cccccc', 'input-border-color-dark': '#555555',
                'input-bg-color': '#ffffff', 'input-bg-color-dark': '#333333',
                // 'input-text-color' will use 'text-primary' / 'text-primary-dark'
                'button-primary-bg-color': '#28a745', 'button-primary-bg-color-dark': '#1a73e8',
                'button-primary-text-color': '#ffffff', // Same for light/dark for this button
            },
            spacing: { 'none': '0', 'xs': '0.25rem', 's': '0.5rem', 'm': '1rem', 'l': '1.5rem', 'xl': '2rem', 'xxl': '4rem', 'auto': 'auto', 'input': '0.75rem' }, // Added 'input' for 0.75rem
            fontSize: { 'default': '1rem', 's': '0.9rem', 'm': '1rem', 'l': '1.5rem', 'xl': '2rem', 'xxl': '2.5rem' },
            fontWeight: { 'normal': '400', 'bold': '700' },
            borderRadius: { 'none': '0', 's': '4px', 'm': '8px', 'l': '16px' },
            shadow: { 'none': 'none', 'subtle': '0 2px 5px rgba(0,0,0,0.1)', 'medium': '0 4px 10px rgba(0,0,0,0.15)' },
            maxWidth: { 'content-container': '1100px', 'full': '100%' },
            breakpoints: { 'mobile': '(max-width: 768px)' },
            flexBasis: { 'auto': 'auto', 'full': '100%', 'third-gap-m': 'calc(33.333% - 1rem)' },
            objectFit: { 'cover': 'cover', 'contain': 'contain', 'fill': 'fill', 'scale-down': 'scale-down', 'none': 'none' },
            fontStyle: { 'normal': 'normal', 'italic': 'italic', 'oblique': 'oblique' },
            borderStyle: { 'none': 'none', 'solid': 'solid', 'dashed': 'dashed', 'dotted': 'dotted' }
        };

        // Add more theme colors
        defaultConfig.colors['text-secondary'] = '#555555';
        defaultConfig.colors['text-secondary-dark'] = '#bbbbbb';
        defaultConfig.colors['border-accent'] = defaultConfig.colors['text-accent']; // Use text-accent for border
        defaultConfig.colors['border-accent-dark'] = defaultConfig.colors['text-accent-dark'];


        // Refined deep merge logic
        const mergedTheme = JSON.parse(JSON.stringify(defaultConfig)); // Simple deep clone

        function deepMerge(target, source) {
            for (const key in source) {
                if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                    if (!target[key]) Object.assign(target, { [key]: {} });
                    deepMerge(target[key], source[key]);
                } else {
                    Object.assign(target, { [key]: source[key] });
                }
            }
        }
        deepMerge(mergedTheme, themeConfig);
        return mergedTheme;
    }

    _createDynamicStyleSheet() {
        let styleEl = document.getElementById('sads-dynamic-styles');
        if (!styleEl) {
            styleEl = document.createElement('style');
            styleEl.id = 'sads-dynamic-styles';
            document.head.appendChild(styleEl);
        } else {
            // Clear existing rules if any, for re-application (e.g. on theme change)
            while (styleEl.sheet.cssRules.length > 0) {
                styleEl.sheet.deleteRule(0);
            }
        }
        return styleEl.sheet;
    }

    // Method to be called if theme changes during runtime
    updateTheme(newThemeConfig) {
        this.theme = this._resolveTheme(newThemeConfig);
        // Re-create (clear) stylesheet and re-apply styles to all SADS components
        this.dynamicStyleSheet = this._createDynamicStyleSheet();
        document.querySelectorAll('[data-sads-component]').forEach(rootEl => this.applyStylesTo(rootEl));
    }

    applyStylesTo(rootElement) {
        if (!rootElement || !rootElement.matches('[data-sads-component]')) {
            // console.warn("SADS: applyStylesTo called on invalid root or non-component element.", rootElement);
            return;
        }

        const elementsToStyle = [rootElement, ...rootElement.querySelectorAll('[data-sads-element]')];

        elementsToStyle.forEach(el => {
            const attributes = el.dataset;
            let baseCssText = '';
            const responsiveStyles = {};

            let targetSelector = Array.from(el.classList).find(cls => cls.startsWith('sads-id-'));
            if (!targetSelector) {
                targetSelector = `sads-id-${this.ruleCounter++}`;
                el.classList.add(targetSelector);
            }
            targetSelector = `.${targetSelector}`;

            for (const attrKey in attributes) {
                if (!attrKey.startsWith('sads')) continue;

                const sadsPropertyKey = attrKey.substring('sads'.length);
                const semanticValue = attributes[attrKey];

                if (sadsPropertyKey.toLowerCase() === 'responsiverules') {
                    try {
                        const parsedRules = JSON.parse(semanticValue);
                        parsedRules.forEach(rule => {
                            const breakpointKey = rule.breakpoint;
                            const bpQuery = this.theme.breakpoints[breakpointKey] || breakpointKey;
                            if (!bpQuery) {
                                console.warn(`SADS: Unknown breakpoint key '${breakpointKey}' for ${targetSelector}`);
                                return;
                            }
                            if (!responsiveStyles[bpQuery]) responsiveStyles[bpQuery] = '';

                            for (const [respSadsPropKey, respSemanticVal] of Object.entries(rule.styles)) {
                                const cssProp = this._mapSadsPropertyToCss(respSadsPropKey);
                                const actualVal = this._mapSemanticValueToActual(cssProp, respSemanticVal);
                                if (cssProp && actualVal !== null) {
                                    // Using !important for responsive overrides can be heavy-handed.
                                    // Consider specificity or order for more finesse later.
                                    responsiveStyles[bpQuery] += `${cssProp}: ${actualVal} !important;\n`;
                                }
                            }
                        });
                    } catch (e) {
                        console.error(`SADS: Error parsing responsive rules for ${targetSelector}:`, semanticValue, e);
                    }
                } else if (sadsPropertyKey.toLowerCase() !== 'component' && sadsPropertyKey.toLowerCase() !== 'element') {
                    const cssProperty = this._mapSadsPropertyToCss(sadsPropertyKey);
                    const actualValue = this._mapSemanticValueToActual(cssProperty, semanticValue);

                    if (cssProperty && actualValue !== null) {
                        baseCssText += `${cssProperty}: ${actualValue};\n`;
                    }
                }
            }

            if (baseCssText) this._addCssRule(targetSelector, baseCssText);
            for (const [bpQuery, cssRules] of Object.entries(responsiveStyles)) {
                if (cssRules) this._addCssRule(targetSelector, cssRules, bpQuery);
            }
        });
    }

    _addCssRule(selector, rules, mediaQuery = null) {
        const ruleContent = `${selector} { ${rules} }`;
        const finalRule = mediaQuery ? `@media ${mediaQuery} { ${ruleContent} }` : ruleContent;
        try {
            this.dynamicStyleSheet.insertRule(finalRule, this.dynamicStyleSheet.cssRules.length);
        } catch (e) {
            // Suppress common "Invalid RULENOTSUPPORTED_ERR" during HMR or rapid changes if sheet is cleared.
            if (this.dynamicStyleSheet.ownerNode) { // Check if sheet is still valid
                 console.error(`SADS: Failed to insert CSS rule: "${finalRule}"`, e);
            }
        }
    }

    _mapSadsPropertyToCss(sadsPropertyKey) {
        const kebabCase = sadsPropertyKey.replace(/([A-Z])/g, g => `-${g[0].toLowerCase()}`);

        // Prioritize direct mappings for clarity and correctness
        const map = {
            'bg-color': 'background-color',
            'text-color': 'color',
            'font-size': 'font-size',
            'font-weight': 'font-weight',
            'text-align': 'text-align',
            'border-radius': 'border-radius',
            'max-width': 'max-width',
            'flex-direction': 'flex-direction',
            'flex-wrap': 'flex-wrap',
            'flex-justify': 'justify-content',
            'flex-align-items': 'align-items',
            'flex-basis': 'flex-basis',
            'shadow': 'box-shadow',
            // simple layout properties
            'padding': 'padding', 'padding-top': 'padding-top', 'padding-bottom': 'padding-bottom',
            'padding-left': 'padding-left', 'padding-right': 'padding-right',
            'margin': 'margin', 'margin-top': 'margin-top', 'margin-bottom': 'margin-bottom',
            'margin-left': 'margin-left', 'margin-right': 'margin-right',
            'gap': 'gap',
            'width': 'width',
            'height': 'height',
            'object-fit': 'object-fit',
            'font-style': 'font-style',
            'border-width': 'border-width',
            'border-style': 'border-style',
            'border-color': 'border-color',
            'display': 'display',
            'text-decoration': 'text-decoration',
            'resize': 'resize',
            'cursor': 'cursor',
            'transition': 'transition',
            'box-sizing': 'box-sizing',
            // 'border': 'border', // For shorthand, if we decide to support it directly
            'layout-type': null, // Not a direct CSS prop, influences other interpretations or JS behavior potentially
        };
        if (map.hasOwnProperty(kebabCase)) return map[kebabCase];
        // console.warn(`SADS: Unmapped SADS property key '${sadsPropertyKey}' (kebab: ${kebabCase})`);
        return kebabCase; // Fallback to direct kebab-case if not in map
    }

    _mapSemanticValueToActual(cssProperty, semanticValue) {
        if (semanticValue === null || semanticValue === undefined) return null;
        const valueStr = String(semanticValue);

        // Handle dark mode colors if a global dark mode is active
        // This is a basic example; a more robust theme system would be needed.
        const isDarkMode = document.body.classList.contains('dark-mode'); // Example global dark mode check

        // Handle 'custom:' prefix for direct value passthrough
        if (valueStr.startsWith('custom:')) {
            return valueStr.substring('custom:'.length);
        }

        switch (cssProperty) {
            case 'padding': case 'padding-top': case 'padding-bottom': case 'padding-left': case 'padding-right':
            case 'margin': case 'margin-top': case 'margin-bottom': case 'margin-left': case 'margin-right':
            case 'gap': case 'border-width': // border-width can use spacing scale or custom
                return this.theme.spacing[valueStr] || valueStr;
            case 'background-color':
                const bgColorKey = isDarkMode ? `${valueStr}-dark` : valueStr;
                return this.theme.colors[bgColorKey] || this.theme.colors[valueStr] || valueStr;
            case 'color':
            case 'border-color': // border-color can use theme colors
                const colorKey = isDarkMode ? `${valueStr}-dark` : valueStr;
                return this.theme.colors[colorKey] || this.theme.colors[valueStr] || valueStr;
            case 'font-size':
                return this.theme.fontSize[valueStr] || valueStr;
            case 'font-weight':
                return this.theme.fontWeight[valueStr] || valueStr;
            case 'font-style':
                return this.theme.fontStyle[valueStr] || valueStr;
            case 'border-radius':
                return this.theme.borderRadius[valueStr] || valueStr;
            case 'border-style':
                return this.theme.borderStyle[valueStr] || valueStr;
            case 'box-shadow':
                return this.theme.shadow[valueStr] || valueStr;
            case 'max-width':
                return this.theme.maxWidth[valueStr] || valueStr;
            case 'width': case 'height': // Can use spacing scale or direct values
                return this.theme.spacing[valueStr] || valueStr;
            case 'flex-basis':
                 return this.theme.flexBasis[valueStr] || valueStr;
            case 'object-fit':
                 return this.theme.objectFit[valueStr] || valueStr;
            default: return valueStr;
        }
    }
}
