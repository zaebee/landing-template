package main

import (
	"encoding/json" // For marshalling and unmarshalling JSON data.
	"fmt"           // For string formatting, primarily for error messages.
	"strings"       // For string operations like TrimPrefix.
	"syscall/js"    // Provides access to JavaScript environment for WASM.
)

// --- Struct Definitions for JSON Parsing ---

// ResponsiveRuleStyle represents the "styles" object within a SADS responsive rule.
// It's a map where keys are SADS property keys (e.g., "padding", "bgColor") and
// values are SADS semantic tokens (e.g., "s", "primary").
// Example: {"padding": "s", "flexDirection": "column"}
type ResponsiveRuleStyle map[string]string

// ResponsiveRule represents a single rule object within the `sadsResponsiveRules` JSON array
// typically found in `data-sads-responsive-rules` attributes.
// It pairs a breakpoint key with a set of styles to apply at that breakpoint.
// Example: {"breakpoint": "mobile", "styles": {"padding": "s"}}
type ResponsiveRule struct {
	Breakpoint string              `json:"breakpoint"` // Key referencing a breakpoint in themeBreakpoints (e.g., "mobile") or a raw media query.
	Styles     ResponsiveRuleStyle `json:"styles"`     // SADS property-value pairs for this rule.
}

// ThemeBreakpoints represents the structure of the theme's breakpoints definition.
// It's a map where keys are breakpoint names (e.g., "mobile", "tablet") and
// values are the corresponding CSS media query strings.
// Example: {"mobile": "(max-width: 768px)", "tablet": "(min-width: 769px)"}
type ThemeBreakpoints map[string]string

// --- Main Exported Function ---

