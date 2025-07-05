package main

import (
	"encoding/json" // Used for unmarshalling JSON strings (theme data) from JavaScript.
	"fmt"           // Used for formatting error messages.
	"strings"       // Used for string manipulations like checking prefixes and trimming.
	"syscall/js"    // Provides types and functions for interacting with JavaScript.
)

// resolveSadsColorTokenInternal is an internal Go helper function that contains the core logic
// for resolving a SADS semantic color token. It checks for "custom:" prefixes,
// handles dark mode variations (e.g., "primary-dark"), and looks up the token
// in the provided color map.
//
// Parameters:
//   token: The SADS color token string (e.g., "primary", "custom:red").
//   colorsMap: A map representing the theme's color palette (e.g., {"primary": "#007bff", "primary-dark": "#0056b3"}).
//   isDarkMode: A boolean indicating whether dark mode is active.
//
// Returns:
//   The resolved CSS color value as a string. If the token is not found, it returns the original token.
//   If it's a custom token (e.g. "custom:red"), it returns the value part ("red").
func resolveSadsColorTokenInternal(token string, colorsMap map[string]string, isDarkMode bool) string {
	if strings.HasPrefix(token, "custom:") {
		return strings.TrimPrefix(token, "custom:")
	}

	if isDarkMode {
		darkTokenKey := token + "-dark" // Construct the dark mode version of the token key.
		if val, ok := colorsMap[darkTokenKey]; ok {
			return val // Return dark mode value if found.
		}
	}

	// If not in dark mode, or if dark mode value was not found, try the base token.
	if val, ok := colorsMap[token]; ok {
		return val
	}
	return token // Return original token if no match is found in the theme.
}

// ResolveSadsGenericValue is a Go function exported to JavaScript (via sads_wasm_bridge.go).
// It resolves a generic SADS semantic token (e.g., "primary" for colors, "m" for spacing)
// against a given theme category's JSON data.
//
// This function is wrapped by `js.FuncOf` in `sads_wasm_bridge.go` to make it callable from JavaScript.
//
// JavaScript Arguments (passed in `args` slice):
//   args[0] (js.Value of type String): The SADS token to resolve (e.g., "surface", "m", "large").
//   args[1] (js.Value of type String): A JSON string representing the specific theme category's
//                                     data (e.g., '{"surface": "#fff", "primary": "#007bff"}').
//   args[2] (js.Value of type String): The name of the theme category (e.g., "colors", "spacing", "fontSize").
//                                     This helps determine if special logic (like for "colors") applies.
//   args[3] (js.Value of type Boolean): A boolean indicating if dark mode is active. This is primarily
//                                      relevant for the "colors" category.
//
// JavaScript Returns (as js.Value, converted from interface{}):
//   A js.Value containing the resolved CSS value as a string (e.g., "#FFFFFF", "16px").
//   If the token cannot be resolved, it returns the original token string.
//   If an error occurs (e.g., incorrect arguments, JSON parsing failure), it returns an error message string.
func ResolveSadsGenericValue(this js.Value, args []js.Value) interface{} {
	// --- 1. Argument Validation & Extraction from JavaScript ---
	if len(args) != 4 {
		// Return an error message string if the wrong number of arguments is provided.
		return js.ValueOf("Error: ResolveSadsGenericValue expects 4 arguments: token (string), themeCategoryJson (string), categoryName (string), isDarkMode (bool)")
	}

	tokenValue := args[0]
	themeCategoryJsonValue := args[1]
	categoryNameValue := args[2]
	isDarkModeValue := args[3]

	// Type check the arguments received from JavaScript.
	if tokenValue.Type() != js.TypeString ||
		themeCategoryJsonValue.Type() != js.TypeString ||
		categoryNameValue.Type() != js.TypeString ||
		isDarkModeValue.Type() != js.TypeBoolean {
		return js.ValueOf("Error: ResolveSadsGenericValue received incorrect argument types.")
	}

	// Convert js.Value arguments to their corresponding Go types.
	token := tokenValue.String()
	themeCategoryJson := themeCategoryJsonValue.String()
	categoryName := categoryNameValue.String()
	isDarkMode := isDarkModeValue.Bool()

	// --- 2. Handle Empty Token ---
	if token == "" {
		return js.ValueOf("") // Return empty string if the token is empty.
	}

	// --- 3. Handle "custom:" Prefix ---
	// Custom values (e.g., "custom:10px", "custom:blue") are returned directly after stripping the prefix.
	if strings.HasPrefix(token, "custom:") {
		return js.ValueOf(strings.TrimPrefix(token, "custom:"))
	}

	// --- 4. Deserialize Theme Category JSON ---
	// Unmarshal the JSON string for the theme category into a Go map.
	var categoryMap map[string]string
	err := json.Unmarshal([]byte(themeCategoryJson), &categoryMap)
	if err != nil {
		// Return an error message if JSON deserialization fails.
		return js.ValueOf(fmt.Sprintf("Error deserializing themeCategoryJson for category '%s': %v. JSON: %s", categoryName, err, themeCategoryJson))
	}

	// --- 5. Resolve Token Based on Category ---
	if categoryName == "colors" {
		// For the "colors" category, use the specialized internal resolver
		// which handles dark mode logic (e.g., checking for "token-dark" keys).
		return js.ValueOf(resolveSadsColorTokenInternal(token, categoryMap, isDarkMode))
	}

	// For other categories (e.g., "spacing", "fontSize"), perform a direct lookup.
	// Currently, these categories do not have special dark mode variations
	// like "m-dark" directly in their values. If such a requirement arises,
	// this logic would need to be expanded similar to how colors are handled.
	if val, ok := categoryMap[token]; ok {
		return js.ValueOf(val) // Return the resolved value from the theme map.
	}

	// --- 6. Fallback: Return Original Token ---
	// If the token is not found in the theme category map (and is not "custom:"),
	// return the original token. The JavaScript side can then decide if this
	// original token is a valid CSS value itself (e.g., a standard CSS color name like "red"
	// if not themed, or a direct pixel value like "10px").
	return js.ValueOf(token)
}

