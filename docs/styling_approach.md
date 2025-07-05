# Styling Approach for Landing Page Generator

This document outlines the hybrid styling strategy used in this project, combining traditional CSS components with an experimental Semantic Attribute-Driven Styling (SADS) system. The "AI" in "SADS AI experimental" is currently an aspirational term reflecting the goal of a more intelligent styling system; the existing engine is rule-based.

## Overview

The project (in its current experimental SADS-for-all setup) primarily uses an experimental styling system called Semantic Attribute-Driven Styling (SADS) for all components, including Header, Footer, and the main content blocks. The "AI" in "SADS AI experimental" is currently an aspirational term reflecting the goal of a more intelligent styling system; the existing engine is rule-based.

SADS dynamically injects its styles into a `<style id="sads-dynamic-styles"></style>` tag in the document head. Any traditional CSS (e.g. from `public/style.css` or potentially component-specific CSS files if they were to be reintroduced) would also be applied.

## Semantic Attribute-Driven Styling (SADS) (Experimental)

SADS is used for all components including Header, Footer, Features, Testimonials, Blog, and Contact Form in this experimental configuration.

- **Concept:** Styling intent is declared directly on HTML elements using `data-sads-*` attributes, which are then processed by a TypeScript/JavaScript engine to generate CSS rules. The SADS engine and theme configuration have been refactored to TypeScript for improved type safety and maintainability.
- **HTML Templates:** Located in `templates/components/<component_name>/<component_name>.html` (e.g., `templates/components/features/features.html`).
- **SADS Engine (Source: `public/ts/sads-style-engine.ts`):**
  - Compiled to JavaScript (e.g., to `public/js/compiled_ts/sads-style-engine.js`) and bundled into `public/dist/main.js`.
  - **Initialization**: Runs on page load (`DOMContentLoaded` via `public/js/app.js`, which is part of the `main.js` bundle).
  - **Element Targeting**:
    - The engine is triggered by `data-sads-component` attributes on root elements of a component.
    - It then processes styling for the component root and any descendant elements that also have `data-sads-*` attributes.
    - The `data-sads-element` attribute is used for semantic clarity within the HTML to denote distinct parts of a component but does not fundamentally change how styles are applied beyond being another element with `data-sads-*` attributes.
    - The engine assigns a unique class (e.g., `sads-id-0`, `sads-id-1`) to each styled element to target it with the generated CSS rules.
  - **Rule Generation**: Parses `data-sads-*` attributes, interprets their semantic meaning (e.g., `padding="m"`, `bg-color="surface"`), and translates them into actual CSS rules using a predefined theme.
  - **Style Injection**: Injects generated CSS rules dynamically into a `<style id="sads-dynamic-styles"></style>` tag in the document's `<head>`.
- **Theming (Source: `public/ts/sads-default-theme.ts`):**
  - The SADS engine uses a theme configuration object (defined in `public/ts/sads-default-theme.ts`, compiled, and bundled). This theme can be customized during the engine's instantiation.
  - This theme maps semantic tokens (e.g., "m" for spacing, "surface" for color) to concrete CSS values.
  - **Schema for SADS Attributes and Tokens:** The underlying semantic tokens (like spacing scales, color names) and attribute structures are being defined using Protocol Buffers (`proto/sads_attributes.proto`). This provides a schema and enables generation of TypeScript types for these tokens, aiming for more robust validation and engine logic in the future.
  - **Theme Categories:**
    - **Colors**: `surface`, `surface-accent`, `text-primary`, `text-accent`, etc. Dark mode is supported by looking for a corresponding key with a `-dark` suffix (e.g., `surface-dark`) when `document.body.classList.contains('dark-mode')`.
    - **Spacing**: `xs`, `s`, `m`, `l`, `xl`, `xxl` for properties like `padding`, `margin`, `gap`.
    - **Font Sizes**: `s`, `m`, `l`, `xl`, etc.
    - **Other Scales**: `borderRadius`, `shadow`, `flexBasis`, `maxWidth`, etc.
