# Exploring Go/WebAssembly for SADS Engine Enhancements

This document outlines a conceptual exploration into using Go compiled to WebAssembly (WASM) to potentially enhance or rewrite parts of the Semantic Attribute-Driven Styling (SADS) engine. The SADS engine source is currently implemented in TypeScript (`public/ts/sads-style-engine.ts`) and compiled to JavaScript.

## 1. Introduction & Concept

The core idea is to leverage Go's performance characteristics and static typing for computationally intensive or complex logic within the SADS (Semantic Attribute-Driven Styling) engine. The SADS engine itself is currently experimental, and this exploration looks at using Go compiled to WebAssembly (WASM) for parts of its rule-based logic. Go code would be compiled into a WASM module, which can then be loaded and called by the main JavaScript application running in the browser. This could lead to a hybrid SADS engine where JavaScript handles DOM interaction and overall orchestration, while Go/WASM modules tackle specific processing tasks.

It's important to note, as stated in `docs/styling_approach.md`, that the "AI" in "SADS AI experimental" (a term sometimes used to describe the overall SADS project ambition) is currently an aspirational term. The existing SADS engine, and thus the parts being considered for Go/WASM porting in this document, are rule-based. This WASM exploration focuses on performance and architectural enhancements for this rule-based system.

## 2. Rationale

Using Go/WASM for parts of SADS could offer several benefits:

- **Performance:** Go is a compiled language, and WASM executes at near-native speeds. For a SADS engine that might parse many attributes, perform complex theme lookups, or evaluate intricate responsive rules across a large DOM, Go/WASM could offer significant performance improvements over pure JavaScript.
- **Static Typing:** Go's static type system can help catch errors at compile time, potentially leading to more robust and maintainable code for the core styling logic.
- **Concurrency (Advanced):** While likely an over-optimization for the current SADS implementation, Go's built-in support for concurrency (goroutines and channels) could be an advantage if SADS were to evolve to handle very complex, parallelizable styling calculations or real-time updates.
- **Code Reusability/Portability:** Go code is portable. If SADS logic were also needed server-side (e.g., for pre-rendering SADS styles), having parts in Go might facilitate this.

## 3. Candidate SADS Logic in SADS Engine for Go/WASM

The existing SADS engine (source: `public/ts/sads-style-engine.ts`) contains several pieces of logic that could be candidates for a rewrite in Go:

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
- **Build Process Complexity:** Integrating Go compilation and WASM generation into the existing (or a new) frontend build process adds complexity. (See Section 8.1 for how the PoC currently handles this).
- **Debugging:** Debugging Go code running as WASM in the browser can be more challenging than debugging JavaScript, though browser devtools are continually improving WASM support.
- **Maturity of Ecosystem:** While Go's WASM support is good, the ecosystem for frontend-focused Go/WASM development (especially direct DOM manipulation libraries) is less mature than JavaScript's.

This exploration represents a significant R&D effort but could lead to a highly performant and robust SADS engine. While the current focus is on the rule-based SADS engine, these Go/WASM enhancements could also serve as a foundational component for potential future AI-driven SADS capabilities (such as those brainstormed in `docs/feature_ideas.md`).

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

This section details the design for the Go function that will implement the "Resolving a Single SADS Color Token" PoC. The SADS attribute and theme token definitions could align with those defined in `proto/sads_attributes.proto` for consistency across JS and potential Go implementations.

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

### PreSetup:

The actual implementation of the Proof-of-Concept (PoC) function (`ResolveSadsColorToken` / `resolveColor`) in Go, its compilation to WASM, and its integration into the existing TypeScript SADS engine (source: `public/ts/sads-style-engine.ts`) are significant development tasks. These tasks include:

- Setting up a Go development environment suitable for WASM compilation.
- Writing and testing the Go code for the PoC function.
- Compiling the Go code to a `.wasm` binary file.
- Integrating the `wasm_exec.js` glue code (or similar) for loading and running the WASM module in the browser.
- Modifying the TypeScript SADS engine to correctly call the exported WASM function and use its results.
- Thoroughly testing the hybrid TS/WASM functionality, including performance and bundle size analysis.

