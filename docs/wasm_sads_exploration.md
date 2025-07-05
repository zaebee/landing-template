# Exploring Go/WebAssembly for SADS Engine Enhancements

This document outlines a conceptual exploration into using Go compiled to WebAssembly (WASM) to potentially enhance or rewrite parts of the Semantic Attribute-Driven Styling (SADS) engine, which is currently implemented in JavaScript (`public/js/sads-style-engine.js`).

## 1. Introduction & Concept

The core idea is to leverage Go's performance characteristics and static typing for computationally intensive or complex logic within the SADS engine. Go code would be compiled into a WASM module, which can then be loaded and called by the main JavaScript application running in the browser. This could lead to a hybrid SADS engine where JavaScript handles DOM interaction and overall orchestration, while Go/WASM modules tackle specific processing tasks.

## 2. Rationale

Using Go/WASM for parts of SADS could offer several benefits:

- **Performance:** Go is a compiled language, and WASM executes at near-native speeds. For a SADS engine that might parse many attributes, perform complex theme lookups, or evaluate intricate responsive rules across a large DOM, Go/WASM could offer significant performance improvements over pure JavaScript.
- **Static Typing:** Go's static type system can help catch errors at compile time, potentially leading to more robust and maintainable code for the core styling logic.
- **Concurrency (Advanced):** While likely an over-optimization for the current SADS implementation, Go's built-in support for concurrency (goroutines and channels) could be an advantage if SADS were to evolve to handle very complex, parallelizable styling calculations or real-time updates.
- **Code Reusability/Portability:** Go code is portable. If SADS logic were also needed server-side (e.g., for pre-rendering SADS styles), having parts in Go might facilitate this.

## 3. Candidate SADS Logic in `sads-style-engine.js` for Go/WASM

The existing `sads-style-engine.js` contains several pieces of logic that could be candidates for a rewrite in Go:

- **Attribute Parsing & Collection:** The logic that iterates through DOM element datasets to find and collect all `data-sads-*` attributes.
- **Theme Value Resolution (`_mapSemanticValueToActual` function):** This is a strong candidate. It involves:
  - Looking up semantic tokens (e.g., `surface`, `m`, `text-primary`) in the theme object.
  - Handling dark mode variations (e.g., `surface-dark`).
  - Processing custom values (e.g., `custom:10px`).
  - Mapping SADS property keys to CSS property names (e.g., `bgColor` to `background-color` in `_mapSadsPropertyToCss`).
- **CSS Rule String Generation:** The construction of the final CSS rule strings for each element.
- **Responsive Rule Processing (`_parseResponsiveRules` function):** This involves parsing JSON-like strings, looking up breakpoint definitions, and applying nested styling logic.

## 4. High-Level Architecture

A hybrid SADS engine using Go/WASM might look like this:

1.  **JavaScript Orchestrator (e.g., modified `sads-style-engine.js` or a new layer):**

    - Still responsible for initially finding all elements with `data-sads-component`.
    - For each SADS component and its SADS-attributed children:

      - Collects all `data-sads-*` attributes (perhaps as a simple key-value map or JSON string).
      - Retrieves the current SADS theme (e.g., as a JSON string).
      - Optionally, gathers viewport context (e.g., current browser width for responsive styling) and passes it as JSON.
      - Calls one or more exported functions from the Go/WASM module. For example:

        ```javascript
        // Assume sadsWasmModule is loaded and exposes processElementSads
        const sadsData = {
          attributes: {
            /*...element.dataset...*/
          },
          viewport: { width: window.innerWidth },
        };
        const themeJson = JSON.stringify(currentSadsTheme); // currentSadsTheme from sads-default-theme.js

        // Call the WASM function
        const cssRulesString = sadsWasmModule.processElementSads(
          JSON.stringify(sadsData),
          themeJson
        );
        ```

      - Takes the CSS rule string(s) returned by the WASM module.
      - Injects these CSS rules into the dynamic stylesheet (`<style id="sads-dynamic-styles">`) in the document head. This part would remain in JavaScript due to WASM's limited direct DOM access.

