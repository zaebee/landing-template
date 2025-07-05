package main

import (
	"syscall/js"
)

// main function to expose Go functions to JavaScript.
// This bridge now initializes all WASM-exported functions from different files
// (though currently they are all in value_resolver.go, this structure allows expansion).
func main() {
	c := make(chan struct{}, 0) // Keep the Go program alive

	exportedFunctions := map[string]interface{}{
		// From value_resolver.go
		"resolveColor":     js.FuncOf(ResolveSadsColorToken), // Kept for backward compatibility
		"resolveSadsValue": js.FuncOf(ResolveSadsGenericValue),
		// From responsive_rules_parser.go
		"parseResponsiveRules": js.FuncOf(ParseResponsiveRules),
	}

	js.Global().Set("sadsPocWasm", js.ValueOf(exportedFunctions))

	// Log that WASM module is ready and functions are exported
	// This can be seen in the browser's developer console.
	js.Global().Get("console").Call("log", "SADS Go/WASM module loaded and functions exported to window.sadsPocWasm.")


	<-c // Block main from exiting, allowing JS to call exported functions
}
