// public/ts/modules/sadsManager.ts
/**
 * @file Manages the initialization and interaction with the SADS (Semantic Attribute-Driven Styling) engine.
 */

import { SADSEngine } from '../sads-style-engine.js'; // Path relative to output dir after compilation
// sads-default-theme is typically passed during SADSEngine instantiation if not using global
// If sadsDefaultTheme is needed directly here, it should also be imported.

let sadsEngineInstance: SADSEngine | null = null;

/**
 * Initializes the SADS (Semantic Attribute-Driven Styling) Engine.
 * Creates a singleton instance of the engine and applies styles to all SADS components.
 * @public
 * @async
 */
export async function initSadsEngine(): Promise<void> {
  // Check if SADSEngine constructor is available and if an instance doesn't already exist.
  // SADSEngine is imported, so `typeof SADSEngine` check is for class availability.
  if (SADSEngine && !sadsEngineInstance) {
    // Accessing global sadsDefaultTheme. If it's also a module, it should be imported.
    const defaultTheme = (window as any).sadsDefaultTheme || {};
    sadsEngineInstance = new SADSEngine({}, defaultTheme);
    console.log("SADS Engine Initialized by sadsManager.");
    await reapplySadsStyles();
  } else if (sadsEngineInstance) {
    console.warn("SADS Engine already initialized. Re-applying styles.");
    await reapplySadsStyles();
  } else { // SADSEngine class itself was not available (should not happen with imports)
    console.error(
      "SADSEngine class not found. SADS styles will not be applied by sadsManager."
    );
  }
}

/**
 * Re-applies SADS styles to all SADS components currently in the DOM.
 * Calls the async `applyStyles` method on the SADSEngine instance.
 * @public
 * @async
 */
export async function reapplySadsStyles(): Promise<void> {
  if (sadsEngineInstance && typeof sadsEngineInstance.applyStyles === "function") {
    try {
      await sadsEngineInstance.applyStyles();
      // console.log("SADS styles re-applied by sadsManager.");
    } catch (error) {
      console.error("sadsManager: Error during sadsEngineInstance.applyStyles():", error);
    }
  } else {
    if (!sadsEngineInstance) {
      console.warn(
        "sadsManager: SADSEngine instance is not available. " +
        "Initialize the engine using initSadsEngine() before attempting to re-apply styles."
      );
    } else if (typeof sadsEngineInstance.applyStyles !== "function") {
      console.error(
        "sadsManager: sadsEngineInstance.applyStyles() is not a function. Did the SADS Engine change?"
      );
    }
  }
}

/**
 * Retrieves the current singleton instance of the SADSEngine.
 * @returns {SADSEngine | null} The SADS engine instance, or null if it has not been initialized.
 * @public
 */
export function getSadsEngineInstance(): SADSEngine | null {
  return sadsEngineInstance;
}
