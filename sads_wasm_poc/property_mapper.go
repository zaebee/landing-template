package main

import (
	"strings"
	// "syscall/js" // Not needed if only used internally by other Go funcs
)

// mapSadsKeyToCssPropertyGo maps a SADS property key (e.g., "bgColor", "paddingTop")
// to its corresponding CSS property name (e.g., "background-color", "padding-top").
// This is an internal Go helper function.
func mapSadsKeyToCssPropertyGo(sadsPropertyKey string) string {
	if sadsPropertyKey == "" {
		return ""
	}
	// Convert from camelCase (e.g., sadsPropertyKey) to kebab-case.
	// Example: "FontSize" -> "font-size", "bgColor" -> "bg-color" (initial kebab)
	var kebabKeyBuilder strings.Builder
	for i, r := range sadsPropertyKey {
		if i > 0 && r >= 'A' && r <= 'Z' {
			// Check if previous char was also uppercase (e.g. "L1" in "neutralL1")
			// or if the next char is lowercase, to handle acronyms correctly (though less common in SADS keys)
			prevIsUpper := false
			if i > 0 {
				prevRune := rune(sadsPropertyKey[i-1])
				prevIsUpper = prevRune >= 'A' && prevRune <= 'Z'
			}

			if !prevIsUpper { // Avoid double dash for sequences like "L1" -> "l-1" if not intended.
				kebabKeyBuilder.WriteRune('-')
			}
		}
		kebabKeyBuilder.WriteRune(r)
	}
	kebabKey := strings.ToLower(kebabKeyBuilder.String())


	// This map should mirror the one in sads-style-engine.js's _mapSadsPropertyToCss
	propertyMap := map[string]string{
		"bg-color":           "background-color",
		"text-color":         "color",
		"font-size":          "font-size",
		"font-weight":        "font-weight",
		"font-style":         "font-style",
		"text-align":         "text-align",
		"text-decoration":    "text-decoration",
		"border-radius":      "border-radius",
		"border-width":       "border-width",
		"border-style":       "border-style",
		"border-color":       "border-color",
		"max-width":          "max-width",
		"width":              "width",
		"height":             "height",
		"display":            "display",
		"flex-direction":     "flex-direction",
		"flex-wrap":          "flex-wrap",
		"flex-justify":       "justify-content", // Note: SADS key is flexJustify
		"flex-align-items":   "align-items",   // Note: SADS key is flexAlignItems
		"flex-basis":         "flex-basis",
		"gap":                "gap",
		"shadow":             "box-shadow",
		"object-fit":         "object-fit",
		"padding":            "padding",
		"padding-top":        "padding-top",
		"padding-bottom":     "padding-bottom",
		"padding-left":       "padding-left",
		"padding-right":      "padding-right",
		"margin":             "margin",
		"margin-top":         "margin-top",
		"margin-bottom":      "margin-bottom",
		"margin-left":        "margin-left",
		"margin-right":       "margin-right",
		"position":           "position", // Added
		"top":                "top",      // Added
		"left":               "left",     // Added
		"right":              "right",    // Added
		"bottom":             "bottom",   // Added
		"z-index":            "z-index",  // Added
		"overflow":           "overflow", // Added
		"list-style":         "list-style", // Added
		"border-bottom-width":"border-bottom-width", // Added
		"border-bottom-style":"border-bottom-style", // Added
		"border-bottom-color":"border-bottom-color", // Added
		"min-height":         "min-height", // Added
		"flex-grow":          "flex-grow", // Added
		"grid-template-columns": "grid-template-columns", // Added
		"resize":             "resize",
		"cursor":             "cursor",
		"transition":         "transition",
		"box-sizing":         "box-sizing",
		// "layout-type" is explicitly not a direct CSS prop and should return "" or be handled by caller.
		// For direct mapping, if it's not in map, it falls through to kebabKey.
	}

	// Handle SADS specific keys that are slightly different from direct CSS
	// The initial kebab conversion handles most camelCase to kebab-case.
	// Specific overrides are for SADS keys that don't map directly after simple kebab-casing.
	// Example: sadsPropertyKey "flexJustify" -> kebab "flex-justify" -> CSS "justify-content"
	// sadsPropertyKey "flexAlignItems" -> kebab "flex-align-items" -> CSS "align-items"

	if mappedValue, ok := propertyMap[kebabKey]; ok {
		return mappedValue
	}

	// Fallback: if not in map, assume the SADS key (after kebab-casing) is a valid CSS property.
	// This handles cases like "position", "top", "z-index" etc. if they are not explicitly in map.
	// However, it's safer to have all known SADS props in the map.
	// The current JS _mapSadsPropertyToCss has a similar fallback.
	return kebabKey
}

/*
// Example of how to export if it were needed directly by JS
func MapSadsKeyToCssPropertyJS(this js.Value, args []js.Value) interface{} {
	if len(args) != 1 {
		return js.ValueOf("Error: MapSadsKeyToCssPropertyJS expects 1 argument: sadsKey (string)")
	}
	sadsKeyValue := args[0]
	if sadsKeyValue.Type() != js.TypeString {
		return js.ValueOf("Error: sadsKey must be a string")
	}
	sadsKey := sadsKeyValue.String()
	return js.ValueOf(mapSadsKeyToCssPropertyGo(sadsKey))
}
*/
