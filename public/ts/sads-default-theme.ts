// TypeScript type definitions for SADS Default Theme

export interface SadsColors {
  surface: string;
  "surface-dark": string;
  "surface-accent": string;
  "surface-accent-dark": string;
  "text-primary": string;
  "text-primary-dark": string;
  "text-accent": string;
  "text-accent-dark": string;
  transparent: string;
  "text-secondary": string;
  "text-secondary-dark": string;
  "header-bg": string;
  "header-bg-dark": string;
  "text-on-header-bg": string;
  "text-on-header-bg-dark": string;
  "text-nav-link": string;
  "text-nav-link-dark": string;
  "border-accent"?: string; // Optional as it's aliased
  "border-accent-dark"?: string; // Optional as it's aliased
  "blog-section-bg": string;
  "blog-section-bg-dark": string;
  "blog-item-bg": string;
  "blog-item-bg-dark": string;
  "contact-section-bg": string;
  "contact-section-bg-dark": string;
  "contact-form-bg": string;
  "contact-form-bg-dark": string;
  "input-border-color": string;
  "input-border-color-dark": string;
  "input-bg-color": string;
  "input-bg-color-dark": string;
  "button-primary-bg-color": string;
  "button-primary-bg-color-dark": string;
  "button-primary-text-color": string;
  [key: string]: string | undefined; // Allow other string properties
}

export interface SadsSpacing {
  none: string;
  xs: string;
  s: string;
  m: string;
  l: string;
  xl: string;
  xxl: string;
  auto: string;
  input: string;
  [key: string]: string; // Allow other string properties
}

export interface SadsFontSizes {
  default: string;
  s: string;
  m: string;
  l: string;
  xl: string;
  xxl: string;
  [key: string]: string; // Allow other string properties
}

export interface SadsFontWeights {
  normal: string;
  bold: string;
  [key: string]: string; // Allow other string properties
}

export interface SadsBorderRadius {
  none: string;
  s: string;
  m: string;
  l: string;
  [key: string]: string; // Allow other string properties
}

export interface SadsShadows {
  none: string;
  subtle: string;
  medium: string;
  [key: string]: string; // Allow other string properties
}

export interface SadsMaxWidth {
  "content-container-narrow": string;
  "content-container": string;
  full: string;
  [key: string]: string; // Allow other string properties
}

export interface SadsBreakpoints {
  mobile: string;
  tablet: string;
  desktop: string;
  [key: string]: string; // Allow other string properties
}

export interface SadsFlexBasis {
  auto: string;
  full: string;
  "third-gap-m": string; // Example: "calc(33.333% - 1rem)"
  [key: string]: string; // Allow other string properties
}

export interface SadsObjectFit {
  cover: string;
  contain: string;
  fill: string;
  "scale-down": string;
  none: string;
  [key: string]: string; // Allow other string properties
}

export interface SadsFontStyle {
  normal: string;
  italic: string;
  oblique: string;
  [key: string]: string; // Allow other string properties
}

export interface SadsBorderStyle {
  none: string;
  solid: string;
  dashed: string;
  dotted: string;
  [key: string]: string; // Allow other string properties
}

export interface SadsTheme {
  colors: SadsColors;
  spacing: SadsSpacing;
  fontSize: SadsFontSizes;
  fontWeight: SadsFontWeights;
  borderRadius: SadsBorderRadius;
  shadow: SadsShadows;
  maxWidth: SadsMaxWidth;
  breakpoints: SadsBreakpoints;
  flexBasis: SadsFlexBasis;
  objectFit: SadsObjectFit;
  fontStyle: SadsFontStyle;
  borderStyle: SadsBorderStyle;
  [key: string]: any; // For extensibility if new top-level categories are added
}

// Actual SADS Default Theme Configuration with TypeScript types

export const sadsDefaultTheme: SadsTheme = {
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
// If this needs to be available globally in a non-module browser context,
// the build process or a separate script would handle that.
// For example, after compilation: window.sadsDefaultTheme = YourCompiledModule.sadsDefaultTheme;