2.  **Go/WASM Module (`sads_processor.go` compiled to `sads.wasm`):**
    - Loaded by JavaScript.
    - Exposes functions to JavaScript (e.g., `processElementSads`).
    - These functions would take input from JavaScript (e.g., element attributes JSON, theme JSON, viewport context JSON).
    - Perform the core SADS logic (parsing attributes, resolving theme values, applying responsive logic, generating CSS rule strings) internally in Go.
    - Return the resulting CSS strings (or an intermediate structured representation) back to JavaScript.

### Example Go/WASM Structure (Conceptual Pseudo-code)

```go
// sads_processor.go
package main

import (
	"encoding/json" // For handling JSON data from/to JavaScript
	"fmt"           // For string formatting (generating CSS)
	"syscall/js"    // Core package for JavaScript interop
	// Potentially other Go packages for string manipulation, data structures, etc.
)

// Define Go structs to model the SADS theme, attributes, viewport context, etc.
// These would be used after deserializing JSON input from JavaScript.
// type SadsTheme struct { ... }
// type SadsElementData struct { Attributes map[string]string; Viewport map[string]int }

// processElementSads is a Go function exposed to JavaScript via WASM.
// It takes element data and theme data (as JSON strings) and returns generated CSS (as a string).
func processElementSads(this js.Value, args []js.Value) interface{} {
	if len(args) < 2 { // Expecting sadsDataJson and themeJson
		// In a real scenario, might return an error object or specific error string
		return js.ValueOf("Error: processElementSads expects at least 2 arguments: sadsDataJson and themeJson.")
	}

	sadsDataJson := args[0].String()
	themeJson := args[1].String()
	// Optional: viewportContextJson := args[2].String()

	// --- Step 1: Deserialize JSON inputs into Go structs ---
	// var sadsData SadsElementData
	// if err := json.Unmarshal([]byte(sadsDataJson), &sadsData); err != nil { ... handle error ... }
	// var theme SadsTheme
	// if err := json.Unmarshal([]byte(themeJson), &theme); err != nil { ... handle error ... }

	// --- Step 2: Implement Core SADS Logic in Go ---
	// This is where the SADS engine's core processing would be re-implemented.
	// - Iterate through sadsData.Attributes.
	// - For each attribute (e.g., "data-sads-bg-color: surface"):
	//     - Map the SADS key (e.g., "bgColor") to its CSS property name ("background-color").
	//       (This would replicate _mapSadsPropertyToCss from the JS engine).
	//     - Resolve the semantic value (e.g., "surface") against the deserialized 'theme' object,
	//       considering dark mode if that state is passed or part of the theme structure.
	//       (This would replicate _mapSemanticValueToActual from the JS engine).
	//     - Consider responsive rules if viewportContextJson was passed and parsed.
	// - Accumulate all resolved CSS property-value pairs.

	// --- Step 3: Construct CSS Rule String(s) ---
	// Example:
	// finalCssProperties := "background-color: #resolvedColor; padding: resolvedPadding;" // Simplified
	// Assume a unique class name is generated/passed by JS for targeting this element.
	// For this example, let's say the class name is passed within sadsDataJson or is a fixed example.
	// uniqueClassName := "sads-wasm-element-" + generateUniqueID()
	// cssRule := fmt.Sprintf(".%s { %s }", uniqueClassName, finalCssProperties)

    // Placeholder for actual, complex CSS generation logic
    cssRule := "/* Go/WASM generated CSS would be here */"
    // For a real implementation, this string would be built based on the processed SADS attributes.
    // For example:
    // cssRule = fmt.Sprintf("background-color: %s; color: %s;", resolvedBgColor, resolvedTextColor)


	// Return the generated CSS string to JavaScript
	return js.ValueOf(cssRule)
}

// main function to set up WASM module and expose Go functions to JavaScript.
func main() {
	c := make(chan struct{}, 0) // Channel to keep the Go program running

	// Expose the processElementSads function to JavaScript under `window.sadsWasm.processElementSads`
	js.Global().Set("sadsWasm", js.ValueOf(map[string]interface{}{
		"processElementSads": js.FuncOf(processElementSads),
		// Other SADS utility functions could be exposed here too.
	}))

	<-c // Wait indefinitely, keeping the WASM module alive and responsive to JS calls.
}
```

