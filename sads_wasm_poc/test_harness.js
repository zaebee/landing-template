// sads_wasm_poc/test_harness.js

async function main() {
  const resultsContainer = document.getElementById("results-container");

  function logResult(testCaseName, inputs, output, error = false) {
    console.groupCollapsed(`Test Case: ${testCaseName}`);
    console.log("Inputs:", inputs);
    if (error) {
      console.error("Output (Error):", output);
    } else {
      console.log("Output (Success):", output);
    }
    console.groupEnd();

    const entry = document.createElement("div");
    entry.classList.add("log-entry");
    entry.innerHTML = `
            <p><strong>Test Case:</strong> ${testCaseName}</p>
            <p><span class="log-input">Inputs:</span> <code>${JSON.stringify(inputs)}</code></p>
            <p><span class="${error ? "log-error" : "log-output"}">Output:</span> <code>${output}</code></p>
        `;
    resultsContainer.appendChild(entry);
  }

  if (!WebAssembly.instantiateStreaming) {
    // Polyfill for older browsers
    WebAssembly.instantiateStreaming = async (resp, importObject) => {
      const source = await (await resp).arrayBuffer();
      return await WebAssembly.instantiate(source, importObject);
    };
  }

  const go = new Go();
  const wasmPath = "/public/dist/assets/wasm/sads_poc.wasm"; // Expected name of the compiled WASM file

  try {
    console.log(`Attempting to load WASM module from: ${wasmPath}`);
    const result = await WebAssembly.instantiateStreaming(
      fetch(wasmPath),
      go.importObject
    );
    go.run(result.instance);
    console.log("WASM module loaded and Go program started.");

    if (
      !window.sadsPocWasm ||
      typeof window.sadsPocWasm.resolveColor !== "function"
    ) {
      const errorMsg =
        "Error: sadsPocWasm.resolveColor function not found on window. Check Go export in main().";
      console.error(errorMsg);
      logResult("WASM Load Check", { wasmPath }, errorMsg, true);
      return;
    }
    logResult(
      "WASM Load Check",
      { wasmPath },
      "sadsPocWasm.resolveColor found on window.",
      false
    );

    // --- Test Cases ---

    const defaultThemeColors = {
      primary: "#007bff",
      "primary-dark": "#0056b3",
      secondary: "#6c757d",
      "secondary-dark": "#494f54",
      accent: "rgba(255,0,0,0.7)",
      "accent-dark": "rgba(200,0,0,0.7)",
      surface: "#ffffff",
      "surface-dark": "#2a2a2a",
      "text-primary": "#212529",
      "text-primary-dark": "#f8f9fa",
      "text-secondary": "#6c757d",
      "text-secondary-dark": "#adb5bd",
      neutral: "#c0c0c0",
      "neutral-L1": "#d0d0d0",
      "neutral-L1-dark": "#b0b0b0",
      "neutral-D1": "#a0a0a0",
      "neutral-D1-dark": "#909090",
    };
    const themeColorsJson = JSON.stringify(defaultThemeColors);

    const defaultThemeSpacing = { s: "4px", m: "8px", l: "16px" };
    const themeSpacingJson = JSON.stringify(defaultThemeSpacing);

    const defaultThemeFontSize = { default: "1rem", large: "1.25rem" };
    const themeFontSizeJson = JSON.stringify(defaultThemeFontSize);

    // Empty objects for other theme parts not directly tested by responsive rules value resolution here,
    // but needed by the function signature.
    const emptyThemePartJson = JSON.stringify({});

    // --- Test Cases for resolveSadsValue (and by extension resolveColor) ---
    if (window.sadsPocWasm && window.sadsPocWasm.resolveSadsValue) {
      console.log("--- Testing resolveSadsValue ---");
      const valueTestCases = [
        {
          name: "Color Primary Light",
          token: "primary",
          categoryJson: themeColorsJson,
          categoryName: "colors",
          darkMode: false,
          expected: "#007bff",
        },
        {
          name: "Color Primary Dark",
          token: "primary",
          categoryJson: themeColorsJson,
          categoryName: "colors",
          darkMode: true,
          expected: "#0056b3",
        },
        {
          name: "Color Custom Red",
          token: "custom:red",
          categoryJson: themeColorsJson,
          categoryName: "colors",
          darkMode: false,
          expected: "red",
        },
        {
          name: "Spacing M",
          token: "m",
          categoryJson: themeSpacingJson,
          categoryName: "spacing",
          darkMode: false,
          expected: "8px",
        },
        {
          name: "Spacing Custom 10px",
          token: "custom:10px",
          categoryJson: themeSpacingJson,
          categoryName: "spacing",
          darkMode: false,
          expected: "10px",
        },
        {
          name: "Unknown Spacing Token",
          token: "xl",
          categoryJson: themeSpacingJson,
          categoryName: "spacing",
          darkMode: false,
          expected: "xl",
        }, // Falls back to token
        {
          name: "Font Size Large",
          token: "large",
          categoryJson: themeFontSizeJson,
          categoryName: "fontSize",
          darkMode: false,
          expected: "1.25rem",
        },
      ];

      for (const tc of valueTestCases) {
        let output;
        let isError = false;
        const inputs = {
          token: tc.token,
          categoryName: tc.categoryName,
          darkMode: tc.darkMode,
          themeCategoryJson: "/* elided */",
        };
        try {
          output = window.sadsPocWasm.resolveSadsValue(
            tc.token,
            tc.categoryJson,
            tc.categoryName,
            tc.darkMode
          );
          if (output !== tc.expected) isError = true;
        } catch (e) {
          output = `JavaScript Error: ${e.message}`;
          isError = true;
        }
        logResult(`resolveSadsValue: ${tc.name}`, inputs, output, isError);
      }
    } else {
      logResult(
        "WASM Function Check",
        {},
        "window.sadsPocWasm.resolveSadsValue not found.",
        true
      );
    }

    // --- Test Cases for parseResponsiveRules ---
    if (window.sadsPocWasm && window.sadsPocWasm.parseResponsiveRules) {
      console.log("--- Testing parseResponsiveRules ---");
      const themeBreakpoints = {
        mobile: "(max-width: 600px)",
        tablet: "(min-width: 601px)",
      };
      const breakpointsJson = JSON.stringify(themeBreakpoints);

      const responsiveTestCases = [
        {
          name: "Simple padding on mobile",
          rules: JSON.stringify([
            { breakpoint: "mobile", styles: { padding: "s" } },
          ]),
          darkMode: false,
          expected: JSON.stringify({
            "(max-width: 600px)": "padding: 4px !important;\n",
          }),
        },
        {
          name: "Color and spacing on tablet, dark mode",
          rules: JSON.stringify([
            {
              breakpoint: "tablet",
              styles: { bgColor: "primary", margin: "m" },
            },
          ]),
          darkMode: true,
          expected: JSON.stringify({
            "(min-width: 601px)":
              "background-color: #0056b3 !important;\nmargin: 8px !important;\n",
          }),
        },
        {
          name: "Multiple rules, mixed values",
          rules: JSON.stringify([
            {
              breakpoint: "mobile",
              styles: { textColor: "accent", fontSize: "large" },
            },
            { breakpoint: "tablet", styles: { padding: "custom:20px" } },
          ]),
          darkMode: false,
          expected: JSON.stringify({
            "(max-width: 600px)":
              "color: red !important;\nfont-size: 1.25rem !important;\n",
            "(min-width: 601px)": "padding: 20px !important;\n",
          }),
        },
        {
          name: "Unknown breakpoint key (used as raw query)",
          rules: JSON.stringify([
            { breakpoint: "(min-height: 500px)", styles: { padding: "l" } },
          ]),
          darkMode: false,
          expected: JSON.stringify({
            "(min-height: 500px)": "padding: 16px !important;\n",
          }),
        },
        {
          name: "Empty rules string",
          rules: "",
          darkMode: false,
          // Go side parses "" as invalid JSON for array, so error is expected.
          // If it were `[]`, then expected would be `{}`.
          expectedPrefix: "Error parsing rulesJSON:",
        },
        {
          name: "Malformed rules JSON",
          rules: "[{breakpoint: 'mobile', styles: {padding: 's'}", // Malformed
          darkMode: false,
          expectedPrefix: "Error parsing rulesJSON:",
        },
        {
          name: "Malformed breakpoints JSON",
          rules: JSON.stringify([
            { breakpoint: "mobile", styles: { padding: "s" } },
          ]),
          breakpointsOverride: "{malformed_json", // Malformed
          darkMode: false,
          expectedPrefix: "Error parsing breakpointsJSON:",
        },
      ];

      for (const tc of responsiveTestCases) {
        let output;
        let isError = false;
        const currentBreakpointsJson =
          tc.breakpointsOverride || breakpointsJson;
        const inputs = {
          rules: tc.rules,
          breakpoints: "/* elided */",
          darkMode: tc.darkMode,
        };

        try {
          output = window.sadsPocWasm.parseResponsiveRules(
            tc.rules,
            currentBreakpointsJson,
            themeColorsJson,
            themeSpacingJson,
            themeFontSizeJson,
            emptyThemePartJson,
            emptyThemePartJson,
            emptyThemePartJson, // fontWeight, borderStyle, borderRadius
            emptyThemePartJson,
            emptyThemePartJson,
            emptyThemePartJson, // shadow, maxWidth, flexBasis
            emptyThemePartJson, // objectFit
            tc.darkMode
          );
          // Compare JSON strings after parsing and re-stringifying for consistent key order (though Go map order isn't guaranteed)
          // For simplicity, direct string compare for non-error cases. For errors, prefix check.
          if (tc.expectedPrefix) {
            if (
              typeof output === "string" &&
              output.startsWith(tc.expectedPrefix)
            ) {
              /* Pass */
            } else {
              isError = true;
            }
          } else {
            // Deep compare for non-error JSON results
            try {
              const outputObj = JSON.parse(output);
              const expectedObj = JSON.parse(tc.expected);
              if (JSON.stringify(outputObj) !== JSON.stringify(expectedObj)) {
                // Basic deep compare
                // A more robust deep equal would be better for complex objects
                if (
                  Object.keys(outputObj).length !==
                  Object.keys(expectedObj).length
                )
                  isError = true;
                for (const key in expectedObj) {
                  if (outputObj[key] !== expectedObj[key]) isError = true;
                }
                for (const key in outputObj) {
                  // Check for extra keys
                  if (expectedObj[key] === undefined) isError = true;
                }
              }
            } catch (parseErr) {
              isError = true;
              output += ` (Parse Error: ${parseErr.message})`;
            }
          }
        } catch (e) {
          output = `JavaScript Error: ${e.message}`;
          isError = true;
        }
        logResult(`parseResponsiveRules: ${tc.name}`, inputs, output, isError);
      }
    } else {
      logResult(
        "WASM Function Check",
        {},
        "window.sadsPocWasm.parseResponsiveRules not found.",
        true
      );
    }
  } catch (err) {
    const errorMsg = `Error loading or running WASM module: ${err}`;
    console.error(errorMsg);
    logResult("WASM Initialization", { wasmPath }, errorMsg, true);
  }
}