// ParseResponsiveRules is a Go function exported to JavaScript (via sads_wasm_bridge.go).
// It processes a JSON string containing SADS responsive rules, a JSON string of theme
// breakpoints, and various theme category JSON strings (colors, spacing, etc.).
// The function resolves semantic SADS values to actual CSS values for each rule and
// returns a JSON string that maps fully resolved CSS media queries to their
// corresponding CSS rule strings.
//
// This function is wrapped by `js.FuncOf` in `sads_wasm_bridge.go` to make it callable from JavaScript.
//
// JavaScript Arguments (passed in `args` slice, order is critical):
//   args[0] (js.Value TypeString): rulesJSON - JSON string for an array of ResponsiveRule objects.
//                                  e.g., '[{"breakpoint": "mobile", "styles": {"padding": "s"}}]'
//   args[1] (js.Value TypeString): breakpointsJSON - JSON string for the ThemeBreakpoints object.
//                                  e.g., '{"mobile": "(max-width: 768px)"}'
//   args[2] (js.Value TypeString): themeColorsJSON - JSON string for the theme's 'colors' category.
//   args[3] (js.Value TypeString): themeSpacingJSON - JSON string for the theme's 'spacing' category.
//   args[4] (js.Value TypeString): themeFontSizeJSON - JSON string for the theme's 'fontSize' category.
//   args[5] (js.Value TypeString): themeFontWeightJSON - JSON string for theme.fontWeight
//   args[6] (js.Value TypeString): themeBorderStyleJSON - JSON string for theme.borderStyle
//   args[7] (js.Value TypeString): themeBorderRadiusJSON - JSON string for theme.borderRadius
//   args[8] (js.Value TypeString): themeShadowJSON - JSON string for theme.shadow
//   args[9] (js.Value TypeString): themeMaxWidthJSON - JSON string for theme.maxWidth
//   args[10] (js.Value TypeString): themeFlexBasisJSON - JSON string for theme.flexBasis
//   args[11] (js.Value TypeString): themeObjectFitJSON - JSON string for theme.objectFit
//   args[12] (js.Value TypeBoolean): isDarkMode - Boolean indicating if dark mode is active.
//
// JavaScript Returns (as js.Value, converted from interface{}):
//   A js.Value containing a JSON string. This string represents a map where keys are
//   CSS media query strings and values are the corresponding CSS rules (e.g., "padding: 4px !important;").
//   If an error occurs (e.g., argument mismatch, JSON parsing failure), it returns an error message string.
func ParseResponsiveRules(this js.Value, args []js.Value) interface{} {
	// --- 1. Argument Validation & Extraction ---
	expectedArgCount := 13 // Ensure this matches the number of documented JS arguments.
	if len(args) != expectedArgCount {
		return js.ValueOf(fmt.Sprintf("Error: ParseResponsiveRules expects %d arguments, got %d", expectedArgCount, len(args)))
	}

	// Extract and type-assert/convert arguments from JavaScript.
	// It's crucial that the order and types match what JavaScript sends.
	// TODO: Add type checking for each js.Value before calling .String() or .Bool() for robustness.
	rulesJSON := args[0].String()
	breakpointsJSON := args[1].String()
	themeColorsJSON := args[2].String()
	themeSpacingJSON := args[3].String()
	themeFontSizeJSON := args[4].String()
	themeFontWeightJSON := args[5].String()
	themeBorderStyleJSON := args[6].String()
	themeBorderRadiusJSON := args[7].String()
	themeShadowJSON := args[8].String()
	themeMaxWidthJSON := args[9].String()
	themeFlexBasisJSON := args[10].String()
	themeObjectFitJSON := args[11].String()
	isDarkMode := args[12].Bool()

	// --- 2. Prepare Theme Data Structures ---
	// Store theme category JSON strings in a map for easier access by category name during value resolution.
	themeParts := map[string]string{
		"colors":       themeColorsJSON,
		"spacing":      themeSpacingJSON,
		"fontSize":     themeFontSizeJSON,
		"fontWeight":   themeFontWeightJSON,
		"borderStyle":  themeBorderStyleJSON,
		"borderRadius": themeBorderRadiusJSON,
		"shadow":       themeShadowJSON,
		"maxWidth":     themeMaxWidthJSON,
		"flexBasis":    themeFlexBasisJSON,
		"objectFit":    themeObjectFitJSON,
		// Note: If new theme categories are added to SADS, they need to be passed as arguments
		// and included in this map to be resolvable by resolveSadsGenericValueInternal.
	}

	// cssPropertyToThemeCategory maps a CSS property (post SADS key mapping) to its relevant theme category name.
	// This helps `resolveSadsGenericValueInternal` know which theme part JSON to use for a given CSS property.
	// This map should align with the SADS engine's logic (e.g., _mapSemanticValueToActual in JS).
	cssPropertyToThemeCategory := map[string]string{
		"padding": "spacing", "padding-top": "spacing", "padding-bottom": "spacing", "padding-left": "spacing", "padding-right": "spacing",
		"margin": "spacing", "margin-top": "spacing", "margin-bottom": "spacing", "margin-left": "spacing", "margin-right": "spacing",
		"gap": "spacing", "border-width": "spacing",
		"width": "spacing", "height": "spacing", // Note: width/height can also be custom strings (e.g., "100%", "auto")
		                                       // which resolveSadsGenericValueInternal handles via "custom:" or fallback.

		"background-color": "colors", "color": "colors", "border-color": "colors", "border-bottom-color": "colors",

		"font-size": "fontSize", "font-weight": "fontWeight",
		"font-style": "fontStyle", // Typically, fontStyle values like "italic" are direct, not theme tokens.
		                            // If themed font styles are needed, "fontStyle" could be added to themeParts.

		"border-radius": "borderRadius", "border-style": "borderStyle", "box-shadow": "shadow",
		"max-width": "maxWidth", "flex-basis": "flexBasis", "object-fit": "objectFit",
		// Properties like "display", "text-align", "position" usually take direct CSS values
		// (e.g., "flex", "center", "absolute") rather than theme tokens, so they aren't typically mapped here.
		// Their values are handled by the fallback in resolveSadsGenericValueInternal or "custom:" prefix.
	}

	// --- 3. Parse Input JSON Strings ---
	var parsedRules []ResponsiveRule
	err := json.Unmarshal([]byte(rulesJSON), &parsedRules)
	if err != nil {
		return js.ValueOf(fmt.Sprintf("Error parsing rulesJSON: %v. Input: %s", err, rulesJSON))
	}

	var themeBreakpoints ThemeBreakpoints
	err = json.Unmarshal([]byte(breakpointsJSON), &themeBreakpoints)
	if err != nil {
		return js.ValueOf(fmt.Sprintf("Error parsing breakpointsJSON: %v. Input: %s", err, breakpointsJSON))
	}

	// --- 4. Process Rules and Generate CSS ---
	// responsiveStyles maps a media query string to its accumulated CSS rules string.
	responsiveStyles := make(map[string]string)

	for _, rule := range parsedRules {
		// Determine the media query: use from theme if breakpoint key exists, else use key as raw query.
		mediaQuery, ok := themeBreakpoints[rule.Breakpoint]
		if !ok {
			// This allows using raw media queries directly in SADS attributes if needed.
			// JavaScript side might log a warning if non-standard breakpoint keys are used often.
			mediaQuery = rule.Breakpoint
		}

		currentCssText := responsiveStyles[mediaQuery] // Get existing CSS for this media query to append to it.

		// Iterate over SADS properties and their semantic values in the current rule.
		for sadsPropKey, semanticToken := range rule.Styles {
			// Convert SADS property key (e.g., "bgColor") to CSS property name (e.g., "background-color").
			cssProp := mapSadsKeyToCssPropertyGo(sadsPropKey) // Defined in property_mapper.go
			if cssProp == "" {
				// If the SADS key doesn't map to a known CSS property, skip it.
				// A warning could be logged here or on the JS side if desired.
				continue
			}

			var actualVal string
			themeCategoryName, foundCategory := cssPropertyToThemeCategory[cssProp]

			if foundCategory {
				// If the CSS property is associated with a theme category (e.g., "background-color" -> "colors").
				themeCategoryJSON, themePartOk := themeParts[themeCategoryName]
				if !themePartOk {
					// This should ideally not happen if all mapped categories in cssPropertyToThemeCategory
					// are correctly passed as arguments and included in the themeParts map.
					// If it does, fall back to using the semantic token as the value directly.
					actualVal = semanticToken
				} else {
					// Resolve the semantic token using the generic value resolver.
					actualVal = resolveSadsGenericValueInternal(semanticToken, themeCategoryJSON, themeCategoryName, isDarkMode)
				}
			} else {
				// If the CSS property has no specific theme category (e.g., "display", "text-align"),
				// or if the value is a custom value.
				if strings.HasPrefix(semanticToken, "custom:") {
					actualVal = strings.TrimPrefix(semanticToken, "custom:")
				} else {
					actualVal = semanticToken // Use the value directly (e.g., "flex", "center").
				}
			}

			// Append the resolved CSS property and value to the current media query's CSS text.
			// `!important` is added to ensure SADS styles take precedence.
			if actualVal != "" {
				currentCssText += fmt.Sprintf("%s: %s !important;\n", cssProp, actualVal)
			}
		}
		responsiveStyles[mediaQuery] = currentCssText // Store updated CSS for the media query.
	}

	// --- 5. Marshal Output to JSON and Return ---
	outputJSON, err := json.Marshal(responsiveStyles)
	if err != nil {
		return js.ValueOf(fmt.Sprintf("Error marshalling responsiveStyles map to JSON: %v", err))
	}

	return js.ValueOf(string(outputJSON)) // Return the JSON string of media queries and their CSS.
}