## 5. Key Challenges & Considerations

- **DOM Interaction:** WASM cannot directly and efficiently manipulate the DOM. All DOM reads (if needed beyond initial attribute collection) and writes (injecting styles) must go through JavaScript calls (JS interop). This can introduce overhead. The strategy of JS collecting data, WASM processing it, and JS applying results is generally preferred.
- **Data Serialization/Deserialization:** Passing data (especially complex objects like the theme or attribute maps) between JavaScript and Go/WASM often involves serialization to JSON and deserialization back. This has a performance cost. For very frequent, small calls, this overhead might outweigh WASM's raw execution speed benefits.
- **Bundle Size:** The compiled WASM binary (`.wasm` file) and the necessary JavaScript glue code (`wasm_exec.js` for Go) will add to the application's total download size. This needs to be weighed against potential performance gains.
- **Build Process Complexity:** Integrating Go compilation and WASM generation into the existing (or a new) frontend build process adds complexity.
- **Debugging:** Debugging Go code running as WASM in the browser can be more challenging than debugging JavaScript, though browser devtools are continually improving WASM support.
- **Maturity of Ecosystem:** While Go's WASM support is good, the ecosystem for frontend-focused Go/WASM development (especially direct DOM manipulation libraries) is less mature than JavaScript's.

This exploration represents a significant R&D effort but could lead to a highly performant and robust SADS engine, especially if combined with AI-driven styling concepts.

## 6. Initial Proof-of-Concept (PoC) Target

For an initial Proof-of-Concept, the goal is to select a small yet representative piece of logic from the existing `sads-style-engine.js` to rewrite in Go and compile to WASM.

**Chosen Functionality for PoC: Resolving a Single SADS Color Token**

This functionality is primarily handled within the `_mapSemanticValueToActual` method in the current JavaScript SADS engine, specifically when dealing with color properties.

**Inputs to the Go/WASM function:**

- `sadsColorToken`: A string representing the semantic color name (e.g., `"surface"`, `"text-primary"`, `"text-accent"`).
- `colorsThemeJson`: A JSON string representing the `colors` object from the SADS theme (e.g., `{"surface": "#FFFFFF", "surface-dark": "#2a2a2a", ...}`).
- `isDarkMode`: A boolean indicating if dark mode is currently active.

**Output from the Go/WASM function:**

- A string representing the resolved CSS color value (e.g., `"#FFFFFF"`, `"#2a2a2a"`). If the token cannot be resolved, it might return the original token or an empty string.

**Why this is a good PoC target:**

- **Core SADS Logic:** Color resolution, including dark mode adaptation, is a fundamental part of the SADS theming system.
- **Data Handling:** It involves passing structured data (the colors theme map as JSON) from JavaScript to Go and simple data (boolean, strings).
- **Conditional Logic:** The Go implementation will need to handle the dark mode logic (checking for and preferring `token-dark` if `isDarkMode` is true).
- **Manageable Complexity:** The logic is self-contained enough for an initial PoC while still being a meaningful part of the engine.
- **Clear Verification:** The output (a color string) is easy to test and verify against the expected output from the JavaScript version.
- **Foundation for Expansion:** Successfully implementing this PoC provides a solid base for porting more complex value resolution logic (like spacing, font sizes) or even entire attribute-to-CSS-property mapping.