// Run the main test function when the script is loaded
main().catch(console.error);

// --- Benchmarking Section ---

function jsResolveSadsValue(
  token,
  themeCategoryJson,
  categoryName,
  isDarkMode
) {
  if (token === "") return "";
  if (token.startsWith("custom:")) {
    return token.substring("custom:".length);
  }

  const categoryMap = JSON.parse(themeCategoryJson);

  if (categoryName === "colors") {
    if (isDarkMode) {
      const darkTokenKey = token + "-dark";
      if (categoryMap[darkTokenKey] !== undefined) {
        return categoryMap[darkTokenKey];
      }
    }
    if (categoryMap[token] !== undefined) {
      return categoryMap[token];
    }
    return token;
  }

  if (categoryMap[token] !== undefined) {
    return categoryMap[token];
  }
  return token;
}

function jsMapSadsPropertyToCss(sadsPropertyKey) {
  if (!sadsPropertyKey) return null;
  let key = sadsPropertyKey.charAt(0).toLowerCase() + sadsPropertyKey.slice(1);
  let kebabKey = key.replace(/([A-Z])/g, (g) => `-${g[0].toLowerCase()}`);

  const propertyMap = {
    "bg-color": "background-color",
    "text-color": "color",
    "font-size": "font-size",
    "font-weight": "font-weight",
    "font-style": "font-style",
    "text-align": "text-align",
    "text-decoration": "text-decoration",
    "border-radius": "border-radius",
    "border-width": "border-width",
    "border-style": "border-style",
    "border-color": "border-color",
    "max-width": "max-width",
    width: "width",
    height: "height",
    display: "display",
    "flex-direction": "flex-direction",
    "flex-wrap": "flex-wrap",
    "flex-justify": "justify-content",
    "flex-align-items": "align-items",
    "flex-basis": "flex-basis",
    gap: "gap",
    shadow: "box-shadow",
    "object-fit": "object-fit",
    padding: "padding",
    "padding-top": "padding-top",
    "padding-bottom": "padding-bottom",
    "padding-left": "padding-left",
    "padding-right": "padding-right",
    margin: "margin",
    "margin-top": "margin-top",
    "margin-bottom": "margin-bottom",
    "margin-left": "margin-left",
    "margin-right": "margin-right",
    position: "position",
    top: "top",
    left: "left",
    right: "right",
    bottom: "bottom",
    "z-index": "z-index",
    overflow: "overflow",
    "list-style": "list-style",
    "border-bottom-width": "border-bottom-width",
    "border-bottom-style": "border-bottom-style",
    "border-bottom-color": "border-bottom-color",
    "min-height": "min-height",
    "flex-grow": "flex-grow",
    "grid-template-columns": "grid-template-columns",
    resize: "resize",
    cursor: "cursor",
    transition: "transition",
    "box-sizing": "box-sizing",
  };
  if (kebabKey === "layout-type") return null;
  if (propertyMap.hasOwnProperty(kebabKey)) return propertyMap[kebabKey];
  return kebabKey;
}