- **Key SADS Attribute Patterns:**
  - `data-sads-component="<component-name>"`: Identifies the root element of a SADS-styled component, initiating SADS processing for itself and its children.
  - `data-sads-element="<element-name>"`: Semantically identifies a distinct part within a SADS component. Useful for organization and readability of the HTML.
  - **Styling Attributes**:
    - Examples: `data-sads-padding="m"`, `data-sads-bg-color="surface"`, `data-sads-font-size="xl"`, `data-sads-text-align="center"`.
    - For layout, prefer explicit properties: `data-sads-display="flex"`, `data-sads-flex-direction="column"`, `data-sads-gap="m"`. (The old `data-sads-layout-type` is not a direct CSS mapping).
  - `data-sads-responsive-rules='[{"breakpoint": "mobile", "styles": {"padding": "s", "flexDirection": "column"}}]'`: Defines style overrides for specific breakpoints. Breakpoints (e.g., "mobile") are defined in the SADS theme and map to media queries (e.g., `(max-width: 768px)`).
  - `custom:<value>`: Allows direct CSS values for a SADS property, bypassing theme lookups. Example: `data-sads-width="custom:100%"`, `data-sads-margin="custom:0 auto"`.
- **Modifying SADS Component Styles:**
  - **Existing Styles**: Change `data-sads-*` attributes directly in the component's HTML template (`templates/components/<block_name>/<block_name>.html`).
  - **New Semantic Values**: To add a new color like `brand-highlight` or a spacing size `xxxs`, update the theme configuration object (source: `public/ts/sads-default-theme.ts`). If these tokens are part of the Protobuf schema (e.g., `SadsColorToken` in `proto/sads_attributes.proto`), consider updating the enum there as well for consistency.
  - **New CSS Properties**: To make SADS aware of a new CSS property, update the `_mapSadsPropertyToCss` method (and potentially `_mapSemanticValueToActual` if it needs special theme mapping) in the SADS engine source (`public/ts/sads-style-engine.ts`).

### Known SADS MVP Limitations (Important)

The current "Minimum Viable Product" (MVP) SADS engine has several limitations:

- **No State Styling (Pseudo-classes):** `:hover`, `:focus`, `:active`, `:disabled`, etc., cannot be styled directly by SADS attributes. These states will rely on browser defaults or require traditional CSS (global or component-specific if the component isn't fully SADS-styled). This is particularly noticeable for interactive elements like links and form inputs.
- **No Pseudo-element Styling:** `::before`, `::after` cannot be styled using SADS attributes.
- **Limited Dark Mode Theming:** Dark mode primarily swaps color values based on theme keys ending in `-dark`. Non-color properties (e.g., `box-shadow` intensity/color changes for dark mode) are not automatically adapted unless explicitly defined with separate semantic tokens in the theme and applied via attributes.
- **No Complex CSS Selectors:** SADS applies styles directly to elements based on their attributes. It does not support descendant, child, sibling selectors, or most pseudo-classes like `:last-child`, `:nth-child()`. For such cases, workarounds include:
  - Applying specific SADS attributes via JavaScript to target elements.
  - Using minimal global CSS overrides.
- **Transitions/Animations:** While a `data-sads-transition="custom:..."` attribute can apply a `transition` property, SADS does not inherently manage transition triggers or complex animation sequences tied to state changes it doesn't manage (e.g., JS-added classes).

## Global Styles

- Minimal global styles are present in `public/style.css`. This typically includes base HTML element styling (e.g., for `html`, `body`) and reset/normalize rules.
- The SADS engine's dark mode logic relies on `document.body.classList.contains('dark-mode')`. This class is toggled by `public/js/app.js` (part of the `public/dist/main.js` bundle), which also initializes the SADS engine.

Understanding this hybrid approach and the SADS system's current capabilities and limitations is crucial for effectively developing and maintaining the site's appearance. Remember to run `npm run build` after any style-related changes (including changes to `.ts` SADS files or `.proto` SADS definitions) to regenerate outputs and see updates. This command now includes TypeScript compilation and Protobuf code generation.
