// TypeScript type definitions for SADS Default Theme
// Actual SADS Default Theme Configuration with TypeScript types
export const sadsDefaultTheme = {
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
    "header-bg": "#ffffff",
    "header-bg-dark": "#2c3e50",
    "text-on-header-bg": "#333333",
    "text-on-header-bg-dark": "#ecf0f1",
    "text-nav-link": "#007bff",
    "text-nav-link-dark": "#3498db",
    // "border-accent" will be aliased by the engine from "text-accent"
    // "border-accent-dark" will be aliased by the engine from "text-accent-dark"
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
    mobile: "(max-width: 767px)",
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
// The original JS file had a check for module.exports.
// In TypeScript, the `export const sadsDefaultTheme` handles the module export.
// To make it available globally for simple script inclusion in nl-sads-test.html:
if (typeof window !== "undefined") {
  window.sadsDefaultTheme = sadsDefaultTheme;
  // Optionally, also expose types if needed for global context, though less common for direct script includes
  // (window as any).SadsTheme = {} as SadsTheme; // This is just a type, can't assign like this
}
//# sourceMappingURL=sads-default-theme.js.map
