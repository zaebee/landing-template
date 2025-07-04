// Default Theme Configuration for SADS (Semantic Attribute-Driven Styling) Engine

const sadsDefaultTheme = {
  colors: {
    surface: "#FFFFFF",
    "surface-dark": "#22272e", // Darker, more modern dark surface
    "surface-accent": "#f8f9fa", // Slightly off-white for light accents
    "surface-accent-dark": "#2d333b", // Slightly lighter dark for accents

    "text-primary": "#212529", // Darker primary text for light mode
    "text-primary-dark": "#c9d1d9", // Lighter primary text for dark mode
    "text-secondary": "#6c757d", // Softer secondary text
    "text-secondary-dark": "#8b949e",

    "text-accent": "#0056b3", // Main accent/action color (deeper blue)
    "text-accent-dark": "#58a6ff", // Lighter blue for dark mode accent

    transparent: "transparent",

    // border-accent will be aliased to text-accent in the engine after load

    // Generic UI element colors
    "ui-border": "#ced4da",
    "ui-border-dark": "#484f58",
    "ui-hover-bg": "rgba(0, 86, 179, 0.1)", // Accent color with alpha for hover
    "ui-hover-bg-dark": "rgba(88, 166, 255, 0.15)",

    // Form specific (can alias to more generic if needed, or be used directly)
    "form-input-border": "#ced4da",
    "form-input-border-dark": "#484f58", // Using ui-border-dark
    "form-input-bg": "#ffffff", // surface
    "form-input-bg-dark": "#2d333b", // surface-accent-dark
    "form-input-text": "#212529", // text-primary
    "form-input-text-dark": "#c9d1d9", // text-primary-dark
    "form-label-text": "#495057",
    "form-label-text-dark": "#adb5bd",

    // Button specific (can alias or use generic action colors)
    "button-primary-bg": "#0056b3", // text-accent
    "button-primary-bg-dark": "#58a6ff", // text-accent-dark
    "button-primary-text": "#ffffff",
    "button-primary-text-dark": "#22272e", // Dark text on light blue button for dark mode

    // Status colors
    "success-bg": "#d1e7dd", // Softer green
    "success-bg-dark": "#0f5132", // Darker container for success in dark
    "success-text": "#0a3622",
    "success-text-dark": "#75b798", // Lighter green text for dark
    "success-border": "#a3cfbb",
    "success-border-dark": "#198754",

    "error-bg": "#f8d7da",
    "error-bg-dark": "#842029", // Darker container for error in dark
    "error-text": "#58151c",
    "error-text-dark": "#ea868f", // Lighter red text for dark
    "error-border": "#f1aeb5",
    "error-border-dark": "#dc3545",

    // Old specific colors (to be phased out or reviewed)
    "blog-section-bg": "#e9ecef", // Consider aliasing to surface-accent or a generic section bg
    "blog-section-bg-dark": "#22272e", // surface-dark
    "blog-item-bg": "#ffffff", // surface
    "blog-item-bg-dark": "#2d333b", // surface-accent-dark
    "contact-section-bg": "#f8f9fa", // surface-accent (new)
    "contact-section-bg-dark": "#22272e", // surface-dark (new)
    "contact-form-inner-bg": "#ffffff", // surface
    "contact-form-inner-bg-dark": "#2d333b", // surface-accent-dark

    // Original SADS contact form colors - will be replaced by new form-* or button-* colors
    // "contact-input-border": "#cccccc", // now form-input-border
    // "contact-input-border-dark": "#555555", // now form-input-border-dark
    // "contact-input-bg": "#ffffff", // now form-input-bg
    // "contact-input-bg-dark": "#333333", // now form-input-bg-dark
    // "contact-label-text": "#333333", // now form-label-text
    // "contact-label-text-dark": "#e0e0e0", // now form-label-text-dark
    // "contact-submit-bg": "#28a745", // now button-primary-bg (themed blue)
    // "contact-submit-bg-dark": "#1a73e8", // now button-primary-bg-dark
    // "contact-submit-text": "#ffffff", // now button-primary-text
    // "contact-submit-text-dark": "#ffffff", // now button-primary-text-dark
  },
  spacing: {
    none: "0",
    xxs: "0.125rem", // ~2px
    xs: "0.25rem", // ~4px
    s: "0.5rem", // ~8px
    "s-m": "0.75rem", // ~12px (good for input padding)
    m: "1rem", // ~16px
    l: "1.5rem", // ~24px
    xl: "2rem", // ~32px
    xxl: "3rem", // ~48px (reduced from 4rem for tighter big spacing)
    auto: "auto",
    // "input": "0.75rem", // Replaced by s-m
  },
  fontSize: {
    default: "1rem",
    s: "0.875rem", // Slightly smaller for small text
    m: "1rem", // Base
    l: "1.25rem", // Large
    xl: "1.75rem", // Extra Large
    xxl: "2.25rem", // Extra Extra Large
  },
  fontWeight: {
    light: "300",
    normal: "400",
    medium: "500",
    semibold: "600",
    bold: "700",
  },
  borderRadius: {
    none: "0",
    s: "2px", // Smaller, subtle radius
    m: "4px", // Default (was s)
    l: "6px", // Good for inputs/buttons (new)
    xl: "8px", // Larger (was m)
    xxl: "12px", // Even larger (new)
    round: "9999px", // Pill shape
  },
  shadow: {
    none: "none",
    // Focus ring variables (color part comes from theme, e.g., text-accent)
    "focus-ring-color": "rgba(0, 86, 179, 0.25)", // Based on new text-accent
    "focus-ring-color-dark": "rgba(88, 166, 255, 0.35)", // Based on new text-accent-dark

    soft: "0 1px 2px 0 rgba(0,0,0,0.05)",
    subtle: "0 2px 4px -1px rgba(0,0,0,0.06), 0 1px 2px -1px rgba(0,0,0,0.05)",
    medium: "0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)",
    strong: "0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05)",
    // Specific shadows for contact form (can be aliased)
    "contact-form-shadow": "0 4px 8px rgba(0,0,0,0.08)",
    "contact-form-shadow-dark": "0 4px 8px rgba(0,0,0,0.25)",
  },
  maxWidth: {
    "content-container-narrow": "800px",
    "content-container": "1100px",
    full: "100%",
  },
  breakpoints: {
    mobile: "(max-width: 767px)",
    tablet: "(min-width: 768px) and (max-width: 1023px)",
    desktop: "(min-width: 1024px)",
  },
  flexBasis: {
    auto: "auto",
    full: "100%",
    "third-gap-m": "calc(33.333% - 1rem)", // Example
  },
  objectFit: {
    cover: "cover",
    contain: "contain",
    fill: "fill",
    "scale-down": "scale-down",
    none: "none",
  },
  fontStyle: { normal: "normal", italic: "italic", oblique: "oblique" },
  borderStyle: {
    none: "none",
    solid: "solid",
    dashed: "dashed",
    dotted: "dotted",
  },
};

// This check is to ensure it can be imported in a Node.js environment (if needed for testing/bundling)
// or used directly in a browser if sads-default-theme.js is loaded before sads-style-engine.js
if (typeof module !== "undefined" && module.exports) {
  module.exports = sadsDefaultTheme;
}
// If not in a Node.js environment, it will be available globally as sadsDefaultTheme
// when <script src="sads-default-theme.js"></script> is used.
// Alternatively, sads-style-engine.js could dynamically load it or expect it to be global.
// For simplicity with current setup, assuming it might be global or imported by a bundler.
// No explicit 'export default' for broadest compatibility without assuming ES modules for all users.