function jsParseResponsiveRules(
  rulesString,
  breakpointsJson,
  themeColorsJson,
  themeSpacingJson,
  themeFontSizeJson,
  isDarkMode,
  _themeOtherPartsNotUsedInJsVersion
) {
  if (!rulesString) return {};

  const themeBreakpoints = JSON.parse(breakpointsJson);
  // In a full JS equivalent, we'd need all theme parts structured as in SADS engine.
  // For this benchmark, jsResolveSadsValue is simplified and takes individual category JSON.

  const responsiveStyles = {};
  try {
    const parsedRules = JSON.parse(rulesString);
    parsedRules.forEach((rule) => {
      const breakpointKey = rule.breakpoint;
      const bpQuery = themeBreakpoints[breakpointKey] || breakpointKey;
      responsiveStyles[bpQuery] = responsiveStyles[bpQuery] || "";

      for (const [respSadsPropKey, respSemanticVal] of Object.entries(
        rule.styles
      )) {
        const cssProp = jsMapSadsPropertyToCss(respSadsPropKey);
        let actualVal;
        // Simplified category determination for JS benchmark version
        if (
          cssProp &&
          (cssProp.includes("color") || cssProp.includes("Color"))
        ) {
          actualVal = jsResolveSadsValue(
            respSemanticVal,
            themeColorsJson,
            "colors",
            isDarkMode
          );
        } else if (
          cssProp &&
          (cssProp.includes("padding") ||
            cssProp.includes("margin") ||
            cssProp.includes("gap") ||
            cssProp.includes("width") ||
            cssProp.includes("height") ||
            cssProp.includes("border-width"))
        ) {
          actualVal = jsResolveSadsValue(
            respSemanticVal,
            themeSpacingJson,
            "spacing",
            isDarkMode
          );
        } else if (cssProp && cssProp.includes("font-size")) {
          actualVal = jsResolveSadsValue(
            respSemanticVal,
            themeFontSizeJson,
            "fontSize",
            isDarkMode
          );
        } else if (respSemanticVal.startsWith("custom:")) {
          actualVal = respSemanticVal.substring("custom:".length);
        } else {
          actualVal = respSemanticVal;
        }

        if (cssProp && actualVal !== null && actualVal !== undefined) {
          responsiveStyles[bpQuery] += `${cssProp}: ${actualVal} !important;\n`;
        }
      }
    });
  } catch (e) {
    console.error("JS Error parsing responsive rules:", e, rulesString);
    return { error: e.message };
  }
  return responsiveStyles;
}

