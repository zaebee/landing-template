// TypeScript type definitions and class for SADS (Semantic Attribute-Driven Styling) Engine
import { SadsAttributeValue, SadsBorderRadiusToken, SadsColorToken, SadsFontWeightToken, SadsSpacingToken, SadsStylingSet, SadsResponsiveStyle as ProtoSadsResponsiveStyle, // Alias to avoid name clash
SadsElementStyles, } from "./generated_proto/sads_styling.v1.js";
// SADS (Semantic Attribute-Driven Styling) Engine v0.1.2 - TypeScript Version
class SADSEngine {
    constructor(customThemeConfig = {}, externalDefaultTheme = null) {
        let baseTheme = externalDefaultTheme;
        if (!baseTheme &&
            typeof window !== "undefined" &&
            window.sadsDefaultTheme) {
            baseTheme = window.sadsDefaultTheme;
            console.log("SADS: Using global sadsDefaultTheme.");
        }
        if (!baseTheme || Object.keys(baseTheme).length === 0) {
            console.warn("SADS: Default theme not found or empty. Engine might not work as expected. Ensure sadsDefaultTheme is loaded or passed.");
            baseTheme = {
                colors: {},
                spacing: {},
                fontSize: {},
                fontWeight: {},
                borderRadius: {},
                shadow: {},
                maxWidth: {},
                breakpoints: {},
                flexBasis: {},
                objectFit: {},
                fontStyle: {},
                borderStyle: {},
            };
        }
        this.theme = this._initializeTheme(baseTheme, customThemeConfig);
        this.dynamicStyleSheet = this._createDynamicStyleSheet();
        this.ruleCounter = 0;
        console.log("SADS Engine (TS) Initialized. Theme:", this.theme);
    }
    _initializeTheme(defaultConfig, customThemeConfig) {
        const clonedDefaultConfig = JSON.parse(JSON.stringify(defaultConfig));
        if (clonedDefaultConfig.colors &&
            clonedDefaultConfig.colors["text-accent"]) {
            clonedDefaultConfig.colors["border-accent"] =
                clonedDefaultConfig.colors["text-accent"];
        }
        else {
            console.warn("SADS: 'text-accent' not found for 'border-accent' alias.");
        }
        if (clonedDefaultConfig.colors &&
            clonedDefaultConfig.colors["text-accent-dark"]) {
            clonedDefaultConfig.colors["border-accent-dark"] =
                clonedDefaultConfig.colors["text-accent-dark"];
        }
        return this._deepMergeThemes(clonedDefaultConfig, customThemeConfig);
    }
    _deepMergeThemes(base, custom) {
        const merged = { ...base };
        for (const key in custom) {
            if (custom.hasOwnProperty(key)) {
                const customValue = custom[key];
                const baseValue = base[key];
                if (typeof customValue === "object" &&
                    customValue !== null &&
                    !Array.isArray(customValue) &&
                    typeof baseValue === "object" &&
                    baseValue !== null &&
                    !Array.isArray(baseValue)) {
                    merged[key] = this._deepMergeThemes(baseValue, customValue);
                }
                else {
                    merged[key] = customValue;
                }
            }
        }
        return merged;
    }
    _createDynamicStyleSheet() {
        if (typeof document === "undefined")
            return null;
        let styleEl = document.getElementById("sads-dynamic-styles");
        if (!styleEl) {
            styleEl = document.createElement("style");
            styleEl.id = "sads-dynamic-styles";
            document.head.appendChild(styleEl);
        }
        else {
            if (styleEl.sheet) {
                while (styleEl.sheet.cssRules.length > 0) {
                    styleEl.sheet.deleteRule(0);
                }
            }
        }
        return styleEl.sheet;
    }
    updateTheme(newThemeConfig) {
        let baseThemeForUpdate;
        if (typeof window !== "undefined" && window.sadsDefaultTheme) {
            baseThemeForUpdate = window.sadsDefaultTheme;
        }
        else {
            console.warn("SADS.updateTheme: Global sadsDefaultTheme not found. Using empty theme as base.");
            baseThemeForUpdate = {
                colors: {},
                spacing: {},
                fontSize: {},
                fontWeight: {},
                borderRadius: {},
                shadow: {},
                maxWidth: {},
                breakpoints: {},
                flexBasis: {},
                objectFit: {},
                fontStyle: {},
                borderStyle: {},
            };
        }
        this.theme = this._initializeTheme(baseThemeForUpdate, newThemeConfig);
        this.applyStyles(); // Use the new applyStyles method
    }
    _getTargetSelector(el) {
        let targetSelector = Array.from(el.classList).find((cls) => cls.startsWith("sads-id-"));
        if (!targetSelector) {
            targetSelector = `sads-id-${this.ruleCounter++}`;
            el.classList.add(targetSelector);
        }
        return `.${targetSelector}`;
    }
    _parseSadsAttributeString(sadsPropertyKey, rawValue) {
        const attributeValue = {
            valueType: { oneofKind: undefined },
        };
        if (rawValue.startsWith("custom:")) {
            attributeValue.valueType = {
                oneofKind: "customValue",
                customValue: rawValue.substring("custom:".length),
            };
            return SadsAttributeValue.create(attributeValue);
        }
        const normalizedKey = sadsPropertyKey.toLowerCase();
        switch (normalizedKey) {
            case "padding":
            case "paddingtop":
            case "paddingbottom":
            case "paddingleft":
            case "paddingright":
            case "margin":
            case "margintop":
            case "marginbottom":
            case "marginleft":
            case "marginright":
            case "gap":
            case "borderwidth":
                const spacingTokenKey = `SPACING_TOKEN_${rawValue.toUpperCase()}`;
                if (spacingTokenKey in SadsSpacingToken) {
                    attributeValue.valueType = {
                        oneofKind: "spacingToken",
                        spacingToken: SadsSpacingToken[spacingTokenKey],
                    };
                }
                else {
                    attributeValue.valueType = {
                        oneofKind: "customValue",
                        customValue: rawValue,
                    };
                }
                break;
            case "bgcolor":
            case "textcolor":
            case "bordercolor":
                const colorTokenKey = `COLOR_TOKEN_${rawValue.toUpperCase()}`;
                if (colorTokenKey in SadsColorToken) {
                    attributeValue.valueType = {
                        oneofKind: "colorToken",
                        colorToken: SadsColorToken[colorTokenKey],
                    };
                }
                else {
                    if (rawValue.toLowerCase() === "transparent") {
                        attributeValue.valueType = {
                            oneofKind: "colorToken",
                            colorToken: SadsColorToken.COLOR_TOKEN_TRANSPARENT,
                        };
                    }
                    else {
                        attributeValue.valueType = {
                            oneofKind: "customValue",
                            customValue: rawValue,
                        };
                    }
                }
                break;
            case "fontweight":
                const fontWeightTokenKey = `FONT_WEIGHT_TOKEN_${rawValue.toUpperCase()}`;
                if (fontWeightTokenKey in SadsFontWeightToken) {
                    attributeValue.valueType = {
                        oneofKind: "fontWeightToken",
                        fontWeightToken: SadsFontWeightToken[fontWeightTokenKey],
                    };
                }
                else {
                    attributeValue.valueType = {
                        oneofKind: "customValue",
                        customValue: rawValue,
                    };
                }
                break;
            case "borderradius":
                const radiusTokenKey = `BORDER_RADIUS_TOKEN_${rawValue.toUpperCase()}`;
                if (radiusTokenKey in SadsBorderRadiusToken) {
                    attributeValue.valueType = {
                        oneofKind: "borderRadiusToken",
                        borderRadiusToken: SadsBorderRadiusToken[radiusTokenKey],
                    };
                }
                else {
                    attributeValue.valueType = {
                        oneofKind: "customValue",
                        customValue: rawValue,
                    };
                }
                break;
            case "fontsize":
                attributeValue.valueType = {
                    oneofKind: "fontSizeValue",
                    fontSizeValue: rawValue,
                };
                break;
            default:
                attributeValue.valueType = {
                    oneofKind: "customValue",
                    customValue: rawValue,
                };
                break;
        }
        if (attributeValue.valueType.oneofKind === undefined)
            return null;
        return SadsAttributeValue.create(attributeValue);
    }
    _extractBaseStylesFromDataset(dataset) {
        const attributes = {};
        for (const key in dataset) {
            if (Object.prototype.hasOwnProperty.call(dataset, key) &&
                key.startsWith("sads") &&
                key.toLowerCase() !== "sadsresponsiverules" &&
                key.toLowerCase() !== "sadscomponent" &&
                key.toLowerCase() !== "sadselement") {
                const sadsPropertyKey = key.substring("sads".length);
                const normalizedSadsKey = sadsPropertyKey.charAt(0).toLowerCase() + sadsPropertyKey.slice(1);
                const rawValue = dataset[key];
                if (rawValue !== undefined) {
                    const parsedValue = this._parseSadsAttributeString(normalizedSadsKey, rawValue);
                    if (parsedValue)
                        attributes[normalizedSadsKey] = parsedValue;
                }
            }
        }
        return SadsStylingSet.create({ attributes });
    }
    _parseResponsiveRulesTS(rulesString) {
        if (!rulesString)
            return [];
        const result = [];
        try {
            const rawParsedRules = JSON.parse(rulesString);
            rawParsedRules.forEach((rawRule) => {
                const stylesAttributes = {};
                for (const sadsKey in rawRule.styles) {
                    if (Object.prototype.hasOwnProperty.call(rawRule.styles, sadsKey)) {
                        const rawValue = rawRule.styles[sadsKey];
                        const parsedValue = this._parseSadsAttributeString(sadsKey, rawValue);
                        if (parsedValue)
                            stylesAttributes[sadsKey] = parsedValue;
                    }
                }
                const responsiveStyle = ProtoSadsResponsiveStyle.create({
                    breakpointKey: rawRule.breakpoint,
                    styles: SadsStylingSet.create({ attributes: stylesAttributes }),
                });
                result.push(responsiveStyle);
            });
        }
        catch (e) {
            console.error(`SADS TS: Error parsing responsive rules string: "${rulesString}"`, e);
        }
        return result;
    }
    _parseElementDatasetToSadsElementStyles(dataset) {
        const baseStylesSet = this._extractBaseStylesFromDataset(dataset);
        const responsiveRulesString = dataset.sadsResponsiveRules;
        const responsiveStylesArray = this._parseResponsiveRulesTS(responsiveRulesString);
        const hasBaseStyles = baseStylesSet.attributes &&
            Object.keys(baseStylesSet.attributes).length > 0;
        const hasResponsiveStyles = responsiveStylesArray.length > 0;
        if (!hasBaseStyles && !hasResponsiveStyles)
            return null;
        return SadsElementStyles.create({
            baseStyles: hasBaseStyles ? baseStylesSet : undefined,
            responsiveStyles: responsiveStylesArray,
        });
    }
    _resolveSadsAttributeValueToCss(cssProperty, sadsValue) {
        if (!cssProperty)
            return null;
        const isDarkMode = typeof document !== "undefined" &&
            document.body.classList.contains("dark-mode");
        let semanticKey;
        let valueFromToken = false;
        switch (sadsValue.valueType.oneofKind) {
            case "customValue":
                semanticKey = sadsValue.valueType.customValue;
                if (semanticKey.startsWith("custom:"))
                    return semanticKey.substring("custom:".length);
                break;
            case "spacingToken":
                const spacingTokenStr = SadsSpacingToken[sadsValue.valueType.spacingToken]
                    ?.replace("SPACING_TOKEN_", "")
                    .toLowerCase();
                semanticKey =
                    spacingTokenStr === "unspecified" ? undefined : spacingTokenStr;
                valueFromToken = true;
                break;
            case "colorToken":
                const colorTokenStr = SadsColorToken[sadsValue.valueType.colorToken]
                    ?.replace("COLOR_TOKEN_", "")
                    .toLowerCase();
                semanticKey =
                    colorTokenStr === "unspecified" ? undefined : colorTokenStr;
                if (semanticKey === "transparent")
                    return "transparent";
                valueFromToken = true;
                break;
            case "fontWeightToken":
                const fontWeightStr = SadsFontWeightToken[sadsValue.valueType.fontWeightToken]
                    ?.replace("FONT_WEIGHT_TOKEN_", "")
                    .toLowerCase();
                semanticKey =
                    fontWeightStr === "unspecified" ? undefined : fontWeightStr;
                valueFromToken = true;
                break;
            case "borderRadiusToken":
                const radiusTokenStr = SadsBorderRadiusToken[sadsValue.valueType.borderRadiusToken]
                    ?.replace("BORDER_RADIUS_TOKEN_", "")
                    .toLowerCase();
                semanticKey =
                    radiusTokenStr === "unspecified" ? undefined : radiusTokenStr;
                valueFromToken = true;
                break;
            case "fontSizeValue":
                semanticKey = sadsValue.valueType.fontSizeValue;
                break;
            default:
                return null;
        }
        if (semanticKey === undefined ||
            semanticKey === null ||
            semanticKey === "unspecified")
            return null;
        const themeCategoryMap = {
            padding: "spacing",
            "padding-top": "spacing",
            "padding-bottom": "spacing",
            "padding-left": "spacing",
            "padding-right": "spacing",
            margin: "spacing",
            "margin-top": "spacing",
            "margin-bottom": "spacing",
            "margin-left": "spacing",
            "margin-right": "spacing",
            gap: "spacing",
            "border-width": "spacing",
            width: "spacing",
            height: "spacing",
            "background-color": "colors",
            color: "colors",
            "border-color": "colors",
            "font-size": "fontSize",
            "font-weight": "fontWeight",
            "font-style": "fontStyle",
            "border-radius": "borderRadius",
            "border-style": "borderStyle",
            "box-shadow": "shadow",
            "max-width": "maxWidth",
            "flex-basis": "flexBasis",
            "object-fit": "objectFit",
        };
        const categoryKey = themeCategoryMap[cssProperty];
        if (categoryKey) {
            const themeCategory = this.theme[categoryKey];
            if (themeCategory) {
                if (categoryKey === "colors") {
                    const colorThemeKey = isDarkMode
                        ? `${semanticKey}-dark`
                        : semanticKey;
                    return (themeCategory[colorThemeKey] ||
                        themeCategory[semanticKey] ||
                        (valueFromToken ? null : semanticKey));
                }
                const themeValue = themeCategory[semanticKey];
                if (themeValue !== undefined)
                    return themeValue;
                else if (!valueFromToken)
                    return semanticKey;
                else
                    return null;
            }
            else if (!valueFromToken)
                return semanticKey;
        }
        if (!valueFromToken)
            return semanticKey;
        return null;
    }
    _generateCssFromSadsStylingSet(stylingSet) {
        let cssText = "";
        if (!stylingSet.attributes)
            return "";
        for (const sadsKey in stylingSet.attributes) {
            if (Object.prototype.hasOwnProperty.call(stylingSet.attributes, sadsKey)) {
                const sadsValue = stylingSet.attributes[sadsKey];
                const cssProperty = this._mapSadsPropertyToCss(sadsKey);
                if (!cssProperty)
                    continue;
                const actualValue = this._resolveSadsAttributeValueToCss(cssProperty, sadsValue);
                if (actualValue !== null)
                    cssText += `${cssProperty}: ${actualValue};\n`;
            }
        }
        return cssText;
    }
    _applyProcessedStylesToElement(el, elementSadsConfig) {
        const targetSelector = this._getTargetSelector(el);
        if (elementSadsConfig.baseStyles &&
            elementSadsConfig.baseStyles.attributes) {
            const baseCssText = this._generateCssFromSadsStylingSet(elementSadsConfig.baseStyles);
            if (baseCssText.trim())
                this._addCssRule(targetSelector, baseCssText);
        }
        if (elementSadsConfig.responsiveStyles &&
            elementSadsConfig.responsiveStyles.length > 0) {
            elementSadsConfig.responsiveStyles.forEach((responsiveStyle) => {
                if (responsiveStyle.breakpointKey &&
                    responsiveStyle.styles &&
                    responsiveStyle.styles.attributes) {
                    const mediaQuery = this.theme.breakpoints[responsiveStyle.breakpointKey] ||
                        responsiveStyle.breakpointKey;
                    const responsiveCssText = this._generateCssFromSadsStylingSet(responsiveStyle.styles);
                    if (responsiveCssText.trim())
                        this._addCssRule(targetSelector, responsiveCssText, mediaQuery);
                }
            });
        }
    }
    applyStyles() {
        if (typeof document === "undefined") {
            console.log("SADS: Document is undefined, cannot apply styles.");
            return;
        }
        console.log("SADS (TS): applyStyles called using typed parsing flow.");
        if (this.dynamicStyleSheet && this.dynamicStyleSheet.ownerNode) {
            while (this.dynamicStyleSheet.cssRules.length > 0) {
                this.dynamicStyleSheet.deleteRule(0);
            }
        }
        else {
            this.dynamicStyleSheet = this._createDynamicStyleSheet();
            if (!this.dynamicStyleSheet) {
                console.error("SADS: Critical error - dynamic stylesheet cannot be created. Styling will not be applied.");
                return;
            }
        }
        this.ruleCounter = 0;
        document
            .querySelectorAll("[data-sads-component]")
            .forEach((rootEl) => {
            const elementsToStyle = [
                rootEl,
                ...Array.from(rootEl.querySelectorAll("[data-sads-element]")),
            ];
            elementsToStyle.forEach((el) => {
                const elementSadsConfig = this._parseElementDatasetToSadsElementStyles(el.dataset);
                if (elementSadsConfig) {
                    this._applyProcessedStylesToElement(el, elementSadsConfig);
                }
            });
        });
        console.log("SADS (TS): Style application process completed with typed parsing.");
    }
    // TODO: The old _parseResponsiveRules, _generateBaseCss, and applyStylesTo (below) need to be removed.
    _parseResponsiveRules(rulesString, targetSelector) {
        const responsiveStyles = {};
        if (!rulesString)
            return responsiveStyles;
        try {
            const parsedRulesOld = JSON.parse(rulesString);
            parsedRulesOld.forEach((rule) => {
                const breakpointKey = rule.breakpoint;
                const bpQuery = this.theme.breakpoints[breakpointKey];
                let targetQuery;
                if (!bpQuery) {
                    console.warn(`SADS: Unknown breakpoint key '${breakpointKey}' for ${targetSelector}. Raw query used: ${breakpointKey}`);
                    targetQuery = breakpointKey;
                }
                else {
                    targetQuery = bpQuery;
                }
                responsiveStyles[targetQuery] = responsiveStyles[targetQuery] || "";
                for (const [respSadsPropKey, respSemanticVal] of Object.entries(rule.styles)) {
                    const cssProp = this._mapSadsPropertyToCss(respSadsPropKey);
                    const actualVal = this._mapSemanticValueToActual(cssProp, respSemanticVal);
                    if (cssProp && actualVal !== null)
                        responsiveStyles[targetQuery] +=
                            `${cssProp}: ${actualVal} !important;\n`;
                    else if (!cssProp)
                        console.warn(`SADS: Unmapped SADS property '${respSadsPropKey}' in responsive rule for ${targetSelector}`);
                }
            });
        }
        catch (e) {
            console.error(`SADS: Error parsing responsive rules (old method) for ${targetSelector}: "${rulesString}"`, e);
        }
        return responsiveStyles;
    }
    _generateBaseCss(attributes, targetSelector) {
        let baseCssText = "";
        for (const attrKey in attributes) {
            if (Object.prototype.hasOwnProperty.call(attributes, attrKey) &&
                attrKey.toLowerCase().startsWith("sads") &&
                attrKey.toLowerCase() !== "sadsresponsiverules" &&
                attrKey.toLowerCase() !== "sadscomponent" &&
                attrKey.toLowerCase() !== "sadselement") {
                const sadsPropertyKey = attrKey.substring("sads".length);
                const semanticValue = attributes[attrKey];
                const cssProperty = this._mapSadsPropertyToCss(sadsPropertyKey);
                const actualValue = this._mapSemanticValueToActual(cssProperty, semanticValue);
                if (cssProperty && actualValue !== null)
                    baseCssText += `${cssProperty}: ${actualValue};\n`;
                else if (!cssProperty && sadsPropertyKey.toLowerCase() !== "layouttype")
                    console.warn(`SADS: Unmapped SADS property '${sadsPropertyKey}' for ${targetSelector}`);
            }
        }
        return baseCssText;
    }
    applyStylesTo(rootElement) {
        console.warn("SADS: applyStylesTo() is deprecated. Use applyStyles() instead.");
        // Call the new applyStyles method to ensure styling still occurs,
        // but log that this entry point is deprecated.
        // Note: applyStyles() processes all components, not just the given rootElement.
        // If granular application is ever needed again, applyStyles would need refactoring
        // or _applyProcessedStylesToElement could be made public.
        this.applyStyles();
    }
    _addCssRule(selector, rules, mediaQuery = null) {
        if (!rules.trim())
            return;
        const ruleContent = `${selector} { ${rules} }`;
        const finalRule = mediaQuery
            ? `@media ${mediaQuery} { ${ruleContent} }`
            : ruleContent;
        console.log(`SADS: Attempting to add CSS rule: "${finalRule}"`);
        try {
            if (this.dynamicStyleSheet) {
                const currentRuleCount = this.dynamicStyleSheet.cssRules.length;
                this.dynamicStyleSheet.insertRule(finalRule, currentRuleCount);
                if (this.dynamicStyleSheet.cssRules.length > currentRuleCount) {
                    console.log(`SADS: Successfully inserted rule. New rule count: ${this.dynamicStyleSheet.cssRules.length}`);
                }
                else {
                    console.warn(`SADS: Rule insertion attempted, but cssRules.length did not increase. Rule: "${finalRule}" Current sheet content:`, this.dynamicStyleSheet.ownerNode?.textContent);
                }
            }
            else {
                console.error(`SADS: Dynamic stylesheet not available. Cannot insert rule: "${finalRule}"`);
            }
        }
        catch (e) {
            console.error(`SADS: Error inserting CSS rule: "${finalRule}"`, e.message, e.stack);
            if (this.dynamicStyleSheet && this.dynamicStyleSheet.ownerNode)
                console.error(`SADS: Stylesheet ownerNode content at time of error:`, this.dynamicStyleSheet.ownerNode.textContent);
            else if (!this.dynamicStyleSheet)
                console.error(`SADS: Dynamic stylesheet was null at time of error.`);
        }
    }
    _mapSadsPropertyToCss(sadsPropertyKey) {
        if (!sadsPropertyKey)
            return null;
        let key = sadsPropertyKey.charAt(0).toLowerCase() + sadsPropertyKey.slice(1);
        let kebabKey = key.replace(/([A-Z])/g, (g) => `-${g[0].toLowerCase()}`);
        if (kebabKey.startsWith("-"))
            kebabKey = kebabKey.substring(1);
        const propertyMap = {
            "bg-color": "background-color",
            "text-color": "color",
            "font-size": "font-size",
            "font-weight": "font-weight",
            "font-style": "font-style",
            "text-align": "text-align",
            "text-decoration": "text-decoration",
            "border-radius": "border-radius",
            "border-width": "border-width",
            "border-style": "border-style",
            "border-color": "border-color",
            "max-width": "max-width",
            width: "width",
            height: "height",
            display: "display",
            "flex-direction": "flex-direction",
            "flex-wrap": "flex-wrap",
            "flex-justify": "justify-content",
            "justify-content": "justify-content",
            "flex-align-items": "align-items",
            "align-items": "align-items",
            "flex-basis": "flex-basis",
            gap: "gap",
            shadow: "box-shadow",
            "object-fit": "object-fit",
            padding: "padding",
            "padding-top": "padding-top",
            "padding-bottom": "padding-bottom",
            "padding-left": "padding-left",
            "padding-right": "padding-right",
            margin: "margin",
            "margin-top": "margin-top",
            "margin-bottom": "margin-bottom",
            "margin-left": "margin-left",
            "margin-right": "margin-right",
            resize: "resize",
            cursor: "cursor",
            transition: "transition",
            "box-sizing": "box-sizing",
            "layout-type": null,
        };
        if (propertyMap.hasOwnProperty(kebabKey))
            return propertyMap[kebabKey];
        return kebabKey;
    }
    _mapSemanticValueToActual(cssProperty, semanticValue) {
        if (semanticValue === null || semanticValue === undefined)
            return null;
        if (cssProperty === null)
            return null;
        const valueStr = String(semanticValue);
        if (valueStr.startsWith("custom:"))
            return valueStr.substring("custom:".length);
        const isDarkMode = typeof document !== "undefined" &&
            document.body.classList.contains("dark-mode");
        const themeCategoryMap = {
            padding: "spacing",
            "padding-top": "spacing",
            "padding-bottom": "spacing",
            "padding-left": "spacing",
            "padding-right": "spacing",
            margin: "spacing",
            "margin-top": "spacing",
            "margin-bottom": "spacing",
            "margin-left": "spacing",
            "margin-right": "spacing",
            gap: "spacing",
            "border-width": "spacing",
            width: "spacing",
            height: "spacing",
            "background-color": "colors",
            color: "colors",
            "border-color": "colors",
            "font-size": "fontSize",
            "font-weight": "fontWeight",
            "font-style": "fontStyle",
            "border-radius": "borderRadius",
            "border-style": "borderStyle",
            "box-shadow": "shadow",
            "max-width": "maxWidth",
            "flex-basis": "flexBasis",
            "object-fit": "objectFit",
        };
        const categoryKey = themeCategoryMap[cssProperty];
        if (categoryKey) {
            const themeCategory = this.theme[categoryKey];
            if (themeCategory) {
                if (categoryKey === "colors") {
                    const colorKey = isDarkMode ? `${valueStr}-dark` : valueStr;
                    return themeCategory[colorKey] || themeCategory[valueStr] || valueStr;
                }
                return themeCategory[valueStr] || valueStr;
            }
        }
        return valueStr;
    }
}
export { SADSEngine };
if (typeof window !== "undefined") {
    window.SADSEngine = SADSEngine;
}
//# sourceMappingURL=sads-style-engine.js.map