Beyond the initial PoC, porting more substantial parts of the SADS engine to Go/WASM would involve further design, implementation, and testing cycles. This document aims to provide the initial direction and considerations for such an undertaking. The user (developer) will be responsible for these implementation efforts.

## 9. Next Steps: Focused PoC Implementation (Follow-up Task Brief)

This section outlines the objectives and key steps for a follow-up task to implement a Proof-of-Concept (PoC) for the Go/WASM SADS engine enhancement.

**Objective:**
Implement a specific, self-contained piece of SADS core logic in Go, compile it to WebAssembly (WASM), and integrate it into the existing TypeScript-based SADS engine. The primary goal is to validate the feasibility of this hybrid approach, understand the development workflow, and assess basic interoperability. The "Resolving a Single SADS Color Token" function, as detailed in Section 7, remains a good candidate for this PoC.

**Leveraging Existing Infrastructure:**

- **Protobuf Definitions:** The SADS attribute schema, including tokens and value structures, is defined in `proto/sads_attributes.proto`. The Go implementation should leverage these definitions by generating Go types from this `.proto` file. This ensures data consistency between the TypeScript and Go portions of the SADS ecosystem.
- **Build Process:**
  - The `npm run generate-proto` script currently generates Python and TypeScript stubs. This script will need to be extended (or a new one created, e.g., `generate-proto:go`) to include `protoc-gen-go` for generating Go types from the `.proto` files into a suitable Go workspace directory.
  - The Go WASM compilation step will need to be added to the project's build tooling (potentially as a new `npm` script).

**Key Technical Steps for the Follow-up Task:**

1.  **Go Environment for WASM:** Ensure a Go development environment is set up with the correct version (supporting WASM compilation, typically Go 1.11+).
2.  **Generate Go Types from Protobuf:**
    - Install `protoc-gen-go` and `protoc-gen-go-grpc` (if any gRPC definitions were planned, though not strictly needed for basic message types).
    - Update `package.json`'s `generate-proto` script (or add `generate-proto:go`) to compile `.proto` files (especially `sads_attributes.proto` and its dependencies like `common.proto`) into Go data structures. These should be output to a new Go module/package dedicated to the SADS WASM logic (e.g., `wasm/sads_processor/`).
3.  **Implement SADS Logic in Go:**
    - Create a Go module (e.g., in a new `wasm/` directory).
    - Implement the chosen PoC function (e.g., `ResolveSadsColorToken`). This function should accept parameters (e.g., JSON strings for SADS token, theme color map, and dark mode status) that can be easily passed from JavaScript. It should use the generated Go Protobuf types internally for processing where applicable.
    - The function should be exposed to JavaScript using `syscall/js.FuncOf`.
4.  **Compile Go to WASM:** Compile the Go module into a `.wasm` binary file (e.g., `sads_poc.wasm`).
5.  **JavaScript Glue Code:**
    - Copy or include Go's `wasm_exec.js` file into the `public/js/` (or `public/vendor/`) directory. This file is necessary to load and run Go-compiled WASM.
    - Create a TypeScript module (e.g., `public/ts/sadsWasmLoader.ts`) responsible for:
      - Loading the `.wasm` binary.
      - Instantiating it using `wasm_exec.js`.
      - Exposing the Go functions (like `sadsPocWasm.resolveColor`) in a type-safe way to the rest of the TypeScript application.
6.  **Integrate into `SADSEngine`:**
    - Modify `public/ts/sads-style-engine.ts` (specifically, the relevant part like color resolution in `_mapSemanticValueToActual`).
    - Conditionally (or directly for the PoC) call the WASM-loaded function instead of the original TypeScript logic for the chosen piece of functionality.
    - Handle any data marshalling (e.g., JS object to JSON string for Go, string from Go back to JS).