## 7. Go Implementation Design for PoC Function: `ResolveSadsColorToken`

This section details the design for the Go function that will implement the "Resolving a Single SADS Color Token" PoC.

**Go Function Name (Exported to JS):** `resolveColor` (within a `sadsPocWasm` global object)

**File:** `sads_poc_module.go` (example name)

**1. Go Function Signature (Internal Go name: `ResolveSadsColorToken`):**
The Go function itself will be wrapped by `js.FuncOf` for export.

```go
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
    // Implementation details below
}
```

**2. Input Data Structures (from JS to Go via `args`):**

- **`sadsColorToken` (string):** The raw semantic token from a SADS attribute.
  - Example: `"surface"`, `"text-primary"`.
- **`colorsThemeJson` (string):** A JSON string representing the `colors` object from the SADS theme.
  - Example JSON: `{"surface": "#FFFFFF", "surface-dark": "#2a2a2a", "text-primary": "#333333", ...}`
- **`isDarkMode` (boolean):** `true` if dark mode is active, `false` otherwise.

**3. Go Implementation Sketch for `ResolveSadsColorToken`:**

```go
package main

import (
	"encoding/json"
	"fmt"
	"strings"
	"syscall/js"
)

func ResolveSadsColorToken(this js.Value, args []js.Value) interface{} {
	// --- 1. Argument Validation & Extraction ---
	if len(args) != 3 {
		// Consider returning a JS Error object or a structured error response
		return js.ValueOf("Error: ResolveSadsColorToken expects 3 arguments: sadsColorToken (string), colorsThemeJson (string), isDarkMode (bool)")
	}
	sadsColorToken := args[0].String()
	colorsThemeJson := args[1].String()
	isDarkMode := args[2].Bool()

	if sadsColorToken == "" {
		return js.ValueOf("") // Return empty for empty token, or original token
	}

	// --- 2. Deserialize colorsThemeJson into a Go map[string]string ---
	var colorsMap map[string]string
	err := json.Unmarshal([]byte(colorsThemeJson), &colorsMap)
	if err != nil {
		// Error during JSON parsing
		return js.ValueOf(fmt.Sprintf("Error deserializing colorsThemeJson: %v", err)) // Return original token or error
	}

	// --- 3. Core Resolution Logic (mimicking _mapSemanticValueToActual for colors) ---
	resolvedValue := sadsColorToken // Default to original token if no match is found

	// Handle "custom:" prefix (if this specific logic is part of the PoC)
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
	// The JS side can then decide if this original token is a valid CSS color itself.
	return js.ValueOf(resolvedValue)
}

// main function to expose the Go function to JavaScript
func main() {
	c := make(chan struct{}, 0) // Keep the Go program alive
	js.Global().Set("sadsPocWasm", js.ValueOf(map[string]interface{}{
		"resolveColor": js.FuncOf(ResolveSadsColorToken),
	}))
	<-c // Block main from exiting, allowing JS to call exported functions
}
```

**4. Expected Output (from Go/WASM function back to JavaScript):**

- A JavaScript string (`js.Value` containing a string) representing the resolved CSS color value.
  - Examples: `"#FFFFFF"`, `"#2a2a2a"`, `"red"` (if a `custom:red` token was processed).
- If the token cannot be resolved against the theme, it will return the original `sadsColorToken` string.
- If there's an error (e.g., argument mismatch, JSON parsing failure), an error message string is returned.

**5. JavaScript Call Example (Conceptual):**
This shows how `sads-style-engine.js` might call the WASM function once `sadsPocWasm.wasm` is loaded and `sadsPocWasm.resolveColor` is available on the `window` object.