// ResolveSadsColorToken is a Go function exported to JavaScript (via sads_wasm_bridge.go),
// specifically for resolving SADS color tokens. It serves as a convenience wrapper
// around ResolveSadsGenericValue, pre-setting the categoryName to "colors".
// This function was part of the initial PoC and is kept for compatibility
// and potentially simpler calls from JS if only color resolution is needed.
//
// JavaScript Arguments (passed in `args` slice):
//   args[0] (js.Value of type String): The SADS color token (e.g., "primary", "surface-dark").
//   args[1] (js.Value of type String): A JSON string representing the theme's 'colors' object.
//   args[2] (js.Value of type Boolean): A boolean indicating if dark mode is active.
//
// JavaScript Returns (as js.Value, converted from interface{}):
//   A js.Value containing the resolved CSS color string or an error message string.
func ResolveSadsColorToken(this js.Value, args []js.Value) interface{} {
	// Validate the number of arguments.
	if len(args) != 3 {
		return js.ValueOf("Error: ResolveSadsColorToken expects 3 arguments: sadsColorToken (string), colorsThemeJson (string), isDarkMode (bool)")
	}

	// Extract JS arguments. Type checking will be done by ResolveSadsGenericValue.
	sadsColorTokenValue := args[0]
	colorsThemeJsonValue := args[1]
	isDarkModeValue := args[2]

	// Prepare arguments for the call to ResolveSadsGenericValue.
	// The key difference is adding js.ValueOf("colors") for the categoryName.
	genericArgs := []js.Value{
		sadsColorTokenValue,    // token
		colorsThemeJsonValue,   // themeCategoryJson (which is the colorsThemeJson for this function)
		js.ValueOf("colors"),   // categoryName is fixed to "colors"
		isDarkModeValue,        // isDarkMode
	}

	// Delegate the actual resolution logic to ResolveSadsGenericValue.
	return ResolveSadsGenericValue(this, genericArgs)
}
