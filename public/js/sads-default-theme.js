// Default Theme Configuration for SADS (Semantic Attribute-Driven Styling) Engine

const sadsDefaultTheme = {
  colors: {
    surface: "#FFFFFF",
    "surface-dark": "#2a2a2a",
    "surface-accent": "#f9f9f9",
    "surface-accent-dark": "#1f1f1f",
    "text-primary": "#333333",
    "text-primary-dark": "#e0e0e0",
    "text-accent": "#007bff",
    "text-accent-dark": "#0af",
    transparent: "transparent",
    "text-secondary": "#555555",
    "text-secondary-dark": "#bbbbbb",
    // border-accent will be aliased to text-accent in the engine after load
    "blog-section-bg": "#e9ecef",
    "blog-section-bg-dark": "#2a2a2a",
    "blog-item-bg": "#ffffff",
    "blog-item-bg-dark": "#1f1f1f",
    "contact-section-bg": "#e9ecef",
    "contact-section-bg-dark": "#2a2a2a",
    "contact-form-bg": "#ffffff",
    "contact-form-bg-dark": "#1f1f1f",
    "input-border-color": "#cccccc",
    "input-border-color-dark": "#555555",
    "input-bg-color": "#ffffff",
    "input-bg-color-dark": "#333333",
    "button-primary-bg-color": "#28a745",
    "button-primary-bg-color-dark": "#1a73e8",
    "button-primary-text-color": "#ffffff",

    // Logo specific colors
    logoIconPrimary: "#4F46E5", // Indigo-700
    "logoIconPrimary-dark": "#6366F1", // Indigo-500 (lighter for dark bg)
    logoIconAccent1: "#6366F1", // Indigo-500
    "logoIconAccent1-dark": "#818CF8", // Indigo-400 (lighter for dark bg)
    logoIconAccent2: "#818CF8", // Indigo-400
    "logoIconAccent2-dark": "#A5B4FC", // Indigo-300 (lighter for dark bg)
    logoIconArrow: "#FFFFFF", // White
    "logoIconArrow-dark": "#E0E7FF", // Indigo-100 (slightly off-white for dark bg)
    logoTextColor: "#1F2937", // Gray-800
    "logoTextColor-dark": "#D1D5DB", // Gray-300
  },
  spacing: {
    none: "0",
    xs: "0.25rem",
    s: "0.5rem",
    m: "1rem",
    l: "1.5rem",
    xl: "2rem",
    xxl: "4rem",
    auto: "auto",
    input: "0.75rem",
  },
  fontSize: {
    default: "1rem",
    s: "0.9rem",
    m: "1rem",
    l: "1.5rem",
    xl: "2rem",
    xxl: "2.5rem",
  },
  fontWeight: { normal: "400", bold: "700" },
  borderRadius: { none: "0", s: "4px", m: "8px", l: "16px" },
  shadow: {
    none: "none",
    subtle: "0 2px 5px rgba(0,0,0,0.1)",
    medium: "0 4px 10px rgba(0,0,0,0.15)",
  },
  maxWidth: {
    "content-container-narrow": "800px",
    "content-container": "1100px",
    full: "100%",
  },
  breakpoints: {
    mobile: "(max-width: 767px)", // Adjusted to not overlap with tablet
    tablet: "(min-width: 768px) and (max-width: 1023px)",
    desktop: "(min-width: 1024px)",
  },
  flexBasis: {
    auto: "auto",
    full: "100%",
    "third-gap-m": "calc(33.333% - 1rem)",
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