// resolveSadsGenericValueInternal is an unexported, pure Go helper function.
// It mirrors the logic of the JS-exported ResolveSadsGenericValue (from value_resolver.go)
// but is intended for internal use within the Go WASM module, avoiding JS interop overhead
// for Go-to-Go calls.
//
// Parameters:
//   token: The SADS token string (e.g., "primary", "m", "custom:10px").
//   themeCategoryJson: JSON string for the specific theme category (e.g., colors, spacing).
//   categoryName: Name of the category (e.g., "colors", "spacing").
//   isDarkMode: Boolean indicating if dark mode is active.
//
// Returns:
//   The resolved CSS value string.
func resolveSadsGenericValueInternal(token string, themeCategoryJson string, categoryName string, isDarkMode bool) string {
	if token == "" {
		return ""
	}
	if strings.HasPrefix(token, "custom:") {
		return strings.TrimPrefix(token, "custom:")
	}

	var categoryMap map[string]string
	// Attempt to unmarshal the theme category JSON.
	if err := json.Unmarshal([]byte(themeCategoryJson), &categoryMap); err != nil {
		// If unmarshalling fails (e.g., bad JSON string), log internally or handle as needed.
		// For now, fallback to returning the original token, as the theme data is unusable.
		// In a production system, this might warrant more robust error reporting.
		// fmt.Printf("Error unmarshalling internal theme category JSON for '%s': %v. JSON: %s\n", categoryName, err, themeCategoryJson)
		return token
	}

	if categoryName == "colors" {
		// Delegate to the specialized color resolver for color-specific logic (like dark mode).
		return resolveSadsColorTokenInternal(token, categoryMap, isDarkMode) // from value_resolver.go
	}

	// For other categories, perform a direct lookup in the category map.
	if val, ok := categoryMap[token]; ok {
		return val
	}

	// If the token is not found in the map, return the original token as a fallback.
	return token
}
