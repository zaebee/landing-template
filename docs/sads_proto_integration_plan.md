# SADS Protobuf Integration Plan

This document outlines the strategy for integrating Protobuf-defined structures into the Semantic Attribute-Driven Styling (SADS) engine and related workflows. The primary goals are to enhance type safety (especially for the ongoing JavaScript to TypeScript refactor), improve the clarity of SADS configurations, and potentially optimize data handling for Go/WASM components.

## 1. Protobuf Definitions

New SADS-specific Protobuf definitions have been introduced in `proto/sads_styling.v1.proto`. These include:

-   **Enums for Tokens:**
    -   `SadsSpacingToken`
    -   `SadsColorToken`
    -   `SadsFontWeightToken`
    -   `SadsBorderRadiusToken`
-   **Messages for Styling Structures:**
    -   `SadsAttributeValue`: Represents a single SADS value (either a token or a custom string).
    -   `SadsStylingSet`: A map of SADS property keys to `SadsAttributeValue`.
    -   `SadsResponsiveStyle`: Defines a `SadsStylingSet` for a specific breakpoint key.
    -   `SadsElementStyles`: Represents the complete SADS styling for an element, including base and responsive styles.
-   **Helper/Future Messages:**
    -   `SadsProcessingContext`, `ResolveSadsStylesRequest`, `ResolveSadsStylesResponse` (conceptual for future Go/WASM enhancements).

## 2. TypeScript Type Generation

The immediate and primary use of these Protobuf definitions is to generate TypeScript types and interfaces for the SADS engine refactor.

-   **Generation Command (`package.json`):**
    The `generate-proto:ts` script is configured as:
    ```bash
    mkdir -p public/ts/generated_proto && protoc --plugin=protoc-gen-ts="$(npm root)/.bin/protoc-gen-ts" --ts_out=public/ts/generated_proto --proto_path=./proto ./proto/*.proto
    ```
    *(Note: Requires `protoc-gen-ts` to be installed, e.g., via `npm install --save-dev protoc-gen-ts` or globally, and accessible to `protoc`.)*

-   **Output Directory:** Generated TypeScript files will be located in `public/ts/generated_proto/`.

-   **Purpose:** These generated types will provide strong typing for SADS configurations, theme structures, and the internal state of the SADS engine (once refactored to TypeScript).

## 3. Initial Usage in SADS Engine (TypeScript Refactor)

The first phase of integration will focus on using the generated TypeScript types within the SADS engine as it's refactored from JavaScript to TypeScript (`sads-style-engine.js` -> `sads-style-engine.ts`).

-   **Typing Internal Data Structures:**
    -   Variables and function parameters/return types that currently handle SADS style objects, rules, or resolved values will be typed using the generated interfaces (e.g., `SadsElementStyles`, `SadsAttributeValue`, `SadsStylingSet`).
