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
  "nav-link-hover-bg-dark"?: string;
  "nav-link-active-bg-dark"?: string;
  "nav-link-active-text-dark"?: string;
  "header-button-hover-bg-dark"?: string;
  "header-button-hover-border-dark"?: string;
  "border-accent"?: string;
  "border-accent-dark"?: string;

  // Hero Section
  "hero-bg"?: string;
  "hero-bg-dark"?: string;
  "text-on-hero"?: string;
  "text-on-hero-dark"?: string;

  // Features Section
  "features-bg"?: string;
  "features-bg-dark"?: string;
  "feature-item-bg"?: string;
  "feature-item-bg-dark"?: string;
  "feature-item-title-text"?: string;
  "feature-item-title-text-dark"?: string;

  // Testimonials Section
  "testimonials-bg"?: string;
  "testimonials-bg-dark"?: string;
  "testimonials-title-text"?: string;
  "testimonials-title-text-dark"?: string;
  "testimonial-item-bg"?: string;
  "testimonial-item-bg-dark"?: string;
  "testimonial-quote-text"?: string;
  "testimonial-quote-text-dark"?: string;
  "testimonial-author-text"?: string;
  "testimonial-author-text-dark"?: string;

  // Chat Section
  "chat-bg"?: string;
  "chat-bg-dark"?: string;
  "chat-messages-bg"?: string;
  "chat-messages-bg-dark"?: string;

  // MCP Section
  "neutral-subtle"?: string;
  "neutral-subtle-dark"?: string;
  "button-primary-bg-hover-color"?: string; // Note: SADS engine doesn't auto-apply hover states
  "button-primary-bg-hover-color-dark"?: string;

  // Portfolio Section
  "portfolio-bg"?: string;
  "portfolio-bg-dark"?: string;
  "portfolio-title-text"?: string;
  "portfolio-title-text-dark"?: string;
  "portfolio-item-bg"?: string;
  "portfolio-item-bg-dark"?: string;
  "portfolio-img-border"?: string;
  "portfolio-img-border-dark"?: string;
  "portfolio-item-heading-text"?: string;
  "portfolio-item-heading-text-dark"?: string;
  "portfolio-item-para-text"?: string;
  "portfolio-item-para-text-dark"?: string;

  // Blog Section
  "blog-section-bg": string; // Existing
  "blog-section-bg-dark": string; // Existing
  "blog-title-text"?: string;
  "blog-title-text-dark"?: string;
  "blog-item-bg": string; // Existing
  "blog-item-bg-dark": string; // Existing
  "blog-item-title-text"?: string;
  "blog-item-title-text-dark"?: string;
  "blog-item-excerpt-text"?: string;
  "blog-item-excerpt-text-dark"?: string;
  "blog-readmore-text"?: string;
  "blog-readmore-text-dark"?: string;

  // Contact Form Section
  "contact-section-bg": string; // Existing
  "contact-section-bg-dark": string; // Existing
  "contact-form-bg": string; // Existing
  "contact-form-bg-dark": string; // Existing
  "contact-label-text"?: string;
  "contact-label-text-dark"?: string;
  "contact-input-border"?: string;
  "contact-input-border-dark"?: string;
  "contact-input-bg"?: string;
  "contact-input-bg-dark"?: string;
  "contact-input-text"?: string;
  "contact-input-text-dark"?: string;
  "contact-submit-bg"?: string;
  "contact-submit-bg-dark"?: string;
  "contact-submit-text"?: string;
  "contact-submit-text-dark"?: string;

  // Footer Section
  "footer-bg"?: string;
  "footer-bg-dark"?: string;
  "text-footer"?: string;
  "text-footer-dark"?: string;

  // Generic Input and Button styles (already well-defined)
  "input-border-color": string;
  "input-border-color-dark": string;
  "input-bg-color": string;
  "input-bg-color-dark": string;
  "button-primary-bg-color": string;
  "button-primary-bg-color-dark": string;
  "button-primary-text-color": string; // Assuming this works for dark bg too

  [key: string]: string | undefined;
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
  fontFamily?: { [key: string]: string }; // Added for default font family
  lineHeight?: { [key: string]: string }; // Added for default line height
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

    "header-button-hover-bg-dark": "#374a5c",
    "header-button-hover-border-dark": "#3498db",

    // Hero Section
    "hero-bg": "#e9ecef",
    "hero-bg-dark": "#2c3e50", // Using header dark bg as a starting point
    "text-on-hero": "#212529",
    "text-on-hero-dark": "#f8f9fa",

    // Features Section
    "features-bg": "#ffffff",
    "features-bg-dark": "#212529",
    "feature-item-bg": "#f8f9fa",
    "feature-item-bg-dark": "#2c3e50", // Slightly lighter than section bg
    "feature-item-title-text": "#007bff",
    "feature-item-title-text-dark": "#3498db",

    // Testimonials Section
    "testimonials-bg": "#f8f9fa",
    "testimonials-bg-dark": "#212529",
    "testimonials-title-text": "#333333",
    "testimonials-title-text-dark": "#e0e0e0",
    "testimonial-item-bg": "#ffffff",
    "testimonial-item-bg-dark": "#2c3e50", // Slightly lighter than section bg
    "testimonial-quote-text": "#555555",
    "testimonial-quote-text-dark": "#bbbbbb",
    "testimonial-author-text": "#212529",
    "testimonial-author-text-dark": "#f8f9fa",

    // Chat Section
    "chat-bg": "#f4f4f4",
    "chat-bg-dark": "#1c1c1c",
    "chat-messages-bg": "#ffffff",
    "chat-messages-bg-dark": "#2b2b2b",

    // MCP Section
    "neutral-subtle": "#e9ecef",
    "neutral-subtle-dark": "#4a4a4a", // Darker grey for subtle lines
    "button-primary-bg-hover-color": "#218838",
    "button-primary-bg-hover-color-dark": "#1558b0",


    // Portfolio Section
    "portfolio-bg": "#ffffff",
    "portfolio-bg-dark": "#212529",
    "portfolio-title-text": "#333333",
    "portfolio-title-text-dark": "#e0e0e0",
    "portfolio-item-bg": "#f8f9fa",
    "portfolio-item-bg-dark": "#2c3e50", // Slightly lighter than section bg
    "portfolio-img-border": "#dddddd",
    "portfolio-img-border-dark": "#4a4a4a",
    "portfolio-item-heading-text": "#007bff",
    "portfolio-item-heading-text-dark": "#3498db",
    "portfolio-item-para-text": "#555555",
    "portfolio-item-para-text-dark": "#bbbbbb",

    // Blog Section
    "blog-section-bg": "#e9ecef", // Existing
    "blog-section-bg-dark": "#2a2a2a", // Existing
    "blog-title-text": "#333333",
    "blog-title-text-dark": "#e0e0e0",
    "blog-item-bg": "#ffffff", // Existing
    "blog-item-bg-dark": "#1f1f1f", // Existing
    "blog-item-title-text": "#007bff",
    "blog-item-title-text-dark": "#3498db",
    "blog-item-excerpt-text": "#555555",
    "blog-item-excerpt-text-dark": "#bbbbbb",
    "blog-readmore-text": "#007bff",
    "blog-readmore-text-dark": "#3498db",

    // Contact Form Section
    "contact-section-bg": "#e9ecef", // Existing
    "contact-section-bg-dark": "#2a2a2a", // Existing
    "contact-form-bg": "#ffffff", // Existing
    "contact-form-bg-dark": "#1f1f1f", // Existing
    "contact-label-text": "#333333",
    "contact-label-text-dark": "#e0e0e0",
    "contact-input-border": "#cccccc",
    "contact-input-border-dark": "#555555", // Using existing input-border-color-dark
    "contact-input-bg": "#ffffff",
    "contact-input-bg-dark": "#333333", // Using existing input-bg-color-dark
    "contact-input-text": "#333333",
    "contact-input-text-dark": "#e0e0e0", // Using existing text-primary-dark
    "contact-submit-bg": "#28a745", // Using existing button-primary-bg-color
    "contact-submit-bg-dark": "#1a73e8", // Using existing button-primary-bg-color-dark
    "contact-submit-text": "#ffffff", // Using existing button-primary-text-color
    // contact-submit-text-dark is not defined, assuming #ffffff is fine.

    // Footer Section
    "footer-bg": "#343a40",
    "footer-bg-dark": "#212529",
    "text-footer": "#f8f9fa",
    "text-footer-dark": "#adb5bd",

    // Generic Input and Button styles (already well-defined)
    "input-border-color": "#cccccc",
    "input-border-color-dark": "#555555",
    "input-bg-color": "#ffffff",
    "input-bg-color-dark": "#333333",
    "button-primary-bg-color": "#28a745",
    "button-primary-bg-color-dark": "#1a73e8",
    "button-primary-text-color": "#ffffff", // Assuming this works for dark bg too
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
  fontFamily: {
    default: "Arial, sans-serif",
    monospace: "monospace", // Example other font
  },
  lineHeight: {
    default: "1.6",
    condensed: "1.2", // Example other line height
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
