// SADS (Semantic Attribute-Driven Styling) Engine v0.1.2

class SADSEngine {
    constructor(themeConfig = {}) {
        this.theme = this._initializeTheme(themeConfig);
        this.dynamicStyleSheet = this._createDynamicStyleSheet();
        this.ruleCounter = 0;
        console.log("SADS Engine Initialized. Theme:", this.theme);
    }

    _initializeTheme(customThemeConfig) {
        const defaultConfig = {
            colors: {
                'surface': '#FFFFFF', 'surface-dark': '#2a2a2a',
                'surface-accent': '#f9f9f9', 'surface-accent-dark': '#1f1f1f',
                'text-primary': '#333333', 'text-primary-dark': '#e0e0e0',
                'text-accent': '#007bff', 'text-accent-dark': '#0af',
                'transparent': 'transparent',
                'text-secondary': '#555555', 'text-secondary-dark': '#bbbbbb',
                'border-accent': '#007bff', 'border-accent-dark': '#0af', // Aliased to text-accent
                'blog-section-bg': '#e9ecef', 'blog-section-bg-dark': '#2a2a2a',
                'blog-item-bg': '#ffffff', 'blog-item-bg-dark': '#1f1f1f',
                'contact-section-bg': '#e9ecef', 'contact-section-bg-dark': '#2a2a2a',
                'contact-form-bg': '#ffffff', 'contact-form-bg-dark': '#1f1f1f',
                'input-border-color': '#cccccc', 'input-border-color-dark': '#555555',
                'input-bg-color': '#ffffff', 'input-bg-color-dark': '#333333',
                'button-primary-bg-color': '#28a745', 'button-primary-bg-color-dark': '#1a73e8',
                'button-primary-text-color': '#ffffff',
            },
            spacing: { 'none': '0', 'xs': '0.25rem', 's': '0.5rem', 'm': '1rem', 'l': '1.5rem', 'xl': '2rem', 'xxl': '4rem', 'auto': 'auto', 'input': '0.75rem' },
            fontSize: { 'default': '1rem', 's': '0.9rem', 'm': '1rem', 'l': '1.5rem', 'xl': '2rem', 'xxl': '2.5rem' },
            fontWeight: { 'normal': '400', 'bold': '700' },
            borderRadius: { 'none': '0', 's': '4px', 'm': '8px', 'l': '16px' },
            shadow: { 'none': 'none', 'subtle': '0 2px 5px rgba(0,0,0,0.1)', 'medium': '0 4px 10px rgba(0,0,0,0.15)' },
            maxWidth: { 'content-container': '1100px', 'full': '100%' },
            breakpoints: { 'mobile': '(max-width: 768px)' },
            flexBasis: { 'auto': 'auto', 'full': '100%', 'third-gap-m': 'calc(33.333% - 1rem)' }, // Example: calc(33.333% - var(--gap-m))
            objectFit: { 'cover': 'cover', 'contain': 'contain', 'fill': 'fill', 'scale-down': 'scale-down', 'none': 'none' },
            fontStyle: { 'normal': 'normal', 'italic': 'italic', 'oblique': 'oblique' },
            borderStyle: { 'none': 'none', 'solid': 'solid', 'dashed': 'dashed', 'dotted': 'dotted' }
        };

        // Ensure aliases are correctly set up if they depend on other default values
        defaultConfig.colors['border-accent'] = defaultConfig.colors['text-accent'];
        defaultConfig.colors['border-accent-dark'] = defaultConfig.colors['text-accent-dark'];

        return this._deepMergeThemes(defaultConfig, customThemeConfig);
    }

    _deepMergeThemes(base, custom) {
        const merged = { ...base }; // Shallow clone base
        for (const key in custom) {
            if (custom.hasOwnProperty(key)) {
                if (typeof custom[key] === 'object' && custom[key] !== null && !Array.isArray(custom[key]) &&
                    typeof base[key] === 'object' && base[key] !== null && !Array.isArray(base[key])) {
                    merged[key] = this._deepMergeThemes(base[key], custom[key]);
                } else {
                    merged[key] = custom[key]; // Custom overrides base
                }
            }
        }
        return merged;
    }


    _createDynamicStyleSheet() {
        let styleEl = document.getElementById('sads-dynamic-styles');
        if (!styleEl) {
            styleEl = document.createElement('style');
            styleEl.id = 'sads-dynamic-styles';
            document.head.appendChild(styleEl);
        } else {
            while (styleEl.sheet && styleEl.sheet.cssRules.length > 0) {
                styleEl.sheet.deleteRule(0);
            }
        }
        return styleEl.sheet;
    }

