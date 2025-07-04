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
 */
export function initSadsEngine() {
  // Check if SADSEngine constructor is available globally and if an instance doesn't already exist.
  if (typeof SADSEngine === "function" && !sadsEngineInstance) {
    sadsEngineInstance = new SADSEngine({
      // Custom theme overrides for the SADS engine can be passed here if needed.
      // e.g., colors: { 'primary-override': 'custom:blue' }
    });
    console.log("SADS Engine Initialized by sadsManager.");
    // Perform an initial application of styles to all SADS components on the page.
    reapplySadsStyles();
  } else if (sadsEngineInstance) {
    console.warn("SADS Engine already initialized. Re-applying styles.");
    reapplySadsStyles(); // If called again, ensure styles are fresh.
  } else if (typeof SADSEngine !== "function") {
    console.warn(
      "SADSEngine class not found globally. SADS styles will not be applied by sadsManager. Ensure sads-style-engine.js is loaded first."
    );
  }
}

/**
 * Re-applies SADS styles to all SADS components currently in the DOM.
 * SADS components are identified by the `data-sads-component` attribute.
 * This is useful after dynamic changes that might affect styling, such as:
 * - Theme changes (e.g., dark mode toggle).
 * - Dynamic content loading that adds new SADS components.
 * - Language changes that might alter text content and thus layout.
 * @public
 */
export function reapplySadsStyles() {
  if (sadsEngineInstance && typeof sadsEngineInstance.applyStylesTo === "function") {
    const components = document.querySelectorAll("[data-sads-component]");
    if (components.length > 0) {
      components.forEach((comp) => {
        // Optional: log which component is being re-styled for debugging.
        // console.log("sadsManager: Re-applying styles to component:", comp.dataset.sadsComponent);
        sadsEngineInstance.applyStylesTo(comp);
      });
      console.log(`SADS styles re-applied to ${components.length} component(s) by sadsManager.`);
    } else {
      // console.log("sadsManager: No SADS components found to re-apply styles to.");
    }
  } else {
    // This warning is helpful if SADS is expected to be running.
    if (typeof SADSEngine === "function" && !sadsEngineInstance) {
      console.warn(
        "sadsManager: SADSEngine class is available, but the instance is not. " +
        "Initialize the engine using initSadsEngine() before attempting to re-apply styles."
      );
    } else if (typeof SADSEngine !== "function") {
      // This case is covered by initSadsEngine, but good for explicitness if reapply is called independently.
      // console.warn("sadsManager: SADSEngine class not found. Cannot re-apply styles.");
    }
  }
}

/**
 * Retrieves the current singleton instance of the SADSEngine.
 * @returns {any | null} The SADS engine instance, or null if it has not been initialized.
 *                       In TypeScript, this would be `SADSEngine | null`.
 * @public
 */
export function getSadsEngineInstance() {
  return sadsEngineInstance;
}

// Note: Direct event listening (e.g., for dark mode changes) is not implemented within sadsManager.
// Instead, the main application orchestrator (app.js) is responsible for calling `reapplySadsStyles`
// after such events occur, promoting better separation of concerns.
