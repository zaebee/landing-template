// Package main is required for Go programs that are compiled to WebAssembly (WASM)
// to be executable.
package main

import (
	"syscall/js" // Provides access to the JavaScript environment when running in WASM.
)

// main is the entry point of the Go WASM module.
// It's responsible for setting up any global state or, more importantly,
// exporting Go functions to the JavaScript global scope so they can be called
// from JavaScript.
// This function does not exit, allowing the WASM module to remain active
// and responsive to JavaScript calls.
func main() {
	// Create a channel that will block indefinitely.
	// This is a common pattern to prevent the Go program from exiting,
	// which is necessary for WASM modules that need to provide services
	// to JavaScript over time (i.e., allow JS to call exported Go functions).
	c := make(chan struct{}, 0)

	// exportedFunctions is a map that defines the Go functions to be exposed
	// to JavaScript. The keys are the names by which JavaScript will access
	// these functions (e.g., window.sadsPocWasm.resolveColor).
	// The values are js.FuncOf wrappers around the actual Go functions.
	exportedFunctions := map[string]interface{}{
		// ---- Functions from value_resolver.go ----

		// ResolveSadsColorToken (exported as "resolveColor"):
		//   Resolves a SADS semantic color token (e.g., "primary", "surface-dark")
		//   against a provided theme's color map, considering dark mode.
		//   This is kept for some backward compatibility with early test harness versions
		//   but ResolveSadsGenericValue is preferred for new color resolutions.
		//   JS Args: token (string), themeColorsJSON (string), isDarkMode (bool)
		//   JS Returns: resolved CSS color (string) or error string.
		"resolveColor": js.FuncOf(ResolveSadsColorToken),

		// ResolveSadsGenericValue (exported as "resolveSadsValue"):
		//   Resolves a generic SADS semantic token (e.g., "primary" for colors,
		//   "m" for spacing) against a relevant theme category JSON.
		//   JS Args: token (string), themeCategoryJson (string), categoryName (string), isDarkMode (bool)
		//   JS Returns: resolved CSS value (string) or error string.
		"resolveSadsValue": js.FuncOf(ResolveSadsGenericValue),

		// ---- Functions from responsive_rules_parser.go ----

		// ParseResponsiveRules (exported as "parseResponsiveRules"):
		//   Parses a JSON string of SADS responsive rules, theme breakpoints,
		//   and various theme category JSON strings. It then generates a JSON string
		//   mapping CSS media queries to their corresponding CSS rule strings.
		//   JS Args: (13 arguments, see responsive_rules_parser.go for details)
		//      rulesJSON (string), breakpointsJSON (string), themeColorsJSON (string),
		//      themeSpacingJSON (string), themeFontSizeJSON (string), ... , isDarkMode (bool)
		//   JS Returns: JSON string (map[string]string) of media queries to CSS, or an error string.
		"parseResponsiveRules": js.FuncOf(ParseResponsiveRules),
	}

	// Expose the 'exportedFunctions' map to JavaScript by setting it as a property
	// on the global 'window' object. JavaScript will be able to access these
	// functions via `window.sadsPocWasm.functionName()`.
	js.Global().Set("sadsPocWasm", js.ValueOf(exportedFunctions))

	// Log a message to the browser's developer console to indicate that the
	// WASM module has loaded successfully and the functions are exported.
	// This is helpful for debugging and confirming the module is active.
	js.Global().Get("console").Call("log", "SADS Go/WASM module loaded and functions exported to window.sadsPocWasm.")

	// Block the main function indefinitely. If main exits, the WASM module
	// might be terminated, and JavaScript would no longer be able to call
	// the exported Go functions.
	<-c
}
