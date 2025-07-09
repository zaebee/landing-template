// TypeScript type definitions for SADS Default Theme

import {
  SadsColorToken,
  SadsSpacingToken,
  SadsFontWeightToken,
  SadsBorderRadiusToken,
  // Other enums can be imported as needed, e.g., SadsFontSizeToken if we create one
} from "@generated/sads_styling.v1.js"; // Updated path with alias

// The theme will still store CSS string values. The SADS engine would be responsible
// for mapping input tokens (like "m" for spacing or "surface" for color)
// to these theme keys, potentially validating them against the enums.

export interface SadsColors {
  // Keys correspond to SadsColorToken members (e.g., "SURFACE" maps to SadsColorToken.COLOR_TOKEN_SURFACE)
  // or direct string keys for colors not in the enum but in the theme.
  // Values are actual CSS color strings.
  surface: string; // Corresponds to a conceptual COLOR_TOKEN_SURFACE
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
  "nav-link-hover-bg-dark"?: string; // Added for dark theme nav hover
  "nav-link-active-bg-dark"?: string; // Added for dark theme nav active
  "nav-link-active-text-dark"?: string; // Added for dark theme nav active text
  "header-button-hover-bg-dark"?: string; // Added for dark theme header button hover bg
  "header-button-hover-border-dark"?: string; // Added for dark theme header button hover border
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
  // New chat widget colors
  "widget-bg"?: string;
  "widget-bg-dark"?: string;
  "widget-border-color"?: string;
  "widget-border-color-dark"?: string;
  "message-bg-user"?: string;
  "message-bg-user-dark"?: string;
  "message-text-user"?: string;
  "message-text-user-dark"?: string;
  "message-bg-other"?: string;
  "message-bg-other-dark"?: string;
  "message-text-other"?: string;
  "message-text-other-dark"?: string;
  "input-focus-border-color"?: string;
  "input-focus-border-color-dark"?: string;
  "send-button-bg-color"?: string;
  "send-button-bg-color-dark"?: string;
  "send-button-text-color"?: string;
  "send-button-text-color-dark"?: string;
  [key: string]: string | undefined; // Allow other string properties, e.g. "button-primary-bg-color"
}

export interface SadsSpacing {
  // Keys correspond to SadsSpacingToken members (e.g., "XS" maps to SadsSpacingToken.SPACING_TOKEN_XS)
  // Values are actual CSS spacing strings.
  none: string; // Corresponds to SPACING_TOKEN_NONE
  xs: string; // Corresponds to SPACING_TOKEN_XS
  s: string; // Corresponds to SPACING_TOKEN_S
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
  // Keys correspond to SadsFontWeightToken members
  // Values are actual CSS font weight strings.
  normal: string; // Corresponds to FONT_WEIGHT_TOKEN_NORMAL
  bold: string; // Corresponds to FONT_WEIGHT_TOKEN_BOLD
  [key: string]: string;
}

export interface SadsBorderRadius {
  // Keys correspond to SadsBorderRadiusToken members
  // Values are actual CSS border radius strings.
  none: string; // Corresponds to BORDER_RADIUS_TOKEN_NONE
  s: string; // Corresponds to BORDER_RADIUS_TOKEN_S
  m: string; // Corresponds to BORDER_RADIUS_TOKEN_M
  l: string; // Corresponds to BORDER_RADIUS_TOKEN_L
  [key: string]: string;
}

export interface SadsShadows {
  none: string;
  subtle: string;
  medium: string;
  "widget-shadow": string; // Made required
  "widget-shadow-dark": string; // Added and made required
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
    "surface-dark": "#2a2a2a", // Base dark surface
    "surface-accent": "#f9f9f9",
    "surface-accent-dark": "#1f1f1f", // Slightly darker accent for dark
    "text-primary": "#333333",
    "text-primary-dark": "#e0e0e0", // Main text on dark surfaces
    "text-accent": "#007bff",
    "text-accent-dark": "#0af", // Accent text (e.g. links not in nav)
    transparent: "transparent",
    "text-secondary": "#555555",
    "text-secondary-dark": "#bbbbbb", // Secondary text on dark surfaces

    "header-bg": "#ffffff",
    "header-bg-dark": "#2c3e50", // Dark slate/blue for header
    "text-on-header-bg": "#333333",
    "text-on-header-bg-dark": "#ecf0f1", // Light text on dark header

