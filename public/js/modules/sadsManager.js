// public/js/modules/sadsManager.js
/**
 * @file Manages the initialization and interaction with the SADS (Semantic Attribute-Driven Styling) engine.
 * Assumes `SADSEngine` class is globally available from `sads-style-engine.js`.
 */

// Forward declaration for type hinting if SADSEngine was an importable module.
// For now, we assume it's global.
// /** @typedef {import('./sads-style-engine.js').SADSEngine} SADSEngine */

/**
 * Holds the singleton instance of the SADSEngine.
 * Type is `any` for now as `SADSEngine` is global and not formally typed here.
 * In a TypeScript environment, this would be `SADSEngine | null`.
 * @type {any | null}
 */
let sadsEngineInstance = null;

/**
 * Initializes the SADS (Semantic Attribute-Driven Styling) Engine.
 * This function should be called after the `SADSEngine` class definition
 * (from `sads-style-engine.js`) has been loaded and executed.
 * It creates a singleton instance of the engine and applies styles to all SADS components.
 * @public
 * @async
 */
async function initSadsEngine() {
  // Check if SADSEngine constructor is available globally and if an instance doesn't already exist.
  if (typeof SADSEngine === "function" && !sadsEngineInstance) {
    sadsEngineInstance = new SADSEngine({
      // Custom theme overrides for the SADS engine can be passed here if needed.
      // e.g., colors: { 'primary-override': 'custom:blue' }
    });
    console.log("SADS Engine Initialized by sadsManager.");
    // Perform an initial application of styles to all SADS components on the page.
    await reapplySadsStyles(); // Now awaits the async style application
  } else if (sadsEngineInstance) {
    console.warn("SADS Engine already initialized. Re-applying styles.");
    await reapplySadsStyles(); // If called again, ensure styles are fresh.
  } else if (typeof SADSEngine !== "function") {
    console.warn(
      "SADSEngine class not found globally. SADS styles will not be applied by sadsManager. Ensure sads-style-engine.js is loaded first."
    );
  }
}

/**
 * Re-applies SADS styles to all SADS components currently in the DOM.
 * This now calls the async `applyStyles` method on the SADSEngine instance.
 * @public
 * @async
 */
async function reapplySadsStyles() {
  if (
    sadsEngineInstance &&
    typeof sadsEngineInstance.applyStyles === "function" // Check for the new async method
  ) {
    try {
      await sadsEngineInstance.applyStyles(); // Call the new async method
      // console.log("SADS styles re-applied by sadsManager using new async applyStyles.");
    } catch (error) {
      console.error("sadsManager: Error during sadsEngineInstance.applyStyles():", error);
    }
  } else {
    if (typeof SADSEngine === "function" && !sadsEngineInstance) {
      console.warn(
        "sadsManager: SADSEngine class is available, but the instance is not. " +
          "Initialize the engine using initSadsEngine() before attempting to re-apply styles."
      );
    } else if (typeof SADSEngine !== "function") {
      // console.warn("sadsManager: SADSEngine class not found. Cannot re-apply styles.");
    } else if (sadsEngineInstance && typeof sadsEngineInstance.applyStyles !== "function") {
      console.error("sadsManager: sadsEngineInstance.applyStyles() is not a function. Did the SADS Engine change?");
    }
  }
}

/**
 * Retrieves the current singleton instance of the SADSEngine.
 * @returns {any | null} The SADS engine instance, or null if it has not been initialized.
 *                       In TypeScript, this would be `SADSEngine | null`.
 * @public
 */
function getSadsEngineInstance() {
  return sadsEngineInstance;
}

// Note: Direct event listening (e.g., for dark mode changes) is not implemented within sadsManager.
// Instead, the main application orchestrator (app.js) is responsible for calling `reapplySadsStyles`
// after such events occur, promoting better separation of concerns.
