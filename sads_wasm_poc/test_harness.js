// sads_wasm_poc/test_harness.js

async function main() {
    const resultsContainer = document.getElementById('results-container');

    function logResult(testCaseName, inputs, output, error = false) {
        console.groupCollapsed(`Test Case: ${testCaseName}`);
        console.log("Inputs:", inputs);
        if (error) {
            console.error("Output (Error):", output);
        } else {
            console.log("Output (Success):", output);
        }
        console.groupEnd();

        const entry = document.createElement('div');
        entry.classList.add('log-entry');
        entry.innerHTML = `
            <p><strong>Test Case:</strong> ${testCaseName}</p>
            <p><span class="log-input">Inputs:</span> <code>${JSON.stringify(inputs)}</code></p>
            <p><span class="${error ? 'log-error' : 'log-output'}">Output:</span> <code>${output}</code></p>
        `;
        resultsContainer.appendChild(entry);
    }

    if (!WebAssembly.instantiateStreaming) { // Polyfill for older browsers
        WebAssembly.instantiateStreaming = async (resp, importObject) => {
            const source = await (await resp).arrayBuffer();
            return await WebAssembly.instantiate(source, importObject);
        };
    }

    const go = new Go();
    const wasmPath = 'sads_poc.wasm'; // Expected name of the compiled WASM file

    try {
        console.log(`Attempting to load WASM module from: ${wasmPath}`);
        const result = await WebAssembly.instantiateStreaming(fetch(wasmPath), go.importObject);
        go.run(result.instance);
        console.log("WASM module loaded and Go program started.");

        if (!window.sadsPocWasm || typeof window.sadsPocWasm.resolveColor !== 'function') {
            const errorMsg = "Error: sadsPocWasm.resolveColor function not found on window. Check Go export in main().";
            console.error(errorMsg);
            logResult("WASM Load Check", { wasmPath }, errorMsg, true);
            return;
        }
        logResult("WASM Load Check", { wasmPath }, "sadsPocWasm.resolveColor found on window.", false);


        // --- Test Cases ---

        const defaultThemeColors = {
            "primary": "#007bff",
            "primary-dark": "#0056b3",
            "secondary": "#6c757d",
            "secondary-dark": "#494f54",
            "accent": "rgba(255,0,0,0.7)",
            "accent-dark": "rgba(200,0,0,0.7)",
            "surface": "#ffffff",
            "surface-dark": "#2a2a2a",
            "text-primary": "#212529",
            "text-primary-dark": "#f8f9fa",
            "text-secondary": "#6c757d",
            "text-secondary-dark": "#adb5bd",
            "neutral": "#c0c0c0",
            "neutral-L1": "#d0d0d0",
            "neutral-L1-dark": "#b0b0b0",
            "neutral-D1": "#a0a0a0",
            "neutral-D1-dark": "#909090",
        };
        const themeColorsJson = JSON.stringify(defaultThemeColors);

        const testCases = [
            // Basic light mode
            { name: "Primary Light", token: "primary", theme: themeColorsJson, darkMode: false, expected: "#007bff" },
            // Basic dark mode
            { name: "Primary Dark", token: "primary", theme: themeColorsJson, darkMode: true, expected: "#0056b3" },
            // Token with -dark but dark mode is false (should use base)
            { name: "Accent Dark (Light Mode)", token: "accent", theme: themeColorsJson, darkMode: false, expected: "rgba(255,0,0,0.7)" },
            // Token with -dark and dark mode is true
            { name: "Accent Dark (Dark Mode)", token: "accent", theme: themeColorsJson, darkMode: true, expected: "rgba(200,0,0,0.7)" },
            // Token without -dark variant, light mode
            { name: "Neutral Light (No Dark Variant)", token: "neutral", theme: themeColorsJson, darkMode: false, expected: "#c0c0c0" },
            // Token without -dark variant, dark mode (should use base)
            { name: "Neutral Dark (No Dark Variant, Fallback)", token: "neutral", theme: themeColorsJson, darkMode: true, expected: "#c0c0c0" },
            // Token with L1/D1 suffix, light mode
            { name: "Neutral L1 Light", token: "neutral-L1", theme: themeColorsJson, darkMode: false, expected: "#d0d0d0" },
            // Token with L1/D1 suffix, dark mode
            { name: "Neutral L1 Dark", token: "neutral-L1", theme: themeColorsJson, darkMode: true, expected: "#b0b0b0" },
            // Custom value
            { name: "Custom Red", token: "custom:red", theme: themeColorsJson, darkMode: false, expected: "red" },
            { name: "Custom Hex", token: "custom:#123456", theme: themeColorsJson, darkMode: true, expected: "#123456" },
            // Unknown token
            { name: "Unknown Token Light", token: "unknown-token", theme: themeColorsJson, darkMode: false, expected: "unknown-token" },
            { name: "Unknown Token Dark", token: "unknown-token", theme: themeColorsJson, darkMode: true, expected: "unknown-token" },
            // Empty token
            { name: "Empty Token", token: "", theme: themeColorsJson, darkMode: false, expected: "" },
            // Malformed JSON (Go function should return error string)
            { name: "Malformed Theme JSON", token: "primary", theme: "{malformed_json", darkMode: false, expectedPrefix: "Error deserializing colorsThemeJson:" },
            // Argument type errors (Go function should return error string)
            // Note: syscall/js might coerce some types, but we test for explicit string/bool checks in Go
            // The Go code explicitly checks types, so these tests are valuable.
            { name: "Token not a string", token: 123, theme: themeColorsJson, darkMode: false, expected: "Error: sadsColorToken must be a string" },
            { name: "Theme not a string", token: "primary", theme: {}, darkMode: false, expected: "Error: colorsThemeJson must be a string" },
            { name: "DarkMode not a boolean", token: "primary", theme: themeColorsJson, darkMode: "true", expected: "Error: isDarkMode must be a boolean" },
        ];

        for (const tc of testCases) {
            let output;
            let isError = false;
            const inputs = { token: tc.token, theme: "/* elided for brevity in UI */", darkMode: tc.darkMode };
            if (tc.name === "Malformed Theme JSON") inputs.theme = tc.theme;


            try {
                // For the actual call, use the full theme tc.theme
                output = window.sadsPocWasm.resolveColor(tc.token, tc.theme, tc.darkMode);

                if (tc.expectedPrefix) {
                    if (typeof output === 'string' && output.startsWith(tc.expectedPrefix)) {
                        // Test passes
                    } else {
                        isError = true; // Mismatch
                    }
                } else if (output !== tc.expected) {
                    isError = true; // Mismatch
                }
            } catch (e) {
                output = `JavaScript Error: ${e.message}`;
                isError = true;
            }
            logResult(tc.name, inputs, output, isError);
        }

    } catch (err) {
        const errorMsg = `Error loading or running WASM module: ${err}`;
        console.error(errorMsg);
        logResult("WASM Initialization", { wasmPath }, errorMsg, true);
    }
}

// Run the main test function when the script is loaded
main().catch(console.error);