async function runBenchmark(fnName, funcToTest, argsArray, iterations = 10000) {
  const resultsContainer = document.getElementById("results-container");
  let totalTime = 0;
  let lastResult;

  // Warm-up run (optional, can help stabilize JIT for JS)
  // for (let i = 0; i < Math.min(iterations / 10, 100); i++) {
  //     funcToTest.apply(null, argsArray);
  // }

  console.log(`Benchmarking ${fnName} for ${iterations} iterations...`);
  const startTime = performance.now();
  for (let i = 0; i < iterations; i++) {
    lastResult = funcToTest.apply(null, argsArray);
  }
  totalTime = performance.now() - startTime;

  const timePerIteration = totalTime / iterations;
  const message = `${fnName}: ${iterations} iterations took ${totalTime.toFixed(3)}ms. Avg: ${timePerIteration.toFixed(5)}ms/op. Last result: ${JSON.stringify(lastResult)}`;
  console.log(message);

  const entry = document.createElement("div");
  entry.classList.add("log-entry", "benchmark-result");
  entry.innerHTML = `<p><strong>Benchmark: ${fnName}</strong></p><p>${message}</p>`;
  resultsContainer.appendChild(entry);
  return { totalTime, timePerIteration, lastResult };
}

// Add a button or trigger to run benchmarks after WASM is loaded
// For now, auto-run after tests if WASM is available
if (window.sadsPocWasm) {
  setTimeout(async () => {
    // Ensure tests have run and console is clear
    console.log("\n--- Starting Benchmarks ---");
    const resultsContainer = document.getElementById("results-container");
    const benchmarkHeader = document.createElement("h2");
    benchmarkHeader.textContent = "Benchmark Results";
    resultsContainer.appendChild(benchmarkHeader);

    const iterations = 20000; // Number of iterations for each benchmark

    // Benchmark data (reusing some from tests)
    const defaultThemeColors = {
      primary: "#007bff",
      "primary-dark": "#0056b3",
      surface: "#ffffff",
      "surface-dark": "#2a2a2a",
      accent: "red",
    };
    const themeColorsJson = JSON.stringify(defaultThemeColors);
    const defaultThemeSpacing = { s: "4px", m: "8px", l: "16px" };
    const themeSpacingJson = JSON.stringify(defaultThemeSpacing);
    const defaultThemeFontSize = { default: "1rem", large: "1.25rem" };
    const themeFontSizeJson = JSON.stringify(defaultThemeFontSize);
    const emptyThemePartJson = JSON.stringify({});
    const themeBreakpoints = {
      mobile: "(max-width: 600px)",
      tablet: "(min-width: 601px)",
    };
    const breakpointsJson = JSON.stringify(themeBreakpoints);

    // 1. Benchmark resolveSadsValue (color)
    await runBenchmark(
      "JS: resolveSadsValue (color)",
      jsResolveSadsValue,
      ["primary", themeColorsJson, "colors", false],
      iterations
    );
    await runBenchmark(
      "WASM: resolveSadsValue (color)",
      window.sadsPocWasm.resolveSadsValue,
      ["primary", themeColorsJson, "colors", false],
      iterations
    );

    await runBenchmark(
      "JS: resolveSadsValue (color dark)",
      jsResolveSadsValue,
      ["surface", themeColorsJson, "colors", true],
      iterations
    );
    await runBenchmark(
      "WASM: resolveSadsValue (color dark)",
      window.sadsPocWasm.resolveSadsValue,
      ["surface", themeColorsJson, "colors", true],
      iterations
    );

    // 2. Benchmark resolveSadsValue (spacing)
    await runBenchmark(
      "JS: resolveSadsValue (spacing)",
      jsResolveSadsValue,
      ["m", themeSpacingJson, "spacing", false],
      iterations
    );
    await runBenchmark(
      "WASM: resolveSadsValue (spacing)",
      window.sadsPocWasm.resolveSadsValue,
      ["m", themeSpacingJson, "spacing", false],
      iterations
    );

    // 3. Benchmark resolveSadsValue (custom)
    await runBenchmark(
      "JS: resolveSadsValue (custom)",
      jsResolveSadsValue,
      ["custom:123px", themeSpacingJson, "spacing", false],
      iterations
    );
    await runBenchmark(
      "WASM: resolveSadsValue (custom)",
      window.sadsPocWasm.resolveSadsValue,
      ["custom:123px", themeSpacingJson, "spacing", false],
      iterations
    );

    // 4. Benchmark parseResponsiveRules
    const responsiveRules1 = JSON.stringify([
      { breakpoint: "mobile", styles: { padding: "s", bgColor: "primary" } },
    ]);
    const responsiveRules2 = JSON.stringify([
      {
        breakpoint: "mobile",
        styles: { textColor: "accent", fontSize: "large", margin: "m" },
      },
      {
        breakpoint: "tablet",
        styles: { padding: "custom:20px", bgColor: "surface" },
      },
    ]);

    const jsParseArgs1 = [
      responsiveRules1,
      breakpointsJson,
      themeColorsJson,
      themeSpacingJson,
      themeFontSizeJson,
      false,
      {},
    ];
    const wasmParseArgs1 = [
      responsiveRules1,
      breakpointsJson,
      themeColorsJson,
      themeSpacingJson,
      themeFontSizeJson,
      emptyThemePartJson,
      emptyThemePartJson,
      emptyThemePartJson,
      emptyThemePartJson,
      emptyThemePartJson,
      emptyThemePartJson,
      emptyThemePartJson,
      false,
    ];

    await runBenchmark(
      "JS: parseResponsiveRules (simple)",
      jsParseResponsiveRules,
      jsParseArgs1,
      iterations / 100
    ); // Fewer iterations for complex func
    await runBenchmark(
      "WASM: parseResponsiveRules (simple)",
      window.sadsPocWasm.parseResponsiveRules,
      wasmParseArgs1,
      iterations / 100
    );

    const jsParseArgs2 = [
      responsiveRules2,
      breakpointsJson,
      themeColorsJson,
      themeSpacingJson,
      themeFontSizeJson,
      true,
      {},
    ];
    const wasmParseArgs2 = [
      responsiveRules2,
      breakpointsJson,
      themeColorsJson,
      themeSpacingJson,
      themeFontSizeJson,
      emptyThemePartJson,
      emptyThemePartJson,
      emptyThemePartJson,
      emptyThemePartJson,
      emptyThemePartJson,
      emptyThemePartJson,
      emptyThemePartJson,
      true,
    ];

    await runBenchmark(
      "JS: parseResponsiveRules (complex, dark)",
      jsParseResponsiveRules,
      jsParseArgs2,
      iterations / 100
    );
    await runBenchmark(
      "WASM: parseResponsiveRules (complex, dark)",
      window.sadsPocWasm.parseResponsiveRules,
      wasmParseArgs2,
      iterations / 100
    );

    console.log("--- Benchmarks Completed ---");
  }, 2000); // Delay to ensure test logs are flushed
}
