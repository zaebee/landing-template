// Package main indicates that this file is part of the main executable program,
// which, in the context of WebAssembly, means it's part of the module loaded by JavaScript.
package main

import (
	"strings" // Provides string manipulation functions, used here for case conversion and builder.
	// "syscall/js" // This package is not directly needed if this function is only called by other Go code
	// within the WASM module and not directly exported to or called by JavaScript.
	// If it were to be exported, syscall/js would be required for js.FuncOf and js.Value.
)

// mapSadsKeyToCssPropertyGo is an internal Go helper function. It translates a SADS
// (Semantic Attribute-Driven Styling) property key, which is typically in camelCase
// (e.g., "bgColor", "paddingTop", "flexJustify"), to its corresponding standard CSS
// property name in kebab-case (e.g., "background-color", "padding-top", "justify-content").
//
// This function is crucial for the SADS engine when converting semantic style definitions
// into actual CSS rules that browsers can understand.
//
// Parameters:
//   sadsPropertyKey: A string representing the SADS property key.
//
// Returns:
//   A string representing the equivalent CSS property name.
//   Returns an empty string if the input sadsPropertyKey is empty.
//   If a direct mapping is not found, it returns the kebab-cased version of the input key
//   as a fallback (assuming it might be a standard CSS property already).
func mapSadsKeyToCssPropertyGo(sadsPropertyKey string) string {
	if sadsPropertyKey == "" {
		return "" // Return empty string for empty input.
	}

	// Convert the SADS property key from camelCase or PascalCase to kebab-case.
	// Example: "FontSize" -> "font-size", "bgColor" -> "bg-color".
	// This initial conversion helps standardize the key before looking it up in the map.
	var kebabKeyBuilder strings.Builder
	for i, r := range sadsPropertyKey {
		// Check if the character is uppercase.
		if i > 0 && r >= 'A' && r <= 'Z' {
			// Check if the previous character was also uppercase (e.g., in "L1" from "neutralL1").
			// This logic aims to prevent double hyphens for acronyms or numbered sequences
			// if they are part of the camelCase key (e.g. "userID" -> "user-id", not "user-i-d").
			// A more robust solution for complex acronyms might be needed if they become common.
			prevIsUpper := false
			if i > 0 { // Ensure there is a previous character
				// It's safe to access sadsPropertyKey[i-1] because i > 0
				prevRune := rune(sadsPropertyKey[i-1])
				prevIsUpper = prevRune >= 'A' && prevRune <= 'Z'
			}

			// Insert a hyphen if the current char is uppercase and the previous wasn't,
			// or if it's an uppercase char following a non-uppercase char.
			if !prevIsUpper { // Avoids "--" for sequences like "URLAddress" -> "url-address"
				kebabKeyBuilder.WriteRune('-')
			}
		}
		kebabKeyBuilder.WriteRune(r) // Append the character (original or lowercased later).
	}
	kebabKey := strings.ToLower(kebabKeyBuilder.String()) // Convert the entire built string to lowercase.

	// propertyMap defines specific mappings from (kebab-cased) SADS keys to CSS properties.
	// This map should ideally mirror the mappings used in the JavaScript SADS engine
	// (e.g., `_mapSadsPropertyToCss` in `sads-style-engine.js`) for consistency.
	// It handles cases where the SADS key, even after kebab-casing, doesn't directly
	// match the CSS property name (e.g., "flex-justify" to "justify-content").
	propertyMap := map[string]string{
		"bg-color":            "background-color",
		"text-color":          "color",
		"font-size":           "font-size",
		"font-weight":         "font-weight",
		"font-style":          "font-style",
		"text-align":          "text-align",
		"text-decoration":     "text-decoration",
		"border-radius":       "border-radius",
		"border-width":        "border-width",
		"border-style":        "border-style",
		"border-color":        "border-color",
		"max-width":           "max-width",
		"width":               "width",
		"height":              "height",
		"display":             "display",
		"flex-direction":      "flex-direction",
		"flex-wrap":           "flex-wrap",
		"flex-justify":        "justify-content", // SADS "flexJustify" -> "flex-justify" -> "justify-content"
		"flex-align-items":    "align-items",     // SADS "flexAlignItems" -> "flex-align-items" -> "align-items"
		"flex-basis":          "flex-basis",
		"gap":                 "gap",
		"shadow":              "box-shadow",
		"object-fit":          "object-fit",
		"padding":             "padding",
		"padding-top":         "padding-top",
		"padding-bottom":      "padding-bottom",
		"padding-left":        "padding-left",
		"padding-right":       "padding-right",
		"margin":              "margin",
		"margin-top":          "margin-top",
		"margin-bottom":       "margin-bottom",
		"margin-left":         "margin-left",
		"margin-right":        "margin-right",
		"position":            "position",
		"top":                 "top",
		"left":                "left",
		"right":               "right",
		"bottom":              "bottom",
		"z-index":             "z-index",
		"overflow":            "overflow",
		"list-style":          "list-style",
		"border-bottom-width": "border-bottom-width",
		"border-bottom-style": "border-bottom-style",
		"border-bottom-color": "border-bottom-color",
		"min-height":          "min-height",
		"flex-grow":           "flex-grow",
		"grid-template-columns": "grid-template-columns",
		"resize":              "resize",
		"cursor":              "cursor",
		"transition":          "transition",
		"box-sizing":          "box-sizing",
		// "layout-type" is a SADS-specific key that doesn't map to a direct CSS property.
		// It's handled by higher-level logic in the SADS engine (e.g., applying display:flex and flex-direction).
		// If such a key were passed here, it would fall through to the kebabKey return if not explicitly handled.
	}

	// Check if the kebab-cased key exists in our explicit propertyMap.
	if mappedValue, ok := propertyMap[kebabKey]; ok {
		return mappedValue // Return the specifically mapped CSS property name.
	}

	// Fallback: If the key is not in propertyMap, assume the kebab-cased SADS key
	// is already a valid CSS property name (e.g., "opacity", "visibility").
	// This makes the mapping more flexible but relies on SADS keys being chosen carefully
	// if they aren't in the explicit map.
	return kebabKey
}

/*
// Example of how this function could be exported to JavaScript if needed directly.
// This is not currently used as mapSadsKeyToCssPropertyGo is called internally
// by other Go functions like ParseResponsiveRules.

import "syscall/js" // Would be needed if this function were exported.

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
