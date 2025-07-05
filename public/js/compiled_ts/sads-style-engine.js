// TypeScript type definitions and class for SADS (Semantic Attribute-Driven Styling) Engine
import { sadsDefaultTheme as importedDefaultTheme } from "./sads-default-theme.js";
// SADS (Semantic Attribute-Driven Styling) Engine v0.1.2 - TypeScript Version
class SADSEngine {
  constructor(customThemeConfig = {}, externalDefaultTheme = null) {
    // Use externalDefaultTheme if provided, otherwise use the imported sadsDefaultTheme
    // This provides flexibility in how the default theme is loaded.
    const baseTheme = externalDefaultTheme || importedDefaultTheme;
    if (Object.keys(baseTheme).length === 0) {
      console.warn(
        "SADS: Default theme not found or empty. Engine might not work as expected."
      );
    }
    this.theme = this._initializeTheme(baseTheme, customThemeConfig);
    this.dynamicStyleSheet = this._createDynamicStyleSheet();
    this.ruleCounter = 0;
    console.log("SADS Engine (TS) Initialized. Theme:", this.theme);
  }
  _initializeTheme(defaultConfig, customThemeConfig) {
    // Deep clone defaultConfig to prevent modification of the original object
    const clonedDefaultConfig = JSON.parse(JSON.stringify(defaultConfig));
    // Ensure aliases are correctly set up if they depend on other default values
    if (
      clonedDefaultConfig.colors &&
      clonedDefaultConfig.colors["text-accent"]
    ) {
      clonedDefaultConfig.colors["border-accent"] =
        clonedDefaultConfig.colors["text-accent"];
    } else {
      console.warn(
        "SADS: 'text-accent' not found in default theme colors for 'border-accent' alias."
      );
    }
    if (
      clonedDefaultConfig.colors &&
      clonedDefaultConfig.colors["text-accent-dark"]
    ) {
      clonedDefaultConfig.colors["border-accent-dark"] =
        clonedDefaultConfig.colors["text-accent-dark"];
    } else {
      // It's okay if text-accent-dark is not present, border-accent-dark might not be used or defined directly
    }
    return this._deepMergeThemes(clonedDefaultConfig, customThemeConfig);
  }
  _deepMergeThemes(base, custom) {
    const merged = { ...base }; // Shallow clone base
    for (const key in custom) {
      if (custom.hasOwnProperty(key)) {
        const customValue = custom[key];
        const baseValue = base[key];
        if (
          typeof customValue === "object" &&
          customValue !== null &&
          !Array.isArray(customValue) &&
          typeof baseValue === "object" &&
          baseValue !== null &&
          !Array.isArray(baseValue)
        ) {
          merged[key] = this._deepMergeThemes(baseValue, customValue);
        } else {
          merged[key] = customValue; // Custom overrides base
        }
      }
    }
    return merged;
  }
  _createDynamicStyleSheet() {
    if (typeof document === "undefined") {
      // Guard for non-browser environments
      return null;
    }
    let styleEl = document.getElementById("sads-dynamic-styles");
    if (!styleEl) {
      styleEl = document.createElement("style");
      styleEl.id = "sads-dynamic-styles";
      document.head.appendChild(styleEl);
    } else {
      // Clear existing rules
      if (styleEl.sheet) {
        while (styleEl.sheet.cssRules.length > 0) {
          styleEl.sheet.deleteRule(0);
        }
      }
    }
    return styleEl.sheet;
  }
  updateTheme(newThemeConfig) {
    // Re-initialize with new config, merging with the original imported default theme as base
    this.theme = this._initializeTheme(importedDefaultTheme, newThemeConfig);
    this.dynamicStyleSheet = this._createDynamicStyleSheet(); // Clears old rules
    if (typeof document !== "undefined") {
      document
        .querySelectorAll("[data-sads-component]")
        .forEach((rootEl) => this.applyStylesTo(rootEl));
    }
  }
  _getTargetSelector(el) {
    let targetSelector = Array.from(el.classList).find((cls) =>
      cls.startsWith("sads-id-")
    );
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
      parsedRules.forEach((rule) => {
        const breakpointKey = rule.breakpoint;
        const bpQuery = this.theme.breakpoints[breakpointKey];
        let targetQuery;
        if (!bpQuery) {
          console.warn(
            `SADS: Unknown breakpoint key '${breakpointKey}' for ${targetSelector}. Raw query used: ${breakpointKey}`
          );
          targetQuery = breakpointKey; // Use raw key as query
        } else {
          targetQuery = bpQuery;
        }
        responsiveStyles[targetQuery] = responsiveStyles[targetQuery] || "";
        for (const [respSadsPropKey, respSemanticVal] of Object.entries(
          rule.styles
        )) {
          const cssProp = this._mapSadsPropertyToCss(respSadsPropKey);
          const actualVal = this._mapSemanticValueToActual(
            cssProp,
            respSemanticVal
          );
          if (cssProp && actualVal !== null) {
            responsiveStyles[targetQuery] +=
              `${cssProp}: ${actualVal} !important;\n`;
          } else if (!cssProp) {
            console.warn(
              `SADS: Unmapped SADS property '${respSadsPropKey}' in responsive rule for ${targetSelector}`
            );
          }
        }
      });
    } catch (e) {
      console.error(
        `SADS: Error parsing responsive rules for ${targetSelector}: "${rulesString}"`,
        e
      );
    }
    return responsiveStyles;
  }
  _generateBaseCss(attributes, targetSelector) {
    let baseCssText = "";
    for (const attrKey in attributes) {
      // Ensure we are only processing sads attributes, excluding special/control ones
      if (
        Object.prototype.hasOwnProperty.call(attributes, attrKey) &&
        attrKey.toLowerCase().startsWith("sads") &&
        attrKey.toLowerCase() !== "sadsresponsiverules" &&
        attrKey.toLowerCase() !== "sadscomponent" &&
        attrKey.toLowerCase() !== "sadselement"
      ) {
        const sadsPropertyKey = attrKey.substring("sads".length); // Remove "sads" prefix
        const semanticValue = attributes[attrKey];
        const cssProperty = this._mapSadsPropertyToCss(sadsPropertyKey);
        const actualValue = this._mapSemanticValueToActual(
          cssProperty,
          semanticValue
        );
        if (cssProperty && actualValue !== null) {
          baseCssText += `${cssProperty}: ${actualValue};\n`;
        } else if (!cssProperty) {
          // Warning for unmapped SADS property, excluding 'LayoutType' which is intentionally not mapped
          if (sadsPropertyKey.toLowerCase() !== "layouttype") {
            console.warn(
              `SADS: Unmapped SADS property '${sadsPropertyKey}' for ${targetSelector}`
            );
          }
        }
      }
    }
    return baseCssText;
  }
  applyStylesTo(rootElement) {
    if (!rootElement || !rootElement.matches("[data-sads-component]")) {
      // console.warn("SADS: applyStylesTo called on invalid root or non-component element.", rootElement);
      return;
    }
    // Ensure we are in a browser environment
    if (typeof document === "undefined") {
      console.log("SADS.applyStylesTo: Document is undefined, exiting."); // New log
      return;
    }
    console.log("SADS.applyStylesTo: Entered for rootElement:", rootElement); // New log
    const elementsToStyle = [
      rootElement,
      ...Array.from(rootElement.querySelectorAll("[data-sads-element]")),
    ];
    console.log("SADS.applyStylesTo: Elements to style:", elementsToStyle); // New log
    elementsToStyle.forEach((el) => {
      console.log("SADS.applyStylesTo: Processing element:", el); // New log
      const targetSelector = this._getTargetSelector(el);
      const attributes = el.dataset;
      // Log a serializable version of dataset for clarity, as DOMStringMap can be tricky in console
      console.log(
        `SADS.applyStylesTo: Element ${targetSelector} dataset:`,
        JSON.parse(JSON.stringify(attributes))
      ); // New log
      const baseCssText = this._generateBaseCss(attributes, targetSelector);
      console.log(
        `SADS.applyStylesTo: Generated base CSS for ${targetSelector}: "${baseCssText.trim()}"`
      ); // New log
      if (baseCssText.trim()) {
        // Ensure we only add non-empty rules
        this._addCssRule(targetSelector, baseCssText);
      } else {
        console.log(
          `SADS.applyStylesTo: No base CSS generated for ${targetSelector}, skipping _addCssRule for base styles.`
        ); // New log
      }
      const responsiveStyles = this._parseResponsiveRules(
        attributes.sadsResponsiveRules, // sadsResponsiveRules might be undefined
        targetSelector
      );
      for (const [bpQuery, cssRules] of Object.entries(responsiveStyles)) {
        if (cssRules) this._addCssRule(targetSelector, cssRules, bpQuery);
      }
    });
  }
  _addCssRule(selector, rules, mediaQuery = null) {
    if (!rules.trim()) return; // Do not add empty rules
    const ruleContent = `${selector} { ${rules} }`;
    const finalRule = mediaQuery
      ? `@media ${mediaQuery} { ${ruleContent} }`
      : ruleContent;
    console.log(`SADS: Attempting to add CSS rule: "${finalRule}"`); // Added log
    try {
      if (this.dynamicStyleSheet) {
        const currentRuleCount = this.dynamicStyleSheet.cssRules.length;
        this.dynamicStyleSheet.insertRule(finalRule, currentRuleCount);
        // Verify insertion if possible (some browsers might not update length immediately or consistently)
        if (this.dynamicStyleSheet.cssRules.length > currentRuleCount) {
          console.log(
            `SADS: Successfully inserted rule. New rule count: ${this.dynamicStyleSheet.cssRules.length}`
          );
        } else {
          // This path might be hit if insertRule succeeded but length didn't update, or if it failed silently before catch.
          // Or if the rule was a duplicate and got ignored by some browser logic (less likely for unique SADS IDs).
          console.warn(
            `SADS: Rule insertion attempted, but cssRules.length did not increase. Rule: "${finalRule}" Current sheet content:`,
            this.dynamicStyleSheet.ownerNode?.textContent
          );
        }
      } else {
        console.error(
          `SADS: Dynamic stylesheet not available. Cannot insert rule: "${finalRule}"`
        );
      }
    } catch (e) {
      // Explicitly type 'e' as any or unknown then check
      console.error(
        `SADS: Error inserting CSS rule: "${finalRule}"`,
        e.message,
        e.stack
      );
      if (this.dynamicStyleSheet && this.dynamicStyleSheet.ownerNode) {
        console.error(
          `SADS: Stylesheet ownerNode content at time of error:`,
          this.dynamicStyleSheet.ownerNode.textContent
        );
      } else if (!this.dynamicStyleSheet) {
        console.error(`SADS: Dynamic stylesheet was null at time of error.`);
      }
    }
  }
  _mapSadsPropertyToCss(sadsPropertyKey) {
    if (!sadsPropertyKey) return null;
    // Ensure first char is lowercase for camelCase to kebab-case conversion
    let key =
      sadsPropertyKey.charAt(0).toLowerCase() + sadsPropertyKey.slice(1);
    // Convert camelCase (e.g., "flexDirection") or PascalCase (e.g., "FlexDirection") to kebab-case ("flex-direction")
    let kebabKey = key.replace(/([A-Z])/g, (g) => `-${g[0].toLowerCase()}`);
    // If the original sadsPropertyKey started with an uppercase letter and was not multi-word,
    // the above might result in something like "-opacity" from "Opacity".
    // Correct this if kebabKey starts with a dash.
    if (kebabKey.startsWith("-")) {
      kebabKey = kebabKey.substring(1);
    }
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
      "flex-justify": "justify-content", // Common alias
      "justify-content": "justify-content",
      "flex-align-items": "align-items", // Common alias
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
      "layout-type": null, // Explicitly not a direct CSS prop
      // Allow direct CSS properties if not in map by falling through
    };
    if (propertyMap.hasOwnProperty(kebabKey)) return propertyMap[kebabKey];
    // Fallback: assumes kebabKey is a valid CSS property if not in map
    // This allows users to use data-sads-some-new-css-prop="value"
    // console.warn(`SADS: Unmapped SADS property key '${sadsPropertyKey}' (kebab: ${kebabKey}). Falling back to kebabKey.`);
    return kebabKey;
  }
  _mapSemanticValueToActual(cssProperty, semanticValue) {
    if (semanticValue === null || semanticValue === undefined) return null;
    if (cssProperty === null) return null; // Cannot map value if CSS property is unknown or irrelevant
    const valueStr = String(semanticValue);
    if (valueStr.startsWith("custom:")) {
      return valueStr.substring("custom:".length);
    }
    const isDarkMode =
      typeof document !== "undefined" &&
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
      width: "spacing", // Can use spacing scale or direct values
      height: "spacing", // Can use spacing scale or direct values
      "background-color": "colors",
      color: "colors",
      "border-color": "colors",
      "font-size": "fontSize",
      "font-weight": "fontWeight",
      "font-style": "fontStyle", // maps to SadsFontStyle
      "border-radius": "borderRadius",
      "border-style": "borderStyle", // maps to SadsBorderStyle
      "box-shadow": "shadow",
      "max-width": "maxWidth",
      "flex-basis": "flexBasis",
      "object-fit": "objectFit", // maps to SadsObjectFit
      // CSS properties not needing theme category lookup (e.g. 'display', 'text-align') are not listed
    };
    const categoryKey = themeCategoryMap[cssProperty];
    if (categoryKey) {
      const themeCategory = this.theme[categoryKey];
      if (themeCategory) {
        if (categoryKey === "colors") {
          const colorKey = isDarkMode ? `${valueStr}-dark` : valueStr;
          // Fallback chain: dark-mode specific -> primary -> direct value
          return themeCategory[colorKey] || themeCategory[valueStr] || valueStr;
        }
        // For other categories (spacing, fontSize, etc.)
        return themeCategory[valueStr] || valueStr;
      }
    }
    // If no specific category mapping, or category not found in theme, return the value string directly
    return valueStr;
  }
}
// Export the class
export { SADSEngine };
// Example of how it might be instantiated (for testing or global exposure if needed by bundler)
// This part would typically be in an app.js or similar entry point.
//
// if (typeof window !== 'undefined' && typeof document !== 'undefined') {
//   // Ensure sadsDefaultTheme is available if not passed directly
//   // For example, if sads-default-theme.ts is bundled and exports sadsDefaultTheme:
//   // import { sadsDefaultTheme } from './sads-default-theme';
//   // const sadsEngineInstance = new SADSEngine({}, sadsDefaultTheme);
//
//   // Or if relying on a global (less ideal with modules):
//   // const sadsEngineInstance = new SADSEngine({}, (window as any).sadsDefaultTheme);
//
//   // (window as any).sadsEngineInstance = sadsEngineInstance;
//   // document.addEventListener('DOMContentLoaded', () => {
//   //   document.querySelectorAll<HTMLElement>('[data-sads-component]').forEach(el => {
//   //     sadsEngineInstance.applyStylesTo(el);
//   //   });
//   // });
// }
// To make it available globally for simple script inclusion in nl-sads-test.html:
if (typeof window !== "undefined") {
  window.SADSEngine = SADSEngine;
}
//# sourceMappingURL=sads-style-engine.js.map