```javascript
// Assuming sadsDefaultTheme.colors is available
const themeColorsJsonString = JSON.stringify(sadsDefaultTheme.colors);
const semanticToken = "surface"; // Example token
const isCurrentlyDarkMode = document.body.classList.contains("dark-mode");

if (
  window.sadsPocWasm &&
  typeof window.sadsPocWasm.resolveColor === "function"
) {
  try {
    const resolvedCssColor = window.sadsPocWasm.resolveColor(
      semanticToken,
      themeColorsJsonString,
      isCurrentlyDarkMode
    );
    console.log(
      `SADS token "${semanticToken}" (dark: ${isCurrentlyDarkMode}) resolved by Go/WASM to: "${resolvedCssColor}"`
    );
    // This resolvedCssColor would then be used to construct a CSS rule.
  } catch (e) {
    console.error("Error calling Go/WASM sadsPocWasm.resolveColor:", e);
  }
} else {
  console.error(
    "Go/WASM function sadsPocWasm.resolveColor not found on window."
  );
}
```

This detailed design for the PoC function provides a clear contract for implementation, covering data types, error handling considerations, and the core logic to be ported from JavaScript to Go.

## 8. PoC Implementation and Integration into SADS Engine (Color Resolution)

The initial Proof-of-Concept (PoC) focusing on the `ResolveSadsColorToken` function was successfully implemented and integrated into the main `sads-style-engine.js`. This section details the key aspects of this integration.

### 8.1. Asset Management and Loading

- **New Files**:
    - `sads_wasm_poc/color_resolver.go`: Contains the Go source code for `ResolveSadsColorToken` and the `main` function to export it.
    - `sads_wasm_poc/sads_poc.wasm`: The compiled WebAssembly module (generated by `go build`).
    - `sads_wasm_poc/wasm_exec.js`: The standard Go JavaScript glue code, copied from the Go installation (`$(go env GOROOT)/misc/wasm/`).
    - `public/js/modules/wasmLoader.js`: A new JavaScript module created to handle the asynchronous loading of `wasm_exec.js` and `sads_poc.wasm`.

- **Build Process (`build_protocols/asset_bundling.py`):**
    - The `DefaultAssetBundler` class was augmented with a new method `copy_wasm_assets`.
    - This method copies `sads_poc.wasm` and `wasm_exec.js` from `sads_wasm_poc/` to `dist/assets/wasm/` during the build process.
    - *Assumption*: The main `build.py` script is expected to call this `copy_wasm_assets` method.

- **HTML Integration (`public/index.html`):**
    - A script tag for `public/js/modules/wasmLoader.js` was added to `index.html` *before* the main application script (`public/dist/main.js`).
    - `wasmLoader.js` makes `wasm_exec.js` and `sads_poc.wasm` (from `assets/wasm/`) available to the application.
    - It defines a global promise: `window.sadsPocWasmReadyPromise`. This promise resolves when the WASM module is loaded and `window.sadsPocWasm.resolveColor` is available, or rejects if loading fails.

    ```html
    <!-- Example snippet from index.html -->
    <script src="public/js/modules/wasmLoader.js" defer></script>
    <script src="public/dist/main.js" defer></script>
    ```

### 8.2. SADS Engine Modifications (`public/js/sads-style-engine.js`)

- **Asynchronous Operations:**
    - The primary styling method `applyStyles()` was made `async`. It now awaits `window.sadsPocWasmReadyPromise` before proceeding with style calculations. This ensures that if WASM is available, the engine waits for it.
    - If the promise rejects (WASM fails to load), a warning is logged, and the engine proceeds using JavaScript fallbacks for WASM-dependent logic (currently, color resolution).
    - The `updateTheme()` method was also made `async` as it calls `applyStyles()`.

