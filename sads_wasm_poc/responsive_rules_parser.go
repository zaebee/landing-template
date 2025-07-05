package main

import (
	"encoding/json"
	"fmt"
	"syscall/js"
	// "strings" // Not directly used here, but dependencies might
)

// Structs for parsing JSON inputs

// ResponsiveRuleStyle represents the "styles" object within a responsive rule.
// e.g., {"padding": "s", "flexDirection": "column"}
type ResponsiveRuleStyle map[string]string

// ResponsiveRule represents a single rule object within the sadsResponsiveRules JSON array.
// e.g., {"breakpoint": "mobile", "styles": {"padding": "s"}}
type ResponsiveRule struct {
	Breakpoint string              `json:"breakpoint"`
	Styles     ResponsiveRuleStyle `json:"styles"`
}

// ThemeBreakpoints represents the structure of the theme's breakpoints object.
// e.g., {"mobile": "(max-width: 768px)", "tablet": "(min-width: 769px) and (max-width: 1024px)"}
type ThemeBreakpoints map[string]string

// ParseResponsiveRules processes a JSON string of responsive rules,
// a JSON string of theme breakpoints, and various theme category JSON strings,
// returning a JSON string that maps media queries to their CSS rules.
//
// JS Input Args:
// args[0]: rulesJSON (string) - e.g., '[{"breakpoint": "mobile", "styles": {"padding": "s"}}]'
// args[1]: breakpointsJSON (string) - e.g., '{"mobile": "(max-width: 768px)"}'
// args[2]: themeColorsJSON (string) - JSON for theme.colors
// args[3]: themeSpacingJSON (string) - JSON for theme.spacing
// args[4]: themeFontSizeJSON (string) - JSON for theme.fontSize
// args[5]: themeFontWeightJSON (string) - JSON for theme.fontWeight
// args[6]: themeBorderStyleJSON (string) - JSON for theme.borderStyle
// args[7]: themeBorderRadiusJSON (string) - JSON for theme.borderRadius
// args[8]: themeShadowJSON (string) - JSON for theme.shadow
// args[9]: themeMaxWidthJSON (string) - JSON for theme.maxWidth
// args[10]: themeFlexBasisJSON (string) - JSON for theme.flexBasis
// args[11]: themeObjectFitJSON (string) - JSON for theme.objectFit
// args[12]: isDarkMode (bool)
//
// Returns: JSON string mapping media query to CSS rules string, or an error string.
func ParseResponsiveRules(this js.Value, args []js.Value) interface{} {
	expectedArgCount := 13
	if len(args) != expectedArgCount {
		return js.ValueOf(fmt.Sprintf("Error: ParseResponsiveRules expects %d arguments", expectedArgCount))
	}

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

	// Store theme parts in a map for easier access by category name
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
	}

	// Helper map for SADS CSS property to theme category
	// This should align with _mapSemanticValueToActual in sads-style-engine.js
	cssPropertyToThemeCategory := map[string]string{
		"padding": "spacing", "padding-top": "spacing", "padding-bottom": "spacing", "padding-left": "spacing", "padding-right": "spacing",
		"margin": "spacing", "margin-top": "spacing", "margin-bottom": "spacing", "margin-left": "spacing", "margin-right": "spacing",
		"gap": "spacing", "border-width": "spacing", "width": "spacing", "height": "spacing", // width/height can also be custom or %

		"background-color": "colors", "color": "colors", "border-color": "colors", "border-bottom-color": "colors",

		"font-size": "fontSize", "font-weight": "fontWeight", "font-style": "fontStyle", // fontStyle usually direct value
		"border-radius": "borderRadius", "border-style": "borderStyle", "box-shadow": "shadow",
		"max-width": "maxWidth", "flex-basis": "flexBasis", "object-fit": "objectFit",
	}


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

	responsiveStyles := make(map[string]string) // Maps media query string to CSS rules string

	for _, rule := range parsedRules {
		mediaQuery, ok := themeBreakpoints[rule.Breakpoint]
		if !ok {
			// If breakpoint key not in theme, use the key itself as a raw media query (e.g. for custom one-offs)
			// console.warn in JS side if this happens often with non-standard keys
			mediaQuery = rule.Breakpoint
		}

		currentCssText := responsiveStyles[mediaQuery] // Get existing rules for this media query

		for sadsPropKey, semanticVal := range rule.Styles {
			cssProp := mapSadsKeyToCssPropertyGo(sadsPropKey) // from property_mapper.go
			if cssProp == "" {
				// console.warn equivalent: SADS: Unmapped SADS property in responsive rule
				continue // Skip if property doesn't map
			}

			var actualVal string
			themeCategoryName, foundCategory := cssPropertyToThemeCategory[cssProp]

			if foundCategory {
				themeCategoryJSON, themePartOk := themeParts[themeCategoryName]
				if !themePartOk {
                     // This case should ideally not happen if all mapped categories are passed as args
					actualVal = semanticVal // Fallback to raw value
				} else {
					// Call ResolveSadsGenericValue - which itself is a JS-exported function.
					// For internal Go calls, we'd ideally call a pure Go version.
					// For now, let's assume we might need to adapt ResolveSadsGenericValue or create an internal version.
					// Let's create resolveSadsGenericValueInternal for this.
					 resolved := resolveSadsGenericValueInternal(semanticVal, themeCategoryJSON, themeCategoryName, isDarkMode)
					 actualVal = resolved
				}
			} else {
				// If CSS property has no specific theme category (e.g. "display", "text-align"),
				// or if it's a custom value.
				if strings.HasPrefix(semanticVal, "custom:") {
					actualVal = strings.TrimPrefix(semanticVal, "custom:")
				} else {
					actualVal = semanticVal // Use value directly
				}
			}

			if actualVal != "" {
				currentCssText += fmt.Sprintf("%s: %s !important;\n", cssProp, actualVal)
			}
		}
		responsiveStyles[mediaQuery] = currentCssText
	}

	outputJSON, err := json.Marshal(responsiveStyles)
	if err != nil {
		return js.ValueOf(fmt.Sprintf("Error marshalling responsiveStyles map to JSON: %v", err))
	}

	return js.ValueOf(string(outputJSON))
}


// resolveSadsGenericValueInternal is a pure Go version for internal calls.
// It mirrors the logic of the JS-exported ResolveSadsGenericValue.
func resolveSadsGenericValueInternal(token string, themeCategoryJson string, categoryName string, isDarkMode bool) string {
	if token == "" {
		return ""
	}
	if strings.HasPrefix(token, "custom:") {
		return strings.TrimPrefix(token, "custom:")
	}

	var categoryMap map[string]string
	if err := json.Unmarshal([]byte(themeCategoryJson), &categoryMap); err != nil {
		// In a real scenario, might log this error or handle it more gracefully
		return token // Fallback to token if category JSON is bad
	}

	if categoryName == "colors" {
		return resolveSadsColorTokenInternal(token, categoryMap, isDarkMode) // from value_resolver.go
	}

	if val, ok := categoryMap[token]; ok {
		return val
	}
	return token
}
