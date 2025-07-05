# SADS Protobuf Integration Plan

This document outlines the strategy for integrating Protobuf-defined structures into the Semantic Attribute-Driven Styling (SADS) engine and related workflows. The primary goals are to enhance type safety (especially for the ongoing JavaScript to TypeScript refactor), improve the clarity of SADS configurations, and potentially optimize data handling for Go/WASM components.

## 1. Protobuf Definitions

New SADS-specific Protobuf definitions have been introduced in `proto/sads_styling.v1.proto`. These include:

- **Enums for Tokens:**
  - `SadsSpacingToken`
  - `SadsColorToken`
  - `SadsFontWeightToken`
  - `SadsBorderRadiusToken`
- **Messages for Styling Structures:**
  - `SadsAttributeValue`: Represents a single SADS value (either a token or a custom string).
  - `SadsStylingSet`: A map of SADS property keys to `SadsAttributeValue`.
  - `SadsResponsiveStyle`: Defines a `SadsStylingSet` for a specific breakpoint key.
  - `SadsElementStyles`: Represents the complete SADS styling for an element, including base and responsive styles.
- **Helper/Future Messages:**
  - `SadsProcessingContext`, `ResolveSadsStylesRequest`, `ResolveSadsStylesResponse` (conceptual for future Go/WASM enhancements).

## 2. TypeScript Type Generation

The immediate and primary use of these Protobuf definitions is to generate TypeScript types and interfaces for the SADS engine refactor.

- **Generation Command (`package.json`):**
  The `generate-proto:ts` script is configured as:

  ```bash
  mkdir -p public/ts/generated_proto && protoc --plugin=protoc-gen-ts="$(npm root)/.bin/protoc-gen-ts" --ts_out=public/ts/generated_proto --proto_path=./proto ./proto/*.proto
  ```

  _(Note: Requires `protoc-gen-ts` to be installed, e.g., via `npm install --save-dev protoc-gen-ts` or globally, and accessible to `protoc`.)_

- **Output Directory:** Generated TypeScript files will be located in `public/ts/generated_proto/`.

- **Purpose:** These generated types will provide strong typing for SADS configurations, theme structures, and the internal state of the SADS engine (once refactored to TypeScript).

## 3. Usage in SADS Engine (TypeScript Refactor)

The generated TypeScript types will be integrated into the SADS engine (`public/ts/sads-style-engine.ts`).

- **Typing Internal Data Structures:** Variables and function parameters that handle SADS style objects will use types like `SadsElementStyles`, `SadsAttributeValue`, `SadsStylingSet`.
- **Parsing `data-sads-*` Attributes:** Logic parsing HTML `data-sads-*` attributes will create objects conforming to these TS interfaces.
- **Function Signatures:** Methods like `_mapSemanticValueToActual` will be adapted to work with these types.

### 3.1. Conceptual Snippets: Processing SADS Attributes with TS Types

The following conceptual TypeScript snippets illustrate how the SADS engine would leverage the Protobuf-generated types. These assume types like `SadsStylingSet`, `SadsAttributeValue`, `SadsElementStyles`, enums (e.g., `SadsColorToken`), and `SadsTheme` are correctly imported and available.

**a. Processing a `SadsStylingSet` for CSS Generation (Attribute Mapping)**

This function shows how SADS keys from a `SadsStylingSet` are mapped to CSS properties and their `SadsAttributeValue` objects are resolved to CSS values.