- **WASM Call for Color Resolution:**
    - The `_mapSemanticValueToActual()` method, specifically the part handling `category === "colors"`, was updated:
        - It checks if `window.sadsPocWasm && window.sadsPocWasm.resolveColor` is available.
        - If yes, it calls `window.sadsPocWasm.resolveColor(token, JSON.stringify(this.theme.colors), this.isDarkMode)`.
        - If the WASM call is successful and returns a valid color string (not prefixed with "Error:"), that color is used.
        - If the WASM call returns an error string or an unexpected value, or if the call itself throws an error, a warning is logged, and the engine falls back to the original JavaScript-based color resolution logic.
        - If `window.sadsPocWasm.resolveColor` is not available (e.g., WASM failed to load entirely), the JavaScript fallback is used directly.

    ```javascript
    // Conceptual snippet from _mapSemanticValueToActual() in sads-style-engine.js
    if (category === "colors") {
      if (window.sadsPocWasm && typeof window.sadsPocWasm.resolveColor === 'function') {
        try {
          const themeColorsJson = JSON.stringify(this.theme.colors);
          const resolvedColor = window.sadsPocWasm.resolveColor(valueStr, themeColorsJson, isDarkMode);
          if (typeof resolvedColor === 'string' && !resolvedColor.startsWith("Error:")) {
            return resolvedColor; // Use WASM resolved color
          }
          // ... (handle WASM error, fallthrough to JS)
        } catch (wasmError) {
          // ... (handle WASM call error, fallthrough to JS)
        }
      }
      // JavaScript fallback logic for colors
      const colorKey = isDarkMode ? `${valueStr}-dark` : valueStr;
      return this.theme.colors[colorKey] || this.theme.colors[valueStr] || valueStr;
    }
    ```

### 8.3. Application Flow Adjustments

- **`public/js/modules/sadsManager.js`:**
    - `initSadsEngine()` and `reapplySadsStyles()` were made `async`.
    - They now correctly `await` the `sadsEngineInstance.applyStyles()` call.

- **`public/js/app.js`:**
    - `initializeApp()` now `await initSadsEngine()`.
    - `window.appGlobal.handleDarkModeToggle()` was made `async` and now `await reapplySadsStyles()`.
    - `window.appGlobal.setAppLanguage()` (already async) now correctly `await reapplySadsStyles()`.

### 8.4. Challenges and Considerations from Integration

- **Asynchronicity:** The primary challenge was managing the asynchronous loading of the WASM module. The Promise-based approach (`window.sadsPocWasmReadyPromise`) provided a clean way for the `SadsStyleEngine` to wait for WASM readiness.
- **Fallback Mechanism:** Implementing a robust fallback to JavaScript logic is crucial for cases where WASM might fail to load or if the WASM function itself encounters an error. This ensures the application remains functional.
- **Build Process:** Ensuring the WASM assets (`.wasm` file and `wasm_exec.js`) are correctly copied to the distribution directory and are accessible at runtime is vital. The new `copy_wasm_assets` in `asset_bundling.py` addresses this.
- **Debugging:** Debugging involved checking console logs from `wasmLoader.js` (for loading status) and `sads-style-engine.js` (for WASM call attempts and fallbacks). Browser developer tools for WASM are helpful but still maturing.
- **Initial Page Load:** The `defer` attribute on script tags for `wasmLoader.js` and `main.js` helps manage execution order, but careful coordination is needed to ensure `sadsPocWasmReadyPromise` is awaited correctly before SADS styling attempts to use it.

This integration demonstrates a viable path for incorporating Go/WASM modules into the SADS engine for specific functionalities, starting with color resolution. The patterns established here (asset bundling, WASM loader, async handling in the engine, JS fallbacks) can be reused for porting other SADS logic.

## 9. Note on Future Development and Implementation

The designs and concepts outlined in this document, along with the successful PoC integration, serve as a foundational guide for exploring further use of Go and WebAssembly to enhance the SADS engine.

Beyond this initial color resolution PoC, porting more substantial parts of the SADS engine to Go/WASM would involve similar design, implementation, and testing cycles. This document aims to provide the initial direction and considerations for such an undertaking. The user (developer) will be responsible for these implementation efforts.