    updateTheme(newThemeConfig) {
        this.theme = this._initializeTheme(newThemeConfig); // Re-initialize with new config
        this.dynamicStyleSheet = this._createDynamicStyleSheet(); // Clears old rules
        document.querySelectorAll('[data-sads-component]').forEach(rootEl => this.applyStylesTo(rootEl));
    }

    _getTargetSelector(el) {
        let targetSelector = Array.from(el.classList).find(cls => cls.startsWith('sads-id-'));
        if (!targetSelector) {
            targetSelector = `sads-id-${this.ruleCounter++}`;
            el.classList.add(targetSelector);
        }
        return `.${targetSelector}`;
    }

    _parseResponsiveRules(rulesString, targetSelector) {
        const responsiveStyles = {};
        if (!rulesString) return responsiveStyles;

        try {
            const parsedRules = JSON.parse(rulesString);
            parsedRules.forEach(rule => {
                const breakpointKey = rule.breakpoint;
                const bpQuery = this.theme.breakpoints[breakpointKey];
                if (!bpQuery) {
                    console.warn(`SADS: Unknown breakpoint key '${breakpointKey}' for ${targetSelector}. Raw query used: ${breakpointKey}`);
                    // Use breakpointKey as raw query if not found in theme, as per original logic
                     responsiveStyles[breakpointKey] = responsiveStyles[breakpointKey] || '';
                } else {
                     responsiveStyles[bpQuery] = responsiveStyles[bpQuery] || '';
                }
                const targetQuery = bpQuery || breakpointKey;


                for (const [respSadsPropKey, respSemanticVal] of Object.entries(rule.styles)) {
                    const cssProp = this._mapSadsPropertyToCss(respSadsPropKey);
                    const actualVal = this._mapSemanticValueToActual(cssProp, respSemanticVal);
                    if (cssProp && actualVal !== null) {
                        responsiveStyles[targetQuery] += `${cssProp}: ${actualVal} !important;\n`;
                    } else if (!cssProp) {
                        console.warn(`SADS: Unmapped SADS property '${respSadsPropKey}' in responsive rule for ${targetSelector}`);
                    }
                }
            });
        } catch (e) {
            console.error(`SADS: Error parsing responsive rules for ${targetSelector}: "${rulesString}"`, e);
        }
        return responsiveStyles;
    }

    _generateBaseCss(attributes, targetSelector) {
        let baseCssText = '';
        for (const attrKey in attributes) {
            if (!attrKey.startsWith('sads') || attrKey.toLowerCase() === 'sadsresponsiverules' ||
                attrKey.toLowerCase() === 'sadscomponent' || attrKey.toLowerCase() === 'sadselement') {
                continue;
            }

            const sadsPropertyKey = attrKey.substring('sads'.length);
            const semanticValue = attributes[attrKey];
            const cssProperty = this._mapSadsPropertyToCss(sadsPropertyKey);
            const actualValue = this._mapSemanticValueToActual(cssProperty, semanticValue);

            if (cssProperty && actualValue !== null) {
                baseCssText += `${cssProperty}: ${actualValue};\n`;
            } else if (!cssProperty) {
                console.warn(`SADS: Unmapped SADS property '${sadsPropertyKey}' for ${targetSelector}`);
            }
        }
        return baseCssText;
    }

    applyStylesTo(rootElement) {
        if (!rootElement || !rootElement.matches('[data-sads-component]')) {
            // console.warn("SADS: applyStylesTo called on invalid root or non-component element.", rootElement);
            return;
        }

        const elementsToStyle = [rootElement, ...rootElement.querySelectorAll('[data-sads-element]')];

        elementsToStyle.forEach(el => {
            const targetSelector = this._getTargetSelector(el);
            const attributes = el.dataset;

            const baseCssText = this._generateBaseCss(attributes, targetSelector);
            if (baseCssText) {
                this._addCssRule(targetSelector, baseCssText);
            }

            const responsiveStyles = this._parseResponsiveRules(attributes.sadsResponsiveRules, targetSelector);
            for (const [bpQuery, cssRules] of Object.entries(responsiveStyles)) {
                if (cssRules) this._addCssRule(targetSelector, cssRules, bpQuery);
            }
        });
    }

