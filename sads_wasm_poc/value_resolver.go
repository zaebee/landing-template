package main

import (
	"encoding/json"
	"fmt"
	"strings"
	"syscall/js"
)

// resolveSadsColorTokenInternal is the actual Go logic for color resolution.
// It's not directly exported to JS, but called by ResolveSadsGenericValue.
func resolveSadsColorTokenInternal(token string, colorsMap map[string]string, isDarkMode bool) string {
	if strings.HasPrefix(token, "custom:") {
		return strings.TrimPrefix(token, "custom:")
	}

	if isDarkMode {
		darkTokenKey := token + "-dark"
		if val, ok := colorsMap[darkTokenKey]; ok {
			return val
		}
	}

	if val, ok := colorsMap[token]; ok {
		return val
	}
	return token // Return original token if not found
}

// ResolveSadsGenericValue resolves a SADS semantic token against a specific theme category.
//
// Inputs from JavaScript (via syscall/js.FuncOf wrapper args):
// args[0] (js.Value): token (string) - e.g., "surface", "m", "large"
// args[1] (js.Value): themeCategoryJson (string) - JSON string of the theme's specific category object (e.g., colors, spacing, fontSize).
// args[2] (js.Value): categoryName (string) - Name of the category (e.g., "colors", "spacing", "fontSize")
// args[3] (js.Value): isDarkMode (bool) - True if dark mode is active (relevant for colors).
//
// Returns (interface{} for js.FuncOf wrapper, will be js.ValueOf(string)):
// Resolved CSS value string, or the original token if not found/error.
func ResolveSadsGenericValue(this js.Value, args []js.Value) interface{} {
	if len(args) != 4 {
		return js.ValueOf("Error: ResolveSadsGenericValue expects 4 arguments: token (string), themeCategoryJson (string), categoryName (string), isDarkMode (bool)")
	}

	tokenValue := args[0]
	themeCategoryJsonValue := args[1]
	categoryNameValue := args[2]
	isDarkModeValue := args[3]

	if tokenValue.Type() != js.TypeString ||
		themeCategoryJsonValue.Type() != js.TypeString ||
		categoryNameValue.Type() != js.TypeString ||
		isDarkModeValue.Type() != js.TypeBoolean {
		return js.ValueOf("Error: ResolveSadsGenericValue received incorrect argument types.")
	}

	token := tokenValue.String()
	themeCategoryJson := themeCategoryJsonValue.String()
	categoryName := categoryNameValue.String()
	isDarkMode := isDarkModeValue.Bool()

	if token == "" {
		return js.ValueOf("") // Return empty for empty token
	}

	// Handle "custom:" prefix universally for any category before further processing.
	// Though for colors, resolveSadsColorTokenInternal also handles it, this is a good general check.
	if strings.HasPrefix(token, "custom:") {
		return js.ValueOf(strings.TrimPrefix(token, "custom:"))
	}

	var categoryMap map[string]string
	err := json.Unmarshal([]byte(themeCategoryJson), &categoryMap)
	if err != nil {
		return js.ValueOf(fmt.Sprintf("Error deserializing themeCategoryJson for category '%s': %v", categoryName, err))
	}

	if categoryName == "colors" {
		// Use the specialized color resolver which handles dark mode nuances correctly
		return js.ValueOf(resolveSadsColorTokenInternal(token, categoryMap, isDarkMode))
	}

	// For other categories (spacing, fontSize, etc.)
	// Currently, these don't have a special dark mode mapping directly in their values (e.g. "m-dark").
	// If they did, this logic would need to be expanded similar to colors.
	if val, ok := categoryMap[token]; ok {
		return js.ValueOf(val)
	}

	// If no specific theme token was found, return the original token.
	// The JS side can then decide if this original token is a valid CSS value itself.
	return js.ValueOf(token)
}

// ResolveSadsColorToken is the JS-exported wrapper for color resolution.
// It now calls ResolveSadsGenericValue with categoryName "colors".
func ResolveSadsColorToken(this js.Value, args []js.Value) interface{} {
    // We need to adapt the arguments for ResolveSadsGenericValue
    // args[0] = sadsColorToken (string)
    // args[1] = colorsThemeJson (string)
    // args[2] = isDarkMode (bool)

    if len(args) != 3 {
         return js.ValueOf("Error: ResolveSadsColorToken expects 3 arguments: sadsColorToken (string), colorsThemeJson (string), isDarkMode (bool)")
    }

    sadsColorTokenValue := args[0]
    colorsThemeJsonValue := args[1]
    isDarkModeValue := args[2]

    // Construct new args for ResolveSadsGenericValue:
    // token (string), themeCategoryJson (string), categoryName (string), isDarkMode (bool)
    genericArgs := []js.Value{
        sadsColorTokenValue,    // token
        colorsThemeJsonValue,   // themeCategoryJson (which is colorsThemeJson)
        js.ValueOf("colors"),   // categoryName
        isDarkModeValue,        // isDarkMode
    }
    return ResolveSadsGenericValue(this, genericArgs)
}