```typescript
// Conceptual snippet for public/ts/sads-style-engine.ts
// class SADSEngine {
//   theme: SadsTheme; // Assuming theme is loaded
//   isDarkMode: boolean; // Assuming this context is available

  private _mapSadsPropertyToCss(sadsPropertyKey: string): string | null {
    // ... current implementation from public/ts/sads-style-engine.ts ...
    // Example: maps "bgColor" to "background-color"
    if (!sadsPropertyKey) return null;
    let key = sadsPropertyKey.charAt(0).toLowerCase() + sadsPropertyKey.slice(1);
    let kebabKey = key.replace(/([A-Z])/g, (g) => `-${g[0].toLowerCase()}`);
    if (kebabKey.startsWith("-")) kebabKey = kebabKey.substring(1);
    const propertyMap: { [key: string]: string | null } = {
      "bg-color": "background-color", "text-color": "color", /* ...many more... */
      "layout-type": null,
    };
    if (propertyMap.hasOwnProperty(kebabKey)) return propertyMap[kebabKey];
    return kebabKey; // Fallback
  }

  private _resolveSadsAttributeValueToCss(
    cssProperty: string | null,
    sadsValue: SadsAttributeValue,
    isDarkMode: boolean
  ): string | null {
    if (!cssProperty) return null;

    const getSpacingTokenString = (token?: SadsSpacingToken): string | undefined => {/* ... */};
    const getColorTokenString = (token?: SadsColorToken): string | undefined => {/* ... */};
    // ... similar helpers for other SADS tokens ...

    let semanticKey: string | undefined;
    if (sadsValue.customValue !== undefined) {
      if (sadsValue.customValue.startsWith("custom:")) {
        return sadsValue.customValue.substring("custom:".length);
      }
      semanticKey = sadsValue.customValue;
    } else if (sadsValue.spacingToken !== undefined) {
      // Map SadsSpacingToken.SPACING_TOKEN_M to "m" for theme lookup
      semanticKey = SadsSpacingToken[sadsValue.spacingToken]?.replace('SPACING_TOKEN_', '').toLowerCase();
    } else if (sadsValue.colorToken !== undefined) {
      // Map SadsColorToken.COLOR_TOKEN_SURFACE to "surface"
      semanticKey = SadsColorToken[sadsValue.colorToken]?.replace('COLOR_TOKEN_', '').toLowerCase();
    } // ... other token types ...
    else if (sadsValue.fontSizeValue !== undefined) {
      semanticKey = sadsValue.fontSizeValue;
    } else { return null; }

    if (semanticKey === undefined) return null;

    // Simplified theme lookup (actual logic is more detailed)
    const themeCategoryMap: { [cssProp: string]: keyof SadsTheme | null } = {
      "padding": "spacing", "background-color": "colors", "font-size": "fontSize", /* ... */
    };
    const categoryKey = themeCategoryMap[cssProperty];
    if (categoryKey) {
      const themeCategory = this.theme[categoryKey] as { [key: string]: string } | undefined;
      if (themeCategory) {
        if (categoryKey === "colors") {
          const colorThemeKey = isDarkMode ? `${semanticKey}-dark` : semanticKey;
          return themeCategory[colorThemeKey] || themeCategory[semanticKey] || semanticKey;
        }
        return themeCategory[semanticKey] || semanticKey;
      }
    }
    return semanticKey; // For direct values or properties not in theme categories
  }

  private _generateCssFromSadsStylingSet(
    stylingSet: SadsStylingSet,
    isDarkMode: boolean
  ): string {
    let cssText = "";
    if (!stylingSet.attributes) return "";

    for (const sadsKey in stylingSet.attributes) {
      const sadsValue: SadsAttributeValue = stylingSet.attributes[sadsKey];
      const cssProperty = this._mapSadsPropertyToCss(sadsKey);
      if (!cssProperty) continue;

      const actualValue = this._resolveSadsAttributeValueToCss(cssProperty, sadsValue, isDarkMode);
      if (actualValue !== null) {
        cssText += `${cssProperty}: ${actualValue};\n`;
      }
    }
    return cssText;
  }
// }
```
**Benefits:** This approach provides type safety for `SadsAttributeValue` (ensuring only defined tokens or custom values are processed) and clarity in how SADS properties are resolved.

**b. Dynamic Style Reapplication using `SadsElementStyles`**

This illustrates how `applyStyles` would work if it operated on a `SadsElementStyles` object, which is assumed to be parsed upstream.