    _addCssRule(selector, rules, mediaQuery = null) {
        if (!rules.trim()) return; // Do not add empty rules

        const ruleContent = `${selector} { ${rules} }`;
        const finalRule = mediaQuery ? `@media ${mediaQuery} { ${ruleContent} }` : ruleContent;
        try {
            if (this.dynamicStyleSheet) {
                this.dynamicStyleSheet.insertRule(finalRule, this.dynamicStyleSheet.cssRules.length);
            } else {
                console.error(`SADS: Dynamic stylesheet not available. Cannot insert rule: "${finalRule}"`);
            }
        } catch (e) {
            // Check if sheet is still valid before logging error
            if (this.dynamicStyleSheet && this.dynamicStyleSheet.ownerNode) {
                 console.error(`SADS: Failed to insert CSS rule: "${finalRule}"`, e);
            } else if (!this.dynamicStyleSheet) {
                // This case might occur if the stylesheet was removed or became invalid
                // console.warn(`SADS: Attempted to insert rule, but stylesheet is invalid or missing. Rule: "${finalRule}"`);
            }
        }
    }

    _mapSadsPropertyToCss(sadsPropertyKey) {
        if (!sadsPropertyKey) return null;
        let key = sadsPropertyKey.charAt(0).toLowerCase() + sadsPropertyKey.slice(1);
        let kebabKey = key.replace(/([A-Z])/g, g => `-${g[0].toLowerCase()}`);

        const propertyMap = {
            'bg-color': 'background-color', 'text-color': 'color',
            'font-size': 'font-size', 'font-weight': 'font-weight', 'font-style': 'font-style',
            'text-align': 'text-align', 'text-decoration': 'text-decoration',
            'border-radius': 'border-radius', 'border-width': 'border-width',
            'border-style': 'border-style', 'border-color': 'border-color',
            'max-width': 'max-width', 'width': 'width', 'height': 'height',
            'display': 'display',
            'flex-direction': 'flex-direction', 'flex-wrap': 'flex-wrap',
            'flex-justify': 'justify-content', 'flex-align-items': 'align-items',
            'flex-basis': 'flex-basis', 'gap': 'gap',
            'shadow': 'box-shadow', 'object-fit': 'object-fit',
            'padding': 'padding', 'padding-top': 'padding-top', 'padding-bottom': 'padding-bottom',
            'padding-left': 'padding-left', 'padding-right': 'padding-right',
            'margin': 'margin', 'margin-top': 'margin-top', 'margin-bottom': 'margin-bottom',
            'margin-left': 'margin-left', 'margin-right': 'margin-right',
            'resize': 'resize', 'cursor': 'cursor', 'transition': 'transition', 'box-sizing': 'box-sizing',
            'layout-type': null, // Not a direct CSS prop
        };
        // Explicitly return null for 'layout-type' as it's not a style.
        if (kebabKey === 'layout-type') return null;

        if (propertyMap.hasOwnProperty(kebabKey)) return propertyMap[kebabKey];

        // console.warn(`SADS: Unmapped SADS property key '${sadsPropertyKey}' (kebab: ${kebabKey}). Falling back to kebabKey.`);
        return kebabKey; // Fallback: assumes kebabKey is a valid CSS property
    }

    _mapSemanticValueToActual(cssProperty, semanticValue) {
        if (semanticValue === null || semanticValue === undefined) return null;
        const valueStr = String(semanticValue);

        if (valueStr.startsWith('custom:')) {
            return valueStr.substring('custom:'.length);
        }

        const isDarkMode = document.body.classList.contains('dark-mode');

        const themeCategoryMap = {
            'padding': 'spacing', 'padding-top': 'spacing', 'padding-bottom': 'spacing',
            'padding-left': 'spacing', 'padding-right': 'spacing',
            'margin': 'spacing', 'margin-top': 'spacing', 'margin-bottom': 'spacing',
            'margin-left': 'spacing', 'margin-right': 'spacing',
            'gap': 'spacing', 'border-width': 'spacing', // border-width can use spacing scale or custom
            'width': 'spacing', // width can use spacing scale or direct values
            'height': 'spacing', // height can use spacing scale or direct values

            'background-color': 'colors', 'color': 'colors', 'border-color': 'colors',

            'font-size': 'fontSize',
            'font-weight': 'fontWeight',
            'font-style': 'fontStyle',
            'border-radius': 'borderRadius',
            'border-style': 'borderStyle',
            'box-shadow': 'shadow',
            'max-width': 'maxWidth',
            'flex-basis': 'flexBasis',
            'object-fit': 'objectFit',
        };

        const category = themeCategoryMap[cssProperty];

        if (category) {
            if (category === 'colors') {
                const colorKey = isDarkMode ? `${valueStr}-dark` : valueStr;
                // Fallback chain: dark-mode specific -> primary -> direct value
                return this.theme.colors[colorKey] || this.theme.colors[valueStr] || valueStr;
            }
            // For other categories (spacing, fontSize, etc.)
            return this.theme[category]?.[valueStr] || valueStr;
        }
        // If no specific category mapping, return the value string directly (e.g., for 'display', 'text-align')
        return valueStr;
    }
}