-   **Parsing `data-sads-*` Attributes:**
    -   The logic that parses HTML `data-sads-*` attributes will be updated. Instead of creating generic JavaScript objects, it will aim to create objects that conform to the generated TypeScript interfaces (e.g., an element's parsed styles would populate an object of type `SadsElementStyles`).
    -   This will involve mapping string attribute values (e.g., "m" for padding, "primary" for color) to the corresponding enum values (e.g., `SadsSpacingToken.SPACING_TOKEN_M`, `SadsColorToken.COLOR_TOKEN_PRIMARY`) or to the `custom_value` field within `SadsAttributeValue`.
-   **Function Signatures:**
    -   Methods like `_mapSemanticValueToActual` (or its TS equivalent) might be refactored to work with or return parts of these structured types, improving clarity on what kind of value is being processed.
    -   `_parseResponsiveRules` would parse into `SadsResponsiveStyle[]`.
-   **Benefits:**
    -   Improved developer experience with autocompletion and type checking.
    -   Reduced runtime errors by catching type mismatches during development.
    -   Clearer and more maintainable SADS engine codebase.

### 3.1. Example: Typing Parsed SADS Attributes and Responsive Rules

The following conceptual TypeScript snippets illustrate how `data-sads-*` attributes can be parsed into the strongly-typed structures generated from `sads_styling.v1.proto`. These examples assume the generated types (e.g., `SadsAttributeValue`, `SadsSpacingToken`, `SadsStylingSet`, `SadsResponsiveStyle`) are imported.

**a. Parsing a single `data-sads-*` attribute value into `SadsAttributeValue`:**

This function demonstrates how a raw string value from a `data-sads-*` attribute can be converted into a `SadsAttributeValue` object, attempting to map it to a known token or treating it as a custom value.

```typescript
// Conceptual TypeScript in sads-style-engine.ts
// Assuming generated types are imported, e.g.:
// import {
//   SadsAttributeValue,
//   SadsSpacingToken,
//   SadsColorToken,
//   SadsFontWeightToken,
//   SadsBorderRadiusToken,
//   // Assuming enums are exported directly or via a namespace like sads_v1
// } from './generated_proto/sads_styling_v1_pb'; // Adjust path as needed

/**
 * Parses a raw SADS attribute string value into a typed SadsAttributeValue object.
 *
 * @param sadsPropertyKey - The SADS property key (e.g., "padding", "bgColor", "fontWeight")
 * @param rawValue - The string value from the data-sads-* attribute.
 * @returns A SadsAttributeValue object, or null if the value is trivial or invalid.
 */
function parseSadsAttributeString(
  sadsPropertyKey: string,
  rawValue: string
): SadsAttributeValue | null {
  // Assuming SadsAttributeValue is a class generated by protoc-gen-ts
  // For ts-protoc-gen, it might be an interface, and you'd create a plain object.
  // Let's assume it's an interface for this example:
  let attributeValue: SadsAttributeValue = {};

  if (rawValue.startsWith("custom:")) {
    attributeValue.customValue = rawValue.substring("custom:".length);
    return attributeValue;
  }

  // Simplified mapping based on property key.
  // A more robust solution would use a comprehensive schema or map.
  switch (sadsPropertyKey.toLowerCase()) {
    case "padding":
    case "margin":
    case "gap":
      const spacingTokenKey = `SPACING_TOKEN_${rawValue.toUpperCase()}` as keyof typeof SadsSpacingToken;
      if (SadsSpacingToken[spacingTokenKey] !== undefined) {
        attributeValue.spacingToken = SadsSpacingToken[spacingTokenKey];
      } else {
        attributeValue.customValue = rawValue; // Fallback
      }
      break;
    case "bgcolor":
    case "textcolor":
    case "bordercolor":
      const colorTokenKey = `COLOR_TOKEN_${rawValue.toUpperCase()}` as keyof typeof SadsColorToken;
      if (SadsColorToken[colorTokenKey] !== undefined) {
        attributeValue.colorToken = SadsColorToken[colorTokenKey];
      } else {
        attributeValue.customValue = rawValue;
      }
      break;
    case "fontweight":
      const fontWeightTokenKey = `FONT_WEIGHT_TOKEN_${rawValue.toUpperCase()}` as keyof typeof SadsFontWeightToken;
      if (SadsFontWeightToken[fontWeightTokenKey] !== undefined) {
        attributeValue.fontWeightToken = SadsFontWeightToken[fontWeightTokenKey];
      } else {
        attributeValue.customValue = rawValue;
      }
      break;
    case "borderradius":
      const radiusTokenKey = `BORDER_RADIUS_TOKEN_${rawValue.toUpperCase()}` as keyof typeof SadsBorderRadiusToken;
      if (SadsBorderRadiusToken[radiusTokenKey] !== undefined) {
        attributeValue.borderRadiusToken = SadsBorderRadiusToken[radiusTokenKey];
      } else {
        attributeValue.customValue = rawValue;
      }
      break;
    case "fontsize":
      attributeValue.fontSizeValue = rawValue; // Directly a string
      break;
    default:
      // For properties like "textAlign", "display", "position", etc.
      attributeValue.customValue = rawValue;
      break;
  }
  // Check if any field in oneof was set
  if (Object.keys(attributeValue).length === 0) return null;
  return attributeValue;
}
```

**b. Transforming `el.dataset` (DOMStringMap) into a `SadsStylingSet`:**

This function would iterate over an element's `dataset` and compile all `data-sads-*` attributes into a structured `SadsStylingSet`.

```typescript
// Conceptual TypeScript in sads-style-engine.ts
// import { SadsStylingSet, SadsAttributeValue } from '...';

function extractBaseStylesFromDataset(
  dataset: DOMStringMap
): SadsStylingSet {
  // Assuming SadsStylingSet is an interface:
  const stylingSet: SadsStylingSet = { attributes: {} };

  for (const key in dataset) {
    if (
      key.startsWith("sads") &&
      key.toLowerCase() !== "sadsresponsiverules" &&
      key.toLowerCase() !== "sadscomponent" &&
      key.toLowerCase() !== "sadselement"
    ) {
      const sadsPropertyKey = key.substring("sads".length);
      const normalizedSadsKey = sadsPropertyKey.charAt(0).toLowerCase() + sadsPropertyKey.slice(1);

      const rawValue = dataset[key];
      if (rawValue !== undefined) {
        const parsedValue = parseSadsAttributeString(normalizedSadsKey, rawValue);
        if (parsedValue) {
          if (!stylingSet.attributes) { // Should be initialized by type if it's a map
             stylingSet.attributes = {};
          }
          stylingSet.attributes[normalizedSadsKey] = parsedValue;
        }
      }
    }
  }
  return stylingSet;
}
```

**c. Typing the return value of `_parseResponsiveRules` (JS fallback part):**

This illustrates how the JavaScript fallback logic within `_parseResponsiveRules` could be typed to produce an array of `SadsResponsiveStyle`.

```typescript
// Conceptual TypeScript in sads-style-engine.ts
// import { SadsResponsiveStyle, SadsStylingSet, SadsAttributeValue } from '...';

interface RawResponsiveRuleInput { // Type for the input JSON structure from data-sads-responsive-rules
  breakpoint: string;
  styles: { [sadsPropertyKey: string]: string }; // e.g. { "padding": "m", "bgColor": "primary" }
}

function parseResponsiveRulesTS(
  rulesString: string | undefined
): SadsResponsiveStyle[] {
  if (!rulesString) return [];

  const result: SadsResponsiveStyle[] = [];

  try {
    const rawParsedRules: RawResponsiveRuleInput[] = JSON.parse(rulesString);

    rawParsedRules.forEach((rawRule) => {
      // Assuming SadsResponsiveStyle and SadsStylingSet are interfaces
      const responsiveStyle: SadsResponsiveStyle = {
        breakpointKey: rawRule.breakpoint,
        styles: { attributes: {} } // Initialize SadsStylingSet with attributes map
      };

      const stylingSetForRule = responsiveStyle.styles!; // Assert styles is defined

      for (const sadsKey in rawRule.styles) {
        const rawValue = rawRule.styles[sadsKey];
        // Normalize sadsKey from data attribute if necessary (e.g. "bgColor" -> "bgColor")
        // Here, assume sadsKey from JSON is already the desired SADS property key.
        const parsedValue = parseSadsAttributeString(sadsKey, rawValue);
        if (parsedValue) {
          if (!stylingSetForRule.attributes) { // Should be initialized
             stylingSetForRule.attributes = {};
          }
          stylingSetForRule.attributes[sadsKey] = parsedValue;
        }
      }
      result.push(responsiveStyle);
    });

  } catch (e) {
    console.error(
      `SADS TS: Error parsing responsive rules: "${rulesString}"`, e
    );
  }
  return result;
}
```
**Note on Protobuf Generated Types:** The exact way to instantiate and set fields (e.g., `new SadsAttributeValue()` vs. `{}`, `setValue()` vs. direct assignment) will depend on the specific `protoc-gen-ts` plugin used and its options. The snippets above use a mix to illustrate, assuming either class-based or interface-based generation.

These examples provide a concrete starting point for how the SADS engine refactor can leverage the new Protobuf-generated TypeScript types for improved code quality and maintainability.


## 4. Future Considerations (High-Level Roadmap)

Once the TypeScript types are integrated and providing value in the SADS engine's TS refactor, the following areas will be explored for deeper Protobuf integration. These will be planned in more detail in subsequent phases.

-   **SADS Theme Representation:**
    -   Investigate defining parts or all of the SADS theme (e.g., color palettes, spacing scales from `sads-default-theme.js`) using structures derived from `sads_styling.v1.proto`.
    -   This could involve loading the theme from a JSON or binary file that conforms to a Protobuf schema.
-   **SADS Engine Core Logic Refactor:**
    -   Beyond just using TS types, refactor the core processing logic of the SADS engine to natively operate on instances of `SadsElementStyles` and related messages. This could simplify how styles are applied and managed.
-   **Go/WASM Function Adaptation:**
    -   Refactor existing Go/WASM functions (`resolveSadsValue`, `parseResponsiveRules`) and design new ones to accept arguments based on these Protobuf structures.
    -   Explore using binary Protobuf serialization for data transfer between JavaScript/TypeScript and Go/WASM for potentially better performance and type safety compared to multiple JSON strings.
    -   The `ResolveSadsStylesRequest` and `ResolveSadsStylesResponse` messages in `sads_styling.v1.proto` are placeholders for this line of thinking.
-   **Alternative Style Configuration Methods:**
    -   Evaluate if these Protobuf structures can enable defining SADS styles via a JavaScript API or a structured configuration file, as an alternative or supplement to HTML `data-sads-*` attributes.
-   **Tooling and Validation:**
    -   Develop tools or scripts to validate SADS style configurations (whether from HTML attributes or other sources) against the Protobuf schema.

This phased approach will allow for incremental adoption of the Protobuf-defined structures, starting with the immediate benefits for the TypeScript refactor and gradually exploring deeper integration for enhanced robustness and potential performance gains.