```typescript
// Conceptual snippet for public/ts/sads-style-engine.ts
// class SADSEngine {
//   dynamicStyleSheet: CSSStyleSheet | null;
//   ruleCounter: number = 0;
//   theme: SadsTheme; // Assume loaded

  private _getTargetSelector(el: HTMLElement): string { /* ... as in current engine ... */ }
  private _addCssRule(selector: string, rules: string, mediaQuery: string | null = null): void { /* ... */ }

  // _generateCssFromSadsStylingSet from snippet (a)

  private _applyProcessedStylesToElement(
    el: HTMLElement,
    elementSadsConfig: SadsElementStyles,
    isDarkMode: boolean
  ): void {
    const targetSelector = this._getTargetSelector(el);

    if (elementSadsConfig.baseStyles) {
      const baseCssText = this._generateCssFromSadsStylingSet(elementSadsConfig.baseStyles, isDarkMode);
      if (baseCssText.trim()) this._addCssRule(targetSelector, baseCssText);
    }

    if (elementSadsConfig.responsiveStyles) {
      elementSadsConfig.responsiveStyles.forEach((rs: SadsResponsiveStyle) => {
        if (rs.breakpointKey && rs.styles) {
          const mediaQuery = this.theme.breakpoints[rs.breakpointKey] || rs.breakpointKey;
          const responsiveCssText = this._generateCssFromSadsStylingSet(rs.styles, isDarkMode);
          if (responsiveCssText.trim()) this._addCssRule(targetSelector, responsiveCssText, mediaQuery);
        }
      });
    }
  }

  public async applyStyles(): Promise<void> {
    // ... (clear dynamicStyleSheet, reset ruleCounter) ...
    const isDarkModeActive = document.body.classList.contains("dark-mode");

    document.querySelectorAll<HTMLElement>("[data-sads-component]").forEach((rootEl) => {
      const elementsToStyle = [rootEl, ...rootEl.querySelectorAll<HTMLElement>("[data-sads-element]")];
      elementsToStyle.forEach((el) => {
        // Assumes _parseElementDatasetToSadsElementStyles parses el.dataset into SadsElementStyles
        // This parser would use functions like `parseSadsAttributeString` and `parseResponsiveRulesTS`
        // (already detailed in section 3.1 of the original plan document).
        const elementSadsConfig = this._parseElementDatasetToSadsElementStyles(el.dataset);
        if (elementSadsConfig) {
          this._applyProcessedStylesToElement(el, elementSadsConfig, isDarkModeActive);
        }
      });
    });
  }

  private _parseElementDatasetToSadsElementStyles(dataset: DOMStringMap): SadsElementStyles | null {
    // Conceptual: This function uses `extractBaseStylesFromDataset` (from plan section 3.1.b)
    // and `parseResponsiveRulesTS` (from plan section 3.1.c)
    // to build and return a SadsElementStyles object.
    // const base = extractBaseStylesFromDataset(dataset);
    // const responsive = parseResponsiveRulesTS(dataset.sadsResponsiveRules);
    // return { baseStyles: base, responsiveStyles: responsive };
    // Placeholder for actual implementation:
    if (Object.keys(dataset).length > 0 && Object.keys(dataset).some(k => k.startsWith("sads")) ) {
        return { baseStyles: { attributes: { temp: { customValue: "parsed" } } } }; // Dummy
    }
    return null;
  }
// }
```
**Benefits:** Decouples parsing from application. `_applyProcessedStylesToElement` receives a clear, typed `SadsElementStyles` object, making the style application logic cleaner and more robust.

### 3.2. Parsing `data-sads-*` Attributes (Summary)

