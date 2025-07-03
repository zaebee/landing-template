# Styling Approach for Landing Page Generator

This document outlines the hybrid styling strategy used in this project, combining traditional CSS components with an experimental Semantic Attribute-Driven Styling (SADS) system.

## Overview

The project employs two main styling methods:

1. **Traditional CSS Components:** Used for global shell components like the Header and Footer.
2. **Semantic Attribute-Driven Styling (SADS):** An experimental system used for the main content blocks (Features, Testimonials, Blog, Contact Form).

All final CSS (from traditional components and SADS-generated styles) is effectively applied to the page, with SADS styles being injected dynamically. The primary CSS bundle linked in the HTML is `public/dist/main.css`, which includes traditional component CSS. SADS injects its styles into a `<style id="sads-dynamic-styles"></style>` tag in the document head.

## 1. Traditional CSS Components (Header, Footer)

* **Structure:**
  * HTML Templates: Located in `templates/components/header/header.html` and `templates/components/footer/footer.html`.
  * CSS Stylesheets: Corresponding CSS files are `templates/components/header/header.css` and `templates/components/footer/footer.css`.
* **Styling:** These components are styled using standard CSS rules within their dedicated files. Class names may follow conventions like BEM, or be directly scoped.
* **Bundling:** The CSS from these component files is bundled into `public/dist/main.css` by the build process.
* **Modification:** To change the style of the Header or Footer, edit their respective `.css` files.

## 2. Semantic Attribute-Driven Styling (SADS) (Experimental)

SADS is used for the main content blocks: Features, Testimonials, Blog, and Contact Form.

* **Concept:** Instead of relying on external CSS classes, styling intent is declared directly on HTML elements using `data-sads-*` attributes.
* **HTML Templates:** Located in `templates/components/<component_name>/<component_name>.html` (e.g., `templates/components/features/features.html`).
* **SADS Engine:**
  * The core logic resides in `public/js/sads-style-engine.js`.
  * This JavaScript engine runs on page load (`DOMContentLoaded` via `public/js/app.js`).
  * It scans the DOM for elements with `data-sads-component` and their children with `data-sads-*` attributes.
  * It parses these attributes, interprets their semantic meaning (e.g., `padding="m"`, `bg-color="surface"`), and translates them into actual CSS rules.
  * These CSS rules are then injected dynamically into a `<style id="sads-dynamic-styles"></style>` tag in the document's `<head>`.
* **Theming:**
  * The SADS engine contains an internal theme configuration object (within `sads-style-engine.js`).
  * This theme defines mappings for semantic values like:
    * Colors: `surface`, `surface-accent`, `text-primary`, `text-accent`, etc. Basic dark mode is supported by looking for a corresponding key with a `-dark` suffix (e.g., `surface-dark`).
    * Spacing: `xs`, `s`, `m`, `l`, `xl`, `xxl` for padding, margins, gaps.
    * Font Sizes: `s`, `m`, `l`, `xl`, etc.
    * Other scales like `borderRadius`, `shadow`, `flexBasis`.
  * The engine uses these theme values to convert semantic SADS attributes into concrete CSS.
* **Key SADS Attribute Patterns:**
  * `data-sads-component="<component-name>"`: Identifies the root element of a SADS-styled component.
  * `data-sads-element="<element-name>"`: Identifies a distinct part within a SADS component.
  * Styling attributes, e.g.:
    * `data-sads-padding="m"`
    * `data-sads-bg-color="surface"`
    * `data-sads-font-size="xl"`
    * `data-sads-text-align="center"`
    * `data-sads-display="flex"` (preferred over abstract `data-sads-layout-type` for clarity)
    * `data-sads-flex-direction="column"`
    * `data-sads-border-color="input-border-color"`
  * `data-sads-responsive-rules='[{"breakpoint": "mobile", "styles": {"padding": "s", "flexDirection": "row"}}]'`: Defines style overrides for specific breakpoints (defined in the engine's theme).
  * `custom:<value>`: For some attributes, allows passing direct CSS values, e.g., `data-sads-width="custom:100%"`, `data-sads-margin="custom:0 auto"`.
* **Modifying SADS Component Styles:**
  * To change existing styles: Modify the `data-sads-*` attributes directly in the component's HTML template.
    * For example, if an element used `data-sads-layout-type="flex"`, it's clearer to use `data-sads-display="flex"` along with other flex properties like `data-sads-flex-direction`, `data-sads-flex-wrap`, etc. The `layout-type` attribute itself does not directly map to a CSS property in the current engine version and is processed to determine behavior, but explicit CSS property mappings are generally preferred for SADS attributes.
  * To use new semantic values (e.g., a new color `brand-primary` or spacing size `xxxs`): Update the theme configuration object within `sads-style-engine.js`.
  * To support new CSS properties: Update the `_mapSadsPropertyToCss` and potentially `_mapSemanticValueToActual` methods in `sads-style-engine.js`.

### Known SADS MVP Limitations (Important)

As SADS is experimental in this project, the current Minimum Viable Product (MVP) engine has several limitations:

* **No State Styling from SADS:** Pseudo-classes like `:hover`, `:focus`, `:active`, `:disabled` are not styled by the SADS engine. These will rely on browser defaults or potentially global CSS if any applies. This is most noticeable on links and form elements.
* **No Pseudo-element Styling:** `::before`, `::after` cannot be styled using SADS attributes.
* **Limited Dark Mode Theming:** Dark mode primarily affects colors defined with a `-dark` suffix in the theme. Non-color properties (e.g., `box-shadow` intensity/color) do not automatically adapt to dark mode unless explicitly handled with separate semantic values or more complex engine logic (e.g., defining `shadow-subtle-dark` in the theme and using that, which is not current practice).
* **No Complex CSS Selectors:** SADS applies styles directly to elements based on their attributes. It does not support descendant, child, sibling, or other complex CSS selector logic. This includes most pseudo-classes like `:last-child`, `:nth-child()`, etc. For such cases, alternative solutions like adding specific SADS attributes via JavaScript to target elements or using minimal global CSS overrides are necessary.
* **Transitions/Animations:** While a `data-sads-transition="custom:..."` attribute can apply a transition property, triggering transitions based on SADS-unaware state changes (like JS-added classes for non-SADS states) is not inherently supported.

## Global Styles

* A minimal set of global styles remains in `public/style.css`. This typically includes base HTML element styling (e.g., `html`, `body`) and very generic utility classes if any were defined (currently none explicitly).
* The SADS engine relies on `body.classList.contains('dark-mode')` for its dark mode color logic. This class is toggled by `public/js/app.js`.

Understanding this hybrid approach and the SADS system's current capabilities/limitations is key to developing and maintaining the site's appearance.