7.  **Build Process for WASM:**
    - Ensure the `.wasm` file and `wasm_exec.js` are copied to an appropriate directory (e.g., `public/dist/wasm/` or alongside `main.js`) by the build process (`build.py` or an npm script) so they are accessible by the client.
    - The `asset_bundling.py` might not directly bundle `.wasm` files; they are usually loaded separately or via specific bundler plugins. For now, focus on making it available.
8.  **Testing:**
    - Update or create test pages (e.g., extend `nl-sads-test.html` or a new page) to specifically invoke and verify the functionality of the WASM-powered SADS logic.
    - Compare results with the pure TypeScript implementation to ensure correctness.

**Success Criteria for PoC:**

- The Go function, compiled to WASM, correctly implements the targeted SADS logic (e.g., resolves color tokens accurately).
- The TypeScript SADS engine can successfully load the WASM module and call the exported Go function.
- The results from the WASM function are correctly used by the SADS engine.
- The overall SADS functionality (for the tested piece) remains correct.
- (Optional Bonus) Initial, even if qualitative, observations on any noticeable performance difference or impact on bundle size.

This detailed brief should provide a clear roadmap for the engineer undertaking the Go/WASM PoC implementation.

### PostSetup: 8.1. Asset Management and Loading

- **New Files**:
  - `sads_wasm_poc/color_resolver.go`: Contains the Go source code for `ResolveSadsColorToken` and the `main` function to export it.
  - `sads_wasm_poc/sads_poc.wasm`: The compiled WebAssembly module (generated by `go build`).
  - `sads_wasm_poc/wasm_exec.js`: The standard Go JavaScript glue code, copied from the Go installation (`$(go env GOROOT)/misc/wasm/`).
  - `public/js/modules/wasmLoader.js`: A new JavaScript module created to handle the asynchronous loading of `wasm_exec.js` and `sads_poc.wasm`.

- **Build Process for WASM Assets:**
  - **Manual Go Compilation:** The Go code in `sads_wasm_poc/color_resolver.go` must be manually compiled by the developer into `sads_wasm_poc/sads_poc.wasm` using the command:
    `GOOS=js GOARCH=wasm go build -o sads_wasm_poc/sads_poc.wasm sads_wasm_poc/color_resolver.go`
    This step is currently _not_ integrated into the project's main `npm run build` (which runs `python build.py`). Automating this Go compilation within the main build script could be a future enhancement.
  - **Copying WASM Assets (`build_protocols/asset_bundling.py`):**
    - The `DefaultAssetBundler` class in `build_protocols/asset_bundling.py` was augmented with a new method `copy_wasm_assets`.
    - This Python method is responsible for copying the pre-compiled `sads_poc.wasm` (from the manual step above) and `wasm_exec.js` from the local `sads_wasm_poc/` directory to `dist/assets/wasm/`.
    - _Assumption_: The main `build.py` script calls this `copy_wasm_assets` method as part of its asset handling.

- **HTML Integration (`public/index.html`):**
  - A script tag for `public/js/modules/wasmLoader.js` was added to `index.html` _before_ the main application script (`public/dist/main.js`).
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
    if (
      window.sadsPocWasm &&
      typeof window.sadsPocWasm.resolveColor === "function"
    ) {
      try {
        const themeColorsJson = JSON.stringify(this.theme.colors);
        const resolvedColor = window.sadsPocWasm.resolveColor(
          valueStr,
          themeColorsJson,
          isDarkMode
        );
        if (
          typeof resolvedColor === "string" &&
          !resolvedColor.startsWith("Error:")
        ) {
          return resolvedColor; // Use WASM resolved color
        }
        // ... (handle WASM error, fallthrough to JS)
      } catch (wasmError) {
        // ... (handle WASM call error, fallthrough to JS)
      }
    }
    // JavaScript fallback logic for colors
    const colorKey = isDarkMode ? `${valueStr}-dark` : valueStr;
    return (
      this.theme.colors[colorKey] || this.theme.colors[valueStr] || valueStr
    );
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

## 9. Future Development: Next Steps for Go/WASM in SADS