The functions `parseSadsAttributeString`, `extractBaseStylesFromDataset`, and `parseResponsiveRulesTS` (detailed in the original plan's section 3.1) are crucial for converting raw string data from HTML attributes into the typed structures like `SadsAttributeValue`, `SadsStylingSet`, and `SadsResponsiveStyle[]`. These would then be assembled into a `SadsElementStyles` object by a function like the conceptual `_parseElementDatasetToSadsElementStyles` shown above.

## 4. Typed Data for Go/WASM Interaction

This section explores how TypeScript types (from `sads_styling.v1.proto`) can interface with Go/WASM functions.

### 4.1. Attribute Mapping in Go/WASM

The internal Go function `mapSadsKeyToCssPropertyGo` can be wrapped for WASM.

**Conceptual Go/WASM Wrapper:**
```go
// In sads_wasm_poc/sads_wasm_bridge.go (or similar)
package main

import (
    "strings" // Required for internal logic if copied
    "syscall/js"
)

// mapSadsKeyToCssPropertyGoInternal is the Go logic (e.g., from property_mapper.go)
func mapSadsKeyToCssPropertyGoInternal(sadsPropertyKey string) string {
    // ... (implementation as in property_mapper.go or current TS engine)
    // Example: "bgColor" -> "background-color"
    var kebabKeyBuilder strings.Builder; /* ... kebab casing logic ... */
    kebabKey := strings.ToLower(kebabKeyBuilder.String())
    propertyMap := map[string]string{ "bg-color": "background-color", /* ... */ }
    if val, ok := propertyMap[kebabKey]; ok { return val }
    return kebabKey
}

func MapSadsKeyToCssPropertyWasm(this js.Value, args []js.Value) interface{} {
    if len(args) != 1 || args[0].Type() != js.TypeString {
        return js.ValueOf("Error: Expects 1 string argument (sadsKey)")
    }
    sadsKey := args[0].String()
    return js.ValueOf(mapSadsKeyToCssPropertyGoInternal(sadsKey))
}

// In main function for WASM setup:
// js.Global().Set("sadsPocWasm", js.ValueOf(map[string]interface{}{
//    "mapSadsKeyToCssProperty": js.FuncOf(MapSadsKeyToCssPropertyWasm),
// }))
```

**Conceptual TypeScript Call:**
```typescript
// In public/ts/sads-style-engine.ts
// async function someFunctionUsingWasm(sadsKey: string): Promise<string | null> {
//   if (window.sadsPocWasm?.mapSadsKeyToCssProperty) {
//     await window.sadsPocWasmReadyPromise; // Ensure WASM is loaded
//     const result = window.sadsPocWasm.mapSadsKeyToCssProperty(sadsKey);
//     if (typeof result === 'string' && !result.startsWith("Error:")) return result;
//     console.error("WASM mapSadsKeyToCssProperty error:", result);
//   }
//   return null; // Or fallback to JS _mapSadsPropertyToCss
// }
```
**Discussion:**
- **Key-by-key calls:** Simple, but multiple JS-to-WASM calls for one element.
- **Passing serialized `SadsStylingSet`:** TS serializes `SadsStylingSet` (JSON or binary proto) to Go, Go processes all keys, returns a map `sadsKey -> cssProperty`. Fewer calls, but more serialization logic. Binary proto is cleaner on Go side if Go types are generated from proto.
- **Recommendation:** Start with key-by-key; optimize if it becomes a bottleneck.

### 4.2. Responsive Rules & WASM with Typed Data

The current `ParseResponsiveRules` WASM function takes many JSON strings. Proposal: Pass a serialized `SadsResponsiveStyle[]` (from TS types).

**Option A: Pass Serialized `SadsResponsiveStyle[]` as JSON String**
- **TS Side:** `JSON.stringify(parsedResponsiveStylesArray)`
- **Go Side:** Define Go structs matching `SadsResponsiveStyle`, `SadsStylingSet`, `SadsAttributeValue` for `json.Unmarshal`. The Go logic would then use these typed structs.
  ```go
  // Go structs mirroring proto definitions for JSON unmarshalling
  type GoSadsAttributeValue struct { /* ... fields like SpacingToken, CustomValue ... */ }
  type GoSadsStylingSet struct { Attributes map[string]GoSadsAttributeValue `json:"attributes"` }
  type GoSadsResponsiveStyle struct {
      BreakpointKey string             `json:"breakpointKey"`
      Styles        GoSadsStylingSet   `json:"styles"`
  }

  // func ParseResponsiveRulesTyped(this js.Value, args []js.Value) interface{} {
  //   sadsResponsiveStylesJSON := args[0].String() // Contains SadsResponsiveStyle[]
  //   var typedRules []GoSadsResponsiveStyle
  //   json.Unmarshal([]byte(sadsResponsiveStylesJSON), &typedRules)
  //   // ... process typedRules ...
  // }
  ```
  Value resolution (e.g., `SadsColorToken` to actual color string) would need to be adapted in Go to work with `GoSadsAttributeValue`.

**Option B: Pass Serialized `SadsResponsiveStyle[]` as Binary Protobuf**
- **TS Side:** Use a Protobuf library (e.g., `protobuf-ts`) to serialize `SadsResponsiveStyle[]` into `Uint8Array`.
- **Go Side:** Use Go Protobuf library to unmarshal bytes into Go structs generated from `sads_styling.v1.proto`.

**Pros & Cons for `SadsResponsiveStyle[]` to WASM:**
- **Pros:**
    - Type safety (especially with binary Protobuf).
    - Simpler WASM function signature (fewer arguments).
    - Aligns data structures between TS and Go.
- **Cons:**
    - Serialization/deserialization overhead (though potentially offset by fewer WASM calls and faster internal Go processing).
    - Added complexity for binary Protobuf setup (libraries on both sides).
    - Binary data harder to debug than JSON.

**Recommendation:**
1. **Iterative:** JSON string of `SadsResponsiveStyle[]` (Option A) is a good first step.
2. **Optimal:** Binary Protobuf (Option B) for better performance and type consistency in the long run.

## 5. Future Considerations (High-Level Roadmap)

(This section remains largely the same as in the original document, focusing on broader future plans like SADS Theme representation in Proto, deeper engine refactoring, etc.)

- **SADS Theme Representation:** ...
- **SADS Engine Core Logic Refactor:** ...
- **Go/WASM Function Adaptation (beyond current scope):** ...
- **Alternative Style Configuration Methods:** ...
- **Tooling and Validation:** ...

This phased approach will allow for incremental adoption of the Protobuf-defined structures, starting with the immediate benefits for the TypeScript refactor and gradually exploring deeper integration for enhanced robustness and potential performance gains.
