// public/ts/modules/wasmLoader.ts
/**
 * Handles the loading of WebAssembly (WASM) modules for the SADS project.
 */

// Minimal Go class definition based on wasm_exec.js usage
declare class Go {
  importObject: WebAssembly.Imports;
  run(instance: WebAssembly.Instance): Promise<void>;
}

// Define the expected structure of the sadsPocWasm global object
interface SadsPocWasm {
  resolveColor?: (token: string, themeColorsJson: string, isDarkMode: boolean) => string;
  resolveSadsValue?: (token: string, themeCategoryJson: string, categoryName: string, isDarkMode: boolean) => string;
  parseResponsiveRules?: (...args: any[]) => string; // Adjust if specific signature is known and stable
  // Add other exported Go functions here
}

// Augment the global Window interface
declare global {
  interface Window {
    sadsPocWasmReadyPromise?: Promise<SadsPocWasm>;
    sadsPocWasm?: SadsPocWasm;
    Go: typeof Go; // Constructor for Go
  }
}

(function () {
  window.sadsPocWasmReadyPromise = new Promise<SadsPocWasm>(async (resolve, reject) => {
    console.log("wasmLoader.ts: Initiating WASM loading sequence.");

    // Path to WASM assets.
    // The Go build command places sads_poc.wasm in public/js/.
    // wasm_exec.js is usually copied from GOROOT/misc/wasm/ to the same directory.
    // Assuming HTML files are served from project root or public/, paths relative to that.
    // If nl-sads-test.html is in public/, then "js/sads_poc.wasm"
    // If sads_wasm_poc/test_harness.html is served from sads_wasm_poc/, then "../public/js/sads_poc.wasm"
    // For this script, let's assume `wasm_exec.js` and `sads_poc.wasm` are in `public/js/`.
    // These paths are relative to the HTML file loading this script.
    // If app.js (in public/js) loads this, then paths should be relative to app.js or absolute from site root.
    // For simplicity, assuming this script is loaded by an HTML in public/, so paths like "js/..." work.
    const wasmExecPath = "js/wasm_exec.js";
    const sadsPocPath = "js/sads_poc.wasm";

    function loadScript(src: string): Promise<void> {
      return new Promise((scriptResolve, scriptReject) => {
        const script = document.createElement("script");
        script.src = src;
        script.async = true;
        script.onload = () => {
          console.log(`wasmLoader.ts: Successfully loaded script: ${src}`);
          scriptResolve();
        };
        script.onerror = (e) => {
          console.error(`wasmLoader.ts: Error loading script: ${src}`, e);
          scriptReject(new Error(`Failed to load script: ${src}`));
        };
        document.head.appendChild(script);
      });
    }

    try {
      await loadScript(wasmExecPath);

      if (typeof window.Go === "undefined") {
        console.error("wasmLoader.ts: Go global object not defined after loading wasm_exec.js.");
        return reject(new Error("Go global object not defined."));
      }
      console.log("wasmLoader.ts: Go object is defined.");

      const go = new window.Go();

      if (!WebAssembly.instantiateStreaming) {
        WebAssembly.instantiateStreaming = async (resp, importObject) => {
          const source = await (await resp).arrayBuffer();
          return await WebAssembly.instantiate(source, importObject);
        };
      }

      console.log(`wasmLoader.ts: Attempting to instantiate WASM module from: ${sadsPocPath}`);
      const result = await WebAssembly.instantiateStreaming(
        fetch(sadsPocPath),
        go.importObject
      );

      // Non-blocking run
      go.run(result.instance);

      setTimeout(() => {
        if (window.sadsPocWasm && (typeof window.sadsPocWasm.resolveColor === "function" || typeof window.sadsPocWasm.resolveSadsValue === "function")) {
          console.log("wasmLoader.ts: WASM module loaded and sadsPocWasm functions are available.");
          resolve(window.sadsPocWasm);
        } else {
          console.error("wasmLoader.ts: sadsPocWasm functions not found after WASM instantiation.");
          reject(new Error("sadsPocWasm functions not found after WASM instantiation."));
        }
      }, 100);
    } catch (error) {
      console.error("wasmLoader.ts: Error during WASM loading or instantiation:", error);
      reject(error);
    }
  });

  window.sadsPocWasmReadyPromise.catch((error) => {
    console.warn("wasmLoader.ts: sadsPocWasmReadyPromise was rejected.", error.message);
  });
})();

// Export nothing, this is a self-executing module setting up a global promise
export {};