The successful PoC integration of `resolveColor` opens several avenues for further enhancing the SADS engine with Go/WebAssembly. The following are suggestions for an AI developer (like Jules) to continue this work, building upon the patterns and infrastructure established:

### 9.1. Porting Additional SADS Logic to Go/WASM

The primary goal is to identify and port other self-contained, computationally beneficial parts of `sads-style-engine.js`.

1.  **Target: `_mapSadsPropertyToCss` function**
    - **Objective**: Rewrite the SADS property key to CSS property name mapping (e.g., `bgColor` to `background-color`) in Go.
    - **Go Function Design**:
      - Name: `MapSadsKeyToCssProperty(sadsKeyString string) string`
      - Input: A single string representing the SADS property key (e.g., "bgColor", "paddingTop").
      - Output: A string representing the corresponding CSS property name (e.g., "background-color", "padding-top"), or an empty string/original key if no mapping exists.
      - Logic: Implement the mapping currently found in `_mapSadsPropertyToCss` within `sads-style-engine.js`. This is mostly a map lookup.
    - **JavaScript Integration**:
      - Export this new Go function (e.g., as `window.sadsPocWasm.mapSadsKey`).
      - Modify `sads-style-engine.js` in `_mapSadsPropertyToCss` to call this WASM function, with a JS fallback.
    - **Considerations**: This function is called frequently. Benchmark the overhead of WASM calls vs. the JS map lookup. The benefit might be minimal unless combined with other operations in WASM.

2.  **Target: Non-Color Value Resolution in `_mapSemanticValueToActual`**
    - **Objective**: Extend Go/WASM capabilities to resolve other semantic tokens like spacing (`m`, `l`), font sizes, border radius, etc.
    - **Go Function Design (Option 1: Extend `ResolveSadsColorToken`)**:
      - Modify `ResolveSadsColorToken` to `ResolveSadsValueToken(tokenString, themeCategoryJsonString, categoryNameString) string`.
      - Inputs: SADS token, JSON string of the relevant theme category (e.g., `theme.spacing`, `theme.fontSize`), and the category name (e.g., "spacing", "fontSize").
      - Output: Resolved CSS value string.
    - **Go Function Design (Option 2: New Specific Functions)**:
      - `ResolveSadsSpacingToken(tokenString, themeSpacingJsonString) string`
      - `ResolveSadsFontSizeToken(tokenString, themeFontSizeJsonString) string`
      - This might be cleaner if theme structures vary significantly.
    - **JavaScript Integration**:
      - Export the new/modified Go function(s).
      - Update `_mapSemanticValueToActual` in `sads-style-engine.js` to delegate to these WASM functions for respective categories, with JS fallbacks.
    - **Theme Data**: This requires passing different parts of the theme object (e.g., `this.theme.spacing`, `this.theme.fontSize`) as JSON strings to the WASM functions.

3.  **Target: `_parseResponsiveRules` (More Complex)**
    - **Objective**: Port the logic for parsing responsive rule strings and generating media query-specific CSS rules to Go/WASM.
    - **Go Function Design**: This would be significantly more complex.
      - Input: Responsive rules JSON string, theme breakpoints JSON string, possibly the `targetSelector` if CSS is generated directly.
      - Output: A JSON string representing structured media queries and their corresponding CSS rules, or a fully formatted CSS string block.
      - Logic: Replicate JSON parsing, breakpoint lookups, and iterating through styles to call other WASM functions (like `ResolveSadsValueToken` and `MapSadsKeyToCssProperty`) internally.
    - **JavaScript Integration**: Modify `_parseResponsiveRules` in `sads-style-engine.js` to call this comprehensive WASM function.
    - **Benefits**: Could offer significant performance gains if responsive rule processing is extensive and involves many lookups.

### 9.2. Performance Benchmarking

- **Objective**: Quantify the performance difference between JavaScript and Go/WASM implementations for the ported functions.
- **Task**:
  - Create dedicated benchmark tests (e.g., using `performance.now()` in JavaScript).
  - For `resolveColor`, run the JS version and WASM version in a loop (e.g., 10,000+ iterations) with various inputs and measure execution time.
  - Compare results, considering the overhead of JS-to-WASM calls versus the Go execution speed.
  - Document findings in `docs/wasm_sads_exploration.md`.

