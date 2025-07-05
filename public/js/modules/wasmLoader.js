// public/js/modules/wasmLoader.js

/**
 * Handles the loading of WebAssembly (WASM) modules for the SADS project.
 * It loads the necessary JavaScript glue code (`wasm_exec.js`) and the
 * compiled WASM binary (`sads_poc.wasm`), then signals when the WASM
 * module's exported functions are ready to be called.
 */

(function () {
  // Create a promise that will resolve when WASM is ready, or reject on error.
  window.sadsPocWasmReadyPromise = new Promise(async (resolve, reject) => {
    console.log("wasmLoader.js: Initiating WASM loading sequence.");

    // Path to WASM assets - assuming they are copied to dist/assets/wasm/
    // and the HTML pages are served from dist/
    // So, the path relative to index.html (in dist/) would be assets/wasm/
    const wasmAssetsBasePath = "assets/wasm/";
    const wasmExecPath = wasmAssetsBasePath + "wasm_exec.js";
    const sadsPocPath = wasmAssetsBasePath + "sads_poc.wasm";

    // Function to load a script and return a promise
    function loadScript(src) {
      return new Promise((scriptResolve, scriptReject) => {
        const script = document.createElement("script");
        script.src = src;
        script.async = true;
        script.onload = () => {
          console.log(`wasmLoader.js: Successfully loaded script: ${src}`);
          scriptResolve();
        };
        script.onerror = (e) => {
          console.error(`wasmLoader.js: Error loading script: ${src}`, e);
          scriptReject(new Error(`Failed to load script: ${src}`));
        };
        document.head.appendChild(script);
      });
    }

    try {
      // 1. Load wasm_exec.js
      await loadScript(wasmExecPath);

      // Check if Go object is available
      if (typeof Go === "undefined") {
        console.error(
          "wasmLoader.js: Go global object not defined after loading wasm_exec.js. WASM setup cannot proceed."
        );
        return reject(new Error("Go global object not defined."));
      }
      console.log("wasmLoader.js: Go object is defined.");

      const go = new Go();

      // Polyfill for older browsers if necessary
      if (!WebAssembly.instantiateStreaming) {
        WebAssembly.instantiateStreaming = async (resp, importObject) => {
          const source = await (await resp).arrayBuffer();
          return await WebAssembly.instantiate(source, importObject);
        };
      }

      console.log(
        `wasmLoader.js: Attempting to instantiate WASM module from: ${sadsPocPath}`
      );
      const result = await WebAssembly.instantiateStreaming(
        fetch(sadsPocPath),
        go.importObject
      );

      // It's important to run the Go instance in a non-blocking way if other JS needs to execute.
      // However, go.run() itself will block until the Go main function exits.
      // For our sads_poc.wasm, main() blocks indefinitely with a channel,
      // so we run it without await here to allow the promise to resolve sooner.
      // The exported functions will be available on `window.sadsPocWasm` set by the Go main.
      go.run(result.instance); // This starts the Go program.

      // Check if the WASM module has set up its global namespace
      // This might need a slight delay or a more robust check if go.run() is truly async
      // in its effects on `window`. For now, assume it's quick enough.
      // A better way might be for Go to call a JS function when it's ready.
      // For this PoC, we'll check for window.sadsPocWasm.

      // Short delay to allow Go's main to execute and set up the global.
      setTimeout(() => {
        if (
          window.sadsPocWasm &&
          typeof window.sadsPocWasm.resolveColor === "function"
        ) {
          console.log(
            "wasmLoader.js: WASM module loaded and sadsPocWasm.resolveColor is available."
          );
          resolve(window.sadsPocWasm);
        } else {
          console.error(
            "wasmLoader.js: sadsPocWasm.resolveColor not found after WASM instantiation. Timing issue or Go export error?"
          );
          reject(
            new Error(
              "sadsPocWasm.resolveColor not found after WASM instantiation."
            )
          );
        }
      }, 100); // 100ms delay, adjust if needed
    } catch (error) {
      console.error(
        "wasmLoader.js: Error during WASM loading or instantiation:",
        error
      );
      reject(error);
    }
  });

  // Optional: Handle unhandled promise rejections for this specific promise for better debugging
  window.sadsPocWasmReadyPromise.catch((error) => {
    console.warn(
      "wasmLoader.js: sadsPocWasmReadyPromise was rejected.",
      error.message
    );
    // This doesn't prevent other .catch() handlers from running.
  });
})();