    "text-nav-link": "#007bff",
    "text-nav-link-dark": "#3498db", // Nav link text (soft blue)
    "nav-link-hover-bg-dark": "rgba(255, 255, 255, 0.08)", // Subtle white tint for nav link hover
    "nav-link-active-bg-dark": "#0088cc", // Deeper blue for active nav link background
    "nav-link-active-text-dark": "#ffffff", // White text on active nav link background

    "header-button-hover-bg-dark": "#374a5c", // Harmonized hover for header buttons (dark mode toggle, lang)
    "header-button-hover-border-dark": "#3498db", // Consistent border hover with nav links

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
    "button-primary-bg-color": "#28a745", // Will be overridden for chat's send button
    "button-primary-bg-color-dark": "#1a73e8", // Will be overridden for chat's send button
    "button-primary-text-color": "#ffffff",

    // Chat Widget Specific Colors
    "widget-bg": "#FFFFFF",
    "widget-bg-dark": "#1E1E1E",
    "widget-border-color": "#E0E0E0",
    "widget-border-color-dark": "#3A3A3A",
    "message-bg-user": "#007AFF",
    "message-bg-user-dark": "#0A84FF",
    "message-text-user": "#FFFFFF",
    "message-text-user-dark": "#FFFFFF",
    "message-bg-other": "#F0F0F0",
    "message-bg-other-dark": "#2C2C2E",
    "message-text-other": "#000000",
    "message-text-other-dark": "#E0E0E0",
    "input-focus-border-color": "#007AFF", // For potential future use or direct JS handling
    "input-focus-border-color-dark": "#0A84FF",
    "send-button-bg-color": "#34C759",
    "send-button-bg-color-dark": "#30D158",
    "send-button-text-color": "#FFFFFF",
    "send-button-text-color-dark": "#FFFFFF",
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
  borderRadius: { none: "0", s: "4px", m: "8px", l: "16px" }, // Consider a 'xl' for very rounded later if needed
  shadow: {
    none: "none",
    subtle: "0 2px 5px rgba(0,0,0,0.1)",
    medium: "0 4px 10px rgba(0,0,0,0.15)",
    "widget-shadow": "0 4px 12px rgba(0,0,0,0.08)", // Light mode shadow
    // Dark mode shadow for widget-shadow will be handled by SADS engine if a widget-shadow-dark is defined,
    // or we can define it explicitly here if SADS engine doesn't auto-suffix shadows.
    // For now, assuming SADS engine might not auto-suffix shadows like it does colors.
    // Let's define it explicitly for clarity or create a new convention.
    // Alternative: SADS engine could be updated to look for `shadow-name-dark`
    // For now, let's assume we might need to use responsive rules or JS to change shadow in dark mode if not directly supported.
    // Given the SADS docs, it seems only colors have automatic -dark suffixing.
    // So, `widget-shadow` will be one value. If a different shadow is needed for dark mode,
    // it would require a different token or a more advanced SADS feature.
    // Let's make the dark shadow part of the token value for now or assume it's acceptable.
    // To keep it simple and within current SADS capability: widget-shadow will be one value.
    // If a distinct dark mode shadow is essential, it might need a separate token and conditional SADS attributes,
    // or a feature request for SADS engine to support `shadow-token-dark`.
    // For this iteration, one shadow definition:
    // "widget-shadow": "0 4px 12px rgba(0,0,0,0.08)", // This will be used for both light and dark.
    // A slightly darker shadow for dark mode might be: "0 4px 12px rgba(0,0,0,0.25)"
    // Let's define one and see. If needed, can revisit.
    // Let's go with a single definition that works okay on both, or is primarily for light mode.
    // If we want a distinct dark mode shadow, we'd need a new token like "widget-shadow-dark"
    // and then conditionally apply it, which SADS doesn't directly support in a single attribute.
    // Sticking to one definition for now:
    "widget-shadow-dark": "0 4px 16px rgba(0,0,0,0.25)", // Added a specific dark variant
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
  (window as any).sadsDefaultTheme = sadsDefaultTheme;
  // Optionally, also expose types if needed for global context, though less common for direct script includes
  // (window as any).SadsTheme = {} as SadsTheme; // This is just a type, can't assign like this
}
