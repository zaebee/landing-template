package main

import (
	"encoding/json"
	"fmt"
	"strings"
	"syscall/js"
)

// ResolveSadsColorToken resolves a SADS semantic color token against a theme's color map,
// considering dark mode.
//
// Inputs from JavaScript (via syscall/js.FuncOf wrapper args):
// args[0] (js.Value): sadsColorToken (string) - e.g., "surface", "text-primary"
// args[1] (js.Value): colorsThemeJson (string) - JSON string of the theme's 'colors' object.
// args[2] (js.Value): isDarkMode (bool) - True if dark mode is active.
//
// Returns (interface{} for js.FuncOf wrapper, will be js.ValueOf(string)):
// Resolved CSS color string (e.g., "#FFFFFF"), or the original token if not found/error.
func ResolveSadsColorToken(this js.Value, args []js.Value) interface{} {
	// --- 1. Argument Validation & Extraction ---
	if len(args) != 3 {
		// In a real application, you might return a JavaScript Error object.
		// For this PoC, a descriptive string is sufficient as per the spec.
		return js.ValueOf("Error: ResolveSadsColorToken expects 3 arguments: sadsColorToken (string), colorsThemeJson (string), isDarkMode (bool)")
	}

	sadsColorTokenValue := args[0]
	colorsThemeJsonValue := args[1]
	isDarkModeValue := args[2]

	if sadsColorTokenValue.Type() != js.TypeString {
		return js.ValueOf("Error: sadsColorToken must be a string")
	}
	sadsColorToken := sadsColorTokenValue.String()

	if colorsThemeJsonValue.Type() != js.TypeString {
		return js.ValueOf("Error: colorsThemeJson must be a string")
	}
	colorsThemeJson := colorsThemeJsonValue.String()

	if isDarkModeValue.Type() != js.TypeBoolean {
		return js.ValueOf("Error: isDarkMode must be a boolean")
	}
	isDarkMode := isDarkModeValue.Bool()

	if sadsColorToken == "" {
		return js.ValueOf("") // Return empty for empty token, as per spec sketch
	}

	// --- 2. Deserialize colorsThemeJson into a Go map[string]string ---
	var colorsMap map[string]string
	err := json.Unmarshal([]byte(colorsThemeJson), &colorsMap)
	if err != nil {
		return js.ValueOf(fmt.Sprintf("Error deserializing colorsThemeJson: %v", err))
	}

	// --- 3. Core Resolution Logic ---
	resolvedValue := sadsColorToken // Default to original token

	// Handle "custom:" prefix
	if strings.HasPrefix(sadsColorToken, "custom:") {
		resolvedValue = strings.TrimPrefix(sadsColorToken, "custom:")
		return js.ValueOf(resolvedValue) // Return the custom value directly
	}

	// Attempt to find dark mode version if isDarkMode is true
	if isDarkMode {
		darkTokenKey := sadsColorToken + "-dark"
		if val, ok := colorsMap[darkTokenKey]; ok {
			resolvedValue = val
			return js.ValueOf(resolvedValue) // Found dark mode specific value
		}
	}

	// Attempt to find the base token if dark mode version wasn't found or dark mode is off
	if val, ok := colorsMap[sadsColorToken]; ok {
		resolvedValue = val
		return js.ValueOf(resolvedValue) // Found base value
	}

	// If no specific theme token (dark or base) was found, return the original token.
	return js.ValueOf(resolvedValue)
}

// main function to expose the Go function to JavaScript
func main() {
	c := make(chan struct{}, 0) // Keep the Go program alive

	// Expose the ResolveSadsColorToken function to JavaScript under `window.sadsPocWasm.resolveColor`
	js.Global().Set("sadsPocWasm", js.ValueOf(map[string]interface{}{
		"resolveColor": js.FuncOf(ResolveSadsColorToken),
	}))

	<-c // Block main from exiting, allowing JS to call exported functions
}