### 9.3. Build Process Automation

- **Objective**: Integrate the Go WASM compilation step into the main project build process.
- **Task**:
  - Modify `build.py` (or the script it calls, like `asset_bundling.py`) to execute the `GOOS=js GOARCH=wasm go build ...` command.
  - This might involve using Python's `subprocess` module.
  - Ensure it runs before `copy_wasm_assets` and that errors during Go compilation are handled and reported by the build script.
  - This would remove the need for developers to manually compile the Go/WASM module.

### 9.4. Advanced: Consolidating SADS Logic in Go

- **Objective**: Create a single, more comprehensive Go/WASM function that takes all SADS attributes for an element and the full theme, then returns all computed CSS properties (perhaps as a JSON string map of CSS property to value).
- **Go Function Design**:
  - `ProcessElementSadsAttributes(attributesJsonString, themeJsonString, isDarkMode bool) string` (returning JSON map of CSS props)
  - This function would internally call the Go versions of `MapSadsKeyToCssProperty` and `ResolveSadsValueToken` for each relevant SADS attribute.
- **JavaScript Integration**:
  - `_generateBaseCss` in `sads-style-engine.js` would primarily call this function.
  - JS would then format the returned CSS properties map into a CSS string.
- **Benefits**: Reduces the number of JS-to-WASM calls per element, potentially improving performance by keeping more logic within the WASM module for a single element's processing.

**AI Developer Prompt Structure for Next Task (Example based on 9.1.1):**

```
**Task Objective:**
Port the `_mapSadsPropertyToCss` function from `public/js/sads-style-engine.js` to Go/WebAssembly.

**Background & Context:**
We have successfully integrated a Go/WASM function for SADS color resolution. This task continues the effort by porting another piece of the SADS engine logic as outlined in `docs/wasm_sads_exploration.md` (Section 9.1.1).

**Specific Requirements:**

1.  **Go Implementation (`sads_wasm_poc/color_resolver.go` or a new file):**
    *   Create a new Go function, e.g., `MapSadsKeyToCssProperty(sadsKey string) string`.
    *   It should take a SADS property key (e.g., "bgColor", "paddingLeft", "flexJustify") as a string.
    *   It should return the corresponding CSS property name (e.g., "background-color", "padding-left", "justify-content").
    *   If no mapping exists, it can return the original key or an empty string (document the chosen behavior).
    *   The mapping logic should replicate that of `_mapSadsPropertyToCss` in `sads-style-engine.js`.
    *   Update the Go `main` function to export this new function to JavaScript (e.g., under `window.sadsPocWasm.mapSadsKey`).
2.  **JavaScript Integration (`public/js/sads-style-engine.js`):**
    *   Modify the existing `_mapSadsPropertyToCss(sadsPropertyKey)` function.
    *   If `window.sadsPocWasm.mapSadsKey` is available, call it. Use its result.
    *   If the WASM function is not available or returns an empty/error indicator, fall back to the existing JavaScript mapping logic.
3.  **Test Harness Update (`sads_wasm_poc/test_harness.js` and `test_harness.html`):**
    *   Add new test cases to `test_harness.js` specifically for `mapSadsKey`.
    *   Include tests for various known SADS keys and some unknown keys to verify fallback or error handling.
    *   Log inputs and outputs.
4.  **Documentation:**
    *   Briefly update `docs/wasm_sads_exploration.md` to note the completion of this porting task.
    *   Ensure Go code is commented.

**Expected Deliverables:**
*   Updated Go source file(s).
*   Updated `public/js/sads-style-engine.js`.
*   Updated `sads_wasm_poc/test_harness.js` and `test_harness.html`.
*   Updated compilation instructions if anything changed (though likely not for this specific task).
```

This provides a more structured guide for future development efforts.
The user (developer) will be responsible for the actual implementation of these further steps.
