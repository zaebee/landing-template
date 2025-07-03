# Styling Approach for Landing Page Generator

This document outlines the hybrid styling strategy used in this project, combining traditional CSS components with an experimental Semantic Attribute-Driven Styling (SADS) system. The "AI" in "SADS AI experimental" is currently an aspirational term reflecting the goal of a more intelligent styling system; the existing engine is rule-based.

## Overview

The project employs two main styling methods:

1.  **Traditional CSS Components:** Used for global shell components like the Header and Footer.
2.  **Semantic Attribute-Driven Styling (SADS):** An experimental, JavaScript-driven system used for the main content blocks (e.g., Features, Testimonials, Blog, Contact Form).

All final CSS (from traditional components and SADS-generated styles) is effectively applied to the page. Traditional CSS is bundled into `public/dist/main.css`. SADS dynamically injects its styles into a `<style id="sads-dynamic-styles"></style>` tag in the document head.

## 1. Traditional CSS Components (Header, Footer)

- **Structure:**
  - HTML Templates: Located in `templates/components/header/header.html` and `templates/components/footer/footer.html`.
  - CSS Stylesheets: Corresponding CSS files are `templates/components/header/header.css` and `templates/components/footer/footer.css`.
- **Styling:** These components are styled using standard CSS rules within their dedicated files.
- **Bundling:** The CSS from these component files is bundled into `public/dist/main.css` by the build process (see `build.py` and `AssetBundler`).
- **Modification:** To change the style of the Header or Footer, edit their respective `.css` files and rebuild using `npm run build`.

## 2. Semantic Attribute-Driven Styling (SADS) (Experimental)

SADS is used for the main content blocks like Features, Testimonials, Blog, and Contact Form.

- **Concept:** Styling intent is declared directly on HTML elements using `data-sads-*` attributes, which are then processed by a JavaScript engine to generate CSS rules.
- **HTML Templates:** Located in `templates/components/<component_name>/<component_name>.html` (e.g., `templates/components/features/features.html`).
- **SADS Engine (`public/js/sads-style-engine.js`):**
  - **Initialization**: Runs on page load (`DOMContentLoaded` via `public/js/app.js`).
  - **Element Targeting**:
    - The engine is triggered by `data-sads-component` attributes on root elements of a component.
    - It then processes styling for the component root and any descendant elements that also have `data-sads-*` attributes.
    - The `data-sads-element` attribute is used for semantic clarity within the HTML to denote distinct parts of a component but does not fundamentally change how styles are applied beyond being another element with `data-sads-*` attributes.
    - The engine assigns a unique class (e.g., `sads-id-0`, `sads-id-1`) to each styled element to target it with the generated CSS rules.
  - **Rule Generation**: Parses `data-sads-*` attributes, interprets their semantic meaning (e.g., `padding="m"`, `bg-color="surface"`), and translates them into actual CSS rules using a predefined theme.
  - **Style Injection**: Injects generated CSS rules dynamically into a `<style id="sads-dynamic-styles"></style>` tag in the document's `<head>`.
- **Theming:**
  - The SADS engine uses a theme configuration object (defined in `sads-default-theme.js` and potentially customized in `sads-style-engine.js` or `app.js`).
  - This theme maps semantic tokens to concrete CSS values:
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
  - **New Semantic Values**: To add a new color like `brand-highlight` or a spacing size `xxxs`, update the theme configuration object (e.g., in `sads-default-theme.js` or the engine's initialization).
  - **New CSS Properties**: To make SADS aware of a new CSS property, update the `_mapSadsPropertyToCss` method (and potentially `_mapSemanticValueToActual` if it needs special theme mapping) in `public/js/sads-style-engine.js`.

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
- The SADS engine's dark mode logic relies on `document.body.classList.contains('dark-mode')`. This class is toggled by `public/js/app.js`, which also initializes the SADS engine.

Understanding this hybrid approach and the SADS system's current capabilities and limitations is crucial for effectively developing and maintaining the site's appearance. Remember to run `npm run build` after any style-related changes to regenerate outputs and see updates.
