// SADS (Semantic Attribute-Driven Styling) Engine v0.1.2

class SADSEngine {
  constructor(customThemeConfig = {}, externalDefaultTheme = null) {
    // Use externalDefaultTheme if provided, otherwise try to use global sadsDefaultTheme
    // This provides flexibility in how the default theme is loaded.
    const baseTheme =
      externalDefaultTheme ||
      (typeof sadsDefaultTheme !== "undefined" ? sadsDefaultTheme : {});
    if (Object.keys(baseTheme).length === 0) {
      console.warn(
        "SADS: Default theme not found or empty. Engine might not work as expected."
      );
    }
    this.theme = this._initializeTheme(baseTheme, customThemeConfig);
    this.dynamicStyleSheet = this._createDynamicStyleSheet();
    this.ruleCounter = 0;
    console.log("SADS Engine Initialized. Theme:", this.theme);
  }

  _initializeTheme(defaultConfig, customThemeConfig) {
    // Deep clone defaultConfig to prevent modification of the original object
    const clonedDefaultConfig = JSON.parse(JSON.stringify(defaultConfig));

    // Ensure aliases are correctly set up if they depend on other default values
    // These aliases are based on the structure of sadsDefaultTheme.js
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
        if (
          typeof custom[key] === "object" &&
          custom[key] !== null &&
          !Array.isArray(custom[key]) &&
          typeof base[key] === "object" &&
          base[key] !== null &&
          !Array.isArray(base[key])
        ) {
          merged[key] = this._deepMergeThemes(base[key], custom[key]);
        } else {
          merged[key] = custom[key]; // Custom overrides base
        }
      }
    }
    return merged;
  }

  _createDynamicStyleSheet() {
    let styleEl = document.getElementById("sads-dynamic-styles");
    if (!styleEl) {
      styleEl = document.createElement("style");
      styleEl.id = "sads-dynamic-styles";
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
    document
      .querySelectorAll("[data-sads-component]")
      .forEach((rootEl) => this.applyStylesTo(rootEl));
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
    if (!rulesString) return {};

    // WASM Integration Point for Responsive Rules Parsing
    if (
      window.sadsPocWasm &&
      typeof window.sadsPocWasm.parseResponsiveRules === "function"
    ) {
      try {
        const breakpointsJSON = JSON.stringify(this.theme.breakpoints || {});
        const themeColorsJSON = JSON.stringify(this.theme.colors || {});
        const themeSpacingJSON = JSON.stringify(this.theme.spacing || {});
        const themeFontSizeJSON = JSON.stringify(this.theme.fontSize || {});
        const themeFontWeightJSON = JSON.stringify(this.theme.fontWeight || {});
        const themeBorderStyleJSON = JSON.stringify(
          this.theme.borderStyle || {}
        );
        const themeBorderRadiusJSON = JSON.stringify(
          this.theme.borderRadius || {}
        );
        const themeShadowJSON = JSON.stringify(this.theme.shadow || {});
        const themeMaxWidthJSON = JSON.stringify(this.theme.maxWidth || {});
        const themeFlexBasisJSON = JSON.stringify(this.theme.flexBasis || {});
        const themeObjectFitJSON = JSON.stringify(this.theme.objectFit || {});
        const isDarkMode = document.body.classList.contains("dark-mode");

        const resultJSON = window.sadsPocWasm.parseResponsiveRules(
          rulesString,
          breakpointsJSON,
          themeColorsJSON,
          themeSpacingJSON,
          themeFontSizeJSON,
          themeFontWeightJSON,
          themeBorderStyleJSON,
          themeBorderRadiusJSON,
          themeShadowJSON,
          themeMaxWidthJSON,
          themeFlexBasisJSON,
          themeObjectFitJSON,
          isDarkMode
        );

        if (
          typeof resultJSON === "string" &&
          !resultJSON.startsWith("Error:")
        ) {
          // console.log(`SADS: Responsive rules for '${targetSelector}' parsed by WASM.`);
          return JSON.parse(resultJSON); // Expected to be a map of media query to CSS rules string
        } else if (
          typeof resultJSON === "string" &&
          resultJSON.startsWith("Error:")
        ) {
          console.warn(
            `SADS: WASM parseResponsiveRules returned error for ${targetSelector}: ${resultJSON}. Falling back to JS logic.`
          );
        } else {
          console.warn(
            `SADS: WASM parseResponsiveRules returned unexpected value for ${targetSelector}:`,
            resultJSON,
            `. Falling back to JS logic.`
          );
        }
      } catch (wasmError) {
        console.error(
          `SADS: Error calling WASM parseResponsiveRules for ${targetSelector}:`,
          wasmError,
          `. Falling back to JS logic.`
        );
      }
    } else {
      // console.log("SADS: WASM parseResponsiveRules not available. Using JS logic for:", targetSelector);
    }

    // Original JavaScript Fallback Logic:
    const responsiveStyles = {};
    try {
      const parsedRules = JSON.parse(rulesString);
      parsedRules.forEach((rule) => {
        const breakpointKey = rule.breakpoint;
        const bpQuery = this.theme.breakpoints[breakpointKey];
        if (!bpQuery) {
          console.warn(
            `SADS: Unknown breakpoint key '${breakpointKey}' for ${targetSelector}. Raw query used: ${breakpointKey}`
          );
          responsiveStyles[breakpointKey] =
            responsiveStyles[breakpointKey] || "";
        } else {
          responsiveStyles[bpQuery] = responsiveStyles[bpQuery] || "";
        }
        const targetQuery = bpQuery || breakpointKey;

        for (const [respSadsPropKey, respSemanticVal] of Object.entries(
          rule.styles
        )) {
          const cssProp = this._mapSadsPropertyToCss(respSadsPropKey);
          // _mapSemanticValueToActual will internally use WASM for colors if available, or JS.
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
        `SADS: Error parsing responsive rules (JS fallback) for ${targetSelector}: "${rulesString}"`,
        e
      );
    }
    return responsiveStyles;
  }

  _generateBaseCss(attributes, targetSelector) {
    let baseCssText = "";
    for (const attrKey in attributes) {
      if (
        !attrKey.startsWith("sads") ||
        attrKey.toLowerCase() === "sadsresponsiverules" ||
        attrKey.toLowerCase() === "sadscomponent" ||
        attrKey.toLowerCase() === "sadselement"
      ) {
        continue;
      }

      const sadsPropertyKey = attrKey.substring("sads".length);
      const semanticValue = attributes[attrKey];
      const cssProperty = this._mapSadsPropertyToCss(sadsPropertyKey);
      const actualValue = this._mapSemanticValueToActual(
        cssProperty,
        semanticValue
      );

      if (cssProperty && actualValue !== null) {
        baseCssText += `${cssProperty}: ${actualValue};\n`;
      } else if (!cssProperty) {
        console.warn(
          `SADS: Unmapped SADS property '${sadsPropertyKey}' for ${targetSelector}`
        );
      }
    }
    return baseCssText;
  }

  // Centralized method to apply styles, now async to await WASM readiness
  async applyStyles() {
    console.log("SADS: applyStyles called. Checking WASM readiness...");
    if (window.sadsPocWasmReadyPromise) {
      try {
        await window.sadsPocWasmReadyPromise;
        console.log("SADS: WASM module is ready.");
      } catch (error) {
        console.warn(
          "SADS: WASM module failed to load or was rejected. Falling back to JS-only styling for colors.",
          error
        );
        // window.sadsPocWasm will likely be undefined or its functions unavailable.
        // The _mapSemanticValueToActual method's fallback logic will handle this.
      }
    } else {
      console.log(
        "SADS: sadsPocWasmReadyPromise not found. Proceeding with JS-only styling for colors."
      );
      // Fallback logic in _mapSemanticValueToActual will handle this.
    }

    // Clear existing rules before reapplying, if dynamicStyleSheet is valid
    if (this.dynamicStyleSheet && this.dynamicStyleSheet.ownerNode) {
      while (this.dynamicStyleSheet.cssRules.length > 0) {
        this.dynamicStyleSheet.deleteRule(0);
      }
    } else {
      // Attempt to re-create it if it became invalid
      this.dynamicStyleSheet = this._createDynamicStyleSheet();
      if (!this.dynamicStyleSheet) {
        console.error(
          "SADS: Critical error - dynamic stylesheet cannot be created or accessed. Styling will not be applied."
        );
        return; // Cannot proceed without a stylesheet
      }
    }
    this.ruleCounter = 0; // Reset rule counter for fresh application

    document.querySelectorAll("[data-sads-component]").forEach((rootEl) => {
      this._applyStylesToElementAndChildren(rootEl);
    });
    console.log("SADS: Style application process completed.");
  }

  _applyStylesToElementAndChildren(rootElement) {
    // This is the original applyStylesTo logic, refactored to be called by the new async applyStyles
    if (!rootElement || !rootElement.matches("[data-sads-component]")) {
      return;
    }

    const elementsToStyle = [
      rootElement,
      ...rootElement.querySelectorAll("[data-sads-element]"),
    ];

    elementsToStyle.forEach((el) => {
      const targetSelector = this._getTargetSelector(el);
      const attributes = el.dataset;

      // _generateBaseCss and _parseResponsiveRules will now potentially use WASM
      const baseCssText = this._generateBaseCss(attributes, targetSelector);
      if (baseCssText) {
        this._addCssRule(targetSelector, baseCssText);
      }

      const responsiveStyles = this._parseResponsiveRules(
        attributes.sadsResponsiveRules,
        targetSelector
      );
      for (const [bpQuery, cssRules] of Object.entries(responsiveStyles)) {
        if (cssRules) this._addCssRule(targetSelector, cssRules, bpQuery);
      }
    });
  }

  // Make updateTheme async as well, as it calls applyStyles
  async updateTheme(newThemeConfig) {
    this.theme = this._initializeTheme(newThemeConfig); // Re-initialize with new config
    // applyStyles will handle clearing rules now
    await this.applyStyles();
  }

  _addCssRule(selector, rules, mediaQuery = null) {
    if (!rules.trim()) return; // Do not add empty rules

    const ruleContent = `${selector} { ${rules} }`;
    const finalRule = mediaQuery
      ? `@media ${mediaQuery} { ${ruleContent} }`
      : ruleContent;
    try {
      if (this.dynamicStyleSheet) {
        this.dynamicStyleSheet.insertRule(
          finalRule,
          this.dynamicStyleSheet.cssRules.length
        );
      } else {
        console.error(
          `SADS: Dynamic stylesheet not available. Cannot insert rule: "${finalRule}"`
        );
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
    let key =
      sadsPropertyKey.charAt(0).toLowerCase() + sadsPropertyKey.slice(1);
    let kebabKey = key.replace(/([A-Z])/g, (g) => `-${g[0].toLowerCase()}`);

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
      "flex-align-items": "align-items",
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
      "layout-type": null, // Not a direct CSS prop
    };
    // Explicitly return null for 'layout-type' as it's not a style.
    if (kebabKey === "layout-type") return null;

    if (propertyMap.hasOwnProperty(kebabKey)) return propertyMap[kebabKey];

    // console.warn(`SADS: Unmapped SADS property key '${sadsPropertyKey}' (kebab: ${kebabKey}). Falling back to kebabKey.`);
    return kebabKey; // Fallback: assumes kebabKey is a valid CSS property
  }

  _mapSemanticValueToActual(cssProperty, semanticValue) {
    if (semanticValue === null || semanticValue === undefined) return null;
    const valueStr = String(semanticValue);

    if (valueStr.startsWith("custom:")) {
      return valueStr.substring("custom:".length);
    }

    const isDarkMode = document.body.classList.contains("dark-mode");

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
      "border-width": "spacing", // border-width can use spacing scale or custom
      width: "spacing", // width can use spacing scale or direct values
      height: "spacing", // height can use spacing scale or direct values

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

    const category = themeCategoryMap[cssProperty];

    if (category) {
      if (category === "colors") {
        // WASM Integration Point for Color Resolution
        if (
          window.sadsPocWasm &&
          typeof window.sadsPocWasm.resolveColor === "function"
        ) {
          try {
            const themeColorsJson = JSON.stringify(this.theme.colors);
            const resolvedColor = window.sadsPocWasm.resolveColor(
              valueStr,
              themeColorsJson,
              isDarkMode
            );

            if (
              typeof resolvedColor === "string" &&
              !resolvedColor.startsWith("Error:")
            ) {
              // console.log(`SADS: Color '${valueStr}' resolved by WASM to '${resolvedColor}' (Dark Mode: ${isDarkMode})`);
              return resolvedColor;
            } else if (
              typeof resolvedColor === "string" &&
              resolvedColor.startsWith("Error:")
            ) {
              console.warn(
                `SADS: WASM resolveColor returned error for token '${valueStr}': ${resolvedColor}. Falling back to JS logic.`
              );
              // Fallthrough to JS logic below
            } else {
              console.warn(
                `SADS: WASM resolveColor returned unexpected value for token '${valueStr}':`,
                resolvedColor,
                `. Falling back to JS logic.`
              );
              // Fallthrough to JS logic below
            }
          } catch (wasmError) {
            console.error(
              `SADS: Error calling WASM resolveColor for token '${valueStr}':`,
              wasmError,
              `. Falling back to JS logic.`
            );
            // Fallthrough to JS logic below
          }
        } else {
          // console.log("SADS: WASM resolveColor not available. Using JS logic for color token:", valueStr);
        }

        // Original JavaScript Fallback Logic for colors:
        const colorKey = isDarkMode ? `${valueStr}-dark` : valueStr;
        const resolvedJsColor =
          this.theme.colors[colorKey] ||
          this.theme.colors[valueStr] ||
          valueStr;
        // console.log(`SADS: Color '${valueStr}' resolved by JS to '${resolvedJsColor}' (Dark Mode: ${isDarkMode})`);
        return resolvedJsColor;
      }
      // For other categories (spacing, fontSize, etc.) - no WASM for these yet
      return this.theme[category]?.[valueStr] || valueStr;
    }
    // If no specific category mapping, return the value string directly (e.g., for 'display', 'text-align')
    return valueStr;
  }
}
